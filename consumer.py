from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import json

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'coffee_orders'
SCHEMA_REGISTRY_URL = 'http://localhost:8081'

with open('coffee_order_schema.json', 'r') as f:    

    schema_str = json.dumps(json.load(f))


schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})
avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)

consumer = DeserializingConsumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'coffee-consumer-group',
    'key.deserializer': lambda k, ctx: k.decode('utf-8') if k else None,
    'value.deserializer': avro_deserializer,
    'auto.offset.reset': 'earliest'
})

consumer.subscribe([KAFKA_TOPIC])

print("Waiting for messages...")
try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        print(f"Received message: {msg.value()}")

except KeyboardInterrupt:
    pass

finally:
    consumer.close()

