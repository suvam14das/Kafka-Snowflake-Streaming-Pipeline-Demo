import time
from datetime import datetime, timezone
import requests
import json
from kafka import KafkaProducer

API_KEY = "<API KEY>"
CITY = "Bangalore"
BASIC_URL_TEMPLATE = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"

print(BASIC_URL_TEMPLATE)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092','localhost:9093','localhost:9094'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',   # important for no data loss
    retries=5
)

def fetch_weather():
    
    return requests.get(BASIC_URL_TEMPLATE).json()

while True:
    data = fetch_weather()
    data["main"]["dt"] = str(datetime.now(timezone.utc))
    producer.send("weather-data", value=data)
    producer.flush()
    print("Sent:", data)
    time.sleep(10)