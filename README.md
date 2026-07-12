# Spark Learning Practice

Hands-on PySpark practice environment — a local, containerized Spark setup used to work through core Spark internals: caching/persistence strategies, join mechanics, and processing at non-trivial scale (1M+ row synthetic datasets), across two learning tracks (Ankit Bansal's PySpark course, DE with Dhairy).

## What's in here

- `docker-compose.yml` — local Spark cluster (no cloud account needed to run any notebook here)
- `generate_1_mn_rows.py` — generates a synthetic ~1M-row orders dataset locally instead of committing raw data to git
- `cache_vs_persist.ipynb` — benchmarking `.cache()` vs `.persist()` storage levels
- `Ankit_Bansal_pyspark_course_practice/`, `DE_with_Dhairy/` — dated lecture notebooks working through joins, partitioning, and Spark SQL
- `data/` — gitignored; run `generate_1_mn_rows.py` locally to populate it

## Running it

```bash
docker compose up -d
python generate_1_mn_rows.py   # writes data/orders_1M.csv locally (gitignored)
```

Then point any notebook at the local Spark cluster started by docker-compose.

## Note on data

Raw datasets are intentionally not committed to version control (see `.gitignore`) — `generate_1_mn_rows.py` regenerates the working dataset locally on demand. An earlier ~44MB CSV that had been committed here was removed for this reason.
