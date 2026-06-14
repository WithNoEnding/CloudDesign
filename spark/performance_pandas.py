import time
import pandas as pd

DATA_PATH = "data/douban_movies.csv"

t0 = time.perf_counter()
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=["year", "rating_score"])
df["genres"] = df["genres"].fillna("未知")

genre = df.assign(genre=df["genres"].str.split("/")).explode("genre")
genre["genre"] = genre["genre"].astype(str).str.strip()
result = genre.groupby("genre").agg(
    movie_count=("movie_id", "count"),
    avg_rating=("rating_score", "mean")
).sort_values("movie_count", ascending=False)

t1 = time.perf_counter()
print(result.head(20))
print(f"Pandas genre aggregation time: {t1 - t0:.4f} seconds")
