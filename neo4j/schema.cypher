// schema.cypher

// Users
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.user_id IS UNIQUE;

// Songs
CREATE CONSTRAINT song_track_id_unique IF NOT EXISTS
FOR (s:Song)
REQUIRE s.track_id IS UNIQUE;

// Artists
CREATE CONSTRAINT artist_name_unique IF NOT EXISTS
FOR (a:Artist)
REQUIRE a.name IS UNIQUE;

// Genres
CREATE CONSTRAINT genre_name_unique IF NOT EXISTS
FOR (g:Genre)
REQUIRE g.name IS UNIQUE;