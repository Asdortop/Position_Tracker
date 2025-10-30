import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer

from app.core.config import settings
from app.api.v1.schemas.trade import Trade
from app.database.connection import AsyncSessionLocal
from app.services.processing_service import processing_service


logger = logging.getLogger(__name__)


class TradeConsumer:
    def __init__(self) -> None:
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None
        self._stopping = asyncio.Event()

    async def start(self) -> None:
        if self._task is not None:
            return

        self._consumer = AIOKafkaConsumer(
            settings.KAFKA_TRADES_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            enable_auto_commit=True,
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        logger.info("TradeConsumer started.")
        self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        assert self._consumer is not None
        try:
            async for msg in self._consumer:
                try:
                    payload: Any = json.loads(msg.value.decode("utf-8"))
                    trade = Trade(**payload)
                except Exception as e:
                    logger.exception("Failed to decode/validate trade payload: %s", e)
                    continue

                try:
                    async with AsyncSessionLocal() as session:
                        await processing_service.process_trade(session, trade)
                    logger.debug("Processed trade message at offset %s", msg.offset)
                except Exception as e:
                    logger.exception("Failed to process trade: %s", e)
        finally:
            await self._shutdown_consumer()

    async def _shutdown_consumer(self) -> None:
        if self._consumer is not None:
            try:
                await self._consumer.stop()
            finally:
                self._consumer = None
                logger.info("TradeConsumer stopped.")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None


trade_consumer = TradeConsumer()


