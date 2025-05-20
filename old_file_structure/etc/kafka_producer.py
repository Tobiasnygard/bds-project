from kafka import KafkaProducer
import json

# Kafka 설정
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 메시지 전송
message = {"text": "Hello Kafka!", "sender": "gptonline.ai"}
producer.send("testTopic", value=message)
producer.flush()

print("[✅ Kafka Producer] 메시지 전송 완료")