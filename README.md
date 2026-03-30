# Coffee Shop Data Platform

An end-to-end data engineering project built on AWS, simulating a real-time 
data platform for a multi-city coffee shop chain.

## Architecture
```
iPhone / Android / POS → Kafka → S3 (raw/Avro) → Spark → S3 (curated/Parquet) → Snowflake
                                                                      → Athena
                              Airflow orchestrates the batch pipeline hourly
                              Terraform provisions all AWS infrastructure
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Streaming | Apache Kafka, Confluent Schema Registry, Avro |
| Storage | AWS S3 (data lake — raw + curated + archive zones) |
| Processing | Apache Spark (PySpark), batch transformation |
| Serving | Snowflake (external stage, Parquet queries) |
| Orchestration | Apache Airflow (DAG, hourly schedule) |
| Infrastructure | Terraform, AWS EC2, IAM, Docker |
| Language | Python 3.12 |

## Project Structure
```
coffee-shop/
├── producer.py              # Kafka producer — simulates iPhone/POS orders
├── consumer.py              # Kafka consumer — Avro deserialisation
├── s3_sink.py               # Micro-batch sink — Kafka → S3 raw zone
├── spark_btach_job.py       # PySpark batch — raw JSON → curated Parquet
├── register_schema.py       # Avro schema registration with Schema Registry
├── coffee_order_schema.json # Avro schema definition
├── docker-compose.yml       # Kafka + ZooKeeper + Schema Registry
├── airflow/
│   └── dags/
│       └── coffee_shop_pipeline.py  # Airflow DAG
└── terraform/
    ├── main.tf              # AWS resources
    ├── variables.tf         # Input variables
    ├── outputs.tf           # Output values
    └── terraform.tfvars     # Variable values (gitignored)
```

## Pipeline Flow

1. **Producer** simulates coffee orders from 3 cities (Delhi, Mumbai, Hyderabad)
   across 3 channels (POS, iOS, Android) and publishes to Kafka topic 
   `coffee_orders` with `store_id` as partition key
   
2. **Schema Registry** enforces the Avro schema on every message — 
   rejects bad data before it enters the topic
   
3. **S3 Sink** consumes from Kafka and micro-batches messages to S3 raw zone
   every 60 seconds as NDJSON, partitioned by year/month/day/hour
   
4. **Spark Batch Job** runs hourly, reads raw JSON, applies transformations
   (timestamp parsing, revenue calculation, data quality filters), 
   and writes Parquet to curated zone partitioned by store_id and order_date
   
5. **Snowflake** queries curated Parquet directly from S3 via external stage
   — no data movement, pay only for compute
   
6. **Airflow DAG** orchestrates steps 4-5 hourly with automatic retries,
   pipeline guarding, and task dependency management

## Key Design Decisions

**Why Kafka over direct S3 upload?**
Decouples producers from consumers. The iPhone app has no knowledge of 
Spark or Snowflake. Adding a new consumer never requires changes to producers.

**Why Avro over JSON?**
Schema enforcement at the source. Breaking changes are rejected before 
entering the pipeline. Binary encoding is ~5x smaller than JSON at scale.

**Why batch Spark over streaming?**
Most business questions (daily revenue, store performance) don't need 
sub-second latency. Hourly batch is simpler, cheaper, and easier to reprocess.

**Why Snowflake over Redshift?**
External stage queries Parquet directly from S3 — no data loading step.
Auto-suspend eliminates idle compute costs during learning.

**Why Terraform?**
Entire infrastructure reproducible with two commands. 
No manual console clicks, no undocumented resources, no surprise costs.

## Sample Queries
```sql
-- Revenue by store
SELECT store_id, COUNT(*) AS orders, ROUND(SUM(revenue), 2) AS total_revenue
FROM coffee_shop.raw.orders
GROUP BY store_id ORDER BY total_revenue DESC;

-- Peak ordering hours
SELECT HOUR(order_ts) AS hour, COUNT(*) AS orders
FROM coffee_shop.raw.orders
GROUP BY hour ORDER BY orders DESC;

-- Most popular drinks by city
SELECT store_id, drink, COUNT(*) AS times_ordered
FROM coffee_shop.raw.orders
GROUP BY store_id, drink ORDER BY times_ordered DESC;
```

## Setup

### Prerequisites
- AWS account with S3 bucket
- Snowflake trial account
- Docker + Docker Compose

### Infrastructure
```bash
cd terraform
terraform init
terraform apply
```

### Start the pipeline
```bash
# Start Kafka stack
docker compose up -d

# Register Avro schema
python3 register_schema.py

# Start producer (terminal 1)
python3 producer.py

# Start S3 sink (terminal 2)  
python3 s3_sink.py

# Run Spark batch job
python3 spark_btach_job.py

# Sync to S3
aws s3 sync data/curated/ s3://coffeeinventory/curated/coffee_orders/
```

### Airflow
```bash
export AIRFLOW_HOME=~/airflow
airflow webserver --port 8080 &
airflow scheduler &
```

Navigate to `http://YOUR_EC2_IP:8080` and trigger `coffee_shop_pipeline`.
