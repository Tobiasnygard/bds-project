from kafka import KafkaConsumer
import base64
import json
import os
import pymysql
from PIL import Image
from io import BytesIO
import numpy as np
import tflite_runtime.interpreter as tflite
from tensorflow.keras.applications.mobilenet_v2 import decode_predictions

# Kafka 설정
consumer = KafkaConsumer(
    "tempImage",
    bootstrap_servers='host2-ip:9092',  # Kafka 서버 주소
    auto_offset_reset='earliest',
    group_id='image-classifier',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# 이미지 저장 경로
save_dir = "./static/classified_images"
os.makedirs(save_dir, exist_ok=True)

# DB 연결
db = pymysql.connect(
    host="localhost", user="root", password="bigdata+", database="webscrap", charset="utf8"
)
cursor = db.cursor()

# DB 테이블 생성
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

# TFLite 모델 로드
interpreter = tflite.Interpreter(model_path="mobilenet_v2.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def classify_image(image):
    img = image.resize((224, 224)).convert('RGB')
    img_np = np.expand_dims(np.array(img, dtype=np.float32) / 255.0, axis=0)
    interpreter.set_tensor(input_details[0]['index'], img_np)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    prediction_id = np.argmax(output_data)

    # 라벨링 룰 예시 (간단하게 처리)
    label = "dog" if prediction_id in range(151, 268) else "cat" if prediction_id in range(281, 287) else "unknown"
    return label

print("[🔥 Kafka Consumer with TFLite 분류기 시작]")

for msg in consumer:
    try:
        data = msg.value
        filename = data['filename']
        image_data = base64.b64decode(data['image_data'])

        image = Image.open(BytesIO(image_data))

        # AI 모델 분류
        label = classify_image(image)

        label_dir = os.path.join(save_dir, label)
        os.makedirs(label_dir, exist_ok=True)

        saved_path = os.path.join(label_dir, filename)
        image.save(saved_path)

        print(f"[✅ 저장됨] {filename} → {label}")

        cursor.execute(
            "INSERT INTO image_results (filename, label, saved_path) VALUES (%s, %s, %s)",
            (filename, label, saved_path)
        )
        db.commit()

    except Exception as e:
        print(f"[❌ 에러] {e}")
