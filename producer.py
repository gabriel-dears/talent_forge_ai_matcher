from kafka import KafkaProducer
import json
import os
import logging

logger = logging.getLogger(__name__)
producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8") if k else None
)


def send_notification_update(candidate_id: str):
    try:
        logger.info(f"📤 Sending notification update for candidate ID: {candidate_id}")

        value = {"candidateId": candidate_id}

        headers = [
            ("__TypeId__", b"com.gabrieldears.talent_forge.adapter.web.dto.NotificationUpdateDto")
        ]

        future = producer.send(
            "match.notification.update",
            value=value,
            headers=headers, )
        result = future.get(timeout=10)
        logger.info(
            f"✅ Kafka message sent to {result.topic} partition {result.partition} at offset {result.offset}"
        )
        producer.flush()
    except Exception as e:
        logger.error(f"❌ Kafka error: {e}")
        logger.exception("❌ Failed to send Kafka notification update")
