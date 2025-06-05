from kafka import KafkaConsumer
import json
import base64
import os
from datetime import datetime
import pymysql
from PIL import Image
from io import BytesIO
import numpy as np
from tflite_runtime.interpreter import Interpreter

# Load TFLite model
interpreter = Interpreter(model_path="mobilenet_v1_1.0_224.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load labels
with open("labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Only consider these sports categories
sports_keywords = {"basketball", "soccer", "tennis", "baseball", "football", "swimming"}
sports_label_indices = [
    i for i, label in enumerate(labels)
    if any(keyword in label.lower() for keyword in sports_keywords)
]

# Kafka Consumer — Docker-safe host
consumer = KafkaConsumer(
    'sports_images',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# MariaDB connection — Docker-safe host
conn = pymysql.connect(
    host='mariadb',
    user='piuser',
    password='password',
    db='sportsdb',
    port=3306
)
cursor = conn.cursor()

# Image folders
raw_dir = "images/raw"
classified_dir = "images/classified"
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(classified_dir, exist_ok=True)

# Classify image using MobileNet
def classify_image(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image = image.resize((224, 224))
    input_data = np.expand_dims(np.array(image, dtype=np.float32) / 255.0, axis=0)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])[0]
    top_index = max(sports_label_indices, key=lambda i: output_data[i])
    return labels[top_index], output_data[top_index]

# Start consuming messages
for msg in consumer:
    data = msg.value
    print("[📩] Received message")

    if 'image_data' not in data:
        print("[⚠️] Skipping message: 'image_data' missing.")
        continue

    img_bytes = base64.b64decode(data['image_data'])

    if len(img_bytes) < 1024:
        print(f"[⚠️] Skipping image: too small ({len(img_bytes)} bytes)")
        continue

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw_filename = f"{timestamp}.jpg"
    raw_path = os.path.join(raw_dir, raw_filename)

    try:
        classification, confidence = classify_image(img_bytes)
        print(f"[🧠] Classification: {classification} ({confidence:.2f})")
    except Exception as e:
        print(f"[❌] Classification error: {e}")
        continue

    if confidence < 0.3:
        print(f"[⚠️] Low confidence ({confidence:.2f}), skipping image.")
        continue

    try:
        with open(raw_path, 'wb') as f:
            f.write(img_bytes)
        print(f"[💾] Saved image: {raw_filename}")
    except Exception as e:
        print(f"[❌] Failed to save raw image: {e}")
        continue

    classified_filename = f"{classification}_{timestamp}.jpg"
    classified_path = os.path.join(classified_dir, classified_filename)

    try:
        os.rename(raw_path, classified_path)
        print(f"[📦] Moved image to: {classified_path}")
    except Exception as e:
        print(f"[❌] Failed to move image: {e}")
        continue

    try:
        cursor.execute(
            "INSERT INTO images (url, source, classification, filename) VALUES (%s, %s, %s, %s)",
            (
                data.get('url', 'N/A'),
                data.get('source', 'unknown'),
                classification,
                classified_filename
            )
        )
        conn.commit()
        print(f"[✅] Inserted into DB: {classified_filename} → {classification}")
    except Exception as e:
        print(f"[❌] DB insert error: {e}")
