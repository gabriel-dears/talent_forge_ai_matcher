from kafka import KafkaConsumer
import json
from models import Candidate
from job_fetcher import fetch_jobs
from producer import send_notification_update
from mailer import send_email
from redis_client import redis_client
from matcher import match_candidate_to_jobs

consumer = KafkaConsumer(
    "match.candidate.request",
    bootstrap_servers="kafka:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="ai-matcher-group"
)

EMAIL_SENT_TTL_SECONDS = 60 * 60 * 24 * 14  # 14 days

def consume_candidates():
    for msg in consumer:
        data = msg.value
        candidate = Candidate(**data)
        print(f"📥 Received candidate: {candidate.name}")

        # Redis check: skip if already sent
        email_key = f"email_sent:{candidate.id}"
        if redis_client.exists(email_key):
            print(f"⏭️ Skipping {candidate.name} — already notified recently.")
            continue

        # Fetch jobs and calculate matches
        jobs = fetch_jobs(candidate.id)
        match_results = match_candidate_to_jobs(candidate, jobs)

        if not match_results:
            print(f"⚠️ No strong matches found for {candidate.name}.")
            continue

        # Send top 10 matches via email
        send_email(candidate.email, candidate.name, match_results[:10])

        # Cache candidate ID to avoid resending
        redis_client.setex(email_key, EMAIL_SENT_TTL_SECONDS, "1")
        print(f"✅ Cached {candidate.name} as notified.")

        # Notify Spring app to update notification date
        send_notification_update(candidate.id)
