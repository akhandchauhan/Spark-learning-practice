# Spark Learning Practice

PySpark practice on a Spark standalone cluster with **1 driver + 2 executors**, running inside GitHub Codespaces with every UI visible.

```
Codespace (one VM)
├── Driver      = notebook kernel (Python 3.11)     -> UI :4040
├── Master      spark://localhost:7077              -> UI :8080
├── Worker 1 -> Executor 1  (1 core, 1g)            -> UI :8081
└── Worker 2 -> Executor 2  (1 core, 1g)            -> UI :8082
```

## Start everything

### 1. Open the Codespace
- **First time:** on GitHub, **Code** -> **Codespaces** -> **Create codespace on main**. Wait until the terminal is ready (installs Java 17 and PySpark 3.5.0).
- **Existing Codespace:** open it, then in the terminal run:
  ```bash
  git pull
  ```
  If `git pull` complains about local changes to the notebook, run `git stash` first.

### 2. Make sure the data exists
```bash
ls data/song_listened | wc -l
```
- Prints `731`: data is ready, go to step 3.
- Anything else, run:
  ```bash
  pgrep -f generate_songs_data.py || python generate_songs_data.py
  ```
  If it prints a process ID, generation is already running in the background. Wait and re-check step 2. Otherwise it generates the data now (5-10 min) and ends with `song_listened: ... GB`.

### 3. Start the cluster (master + 2 workers)
```bash
bash .devcontainer/start-cluster.sh
```
It must print `Spark workers running: 2 (expected 2)`. It is safe to re-run; it starts only what is missing.

### 4. Open the notebook and pick the kernel
1. Open `dynamic_partition_pruning.ipynb`.
2. Click the kernel picker (top right), then **Python Environments...**, then **Python 3.11**.
   If it shows **Install/Enable suggested extensions**, click that first.

### 5. Start the driver
1. Click **Restart** in the notebook toolbar. This clears any old session.
2. Run the first cell.
3. Wait about 10 seconds. Then run this in a new cell:
   ```python
   spark.sparkContext._jsc.sc().getExecutorMemoryStatus().size()
   ```
   It must print `3` (1 driver + 2 executors). If it prints `1` or `2`, wait and run it again.

### 6. Open the UIs
Go to the **Ports** tab and click the globe icon on each row:

| Port | What you should see |
|---|---|
| 8080 | Master: **Alive Workers: 2**; `dynamic_partition_pruning` under Running Applications with 2 cores |
| 4040 | Driver/app UI: **Executors** tab lists `driver`, `0`, `1`. **SQL** tab shows query plans |
| 8081 | Worker 1, with one executor running |
| 8082 | Worker 2, with one executor running |

4040 only works while the notebook's Spark session is alive.

### 7. Run the rest of the notebook
Run the remaining cells top to bottom.

## Every time you come back
1. Open the Codespace.
2. Run step 3 (`bash .devcontainer/start-cluster.sh`).
3. Run step 5.

The data stays on disk, so you don't need step 2 again.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Step 3 prints fewer than 2 workers | Run `tail -20 /tmp/spark-logs/worker1.log /tmp/spark-logs/worker2.log` and check for errors |
| `PATH_NOT_FOUND ... data/...` in the notebook | Data is missing. Do step 2 |
| `LiveListenerBus is stopped` or a dead session | Click **Restart** in the notebook, then do step 5 |
| No 4040 row in the Ports tab | Run step 5 first. If it still isn't there, use **Forward a Port** and enter `4040` |
| Everything is slow | All four processes share one VM. Use a 4-core Codespace machine type |

## What's in here

| Path | Purpose |
|---|---|
| `.devcontainer/devcontainer.json` | Codespaces environment: Python 3.11, Java 17, PySpark, forwarded ports 8080/8081/8082/4040 |
| `.devcontainer/start-cluster.sh` | Starts the master and 2 workers (1 core, 1g each); logs in `/tmp/spark-logs/` |
| `requirements.txt` | PySpark 3.5.0 and the data generator's dependencies |
| `dynamic_partition_pruning.ipynb` | DPP demo: fact table partitioned by `listen_date` joined to a filtered date dimension |
| `generate_songs_data.py` | Generates `data/songs.csv` (~100 MB) and `data/song_listened/` (~2.4 GB parquet, 731 `listen_date=` partitions) |
| `generate_1_mn_rows.py` | Generates a synthetic ~1M-row orders CSV |
| `cache_vs_persist.ipynb` | `.cache()` vs `.persist()` storage levels |
| `Ankit_Bansal_pyspark_course_practice/`, `DE_with_Dhairy/` | Dated lecture notebooks: joins, partitioning, Spark SQL |

## Datasets

| File | Columns |
|---|---|
| `data/songs.csv` | `song_id`, `title`, `artist`, `album`, `genre`, `duration_sec`, `release_year` |
| `data/song_listened/listen_date=YYYY-MM-DD/` | `listen_id`, `user_id`, `song_id`, `listened_at`, `listen_duration_sec`, `device`, `country`, `session_id` (+ `listen_date` from the folder) |

`song_listened.song_id` references `songs.song_id`. Generated data is gitignored.
