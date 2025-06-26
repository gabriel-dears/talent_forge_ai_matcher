from kafka import KafkaProducer
import json
import os

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_notification_update(candidate_id: str):
    producer.send("match.notification.update", candidate_id.encode("utf-8"))
    producer.flush()
