import json
import requests
from kafka import KafkaConsumer
from textblob import TextBlob

# Kafka Consumer
consumer = KafkaConsumer(
    "reviews",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="latest"
)

API_URL = "http://127.0.0.1:8000/api/reviews/"  

print(" Consumer started and sending data to API...")

for message in consumer:
    title = message.value.get("title", "")
    text = message.value.get("description", "")
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0:
        sentiment = "POSITIVE"
    elif polarity < 0:
        sentiment = "NEGATIVE"
    else:
        sentiment = "NEUTRAL"

    payload = {
        "title": title,
        "description": text,
        "sentiment": sentiment,
        "polarity": polarity
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 201:
            print(f" Sent to API: {title} => {sentiment}")
        else:
            print(f" Failed to send {title}: {response.status_code} {response.text}")
    except Exception as e:
        print(f" Error sending {title}: {e}")
