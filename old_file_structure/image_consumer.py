from kafka import KafkaConsumer
import base64
import json
import os
from io import BytesIO
from PIL import Image
import pymysql

from datetime import datetime
import numpy as np

# Kafka 설정
consumer = KafkaConsumer(
    "tempImage",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='image-analyzer',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Flask 기준 static 이미지 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 consumer.py 위치
STATIC_DIR = os.path.join(BASE_DIR, "static", "classified_images")
os.makedirs(STATIC_DIR, exist_ok=True)

# DB 연결
db = pymysql.connect(
    host="localhost",
    user="root",
    password="bigdata+",
    database="webscrap",
    charset="utf8"
)
cursor = db.cursor()

# 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS image_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    label VARCHAR(100),
    saved_path VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
db.commit()

print("[🧠 Kafka Consumer 작동 시작]")

for msg in consumer:
    try:
        data = msg.value
        filename = data['filename']
        keyword = data['keyword']
        image_data = base64.b64decode(data['image_data'])

        # 이미지 복원
        image = Image.open(BytesIO(image_data)).convert("RGB")
        label = "dog" if "dog" in filename.lower() else "cat" if "cat" in filename.lower() else "unknown"

        # 저장 경로 구성
        label_dir = os.path.join(STATIC_DIR, label)
        os.makedirs(label_dir, exist_ok=True)

        saved_path = os.path.join(label_dir, filename)
        image.save(saved_path)

        print(f"[✅ 저장됨] {filename} → {label} → {saved_path}")

        # DB 저장 (웹에서 접근 가능한 경로로 변환)
        web_path = os.path.relpath(saved_path, BASE_DIR).replace("\\", "/")  # Flask에서 쓸 경로
        cursor.execute(
            "INSERT INTO image_results (filename, label, saved_path) VALUES (%s, %s, %s)",
            (filename, label, web_path)
        )
        db.commit()

    except Exception as e:
        print(f"[❌ 에러] {e}")
