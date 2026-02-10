import pandas as pd
from pathlib import Path
import os

def main():
    print("Running Pandas ETL...")
    
    base_path = Path("data_raw/Million Song Dataset + Spotify + Last")
    out_dir = Path("data_processed")
    out_dir.mkdir(exist_ok=True)
    
    music_path = base_path / "Music Info.csv"
    history_path = base_path / "User Listening History.csv"
    
    print(f"Reading {music_path}...")
    music_df = pd.read_csv(music_path)
    print(f"Reading {history_path}...")
    history_df = pd.read_csv(history_path)
    
    # Clean history
    history_clean = history_df[['user_id', 'track_id', 'playcount']].dropna()
    history_clean['playcount'] = history_clean['playcount'].astype(int)
    history_clean = history_clean[history_clean['playcount'] > 0]
    
    # Clean music
    music_cols = [
        "track_id", "name", "artist", "genre", "year", "duration_ms", 
        "danceability", "energy", "key", "loudness", "mode", "speechiness", 
        "acousticness", "instrumentalness", "liveness", "valence", "tempo", 
        "time_signature", "spotify_id", "spotify_preview_url", "tags"
    ]
    # Select only columns that exist
    music_cols = [c for c in music_cols if c in music_df.columns]
    music_clean = music_df[music_cols]
    
    # Nodes
    print("Building nodes...")
    users_df = history_clean[['user_id']].drop_duplicates()
    
    # Songs: only those in history
    songs_df = history_clean[['track_id']].drop_duplicates().merge(music_clean, on='track_id', how='left')
    
    artists_df = music_clean[['artist']].dropna().drop_duplicates().rename(columns={'artist': 'artist_name'})
    genres_df = music_clean[['genre']].dropna().drop_duplicates().rename(columns={'genre': 'genre_name'})
    
    # Edges
    print("Building edges...")
    listened_df = history_clean.groupby(['user_id', 'track_id'])['playcount'].sum().reset_index()
    
    performed_by_df = music_clean[['track_id', 'artist']].dropna().drop_duplicates()
    in_genre_df = music_clean[['track_id', 'genre']].dropna().drop_duplicates()
    
    # Write outputs
    print(f"Writing to {out_dir}...")
    
    def write_csv(df, name):
        p = out_dir / name 
        p.mkdir(exist_ok=True) # Spark writes to a folder, but Pandas writes to a file. 
        # To mimic Spark structure for the app:
        # The app expects: load_spark_single_csv -> reads *.csv in the folder.
        # So we should create a folder and put one CSV in it.
        file_path = p / f"{name}.csv"
        df.to_csv(file_path, index=False)
        print(f"  Saved {name}")

    write_csv(users_df, "users")
    write_csv(songs_df, "songs")
    write_csv(artists_df, "artists")
    write_csv(genres_df, "genres")
    write_csv(listened_df, "listened")
    write_csv(performed_by_df, "performed_by")
    write_csv(in_genre_df, "in_genre")
    
    print("ETL Complete.")

if __name__ == "__main__":
    main()
