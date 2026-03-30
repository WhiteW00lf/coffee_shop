from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka import SerializingProducer
from kafka import KafkaProducer
import json, time, uuid, random
from datetime import datetime

KAFKA_BROKER = "localhost:29092"
KAFKA_TOPIC = "coffee_orders"
SCHEMA_REGISTRY_URL = "http://localhost:8081"


DRINKS = ["Espresso", "Latte", "Cappuccino", "Americano", "Mocha"]
SYSTEMS = ["ANDROID", "IOS", "POS"]
STORES = ["Store_mumbai", "Store_delhi", "Store_bangalore", "Store_hyderabad"]

with open("coffee_order_schema.json", "r") as f:
    schema_str = json.dumps(json.load(f))

schema_registry_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
avro_serializer = AvroSerializer(schema_registry_client, schema_str)

producer = SerializingProducer(
    {
        "bootstrap.servers": KAFKA_BROKER,
        "key.serializer": lambda k, ctx: k.encode(),
        "value.serializer": avro_serializer,
    }
)


def generate_order():
    order = {
        "order_id": str(uuid.uuid4()),
        "store_id": random.choice(STORES),
        "system": random.choice(SYSTEMS),
        "drink": random.choice(DRINKS),
        "quantity": random.randint(1, 5),
        "price": round(random.uniform(200, 2000), 2),
        "timestamp": datetime.now().isoformat(),
        "customer_id": f"customer_{random.randint(1, 1000)}",
    }

    return order


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


if __name__ == "__main__":
    while True:
        print("Generating order...")
        order = generate_order()
        producer.produce(
            topic=KAFKA_TOPIC,
            key=order["order_id"],
            value=order,
            on_delivery=delivery_report,
        )
        producer.poll(0)
        print(f"Sent order: {order}")
        time.sleep(random.uniform(0.5, 2))
