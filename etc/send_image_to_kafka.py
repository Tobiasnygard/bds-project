import base64
import json
from kafka import KafkaProducer

# Kafka 설정
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_image_to_kafka(keyword, filepath):
    with open(filepath, "rb") as f:
        encoded_img = base64.b64encode(f.read()).decode('utf-8')

    payload = {
        "keyword": keyword,
        "filename": os.path.basename(filepath),
        "image_data": encoded_img
    }

    producer.send("tempImage", value=payload)
    producer.flush()
    print(f"[Kafka] 전송됨: {filepath}")
