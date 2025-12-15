import requests
import json
import time
from kafka import KafkaProducer

API_URL = "https://fakestoreapi.com/products"

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print(" Producer started...")

while True:
    response = requests.get(API_URL)
    products = response.json()

    for product in products:
        message = {
            "title": product["title"],
            "description": product["description"]
        }

        producer.send("reviews", message)
        print(" Sent:", message["title"])

        time.sleep(2)
