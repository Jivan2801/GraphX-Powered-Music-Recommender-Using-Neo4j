// A1. Drop any old projection (safe to run)
CALL gds.graph.drop('music_graph', false) YIELD graphName
  RETURN graphName;

// A2. Project User + Song with LISTENED edges
CALL gds.graph.project(
  'music_graph',
  ['User', 'Song'],
  {
    LISTENED: {
      type: 'LISTENED',
      orientation: 'UNDIRECTED',
      properties: 'playcount'
    }
  }
)
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount;

// B1. Run PageRank and write to node property
CALL gds.pageRank.write(
  'music_graph',
  {
    relationshipWeightProperty: 'playcount',
    writeProperty: 'pagerank_score'
  }
)
YIELD nodePropertiesWritten, ranIterations, didConverge;

// B2. Inspect top 20 songs by PageRank
MATCH (s:Song)
RETURN s.track_id, s.name AS song, s.artist_raw AS artist, s.pagerank_score
ORDER BY s.pagerank_score DESC
LIMIT 20;

// C1. Drop old SIMILAR_TO edges if you re-run
MATCH ()-[r:SIMILAR_TO]->() DELETE r;

// C2. Compute Song–Song similarity from the projected graph
CALL gds.nodeSimilarity.stream(
  'music_graph',
  {
    nodeLabels: ['Song'],
    relationshipTypes: ['LISTENED'],
    topK: 10,             // keep top 10 similar songs per song
    similarityCutoff: 0.4 // ignore weak similarities
  }
)
YIELD node1, node2, similarity
WITH gds.util.asNode(node1) AS s1,
     gds.util.asNode(node2) AS s2,
     similarity
MERGE (s1)-[r:SIMILAR_TO]->(s2)
SET r.similarity = similarity;

// D1. Replace TRACK_ID_HERE with a real track_id from your DB
MATCH (s:Song {track_id: 'TRACK_ID_HERE'})- [r:SIMILAR_TO]->(other:Song)
RETURN s.name AS base_song,
       other.track_id,
       other.name AS similar_song,
       other.artist_raw AS artist,
       r.similarity
ORDER BY r.similarity DESC
LIMIT 20;

// D2. 
MATCH (s:Song)-[r:SIMILAR_TO]->(other:Song)
RETURN s, r, other
LIMIT 50;

// E1. Recommend new songs for a specific user using similar songs
WITH 'SOME_USER_ID_HERE' AS targetUser

// Songs the user has already listened to
MATCH (u:User {user_id: targetUser})-[:LISTENED]->(s:Song)

// Similar songs they have NOT listened to yet
MATCH (s)-[sim:SIMILAR_TO]->(candidate:Song)
WHERE NOT (u)-[:LISTENED]->(candidate)

// Score candidates by sum of similarity
WITH candidate, sum(sim.similarity) AS score
ORDER BY score DESC
LIMIT 20

MATCH (candidate)-[:PERFORMED_BY]->(a:Artist)
RETURN candidate.track_id,
       candidate.name AS recommended_song,
       a.name AS artist,
       score
ORDER BY score DESC;
