import requests
import json

SCHEMA_REGISTRY = "http://localhost:8081"

schema = {
    "type": "record",
    "name": "CoffeeOrder",
    "namespace": "com.coffeeshop",
    "fields": [
        {"name": "order_id",    "type": "string"},
        {"name": "store_id",    "type": "string"},
        {"name": "system",      "type": "string"},
        {"name": "drink",       "type": "string"},
        {"name": "quantity",    "type": "int"},
        {"name": "price",       "type": "double"},
        {"name": "timestamp",   "type": "string"},
        {"name": "customer_id", "type": "string"}
    ]
}

payload = {"schema": json.dumps(schema)}

response = requests.post(
    f"{SCHEMA_REGISTRY}/subjects/coffee_orders-value/versions",
    headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
    json=payload
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
