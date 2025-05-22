from kafka import KafkaConsumer
import json
import base64
import os
from datetime import datetime
import pymysql
import random

# Simulated AI model classification
def classify_image():
    return random.choice(['soccer', 'basketball', 'tennis'])

# Kafka consumer to receive image messages
consumer = KafkaConsumer(
    'sports_images',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Connect to local MariaDB
conn = pymysql.connect(host='mariadb', user='piuser', password='password', db='sportsdb')
cursor = conn.cursor()

# Create folders for image storage
hadoop_raw_dir = "hadoop_images/raw"
hadoop_classified_dir = "hadoop_images/classified"
os.makedirs(hadoop_raw_dir, exist_ok=True)
os.makedirs(hadoop_classified_dir, exist_ok=True)

# Process incoming messages
for msg in consumer:
    data = msg.value
    if 'image_data' not in data:
        print(f"Skipping message, missing image_data: {data}")
        continue
    img_bytes = base64.b64decode(data['image_data'])
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}.jpg"

    raw_path = os.path.join(hadoop_raw_dir, filename)
    with open(raw_path, 'wb') as f:
        f.write(img_bytes)

    classification = classify_image()

    classified_path = os.path.join(hadoop_classified_dir, f"{classification}_{filename}")
    os.rename(raw_path, classified_path)

    cursor.execute(
        "INSERT INTO images (url, source, classification) VALUES (%s, %s, %s)",
        (data['url'], data['source'], classification)
    )
    conn.commit()
    print(f"Stored image as {classification}")
