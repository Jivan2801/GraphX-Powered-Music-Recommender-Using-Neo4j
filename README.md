# Graph-Based Music Recommendation System (Neo4j + Spark + NetworkX)

An end-to-end graph analytics project that builds a scalable music recommendation engine using ETL pipelines, graph algorithms (PageRank & co-listen similarity), and a hybrid scoring strategy.

---

## 🚀 Project Overview

This project models user listening history as a **user–song bipartite graph** and applies graph-based techniques to generate personalized song recommendations.

The system combines:

- Collaborative filtering via co-listen pairs
- Graph centrality (PageRank)
- Popularity metrics (play counts & unique listeners)

These signals are fused into a hybrid scoring model to recommend songs users have not listened to yet.

---

## 🏗 System Architecture

Data → ETL → Graph Construction → Graph Analytics → Hybrid Scoring → Recommendations → HTML Report

---

## ✨ Key Features

- Synthetic dataset generator for quick local testing
- Pandas-based ETL (lightweight, laptop-friendly)
- Optional PySpark & GraphFrames support
- PageRank on user–song bipartite graph
- Co-listen similarity computation
- Hybrid scoring model
- CLI-based recommendation generation
- Dark-themed HTML report output
- Optional Neo4j integration with Cypher scripts

---

## 📂 Project Structure

app/  
&nbsp;&nbsp;&nbsp;&nbsp;generate_recs.py – Generate top-K recommendations  
&nbsp;&nbsp;&nbsp;&nbsp;generate_html_report.py – Create styled HTML report

etl/  
&nbsp;&nbsp;&nbsp;&nbsp;etl_pandas.py – Local ETL pipeline  
&nbsp;&nbsp;&nbsp;&nbsp;etl_pyspark.py – Spark-based ETL

spark/  
&nbsp;&nbsp;&nbsp;&nbsp;pandas_recs.py – Graph analytics using NetworkX  
&nbsp;&nbsp;&nbsp;&nbsp;graphframes_recs.py – Spark GraphFrames variant

neo4j/  
&nbsp;&nbsp;&nbsp;&nbsp;Cypher scripts for schema + data loading

data_raw/ – Raw datasets  
data_processed/ – Cleaned tables + graph outputs  
notebooks/ – Exploratory analysis

---

## 🛠 Requirements

- Python 3.8+
- pandas
- networkx
- pyspark (optional)
- neo4j driver (optional)
- Java 8/11 (only for Spark)

Install dependencies:

```bash
pip install pandas networkx pyspark neo4j
```

---

## ▶️ Quickstart (Local Demo)

### 1. Generate Dummy Data

```bash
python data_generation_script.py
```

### 2. Run ETL

```bash
python etl/etl_pandas.py
```

### 3. Run Graph Analytics

```bash
python spark/pandas_recs.py
```

### 4. Generate Recommendations

```bash
python app/generate_recs.py --top_k 20
```

### 5. Build HTML Report

```bash
python app/generate_html_report.py
```

---

## 🧠 Technical Highlights

- Models heterogeneous entities (User, Song, Artist, Genre)
- Applies graph centrality to recommendation ranking
- Demonstrates graph thinking beyond matrix-based CF
- Clean separation of ETL, analytics, and application layers
- Reproducible local execution (no Hadoop cluster required)

---

## 📊 Future Improvements

- Precision@K / Recall@K evaluation metrics
- Graph Neural Network embeddings
- REST API layer for real-time recommendations
- Cloud deployment (AWS Neptune / Azure Cosmos DB)
- Interactive dashboard

---

## 📜 License

Add your preferred open-source license (MIT recommended).
