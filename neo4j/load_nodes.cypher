// load_nodes.cypher

// 1) Load Users
LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row
WITH row
WHERE row.user_id IS NOT NULL
MERGE (:User {user_id: row.user_id});

// 2) Load Songs
LOAD CSV WITH HEADERS FROM 'file:///songs.csv' AS row
WITH row
WHERE row.track_id IS NOT NULL
MERGE (s:Song {track_id: row.track_id})
SET
  s.name                   = row.name,
  s.artist_raw             = row.artist,
  s.genre                  = row.genre,
  s.year                   = row.year,
  s.duration_ms            = toInteger(row.duration_ms),
  s.danceability           = toFloat(row.danceability),
  s.energy                 = toFloat(row.energy),
  s.key                    = row.key,
  s.loudness               = toFloat(row.loudness),
  s.mode                   = row.mode,
  s.speechiness            = toFloat(row.speechiness),
  s.acousticness           = toFloat(row.acousticness),
  s.instrumentalness       = toFloat(row.instrumentalness),
  s.liveness               = toFloat(row.liveness),
  s.valence                = toFloat(row.valence),
  s.tempo                  = toFloat(row.tempo),
  s.time_signature         = row.time_signature,
  s.spotify_id             = row.spotify_id,
  s.spotify_preview_url    = row.spotify_preview_url,
  s.tags                   = row.tags;

// 3) Load Artists
LOAD CSV WITH HEADERS FROM 'file:///artists.csv' AS row
WITH row
WHERE row.artist_name IS NOT NULL
MERGE (a:Artist {name: row.artist_name});

// 4) Load Genres
LOAD CSV WITH HEADERS FROM 'file:///genres.csv' AS row
WITH row
WHERE row.genre_name IS NOT NULL
MERGE (g:Genre {name: row.genre_name});