import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, min as spark_min, max as spark_max, stddev,
    split, explode, trim, desc, row_number, when, isnan, sum as spark_sum
)
from pyspark.sql.window import Window

DATA_PATH = "/opt/spark/work/data/douban_movies.csv"

spark = SparkSession.builder.appName("DoubanMoviesAnalysis").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

start_total = time.perf_counter()

# 1. 加载数据
raw = spark.read.option("header", True).option("inferSchema", True).csv(DATA_PATH)
print("========== Schema ==========")
raw.printSchema()
print("========== 前5行 ==========")
raw.show(5, truncate=60)

raw_count = raw.count()
print(f"清洗前行数: {raw_count}")

# 2. 缺失值统计
print("========== 缺失值统计 ==========")
missing_exprs = []
for c, t in raw.dtypes:
    if t in ("double", "float"):
        expr = spark_sum(when(col(c).isNull() | isnan(col(c)), 1).otherwise(0)).alias(c)
    else:
        expr = spark_sum(when(col(c).isNull() | (trim(col(c).cast("string")) == ""), 1).otherwise(0)).alias(c)
    missing_exprs.append(expr)
missing = raw.select(missing_exprs)
missing.show(truncate=False)

# 3. 数据清洗：对至少两个字段采用不同策略
# 策略1：关键数值字段 year/rating_score 缺失会影响统计，直接删除。
# 策略2：文本字段 genres/countries/directors/summary 缺失不影响评分统计，用“未知”填充。
df = raw.dropna(subset=["year", "rating_score"])
df = df.fillna({
    "genres": "未知",
    "countries": "未知",
    "directors": "未知",
    "summary": "无简介",
    "original_title": "未知"
})
df = df.filter((col("rating_score") >= 0) & (col("rating_score") <= 10))
df = df.withColumn("year", col("year").cast("int"))
clean_count = df.count()
print(f"清洗后行数: {clean_count}")
print(f"删除行数: {raw_count - clean_count}")

print("========== 数值字段基本统计 ==========")
df.select("year", "rating_score", "rating_count", "collect_count").describe().show()

# 4. SQL/DataFrame统计分析
print("========== 查询1：按类型统计电影数量和平均评分（GROUP BY） ==========")
genre_df = df.withColumn("genre", explode(split(col("genres"), "/"))).withColumn("genre", trim(col("genre")))
q1 = genre_df.groupBy("genre").agg(
    count("*").alias("movie_count"),
    avg("rating_score").alias("avg_rating")
).filter(col("movie_count") >= 20).orderBy(desc("avg_rating"))
q1.show(20, truncate=False)

print("========== 查询2：评分人数大于10000的电影评分Top10（ORDER BY Top-N） ==========")
q2 = df.filter(col("rating_count") >= 10000).select(
    "title", "year", "rating_score", "rating_count", "genres"
).orderBy(desc("rating_score"), desc("rating_count")).limit(10)
q2.show(10, truncate=False)

print("========== 查询3：按年份统计电影数量和平均评分（时间维度趋势） ==========")
q3 = df.groupBy("year").agg(
    count("*").alias("movie_count"),
    avg("rating_score").alias("avg_rating")
).filter((col("year") >= 1980) & (col("year") <= 2025)).orderBy("year")
q3.show(80, truncate=False)

print("========== 查询4：每个类型内评分排名Top5（窗口函数） ==========")
w = Window.partitionBy("genre").orderBy(desc("rating_score"), desc("rating_count"))
q4 = genre_df.filter((col("genre") != "未知") & (col("rating_count") >= 5000)).select(
    "genre", "title", "year", "rating_score", "rating_count"
).withColumn("rank_in_genre", row_number().over(w)).filter(col("rank_in_genre") <= 5).orderBy("genre", "rank_in_genre")
q4.show(100, truncate=False)

# 5. 性能测试查询：类型聚合
print("========== PySpark性能测试：类型聚合查询 ==========")
t0 = time.perf_counter()
perf = genre_df.groupBy("genre").agg(
    count("*").alias("movie_count"),
    avg("rating_score").alias("avg_rating")
).orderBy(desc("movie_count"))
perf.collect()
t1 = time.perf_counter()
print(f"PySpark genre aggregation time: {t1 - t0:.4f} seconds")
print(f"Total job time: {time.perf_counter() - start_total:.4f} seconds")

spark.stop()
