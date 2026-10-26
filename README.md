# Spark Learning Practice

Hands-on PySpark practice for core Spark internals: caching/persistence, join mechanics, dynamic partition pruning, and processing at non-trivial scale (1M+ row and multi-GB synthetic datasets). Two learning tracks: Ankit Bansal's PySpark course and DE with Dhairy.

## Quick start (GitHub Codespaces)

1. **Code** -> **Codespaces** -> **Create codespace on main**. The `.devcontainer/` config installs Python 3.11, Java 17 and `requirements.txt` (PySpark 3.5.0), starts a standalone cluster (1 master + 2 workers, no docker), and generates the datasets in the background (~5-10 min, ~2.4 GB).
2. Check progress: `tail -f /tmp/generate_songs.log`. It prints `song_listened: ... GB` when done.
3. Open `dynamic_partition_pruning.ipynb`, click the kernel picker and select the **Python 3.11** interpreter. If the Jupyter extension isn't active, accept **Install/Enable suggested extensions**.
4. Run the first cell. The notebook kernel is the **driver**; it connects to `spark://localhost:7077`.
5. Open the UIs from the **Ports** tab (globe icon):

| Port | UI | Shows |
|---|---|---|
| 8080 | Spark Master UI | 2 alive workers, running applications |
| 8081, 8082 | Worker 1, Worker 2 | Executors running on each worker |
| 4040 | Spark App UI (driver) | Jobs, Stages, SQL, **Executors** tab (driver + 2 executors) |

The 4040 UI only responds while a SparkSession is alive. If it moves to 4041, check `spark.sparkContext.uiWebUrl`.

Troubleshooting: master/worker logs are in `/tmp/spark-logs/`. To restart the cluster: `pkill -f org.apache.spark.deploy; bash .devcontainer/start-cluster.sh`.

All three "nodes" are processes in one Codespace VM, so they share its CPU and memory. Use a 4-core machine type for comfortable runs.

## Quick start (local)

```bash
pip install -r requirements.txt   # needs Java 17+ on PATH
python generate_songs_data.py     # writes data/songs.csv and data/song_listened/
jupyter notebook                  # use .master("local[2]") in the session cell
```

Spark UI is at `http://localhost:4040` while a session is running.

## What's in here

| Path | Purpose |
|---|---|
| `.devcontainer/` (`devcontainer.json`, `start-cluster.sh`), `requirements.txt` | One-click Codespaces environment: Python 3.11, Java 17, PySpark 3.5.0, standalone master + 2 workers, forwarded UI ports |
| `dynamic_partition_pruning.ipynb` | DPP demo: fact table partitioned by `listen_date` joined to a filtered date dimension |
| `generate_songs_data.py` | Generates `data/songs.csv` (~100 MB) and `data/song_listened/` (~2.4 GB parquet, 731 `listen_date=` partitions) |
| `generate_1_mn_rows.py` | Generates a synthetic ~1M-row orders CSV |
| `cache_vs_persist.ipynb` | `.cache()` vs `.persist()` storage levels |
| `Ankit_Bansal_pyspark_course_practice/`, `DE_with_Dhairy/` | Dated lecture notebooks: joins, partitioning, Spark SQL |
| `docker-compose.yml` | Optional docker version of the cluster (master, 2 workers, Jupyter). Heavier (~2.5 GB of images); not needed in Codespaces |

## Datasets

| File | Columns |
|---|---|
| `data/songs.csv` | `song_id`, `title`, `artist`, `album`, `genre`, `duration_sec`, `release_year` |
| `data/song_listened/listen_date=YYYY-MM-DD/` | `listen_id`, `user_id`, `song_id`, `listened_at`, `listen_duration_sec`, `device`, `country`, `session_id` (+ `listen_date` from the folder) |

`song_listened.song_id` references `songs.song_id`. Generated data is gitignored; regenerate with the scripts above.

## Optional: docker-compose cluster

```bash
docker compose up -d
```

Master UI on 8080, Jupyter on 8888, app UI on 4040. The repo is mounted at `/data` in every container, so data paths become `/data/data/...` and the session must use `.master("spark://spark-master:7077")`. Run the notebook from the Jupyter container's kernel (`http://localhost:8888`), not the Codespace's Python.
