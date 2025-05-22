from kafka import KafkaConsumer
import json

# Kafka 설정
consumer = KafkaConsumer(
    "testTopic",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',       # 가장 처음부터 읽기
    group_id="test-consumer-group",
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("[🔄 Kafka Consumer] 메시지 대기 중...")

for message in consumer:
    print(f"[📥 수신된 메시지] {message.value}")
