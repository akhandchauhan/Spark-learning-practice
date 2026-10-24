"""Generates data/songs.csv (~100 MB) and data/song_listened/ (~2 GB parquet, hive-partitioned by listen_date)."""
import os
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

OUT = "data"
N_SONGS = 1_430_000
START, N_DAYS = date(2024, 1, 1), 731          # 2024-01-01 .. 2025-12-31
ROWS_PER_DAY = 70_000                          # ~2 GB total across N_DAYS
rng = np.random.default_rng(42)

words = np.array(["Love", "Night", "Fire", "Dream", "Road", "Heart", "Sky", "Rain", "Gold", "Blue",
                  "Wild", "Echo", "Summer", "Shadow", "River", "Dance", "Midnight", "Lost", "Home", "Star"])
artists = np.array([f"Artist_{i:05d}" for i in range(20_000)])
genres = np.array(["Pop", "Rock", "Hip-Hop", "Jazz", "Classical", "Electronic", "Country", "R&B", "Metal", "Folk"])
devices = np.array(["mobile", "web", "desktop", "tv", "speaker"])
countries = np.array(["India", "USA", "UK", "Germany", "Canada", "Brazil", "Japan", "France"])


def pick(a, n):
    return a[rng.integers(0, len(a), n)]


def write_songs():
    n = N_SONGS
    df = pd.DataFrame({
        "song_id": np.arange(1, n + 1),
        "title": pd.Series(pick(words, n)) + " " + pd.Series(pick(words, n)) + " " + pd.Series(pick(words, n)),
        "artist": pick(artists, n),
        "album": "Album " + pd.Series(pick(words, n)) + " " + pd.Series(rng.integers(1, 5000, n).astype(str)),
        "genre": pick(genres, n),
        "duration_sec": rng.integers(90, 420, n),
        "release_year": rng.integers(1970, 2026, n),
    })
    df.to_csv(f"{OUT}/songs.csv", index=False)
    print(f"songs.csv: {os.path.getsize(f'{OUT}/songs.csv') / 1e6:.0f} MB")


def write_song_listened():
    base = f"{OUT}/song_listened"
    for d in range(N_DAYS):
        day = START + timedelta(days=d)
        n = ROWS_PER_DAY
        ts = pd.Timestamp(day) + pd.to_timedelta(rng.integers(0, 86_400, n), unit="s")
        tbl = pa.table({
            "listen_id": np.arange(d * n, (d + 1) * n),
            "user_id": rng.integers(1, 5_000_000, n),
            "song_id": rng.integers(1, N_SONGS + 1, n),
            "listened_at": ts,
            "listen_duration_sec": rng.integers(5, 420, n),
            "device": pick(devices, n),
            "country": pick(countries, n),
            "session_id": pd.Series(rng.integers(0, 2**62, n)).map("{:x}".format),
        })
        part = f"{base}/listen_date={day}"
        os.makedirs(part, exist_ok=True)
        pq.write_table(tbl, f"{part}/part-0.parquet", compression="snappy")
        if d % 50 == 0:
            print(f"day {d + 1}/{N_DAYS}")
    total = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(base) for f in fs)
    print(f"song_listened: {total / 1e9:.2f} GB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    write_songs()
    write_song_listened()
