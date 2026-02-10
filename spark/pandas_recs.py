import pandas as pd
import networkx as nx
from pathlib import Path
import shutil

def main():
    print("Running Pandas Analysis (replacing Spark)...")
    
    project_root = Path(".")
    processed_dir = project_root / "data_processed"
    
    # Input paths (from my ETL pandas)
    # ETL wrote to folders: users, songs, listened
    # each folder contains {name}.csv
    
    users_source = processed_dir / "users" / "users.csv"
    songs_source = processed_dir / "songs" / "songs.csv"
    listened_source = processed_dir / "listened" / "listened.csv"
    
    # Target directory for app inputs
    graph_for_spark = processed_dir / "graph_for_spark"
    graph_for_spark.mkdir(parents=True, exist_ok=True)
    
    # 1. Prepare Inputs for App (Copy to flat csvs where needed)
    # App expects: data_processed/graph_for_spark/listened_edges.csv
    # App expects: data_processed/graph_for_spark/songs.csv
    
    print("Preparing input files for App...")
    target_listened = graph_for_spark / "listened_edges.csv"
    target_songs = graph_for_spark / "songs.csv"
    
    shutil.copy(listened_source, target_listened)
    shutil.copy(songs_source, target_songs)
    
    # Load Data for Analysis
    print("Loading data...")
    listened_df = pd.read_csv(target_listened)
    songs_df = pd.read_csv(target_songs)
    
    # 2. Song Popularity
    print("Calculating Popularity...")
    popularity_df = listened_df.groupby("track_id").agg(
        total_playcount=("playcount", "sum"),
        unique_users=("user_id", "nunique")
    ).reset_index()
    
    popularity_df = popularity_df.sort_values("total_playcount", ascending=False)
    
    # 3. PageRank
    print("Calculating PageRank...")
    # Build graph
    G = nx.Graph()
    # Edges: user <-> song
    # We need to distinguish user nodes from song nodes to avoid collision if ids overlap (unlikely but safe)
    # But for simplicity, assuming no collision or just using raw IDs
    
    # Bipartite graph
    users = listened_df["user_id"].unique()
    songs = listened_df["track_id"].unique()
    
    G.add_nodes_from(users, bipartite=0)
    G.add_nodes_from(songs, bipartite=1)
    
    edges = list(zip(listened_df["user_id"], listened_df["track_id"]))
    G.add_edges_from(edges)
    
    # Run PageRank
    pr = nx.pagerank(G, alpha=0.85)
    
    # Extract song ranks
    pr_data = [{"track_id": k, "pagerank": v} for k, v in pr.items() if k in songs]
    pagerank_df = pd.DataFrame(pr_data).sort_values("pagerank", ascending=False)
    
    # 4. Co-listen pairs
    print("Calculating Co-listen pairs...")
    # Top 500 songs for co-listen to save time
    top_songs = popularity_df.head(500)["track_id"].unique()
    
    # Filter history
    history_sub = listened_df[listened_df["track_id"].isin(top_songs)]
    
    # Self join on user_id
    merged = history_sub.merge(history_sub, on="user_id")
    # Filter track_1 < track_2
    pairs = merged[merged["track_id_x"] < merged["track_id_y"]]
    
    co_listen_df = pairs.groupby(["track_id_x", "track_id_y"]).size().reset_index(name="co_listen_count")
    co_listen_df.columns = ["track_id_1", "track_id_2", "co_listen_count"]
    co_listen_df = co_listen_df.sort_values("co_listen_count", ascending=False)
    
    # 5. Write Outputs (As Folders with 1 CSV inside)
    spark_out_dir = processed_dir / "spark_outputs"
    spark_out_dir.mkdir(parents=True, exist_ok=True)
    
    def save_as_spark_folder(df, name):
        folder = spark_out_dir / f"{name}.csv"
        folder.mkdir(parents=True, exist_ok=True)
        # Save as part-00000.csv
        file_path = folder / "part-00000.csv"
        df.to_csv(file_path, index=False)
        print(f"  Saved {name} to {folder}")

    save_as_spark_folder(popularity_df.head(1000), "song_popularity_top1000")
    save_as_spark_folder(pagerank_df.head(1000), "song_pagerank_top1000")
    save_as_spark_folder(co_listen_df.head(1000), "song_co_listen_pairs_top1000")
    
    print("Analysis Complete.")

if __name__ == "__main__":
    main()
