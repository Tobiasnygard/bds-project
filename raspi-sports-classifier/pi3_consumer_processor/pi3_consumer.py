from kafka import KafkaConsumer
import json
import base64
import os
from datetime import datetime
import pymysql
import random

def classify_image():
    return random.choice(['soccer', 'basketball', 'tennis'])

consumer = KafkaConsumer(
    'sports_images',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

conn = pymysql.connect(host='<pi2_ip>', user='piuser', password='password', db='sportsdb')
cursor = conn.cursor()

hadoop_raw_dir = "/home/pi/hadoop_images/raw"
hadoop_classified_dir = "/home/pi/hadoop_images/classified"
os.makedirs(hadoop_raw_dir, exist_ok=True)
os.makedirs(hadoop_classified_dir, exist_ok=True)

for msg in consumer:
    data = msg.value
    img_bytes = base64.b64decode(data['image'])
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
