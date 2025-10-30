import json
import logging
from aiokafka import AIOKafkaProducer
from app.core.config import settings

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        # We no longer create the producer here. We just initialize it to None.
        self.producer: AIOKafkaProducer | None = None
        self._started = False

    async def start(self):
        if not self._started:
            # We now create the AIOKafkaProducer here, inside an async function.
            # This ensures an event loop is running.
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            await self.producer.start()
            self._started = True
            logger.info("Kafka producer started.")

    async def stop(self):
        if self._started and self.producer:
            await self.producer.stop()
            self._started = False
            logger.info("Kafka producer stopped.")

    async def send(self, topic: str, value: dict, headers: list[tuple[str, bytes]] | None = None):
        if not self._started or not self.producer:
            raise RuntimeError("KafkaProducer has not been started.")
        try:
            await self.producer.send_and_wait(topic, value=value, headers=headers)
        except Exception as e:
            logger.error(f"Failed to send message to topic {topic}: {e}")
            raise

# This line is now safe, because __init__ is a lightweight sync function.
kafka_producer = KafkaProducer()

async def get_kafka_producer() -> KafkaProducer:
    """
    Dependency provider for FastAPI to get the kafka producer.
    """
    return kafka_producer


# Test script to verify the code works
if __name__ == "__main__":
    import asyncio
    
    async def test_producer():
        print("[OK] KafkaProducer module loaded successfully!")
        print(f"[INFO] Producer instance created: {kafka_producer}")
        
        # Try to test the configuration
        try:
            print(f"[INFO] Attempting to access Kafka settings...")
            kafka_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'NOT CONFIGURED')
            print(f"[CONFIG] Bootstrap servers: {kafka_servers}")
        except Exception as e:
            print(f"[ERROR] Configuration error: {e}")
    
    # Run the test
    asyncio.run(test_producer())