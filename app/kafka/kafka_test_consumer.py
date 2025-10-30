# app/kafka_consumer.py
import asyncio
import json
from aiokafka import AIOKafkaConsumer

BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'transactions.enriched'
GROUP_ID = 'test-consumer-group'

async def consume():
    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset='earliest'
    )
    await consumer.start()
    print(f"Kafka consumer started on topic '{TOPIC_NAME}'")
    try:
        async for msg in consumer:
            try:
                trade_data = json.loads(msg.value.decode('utf-8'))
                print(f"Received trade: {trade_data}")
            except Exception as e:
                print(f"⚠️ Error processing message: {e}")
    finally:
        await consumer.stop()
        print("Kafka consumer stopped")

async def start_consumer_background():
    """Runs the Kafka consumer in the background."""
    loop = asyncio.get_event_loop()
    loop.create_task(consume())
