# Spark Learning Practice

Hands-on PySpark practice for core Spark internals: caching/persistence, join mechanics, dynamic partition pruning, and processing at non-trivial scale (1M+ row and multi-GB synthetic datasets). Two learning tracks: Ankit Bansal's PySpark course and DE with Dhairy.

Runs in **GitHub Codespaces** as a Spark standalone cluster with **1 driver + 2 executors**, all with visible UIs. No docker needed.

## Cluster layout

```
Codespace (one VM)
├── Driver      = notebook kernel (Python 3.11)     -> UI :4040
├── Master      spark://localhost:7077              -> UI :8080
├── Worker 1 -> Executor 1  (1 core, 1g)            -> UI :8081
└── Worker 2 -> Executor 2  (1 core, 1g)            -> UI :8082
```

| Component | Where it runs | Started by | Where to see it |
|---|---|---|---|
| Driver | Notebook kernel | Running the notebook's first cell | Port **4040**, Executors tab, row `driver` |
| Executor 1 | Worker 1 | Driver requests it from the master | Port **4040**, Executors tab, row `0`; port **8081** |
| Executor 2 | Worker 2 | Driver requests it from the master | Port **4040**, Executors tab, row `1`; port **8082** |
| Master | Codespace background process | `.devcontainer/start-cluster.sh` on every Codespace start | Port **8080** |

The session asks for `spark.executor.cores=1` and `spark.cores.max=2`. Each worker has 1 core, so the driver gets exactly one executor per worker.

## Run it in Codespaces

1. Create or rebuild the Codespace:
   - New: on GitHub, **Code** -> **Codespaces** -> **Create codespace on main**.
   - Existing: run `git pull`, then press F1 and choose **Codespaces: Rebuild Container**.

   The `.devcontainer/` config installs Python 3.11, Java 17 and `requirements.txt` (PySpark 3.5.0). It starts the master and 2 workers, then generates the datasets in the background.
2. Wait for the data. Run `tail -f /tmp/generate_songs.log` and wait for `song_listened: ... GB` (about 5-10 min, ~2.4 GB).
3. Check the cluster. Run `bash .devcontainer/start-cluster.sh`. It is safe to re-run and should print `Spark workers running: 2`. Then, in the **Ports** tab, click the globe icon on **8080**. It should show **Alive Workers: 2**.
4. Open `dynamic_partition_pruning.ipynb`. In the kernel picker, choose **Python 3.11**. If prompted, accept **Install/Enable suggested extensions**.
5. Run the first cell. It starts the driver and connects to `spark://localhost:7077`.
6. Verify you have **1 driver + 2 executors**:
   - The first cell prints `3` (1 driver + 2 executors).
   - On port **4040**, the **Executors** tab lists `driver`, `0` and `1`.
   - On port **8080**, under **Running Applications**, `dynamic_partition_pruning` uses 2 cores.

The 4040 UI only responds while the SparkSession is alive.

## Troubleshooting

| Symptom | Fix |
|---|---|
| 8080 shows fewer than 2 workers | Run `bash .devcontainer/start-cluster.sh`. It starts only the missing master/workers and prints the worker count. Logs: `tail /tmp/spark-logs/*.log` |
| First cell prints `1` or `2`, not `3` | Executors are still starting. Re-run the line after a few seconds. If it stays low, check 8080 for 2 alive workers. |
| Notebook can't find `data/...` | If `pgrep -f generate_songs_data.py` shows it, wait for `song_listened: ... GB` in `/tmp/generate_songs.log`. If no process and no `data/`, run `python generate_songs_data.py` |
| 4040 won't load | Run the first cell first. If a second session is running, it moves to 4041; check `spark.sparkContext.uiWebUrl`. |
| Everything is slow | Driver, master and both workers share one VM. Use a 4-core Codespace machine type. |

## What's in here

| Path | Purpose |
|---|---|
| `.devcontainer/devcontainer.json` | Codespaces environment: Python 3.11, Java 17, forwarded ports 8080/8081/8082/4040 |
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

`song_listened.song_id` references `songs.song_id`. Generated data is gitignored; the Codespace regenerates it on creation.
