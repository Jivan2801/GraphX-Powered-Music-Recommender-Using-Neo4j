import random
import csv
import os
from pathlib import Path

def generate_dummy_data():
    base_path = Path("data_raw/Million Song Dataset + Spotify + Last")
    base_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating dummy data in {base_path}...")

    # 1. Generate Music Info.csv
    music_info_path = base_path / "Music Info.csv"
    headers_music = [
        'track_id', 'name', 'artist', 'spotify_preview_url', 'spotify_id', 'tags', 'genre', 'year',
        'duration_ms', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature'
    ]
    
    genres = ['Rock', 'Pop', 'Jazz', 'Metal', 'Electronic', 'Classical']
    artists = [f"Artist_{i}" for i in range(1, 51)]
    
    tracks = []
    print("  Creating Music Info.csv...")
    with open(music_info_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers_music)
        for i in range(1, 201): # 200 tracks
            track_id = f"TRACK_{i:03d}"
            name = f"Song Title {i}"
            artist = random.choice(artists)
            genre = random.choice(genres)
            year = random.randint(1990, 2023)
            tracks.append(track_id)
            
            row = [
                track_id, name, artist, "http://example.com", f"spot_{i}", "tag1, tag2", genre, year,
                200000, 0.5, 0.5, 5, -5.0, 1, 0.05,
                0.1, 0.0, 0.1, 0.5, 120.0, 4
            ]
            writer.writerow(row)

    # 2. Generate User Listening History.csv
    history_path = base_path / "User Listening History.csv"
    headers_history = ['track_id', 'user_id', 'playcount']
    
    users = [f"user_{i:03d}" for i in range(1, 21)] # 20 users
    
    print("  Creating User Listening History.csv...")
    with open(history_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers_history)
        
        for user in users:
            # Each user listens to 10-50 random tracks
            num_listens = random.randint(10, 50)
            listened_tracks = random.sample(tracks, num_listens)
            for track in listened_tracks:
                playcount = random.randint(1, 50)
                writer.writerow([track, user, playcount])
                
    print("Dummy data generation complete.")

if __name__ == "__main__":
    generate_dummy_data()
