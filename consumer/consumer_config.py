from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")

KAFKA_USER = os.environ.get("KAFKA_CLIENT_USERS")
KAFKA_PASSWORD = os.environ.get("KAFKA_CLIENT_PASSWORDS")
KAFKA_TOPIC = "emailsss"

KAFKA_BASE_CONFIG = {
    "bootstrap_servers": ["kafka1:9092", "kafka2:9092"],
    "security_protocol": "SASL_PLAINTEXT",
    "sasl_mechanism": "PLAIN",
    "sasl_plain_username": KAFKA_USER,
    "sasl_plain_password": KAFKA_PASSWORD,
    "request_timeout_ms": 30000,
    "api_version": "auto",
    "retry_backoff_ms": 100,
    "metadata_max_age_ms": 300000,
    "connections_max_idle_ms": 540000,
}

KAFKA_CONSUMER_CONFIG = {
    **KAFKA_BASE_CONFIG,
    "group_id": "email_sender_group",
    "enable_auto_commit": False,
    "auto_offset_reset": "earliest",
}
