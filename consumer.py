import asyncio
import json

from aiokafka import AIOKafkaConsumer
from kafka import KafkaConsumer

from job_fetcher import fetch_jobs
from mailer import send_email
from matcher import match_candidate_to_jobs
from models import Candidate
from producer import send_notification_update
from redis_client import redis_client

consumer = AIOKafkaConsumer(
        "match.candidate.request",
        bootstrap_servers="kafka:9092",
        group_id="ai-matcher-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

EMAIL_SENT_TTL_SECONDS = 60 * 60 * 24 * 14  # 14 days


async def consume_candidates():
    await consumer.start()
    print("✅ Consumer started and ready to receive messages")
    try:
        async for msg in consumer:
            data = msg.value
            candidate = Candidate(**data)
            print(f"📥 Received candidate: {candidate.name}")

            email_key = f"email_sent:{candidate.id}"

            # Async wrapper for sync Redis exists
            if await asyncio.to_thread(redis_client.exists, email_key):
                print(f"⏭️ Skipping {candidate.name} — already notified recently.")
                continue

            jobs = await fetch_jobs()
            match_results = match_candidate_to_jobs(candidate, jobs)

            if not match_results:
                print(f"⚠️ No strong matches found for {candidate.name}.")
                continue

            send_email(candidate.email, candidate.name, match_results)

            # Async wrapper for sync Redis setex
            await asyncio.to_thread(redis_client.setex, email_key, EMAIL_SENT_TTL_SECONDS, "1")
            print(f"✅ Cached {candidate.name} as notified.")

            print(f"📡 Triggering Kafka notification update for {candidate.id}")
            # Run the blocking Kafka producer in thread to avoid blocking event loop
            await asyncio.to_thread(send_notification_update, candidate.id)

    finally:
        await consumer.stop()
