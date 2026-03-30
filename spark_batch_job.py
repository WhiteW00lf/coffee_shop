from pyspark.sql import SparkSession
<<<<<<< HEAD
from pyspark.sql.functions import col, to_timestamp,date_format,round,trim

spark = SparkSession.builder \
    .appName("CoffeeShopBatch") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.367") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.InstanceProfileCredentialsProvider") \
    .config("spark.hadoop.fs.s3a.connection.timeout", "600000") \
    .config("spark.hadoop.fs.s3a.socket.timeout", "600000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

RAW = "/home/ubuntu/coffee-shop/data/raw/coffee_orders/"
CURATED = "/home/ubuntu/coffee-shop/data/curated/coffee_orders/"
=======
from pyspark.sql.functions import col, to_timestamp, date_format, round,trim

spark = (
    SparkSession.builder.appName("CoffeeShopBatch")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

RAW     = "/home/ubuntu/coffee-shop/data/raw/"
CURATED = "/home/ubuntu/coffee-shop/data/curated/"
>>>>>>> 0f69dad (Added Terraform Infrastructure As Code)

df = spark.read.json(RAW)

print(df.schema)

df = df.withColumn("timestamp", to_timestamp(col("timestamp")))
<<<<<<< HEAD
df = df.withColumn("order_date", trim(date_format(col("timestamp"), "yyyy-MM-dd "))) 
=======
df = df.withColumn("order_date", trim(date_format(col("timestamp"), "yyyy-MM-dd ")))
>>>>>>> 0f69dad (Added Terraform Infrastructure As Code)
df = df.withColumn("revenue", round(col("quantity") * col("price"), 2))
df = df.withColumn("order_hour", date_format(col("timestamp"), "HH"))


<<<<<<< HEAD
df = df.filter((col("price") >= 0) & col("store_id").isNotNull() & col("order_id").isNotNull() & col("timestamp").isNotNull())
=======
df = df.filter(
    (col("price") >= 0)
    & col("store_id").isNotNull()
    & col("order_id").isNotNull()
    & col("timestamp").isNotNull()
)
>>>>>>> 0f69dad (Added Terraform Infrastructure As Code)


df = df.select(
    "order_id",
    "store_id",
    "system",
    "drink",
    "quantity",
    "price",
    "revenue",
    "customer_id",
    "timestamp",
    "order_date",
<<<<<<< HEAD
    "order_hour"
=======
    "order_hour",
>>>>>>> 0f69dad (Added Terraform Infrastructure As Code)
)

print(df.printSchema())
df.show(5, truncate=False)

print("Group by stores")
df.groupBy("store_id").sum("revenue").show()

print("Group by drinks")
df.groupBy("drink").sum("revenue").show()

print("Group by system")
df.groupBy("system").sum("revenue").show()

print("Writing curated data to S3...")

<<<<<<< HEAD
df.write\
    .mode("overwrite") \
    .partitionBy("order_date", "order_hour") \
    .parquet(CURATED)
print("Batch job completed successfully.")

spark.stop()


=======
df.write.mode("overwrite").partitionBy("order_date", "order_hour").parquet(CURATED)
print("Batch job completed successfully.")

spark.stop()
>>>>>>> 0f69dad (Added Terraform Infrastructure As Code)
