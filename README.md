# GraphX‑Powered Music Recommender (Neo4j & Graph Analytics)

A small end‑to‑end project that builds a **graph‑based music recommendation system** using:

- Synthetic or real listening history
- ETL (Pandas or PySpark)
- Graph analysis (popularity, PageRank, co‑listen pairs)
- A simple CLI + HTML report for viewing recommendations

This repository is designed to be **easy to run locally** on a laptop (no Hadoop cluster required).

---

## 1. Features

- **Data generation** – create a dummy Million Song / Spotify / Last.fm‑style dataset for quick testing.
- **ETL pipeline** – clean and reshape raw CSVs into user / song / listening tables.
- **Graph analytics**
  - Song **popularity** (total playcount, unique listeners)
  - **PageRank** on the user–song bipartite graph
  - **Co‑listen pairs** for collaborative filtering
- **Hybrid recommender**
  - Combines co‑listen score, popularity, and PageRank into a single `final_score`
  - Excludes songs the target user has already listened to
- **Reporting**
  - CSV output with top‑K recommendations
  - Modern, dark‑themed HTML report (`recommendations_report.html`)
- **Neo4j support (optional)**
  - Cypher scripts to define the graph schema, load data, and run additional GDS algorithms

---

## 2. Project Structure

- `app/`
  - `generate_recs.py` – main recommender script (reads processed CSVs and graph metrics).
  - `generate_html_report.py` – converts the latest recommendations CSV into an HTML report.
- `data_raw/` – raw input CSVs (real or synthetic).
- `data_processed/`
  - ETL outputs (`users`, `songs`, `listened`, `artists`, `genres`, etc.).
  - `graph_for_spark/` – flat CSVs used as inputs by the recommender.
  - `spark_outputs/` – popularity, PageRank, and co‑listen outputs.
  - `recs/` – final recommendations per user.
- `etl/`
  - `etl_pandas.py` – Pandas‑based ETL (recommended for local use).
  - `etl_pyspark.py` – original Spark ETL (optional).
- `spark/`
  - `pandas_recs.py` – Pandas + NetworkX implementation of the graph analysis.
  - `graphframes_recs.py`, `graphx_recs.scala` – original Spark variants (optional).
- `neo4j/` – Cypher scripts (`schema.cypher`, `load_nodes.cypher`, `load_edges.cypher`, `gds_queries.cypher`).
- `notebooks/` – Jupyter notebooks for profiling and experiments.

---

## 3. Requirements

- **Python** 3.8 or higher
- **pip** for installing dependencies
- **Java 8 or 11** (only if you want to run the Spark‑based scripts)
- **Neo4j Desktop** (optional, for graph exploration)

Python libraries:

```bash
pip install pandas networkx neo4j pyspark
```

> If PySpark or Java is problematic on Windows, you can **skip Spark** and just use `etl_pandas.py` + `spark/pandas_recs.py`.

---

## 4. Quickstart (Local Demo)

All commands below are executed from the repository root.

### 4.1 Generate Dummy Data

If you don’t have real Million Song / Spotify / Last.fm data, generate a small synthetic dataset:

```bash
python data_generation_script.py
```

This creates two CSVs under `data_raw/Million Song Dataset + Spotify + Last/`:

- `Music Info.csv`
- `User Listening History.csv`

### 4.2 Run ETL (Pandas)

Transform raw CSVs into clean tables:

```bash
python etl/etl_pandas.py
```

This populates `data_processed/` with:

- `users/users.csv`
- `songs/songs.csv`
- `listened/listened.csv`
- `artists/artists.csv`
- `genres/genres.csv`
- `performed_by/performed_by.csv`
- `in_genre/in_genre.csv`

and prepares `graph_for_spark/listened_edges.csv` and `graph_for_spark/songs.csv` for downstream steps.

### 4.3 Run Graph Analysis

Compute popularity, PageRank, and co‑listen pairs:

```bash
python spark/pandas_recs.py
```

This writes Spark‑style outputs to `data_processed/spark_outputs/`:

- `song_popularity_top1000.csv/part-00000.csv`
- `song_pagerank_top1000.csv/part-00000.csv`
- `song_co_listen_pairs_top1000.csv/part-00000.csv`

### 4.4 Generate Recommendations

Create top‑K recommendations for a user:

```bash
python app/generate_recs.py --top_k 20
```

If `--user_id` is omitted, the script automatically picks a “top” user (with many listens).  
To specify a user explicitly:

```bash
python app/generate_recs.py --user_id user_001 --top_k 20
```

Outputs are saved under:

- `data_processed/recs/user_<user_id>_top<k>.csv`

### 4.5 Build the HTML Report

Render the most recent recommendations CSV as an HTML report:

```bash
python app/generate_html_report.py
```

This generates:

- `recommendations_report.html`

and (where supported) opens it in your default browser.

---

## 5. Neo4j Workflow (Optional)

If you want to explore this graph in Neo4j or run additional GDS algorithms:

1. Run the ETL step so that `data_processed/` is populated.
2. Copy the relevant CSVs from `data_processed/` into Neo4j’s `import` directory.
3. In Neo4j Browser, execute:
   - `schema.cypher` to create constraints and indexes
   - `load_nodes.cypher` and `load_edges.cypher` to import data
4. Optionally run `gds_queries.cypher` for graph algorithms inside Neo4j.

---

## 6. Troubleshooting

- **`data_raw` missing or empty**  
  Run:

  ```bash
  python data_generation_script.py
  ```

- **Spark / Java errors on Windows**  
  Use the Pandas/NetworkX pipeline instead:

  ```bash
  python etl/etl_pandas.py
  python spark/pandas_recs.py
  ```

- **No recommendations produced**  
  Make sure you have run ETL and analysis steps first, and that:
  - `data_processed/graph_for_spark/listened_edges.csv` exists
  - `data_processed/spark_outputs/` contains the three metric folders

---

## 7. Using This Repo in a Portfolio

- Show the **end‑to‑end pipeline**: data → ETL → graph analysis → recommendations → report.
- Highlight:
  - Use of **graph thinking** (user–song bipartite graph, PageRank, co‑listen).
  - Choice of **Pandas/NetworkX** to make a Spark‑style project run easily on a laptop.
  - Clear, reproducible commands (Quickstart section above).

You can further customize the scoring weights or the HTML report design to match your personal style.

# GraphX‑Powered Music Recommender (Neo4j & Graph Analytics)

A small end‑to‑end project that builds a **graph‑based music recommendation system** using:

- Synthetic or real listening history
- ETL (Pandas or PySpark)
- Graph analysis (popularity, PageRank, co‑listen pairs)
- A simple CLI + HTML report for viewing recommendations

This repository is meant to be **easy to run locally** on a laptop (no Hadoop cluster required).

---

## 1. Features

- **Data generation**: Create a dummy version of the Million Song / Spotify / Last.fm dataset for quick testing.
- **ETL pipeline**: Clean and reshape raw CSVs into user / song / listening tables.
- **Graph analytics**:
  - Song **popularity** (total playcount, unique listeners)
  - **PageRank** on the user–song bipartite graph
  - **Co‑listen pairs** for collaborative filtering
- **Hybrid recommender**:
  - Combines co‑listen score, popularity, and PageRank into a single `final_score`
  - Excludes songs the target user has already listened to
- **Reporting**:
  - CSV output with top‑K recommendations
  - Modern, dark‑themed HTML report (`recommendations_report.html`)
- **Neo4j support (optional)**:
  - Cypher scripts to create the graph schema, load data, and run additional GDS algorithms

---

## 2. Project Structure

- `app/`
  - `generate_recs.py` – main recommender script (reads processed CSVs and graph metrics).
  - `generate_html_report.py` – converts the latest recommendations CSV into an HTML report.
- `data_raw/` – raw input CSVs (real or synthetic).
- `data_processed/`
  - ETL outputs (`users`, `songs`, `listened`, `artists`, `genres`, etc.).
  - `graph_for_spark/` – flat CSVs used as inputs by the recommender.
  - `spark_outputs/` – popularity, PageRank, and co‑listen outputs.
  - `recs/` – final recommendations per user.
- `etl/`
  - `etl_pandas.py` – Pandas‑based ETL (recommended for local use).
  - `etl_pyspark.py` – original Spark ETL (optional).
- `spark/`
  - `pandas_recs.py` – Pandas + NetworkX implementation of the graph analysis.
  - `graphframes_recs.py`, `graphx_recs.scala` – original Spark variants (optional).
- `neo4j/` – Cypher scripts (`schema.cypher`, `load_nodes.cypher`, `load_edges.cypher`, `gds_queries.cypher`).
- `notebooks/` – Jupyter notebooks for profiling and experiments.

---

## 3. Requirements

- **Python** 3.8 or higher
- **pip** for installing dependencies
- **Java 8 or 11** (only if you want to run the Spark‑based scripts)
- **Neo4j Desktop** (optional, for graph exploration)

Python libraries:

```bash
pip install pandas networkx neo4j pyspark
```

> If PySpark or Java is problematic on Windows, you can **skip Spark** and just use `etl_pandas.py` + `spark/pandas_recs.py`.

---

## 4. Quickstart: Run the Full Pipeline (Local Demo)

All commands below are executed from the repository root.

### 4.1 Generate Dummy Data

If you don’t have real Million Song / Spotify / Last.fm data, generate a small synthetic dataset:

```bash
python data_generation_script.py
```

This creates two CSVs under `data_raw/Million Song Dataset + Spotify + Last/`:

- `Music Info.csv`
- `User Listening History.csv`

### 4.2 Run ETL (Pandas)

Transform raw CSVs into clean tables:

```bash
python etl/etl_pandas.py
```

This populates `data_processed/` with:

- `users/users.csv`
- `songs/songs.csv`
- `listened/listened.csv`
- `artists/artists.csv`
- `genres/genres.csv`
- `performed_by/performed_by.csv`
- `in_genre/in_genre.csv`

and prepares `graph_for_spark/listened_edges.csv` and `graph_for_spark/songs.csv` for downstream steps.

### 4.3 Run Graph Analysis (Pandas + NetworkX)

Compute popularity, PageRank, and co‑listen pairs:

```bash
python spark/pandas_recs.py
```

This writes Spark‑style outputs to `data_processed/spark_outputs/`:

- `song_popularity_top1000.csv/part-00000.csv`
- `song_pagerank_top1000.csv/part-00000.csv`
- `song_co_listen_pairs_top1000.csv/part-00000.csv`

### 4.4 Generate Recommendations

Create top‑K recommendations for a user:

```bash
python app/generate_recs.py --top_k 20
```

If `--user_id` is omitted, the script automatically picks a “top” user (with many listens).  
To specify a user explicitly:

```bash
python app/generate_recs.py --user_id user_001 --top_k 20
```

Outputs are saved under:

- `data_processed/recs/user_<user_id>_top<k>.csv`

### 4.5 Build the HTML Report

Render the most recent recommendations CSV as an HTML report:

```bash
python app/generate_html_report.py
```

This generates:

- `recommendations_report.html`

and (where supported) opens it in your default browser.

---

## 5. Neo4j Workflow (Optional)

If you want to explore this graph in Neo4j or run additional GDS algorithms:

1. **Run ETL** so that `data_processed/` is populated.
2. Copy the relevant CSVs from `data_processed/` into Neo4j’s `import` directory.
3. In Neo4j Browser, execute:
   - `:play cypher` (optional, to familiarize yourself)
   - `schema.cypher` to create constraints and indexes
   - `load_nodes.cypher` and `load_edges.cypher` to import data
4. Optionally run `gds_queries.cypher` for graph algorithms inside Neo4j.

---

## 6. Troubleshooting

- **`data_raw` missing or empty**
  - Run `python data_generation_script.py` to create dummy data.

- **Spark / Java errors on Windows**
  - Stick to the Pandas/NetworkX flow:
    ```bash
    python etl/etl_pandas.py
    python spark/pandas_recs.py
    ```

- **No recommendations produced**
  - Ensure you have run both ETL and graph analysis steps.
  - Check that:
    - `data_processed/graph_for_spark/listened_edges.csv` exists.
    - `data_processed/spark_outputs/` contains the three metric folders.

---

## 7. How to Use This Repo in a Portfolio

- Show the **end‑to‑end pipeline**: data → ETL → graph analysis → recommendations → report.
- Highlight:
  - Use of **graph thinking** (user–song bipartite graph, PageRank, co‑listen).
  - Choice of **Pandas/NetworkX** to make a Spark‑style project run easily on a laptop.
  - Clear, reproducible commands (Quickstart section above).

You can further customize the scoring weights or the HTML report design to match your personal style.

# GraphX-Powered Music Recommender Using Neo4j

A graph-based music recommendation system that combines ETL, graph analytics (PageRank, co‑listen counts), and a simple reporting app to generate personalized song recommendations.

---

## 1. Project Overview

This project builds a user–song graph from listening history and uses:

- **Collaborative filtering** via co‑listen pairs.
- **Graph centrality** (PageRank) on a bipartite user–track graph.
- **Popularity signals** (total playcount).

These signals are combined into a final score to recommend songs a user has not listened to yet. Results are exported both as CSV and as a modern HTML report.

---

## 2. Project Structure

- `app/` – CLI apps:
  - `generate_recs.py` – generates top‑K recommendations for a user.
  - `generate_html_report.py` – turns the latest recommendations into a styled HTML report.
- `data_raw/` – Input data (Million Song Dataset + Spotify + Last.fm, or dummy data).
- `data_processed/` – Cleaned tables, graph-friendly CSVs, and analysis outputs.
- `etl/` – ETL scripts to clean and transform raw data (Pandas and original PySpark).
- `spark/` – Spark / Pandas graph analysis scripts (popularity, PageRank, co‑listen).
- `neo4j/` – Cypher scripts to load the processed graph into Neo4j and run GDS queries.
- `notebooks/` – Exploration and experiment notebooks.

---

## 3. Prerequisites

- **Python** 3.8+
- **Pip** for installing Python packages
- **Java 8 or 11** (only if you want to run the original Spark scripts)
- **Neo4j Desktop** (optional, for graph visualization / GDS)

---

## 4. Setup & Installation

From the project root:

```bash
pip install pandas pyspark networkx neo4j
```

> On Windows, if Spark is troublesome, you can ignore PySpark and rely on the provided Pandas/NetworkX fallbacks.

---

## 5. Running the Pipeline (Local Demo)

All commands below are run from the project root.

### 5.1 Generate Dummy Data (optional but easiest)

If you do not have the original Million Song + Spotify + Last.fm data, generate a small synthetic dataset:

```bash
python data_generation_script.py
```

This creates:

- `data_raw/Million Song Dataset + Spotify + Last/Music Info.csv`
- `data_raw/Million Song Dataset + Spotify + Last/User Listening History.csv`

### 5.2 Run ETL (Data Processing)

Use the Pandas-based ETL for a lightweight, local flow:

```bash
python etl/etl_pandas.py
```

This produces cleaned node/edge tables under `data_processed/` (users, songs, listened, artists, genres, etc.) and structures them in a Spark‑like “folder with one CSV” layout.

> Original Spark version (optional):  
> `python etl/etl_pyspark.py`

### 5.3 Run Graph Analysis (Popularity, PageRank, Co‑listen)

Run the Pandas/NetworkX analysis to generate features used by the recommender:

```bash
python spark/pandas_recs.py
```

This creates:

- `data_processed/spark_outputs/song_popularity_top1000.csv/part-00000.csv`
- `data_processed/spark_outputs/song_pagerank_top1000.csv/part-00000.csv`
- `data_processed/spark_outputs/song_co_listen_pairs_top1000.csv/part-00000.csv`

> Original Spark GraphFrames script (optional):  
> `python spark/graphframes_recs.py`

### 5.4 Generate Recommendations

Generate top‑K recommendations for an automatically selected “top” user:

```bash
python app/generate_recs.py --top_k 20
```

Or for a specific user ID:

```bash
python app/generate_recs.py --user_id <user_id> --top_k 20
```

Outputs are saved under:

- `data_processed/recs/user_<user_id>_top<k>.csv`

### 5.5 Build the HTML Report

Convert the latest recommendations CSV into a web-friendly report:

```bash
python app/generate_html_report.py
```

This generates:

- `recommendations_report.html`

and attempts to open it in your default browser.

---

## 6. Neo4j Setup (Optional)

To explore the graph in Neo4j and run additional algorithms:

1. Start a Neo4j database in Neo4j Desktop.
2. Copy the processed CSVs from `data_processed/` into Neo4j’s `import` folder.
3. In Neo4j Browser, run:
   - `neo4j/schema.cypher`
   - `neo4j/load_nodes.cypher`
   - `neo4j/load_edges.cypher`
4. Optionally run graph algorithms from `neo4j/gds_queries.cypher`.

---

## 7. Troubleshooting

- **Missing `data_raw` folder**  
  Run:

  ```bash
  python data_generation_script.py
  ```

- **Spark / Java issues on Windows**  
  Use the Pandas/NetworkX pipeline instead:

  ```bash
  python etl/etl_pandas.py
  python spark/pandas_recs.py
  ```

- **No recommendations generated**  
  Make sure you have run ETL and analysis steps first, and that `data_processed/spark_outputs` and `data_processed/graph_for_spark` exist.

---

## 8. License

Update this section with your chosen license (e.g., MIT) if you plan to open‑source the project.

# Graph Music Recommendation System

A graph-based music recommendation system using data processing (ETL) and graph algorithms (PageRank, Co-listen counts).

## Project Structure

- `app/`: Application code (recommender script).
- `data_raw/`: Input data (Million Song Dataset + Spotify + Last.fm).
- `data_processed/`: Processed CSVs and graph data.
- `etl/`: ETL scripts to clean and transform data.
- `neo4j/`: Cypher scripts for loading data into Neo4j.
- `spark/`: Spark (and Pandas) scripts for graph analysis.
- `notebooks/`: Data exploration notebooks.

## Prerequisites

- Python 3.8+
- Java 8 or 11 (if running Spark scripts, otherwise not needed for Pandas fallback).
- Neo4j Desktop (Optional, for visualization).

## Setup & Run

### 1. Install Dependencies

```bash
pip install pandas pyspark networkx neo4j
```

### 2. Prepare Data

If you do not have the raw dataset, you can generate dummy data for testing:

```bash
python data_generation_script.py
```

This populates `data_raw/`.

### 3. Run ETL (Data Processing)

We provide a Pandas-based ETL for easy local setup (bypassing Hadoop requirements):

```bash
python etl/etl_pandas.py
```

This creates `data_processed/users`, `songs`, `listened`, etc.

_(Original Spark script: `python etl/etl_pyspark.py`)_

### 4. Run Analysis (PageRank & Popularity)

Run the analysis script to generate graph metrics (Popularity, PageRank, Co-listen pairs):

```bash
python spark/pandas_recs.py
```

This creates `data_processed/spark_outputs`.

_(Original Spark script: `python spark/graphframes_recs.py`)_

### 5. Generate Recommendations

Run the application to generate recommendations for a specific user (or auto-picked top user):

```bash
python app/generate_recs.py --top_k 20
```

or for a specific user:

```bash
python app/generate_recs.py --user_id <user_id>
```

Output is saved to `data_processed/recs/`.

## Neo4j Setup (Optional)

To load data into Neo4j:

1.  Start Neo4j Database.
2.  Copy CSVs from `data_processed/` to the Neo4j `import` folder.
3.  Run `neo4j/schema.cypher` in Neo4j Browser.
4.  Run `neo4j/load_nodes.cypher`.
5.  Run `neo4j/load_edges.cypher`.

## troubleshooting

- **Missing `data_raw`**: Run `data_generation_script.py`.
- **Spark errors on Windows**: Use the provided `etl_pandas.py` and `pandas_recs.py` instead of the Spark variants.

#
