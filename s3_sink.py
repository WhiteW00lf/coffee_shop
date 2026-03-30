from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import json
import boto3
from datetime import datetime, time, timezone

KAFKA_BROKER = 'localhost:29092'
KAFKA_TOPIC = 'coffee_orders'
SCHEMA_REGISTRY_URL = 'http://localhost:8081'
BUCKET = 'coffeeinventory'
TOPIC = 'coffee_orders'
BATCH_SECONDS = 60

with open('coffee_order_schema.json') as f:
    schema_str = json.dumps(json.load(f))



consumer = DeserializingConsumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 's3-sink-group',
    'auto.offset.reset': 'earliest',
    'schema.registry.url': SCHEMA_REGISTRY_URL,
    'key.deserializer': AvroDeserializer(SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL}), schema_str),
    'value.deserializer': lambda x: x.decode('utf-8') if x else None
})


s3 = boto3.client('s3')

consumer.subscribe([KAFKA_TOPIC])

batch = []

batch_start_time = time.time()

print("Starting S3 sink consumer...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        if msg.value() is not None:
            batch.append(msg.value())
        if time.time() - batch_start_time >= BATCH_SECONDS:
            if batch:
                now = datetime.now(timezone.utc)
                key = f"/raw/coffee_orders/YEAR={now.year}/MONTH={now.month:02d}/DAY={now.day:02d}/HOUR={now.hour:02d}/coffee_orders_{now.strftime('%Y%m%d_%H%M%S')}.json"
                s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(batch))
                print(f"Wrote {len(batch)} records to S3:", key)
except KeyboardInterrupt:
    pass

finally:
    consumer.close()
    print("S3 sink consumer stopped.")