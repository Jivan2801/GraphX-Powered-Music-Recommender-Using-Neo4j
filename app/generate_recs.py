import argparse
from pathlib import Path

import pandas as pd


def load_spark_single_csv(dir_path: Path) -> pd.DataFrame:
    """
    Spark writes each dataset as a folder with one part-*.csv file.
    This helper finds that file and loads it with pandas.
    """
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    csv_files = [p for p in dir_path.glob("*.csv") if not p.name.startswith("_")]
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {dir_path}")

    return pd.read_csv(csv_files[0])


def normalize_column(df: pd.DataFrame, col: str, new_col: str) -> None:
    """Min–max normalize df[col] into [0, 1] and store in df[new_col]."""
    if col not in df.columns:
        df[new_col] = 0.0
        return

    col_min = df[col].min()
    col_max = df[col].max()

    if pd.isna(col_min) or pd.isna(col_max) or col_min == col_max:
        df[new_col] = 0.0
    else:
        df[new_col] = (df[col] - col_min) / (col_max - col_min)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Top-K song recommendations for a user."
    )
    parser.add_argument(
        "--user_id",
        type=str,
        help="User ID to generate recommendations for. "
             "If omitted, the script will pick a 'top' user from sample history."
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=20,
        help="Number of recommendations to output (default: 20).",
    )
    args = parser.parse_args()

    project_root = Path(".").resolve()
    print("Project root:", project_root)

    # ---------- Paths ----------
    # User listening history: prefer sample (smaller), fall back to full if needed
    sample_history_path = project_root / "data_processed" / "sample" / "user_listening_history_sample.csv"
    full_history_path = project_root / "data_processed" / "graph_for_spark" / "listened_edges.csv"

    if sample_history_path.exists():
        history_path = sample_history_path
        print("Using SAMPLE history:", history_path)
    else:
        history_path = full_history_path
        print("Using FULL history (may be large):", history_path)

    # Song metadata (processed by ETL)
    songs_path = project_root / "data_processed" / "graph_for_spark" / "songs.csv"

    # Spark outputs
    spark_out_dir = project_root / "data_processed" / "spark_outputs"
    pop_dir = spark_out_dir / "song_popularity_top1000.csv"
    pr_dir = spark_out_dir / "song_pagerank_top1000.csv"
    pairs_dir = spark_out_dir / "song_co_listen_pairs_top1000.csv"

    # Output recommendations dir
    recs_dir = project_root / "data_processed" / "recs"
    recs_dir.mkdir(parents=True, exist_ok=True)

    # ---------- Load data ----------
    history_df = pd.read_csv(history_path)
    print("History rows:", len(history_df))

    songs_df = pd.read_csv(songs_path)
    print("Songs rows (metadata):", len(songs_df))

    popularity_df = load_spark_single_csv(pop_dir)
    print("Loaded popularity:", popularity_df.shape)

    pagerank_df = load_spark_single_csv(pr_dir)
    print("Loaded pagerank:", pagerank_df.shape)

    pairs_df = load_spark_single_csv(pairs_dir)
    print("Loaded co-listen pairs:", pairs_df.shape)

    # Ensure consistent column names / types
    history_df["track_id"] = history_df["track_id"].astype(str)
    history_df["user_id"] = history_df["user_id"].astype(str)
    songs_df["track_id"] = songs_df["track_id"].astype(str)
    popularity_df["track_id"] = popularity_df["track_id"].astype(str)
    pagerank_df["track_id"] = pagerank_df["track_id"].astype(str)
    pairs_df["track_id_1"] = pairs_df["track_id_1"].astype(str)
    pairs_df["track_id_2"] = pairs_df["track_id_2"].astype(str)

    # ---------- Choose user ----------
    if args.user_id:
        target_user = args.user_id
    else:
        # auto-pick a "top" user from the history
        user_counts = history_df.groupby("user_id")["track_id"].nunique()
        target_user = user_counts.sort_values(ascending=False).index[0]

    print(f"\nTarget user: {target_user}")

    user_history = history_df[history_df["user_id"] == target_user]
    if user_history.empty:
        print(f"No history found for user {target_user}.")
        return

    seed_tracks = set(user_history["track_id"].unique())
    print(f"Tracks listened by user: {len(seed_tracks)}")

    # ---------- Candidate generation via co-listen pairs ----------
    # Keep only pairs where either side is in seed_tracks
    mask = pairs_df["track_id_1"].isin(seed_tracks) | pairs_df["track_id_2"].isin(seed_tracks)
    pairs_user = pairs_df[mask].copy()

    if pairs_user.empty:
        print("No co-listen pairs intersect with this user's tracks. "
              "Try another user or re-run Spark step with different limits.")
        return

    def candidate_from_row(row):
        if row["track_id_1"] in seed_tracks:
            return row["track_id_2"]
        else:
            return row["track_id_1"]

    pairs_user["candidate_track_id"] = pairs_user.apply(candidate_from_row, axis=1)

    # Sum co_listen_count per candidate
    cf_scores = (
        pairs_user.groupby("candidate_track_id")["co_listen_count"]
        .sum()
        .reset_index()
        .rename(columns={"candidate_track_id": "track_id", "co_listen_count": "cf_score"})
    )

    print("Number of CF candidate songs:", len(cf_scores))

    # ---------- Merge with popularity & PageRank ----------
    merged = cf_scores.merge(
        popularity_df[["track_id", "total_playcount"]], on="track_id", how="left"
    ).merge(
        pagerank_df[["track_id", "pagerank"]], on="track_id", how="left"
    )

    # Fill missing numeric values with 0
    for col in ["cf_score", "total_playcount", "pagerank"]:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)

    # ---------- Normalize each signal ----------
    normalize_column(merged, "cf_score", "cf_norm")
    normalize_column(merged, "total_playcount", "pop_norm")
    normalize_column(merged, "pagerank", "pr_norm")

    # ---------- Final score (weighted combination) ----------
    # You can tune these weights later and mention them in the report.
    merged["final_score"] = (
        0.5 * merged["cf_norm"] +
        0.3 * merged["pop_norm"] +
        0.2 * merged["pr_norm"]
    )

    # Remove tracks the user already listened to
    merged = merged[~merged["track_id"].isin(seed_tracks)]

    if merged.empty:
        print("No candidate tracks left after removing already-listened songs.")
        return

    # ---------- Join with song metadata ----------
    songs_meta = songs_df[["track_id", "name", "artist", "genre", "year"]].copy()
    final_recs = merged.merge(songs_meta, on="track_id", how="left")

    final_recs = final_recs.sort_values("final_score", ascending=False)

    top_k = args.top_k
    final_topk = final_recs.head(top_k).reset_index(drop=True)

    # ---------- Save & print ----------
    out_path = recs_dir / f"user_{target_user}_top{top_k}.csv"
    final_topk.to_csv(out_path, index=False)
    print(f"\nSaved Top-{top_k} recommendations to:\n  {out_path}\n")

    print("Top recommendations:")
    print(
        final_topk[
            ["track_id", "name", "artist", "genre", "final_score", "cf_score", "total_playcount", "pagerank"]
        ].head(10)
    )


main()