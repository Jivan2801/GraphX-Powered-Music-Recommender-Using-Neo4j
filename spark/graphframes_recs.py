from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from graphframes import GraphFrame
from pathlib import Path
import pyspark


def main():
    # ---- 1. Spark session with GraphFrames package ----
    # NOTE: If this errors about version mismatch, you may need to change
    # "graphframes:graphframes:0.8.3-spark3.5-s_2.12" to match your Spark version.
    spark_version = pyspark.__version__
    print("PySpark version:", spark_version)

    builder = (
        SparkSession.builder
        .appName("MusicGraphFramesRecs")
        .config("spark.driver.memory", "4g")      # ⬅ more RAM
        .config("spark.executor.memory", "4g")    # ⬅ for local mode, same as driver
    )

    if spark_version.startswith("4."):
        gf_coord = "io.graphframes:graphframes-spark4_2.13:0.10.0"
    else:
        gf_coord = "io.graphframes:graphframes-spark3_2.13:0.10.0"

    print("Using GraphFrames package:", gf_coord)

    spark = (
        builder
        .config("spark.jars.packages", gf_coord)
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    # ---- 2. Paths ----
    project_root = Path(".").resolve()
    graph_dir = project_root / "data_processed" / "graph_for_spark"
    output_dir = project_root / "data_processed" / "spark_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Project root:", project_root)
    print("Graph data dir:", graph_dir)
    print("Output dir:", output_dir)

    users_path = str(graph_dir / "users.csv")
    songs_path = str(graph_dir / "songs.csv")
    edges_path = str(graph_dir / "listened_edges.csv")

    # ---- 3. Load CSVs into Spark DataFrames ----
    users_df = (
        spark.read
        .option("header", True)
        .csv(users_path)
    )

    songs_df = (
        spark.read
        .option("header", True)
        .csv(songs_path)
    )

    listened_df = (
        spark.read
        .option("header", True)
        .csv(edges_path)
        .withColumn("playcount", F.col("playcount").cast("int"))
    )

    print("Users:", users_df.count())
    print("Songs:", songs_df.count())
    print("LISTENED edges:", listened_df.count())

    # ---- 4. Build GraphFrame (User + Song bipartite graph) ----
    # Vertices: need a single 'id' column
    v_users = users_df.select(
        F.col("user_id").alias("id")
    ).withColumn("node_type", F.lit("user"))

    v_songs = songs_df.select(
        F.col("track_id").alias("id"),
        "name",
        "artist",
        "genre",
        "year",
        "danceability",
        "energy",
        "valence",
        "tempo"
    ).withColumn("node_type", F.lit("song"))

    vertices = v_users.unionByName(v_songs, allowMissingColumns=True)

    # Edges: src=user, dst=song, weight=playcount
    edges = listened_df.select(
        F.col("user_id").alias("src"),
        F.col("track_id").alias("dst"),
        F.col("playcount").alias("weight")
    )

    print("Vertices:", vertices.count())
    print("Edges:", edges.count())

    g = GraphFrame(vertices, edges)

    # ---- 5. Song popularity in Spark (DataFrame-based) ----
    song_popularity = (
        listened_df.groupBy("track_id")
        .agg(
            F.sum("playcount").alias("total_playcount"),
            F.countDistinct("user_id").alias("unique_users")
        )
    )

    song_popularity = (
        song_popularity
        .join(songs_df, on="track_id", how="left")
        .orderBy(F.col("total_playcount").desc())
    )

    popularity_out = str(output_dir / "song_popularity_top1000.csv")
    (
        song_popularity
        .limit(1000)
        .coalesce(1)
        .write.mode("overwrite")
        .option("header", True)
        .csv(popularity_out)
    )
    print("Saved song popularity to:", popularity_out)

    # ---- 6. PageRank on the bipartite graph (GraphFrames) ----
    
    edges_pr = edges.sample(fraction=0.01, seed=42)

    # Collect the vertex IDs that actually appear in the sampled edges
    vertex_ids_pr = (
        edges_pr.select(F.col("src").alias("id"))
        .union(edges_pr.select(F.col("dst").alias("id")))
        .distinct()
    )

    # Filter the vertices to only those in the sampled graph
    vertices_pr = vertices.join(vertex_ids_pr, on="id", how="inner")

    print("Sampled PageRank vertices:", vertices_pr.count())
    print("Sampled PageRank edges:", edges_pr.count())

    # Build a smaller GraphFrame just for PageRank
    g_pr = GraphFrame(vertices_pr, edges_pr)

    # Run unweighted PageRank on the sampled subgraph
    pr_result = g_pr.pageRank(
        resetProbability=0.15,
        maxIter=10
    )

    pr_vertices = pr_result.vertices

    # Filter to songs only
    song_pr = (
        pr_vertices
        .filter(F.col("node_type") == "song")
        .select(
            F.col("id").alias("track_id"),
            "pagerank"
        )
        .join(songs_df, on="track_id", how="left")
        .orderBy(F.col("pagerank").desc())
    )

    pagerank_out = str(output_dir / "song_pagerank_top1000.csv")
    (
        song_pr
        .limit(1000)
        .coalesce(1)
        .write.mode("overwrite")
        .option("header", True)
        .csv(pagerank_out)
    )
    print("Saved song PageRank (sampled graph) to:", pagerank_out)



    # ---- 7. Co-listen song–song pairs (simple similarity signal) ----
    # Restrict to top 5000 popular songs to keep this manageable
    popular_song_ids = (
        song_popularity
        .select("track_id")
        .orderBy(F.col("total_playcount").desc())
        .limit(5000)
    )

    history_subset = (
        listened_df.join(popular_song_ids, on="track_id", how="inner")
    )

    song_pairs = (
        history_subset.alias("h1")
        .join(
            history_subset.alias("h2"),
            (F.col("h1.user_id") == F.col("h2.user_id")) &
            (F.col("h1.track_id") < F.col("h2.track_id")),
            "inner"
        )
        .groupBy(
            F.col("h1.track_id").alias("track_id_1"),
            F.col("h2.track_id").alias("track_id_2")
        )
        .agg(F.count("*").alias("co_listen_count"))
        .orderBy(F.col("co_listen_count").desc())
    )

    song_pairs_out = str(output_dir / "song_co_listen_pairs_top1000.csv")
    (
        song_pairs
        .limit(1000)
        .coalesce(1)
        .write.mode("overwrite")
        .option("header", True)
        .csv(song_pairs_out)
    )
    print("Saved song co-listen pairs to:", song_pairs_out)

    # ---- 8. Stop Spark ----
    spark.stop()


# if __name__ == "__main__":
main()