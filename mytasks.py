from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import snowflake.connector

default_args = {
    'owner': 'surya',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

def check_s3_files():
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket='coffeeinventory',
                                Prefix='raw/coffee_orders/')
    files = response.get('Contents', [])
    if not files:
        raise ValueError('No files found in S3 bucket')
    print(f"Found {len(files)} files in raw zone. Proceeding")



def reload_snowflake():
    print("Reloading Snowflake with new data from S3...")
    # Snowflake connection parameters
    conn = snowflake.connector.connect(
        user='',
        password='',
        account='',
        warehouse='',
        database='',
        schema=''
    )

    cursor = conn.cursor()
    cursor.execute("USE WAREHOUSE coffee_wh")
    cursor.execute("USE DATABASE coffee_shop")
    cursor.execute("USE SCHEMA raw")
    cursor.execute("TRUNCATE TABLE orders")
    cursor.execute("""
            INSERT INTO coffee_shop.raw.orders (
                order_id,
                store_id,
                system,
                drink,
                quantity,
                price,
                revenue,
                customer_id,
                order_ts
            )
            SELECT
                $1:order_id::STRING      AS order_id,
                $1:store_id::STRING      AS store_id,
                $1:system::STRING        AS system,
                $1:drink::STRING         AS drink,
                $1:quantity::INT         AS quantity,
                $1:price::FLOAT          AS price,
                $1:revenue::FLOAT        AS revenue,
                $1:customer_id::STRING   AS customer_id,
                $1:timestamp::TIMESTAMP  AS order_ts
            FROM @coffee_shop.raw.coffee_stage
            (FILE_FORMAT => parquet_format, PATTERN => '.*[.]parquet')
        """)

    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    print(f"Loaded {count} rows into orders table.")
    conn.close()


with DAG(
    dag_id='coffee_shop_pipeline',
    default_args=default_args,
    description='A DAG to process coffee orders from S3 to Snowflake',
    start_date=datetime(2026, 3, 26),
    schedule='@hourly',
    catchup=False,
    tags=['coffee','kafka','snowflake']


) as dag:


    task_1 = PythonOperator(
    task_id='check_s3_files',
    python_callable=check_s3_files
    )

    task_2 = BashOperator(
    task_id='run_spark_job',
    bash_command='cd /home/ubuntu/coffee-shop && python3 spark_batch_job.py'
    )

    task_3 = PythonOperator(
    task_id='reload_snowflake',
    python_callable=reload_snowflake
    )


    task_4 = BashOperator(
    task_id='aws_sync_files',
    bash_command='aws s3 sync /home/ubuntu/coffee-shop/data/curated/ s3://coffeeinventory/curated/coffee_orders/'
    )


    task_1 >> task_2 >> task_4 >> task_3