from kafka import KafkaConsumer
import json
import base64
import time
from datetime import datetime
import sys

import pymysql
from PIL import Image
from io import BytesIO
import numpy as np
from tflite_runtime.interpreter import Interpreter

# ─── 1. LOAD MODEL & LABELS ────────────────────────────────────────────────────

interpreter = Interpreter(model_path="mobilenet_v1_1.0_224.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

with open("labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

sports_keywords = {"basketball", "soccer", "tennis", "baseball", "football", "swimming"}
sports_label_indices = [
    i for i, label in enumerate(labels)
    if any(keyword in label.lower() for keyword in sports_keywords)
]

# ─── 2. KAFKA CONSUMER SETUP ────────────────────────────────────────────────────
try:
    consumer = KafkaConsumer(
        'sports_images',
        bootstrap_servers=['kafka:9092'],
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    print("[ℹ️] Connected to Kafka broker.")
except KafkaError as e:
    print(f"[❌] Kafka error when trying to connect: {e}")
    print(f"Shutting down consumer, please restart it maunally")
    sys.exit(1)

# ─── 3. DB CONNECTION HELPERS ──────────────────────────────────────────────────

def make_db_connection():
    return pymysql.connect(
        host='mariadb',
        user='piuser',
        password='password',
        db='sportsdb'
    )

try:
    conn = make_db_connection()
    print("[ℹ️] MariaDB connection established.")
except pymysql.MySQLError as e:
    print(f"[❌] Could not connect to MariaDB at startup: {e}")
    print(f"Shutting down consumer, please restart it maunally")

# ─── 4. IMAGE CLASSIFICATION FUNCTION ─────────────────────────────────────────

def classify_image(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image = image.resize((224, 224))
    input_data = np.expand_dims(np.array(image, dtype=np.float32) / 255.0, axis=0)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])[0]
    top_index = max(sports_label_indices, key=lambda i: output_data[i])
    return labels[top_index], output_data[top_index]

# ─── 5. MAIN CONSUMER LOOP ────────────────────────────────────────────────────

def consumer_loop():
    global conn

    for msg in consumer:
        data = msg.value
        print("[📩] Received message")

        # A: Reconnect if needed
        if conn is None or not conn.open:
            try:
                conn = make_db_connection()
                print("[ℹ️] Reconnected to MariaDB.")
            except pymysql.MySQLError as e:
                print(f"[⚠️] Failed to reconnect to MariaDB: {e}. Sleeping 5s.")
                time.sleep(5)
                continue

        # B: Ensure 'image_data'
        if 'image_data' not in data:
            print("[⚠️] Skipping message: 'image_data' missing.")
            continue

        # C: Decode Base64 → raw bytes
        try:
            img_bytes = base64.b64decode(data['image_data'])
        except Exception as e:
            print(f"[❌] Base64 decode error: {e}")
            continue

        if len(img_bytes) < 1024:
            print(f"[⚠️] Skipping image: too small ({len(img_bytes)} bytes).")
            continue

        # D: Classify
        try:
            label, confidence = classify_image(img_bytes)
            print(f"[🧠] Classification: {label} ({confidence:.2f})")
        except Exception as e:
            print(f"[❌] Classification error: {e}")
            continue

        # If below threshold, tag as 'skipped' instead of skipping outright
        if confidence >= 0.01:
            classification = label
        else:
            classification = 'skipped'
            print(f"[⚠️] Low confidence ({confidence:.2f}), tagging as 'skipped'")

        # E: Insert into MariaDB
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO images
                      (url, source, classification, image_blob)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        data.get('url', 'N/A'),
                        data.get('source', 'unknown'),
                        classification,
                        img_bytes
                    )
                )
                conn.commit()

                new_id = cursor.lastrowid
                print(f"[✅] Inserted row id={new_id} → {classification}")
        except pymysql.MySQLError as e:
            conn.rollback()
            print(f"[❌] DB insert error: {e}")
            # If lost connection
            if e.args[0] in (2006, 2013):
                print("[⚠️] Lost DB connection; will reconnect next iteration.")
                try:
                    conn.close()
                except Exception:
                    pass
                conn = None

if __name__ == '__main__':
    try:
        consumer_loop()
    except KeyboardInterrupt:
        print("\n[ℹ️] Interrupted by user, shutting down...")
    finally:
        if conn is not None and conn.open:
            conn.close()
            print("[ℹ️] MariaDB connection closed.")
        consumer.close()
        print("[ℹ️] Kafka consumer closed.")
