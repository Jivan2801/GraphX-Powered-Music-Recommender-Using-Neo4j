from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum

def main():
    # ---- 1. Spark session ----
    spark = SparkSession.builder.appName("MusicGraphETL").getOrCreate()

    base_path = "data_raw/Million Song Dataset + Spotify + Last"
    out_dir = "data_processed"

    music_path = f"{base_path}/Music Info.csv"
    history_path = f"{base_path}/User Listening History.csv"

    print("Music Info path:", music_path)
    print("User Listening History path:", history_path)

    # ---- 2. Load raw CSVs ----
    music_df = (
        spark.read
        .option("header", True)
        .csv(music_path)
    )

    history_df = (
        spark.read
        .option("header", True)
        .csv(history_path)
    )

    print("\n=== Raw schemas ===")
    music_df.printSchema()
    history_df.printSchema()

    # ---- 3. Clean and select relevant columns ----
    # History: user_id, track_id, playcount (as int)
    history_clean = (
        history_df
        .select(
            col("user_id").alias("user_id"),
            col("track_id").alias("track_id"),
            col("playcount").cast("int").alias("playcount")
        )
        .na.drop(subset=["user_id", "track_id", "playcount"])
    )

    # Optionally filter out non-positive playcounts
    history_clean = history_clean.filter(col("playcount") > 0)

    # Music: track metadata and audio features
    music_clean = (
        music_df
        .select(
            "track_id",
            "name",
            "artist",
            "genre",
            "year",
            "duration_ms",
            "danceability",
            "energy",
            "key",
            "loudness",
            "mode",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
            "time_signature",
            "spotify_id",
            "spotify_preview_url",
            "tags"
        )
    )

    # ---- 4. Build node tables ----

    # Users
    users_df = history_clean.select("user_id").distinct()

    # Songs: only those that appear in listening history
    songs_df = (
        history_clean
        .select("track_id")
        .distinct()
        .join(music_clean, on="track_id", how="left")
    )

    # Artists
    artists_df = (
        music_clean
        .select(col("artist").alias("artist_name"))
        .na.drop(subset=["artist_name"])
        .distinct()
    )

    # Genres (optional)
    genres_df = (
        music_clean
        .select(col("genre").alias("genre_name"))
        .na.drop(subset=["genre_name"])
        .distinct()
    )

    # ---- 5. Build relationship tables ----

    # LISTENED: aggregate playcount per (user, track)
    listened_df = (
        history_clean
        .groupBy("user_id", "track_id")
        .agg(spark_sum("playcount").alias("playcount"))
    )

    # PERFORMED_BY: Song -> Artist (from music info)
    performed_by_df = (
        music_clean
        .select("track_id", "artist")
        .na.drop(subset=["track_id", "artist"])
        .distinct()
    )

    # IN_GENRE: Song -> Genre (from music info where genre is not null)
    in_genre_df = (
        music_clean
        .select("track_id", "genre")
        .na.drop(subset=["track_id", "genre"])
        .distinct()
    )

    # ---- 6. Write outputs to data_processed/ ----
    # Small tables as single files (coalesce(1) is fine)
    users_out = f"{out_dir}/users"
    songs_out = f"{out_dir}/songs"
    artists_out = f"{out_dir}/artists"
    genres_out = f"{out_dir}/genres"

    listened_out = f"{out_dir}/listened"
    performed_by_out = f"{out_dir}/performed_by"
    in_genre_out = f"{out_dir}/in_genre"

    print("\n=== Writing node tables ===")
    users_df.coalesce(1).write.mode("overwrite").option("header", True).csv(users_out)
    songs_df.coalesce(1).write.mode("overwrite").option("header", True).csv(songs_out)
    artists_df.coalesce(1).write.mode("overwrite").option("header", True).csv(artists_out)
    genres_df.coalesce(1).write.mode("overwrite").option("header", True).csv(genres_out)

    print("\n=== Writing relationship tables ===")
    # For large tables, keep multiple parts
    listened_df.write.mode("overwrite").option("header", True).csv(listened_out)
    performed_by_df.coalesce(1).write.mode("overwrite").option("header", True).csv(performed_by_out)
    in_genre_df.coalesce(1).write.mode("overwrite").option("header", True).csv(in_genre_out)

    # ---- 7. Sanity counts ----
    print("\n=== Row counts ===")
    print("Users:        ", users_df.count())
    print("Songs:        ", songs_df.count())
    print("Artists:      ", artists_df.count())
    print("Genres:       ", genres_df.count())
    print("LISTENED edges:", listened_df.count())
    print("PERFORMED_BY: ", performed_by_df.count())
    print("IN_GENRE:     ", in_genre_df.count())

    spark.stop()


if __name__ == "__main__":
    main()