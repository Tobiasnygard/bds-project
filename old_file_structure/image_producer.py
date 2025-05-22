import os
import base64
import json
from kafka import KafkaProducer

# Kafka 설정
producer = KafkaProducer(
    #bootstrap_servers='localhost:9092',
    bootstrap_servers='192.168.219.100:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 이미지 폴더 경로
image_dir = "./images"
keyword = "dog"  # 또는 cat

for filename in os.listdir(image_dir):
    if not filename.lower().endswith(".jpg"):
        continue

    filepath = os.path.join(image_dir, filename)
    with open(filepath, "rb") as f:
        encoded_img = base64.b64encode(f.read()).decode('utf-8')

    message = {
        "keyword": keyword,
        "filename": filename,
        "image_data": encoded_img
    }

    producer.send("tempImage", value=message)
    print(f"[Kafka 전송] {filename}")
    producer.flush()
