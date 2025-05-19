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

# 이미지 저장 경로
#save_dir = "./classified_images"
save_dir = "./static/classified_images"
os.makedirs(save_dir, exist_ok=True)

# DB 연결 설정
db = pymysql.connect(
    host="localhost",
    user="root",
    password="bigdata+",
    database="webscrap",
    charset="utf8"
)
cursor = db.cursor()

# DB 테이블 생성 (최초 1회만 실행)
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

        # 이미지 복원 및 저장
        image = Image.open(BytesIO(image_data)).convert("RGB")
        label = "dog" if "dog" in filename.lower() else "cat" if "cat" in filename.lower() else "unknown"

        # 분류 폴더 분기
        label_dir = os.path.join(save_dir, label)
        os.makedirs(label_dir, exist_ok=True)

        saved_path = os.path.join(label_dir, filename)
        image.save(saved_path)

        print(f"[✅ 저장됨] {filename} → {label}")

        # MariaDB 저장
        sql = "INSERT INTO image_results (filename, label, saved_path) VALUES (%s, %s, %s)"
        cursor.execute(sql, (filename, label, saved_path))
        db.commit()

    except Exception as e:
        print(f"[❌ 에러] {e}")