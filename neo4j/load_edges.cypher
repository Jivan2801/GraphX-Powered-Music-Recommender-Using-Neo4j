LOAD CSV WITH HEADERS FROM 'file:///listened.csv' AS row
WITH row
WHERE row.user_id IS NOT NULL
  AND row.track_id IS NOT NULL
  AND row.playcount IS NOT NULL

CALL {
  WITH row
  MATCH (u:User {user_id: row.user_id})
  MATCH (s:Song {track_id: row.track_id})
  MERGE (u)-[r:LISTENED]->(s)
  SET r.playcount = toInteger(row.playcount)
} IN TRANSACTIONS OF 5000 ROWS;


LOAD CSV WITH HEADERS FROM 'file:///performed_by.csv' AS row
WITH row
WHERE row.track_id IS NOT NULL
  AND row.artist IS NOT NULL

CALL {
  WITH row
  MATCH (s:Song {track_id: row.track_id})
  MATCH (a:Artist {name: row.artist})
  MERGE (s)-[:PERFORMED_BY]->(a)
} IN TRANSACTIONS OF 5000 ROWS;


LOAD CSV WITH HEADERS FROM 'file:///in_genre.csv' AS row
WITH row
WHERE row.track_id IS NOT NULL
  AND row.genre IS NOT NULL

CALL {
  WITH row
  MATCH (s:Song {track_id: row.track_id})
  MATCH (g:Genre {name: row.genre})
  MERGE (s)-[:IN_GENRE]->(g)
} IN TRANSACTIONS OF 5000 ROWS;
