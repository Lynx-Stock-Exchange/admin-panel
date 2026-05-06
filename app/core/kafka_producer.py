import json
import logging

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from app.core.config import settings

logger = logging.getLogger(__name__)

_producer: KafkaProducer | None = None


def _get_producer() -> KafkaProducer | None:
    global _producer
    if _producer is not None:
        return _producer
    try:
        _producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    except NoBrokersAvailable:
        logger.warning("Kafka unavailable — commands will not be published.")
    return _producer


def publish(topic: str, payload: dict) -> None:
    producer = _get_producer()
    if producer is None:
        return
    try:
        producer.send(topic, payload)
        producer.flush()
    except Exception as e:
        logger.warning("Failed to publish to Kafka topic '%s': %s", topic, e)