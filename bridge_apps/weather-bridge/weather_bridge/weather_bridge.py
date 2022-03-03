"""Weather Station Bridge."""

from __future__ import annotations

import asyncio
from asyncio import Queue
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

import structlog
from aiohttp import ClientSession

from kelvin.sdk.app.bridge import Bridge, BridgeConfiguration, Configuration, MetricConfiguration
from kelvin.sdk.datatype import Message, Model

logger = structlog.get_logger(__name__)


class Connection(Model):
    """Connection configuration."""

    base_url: str
    api_key: str


class WeatherBridgeConfiguration(BridgeConfiguration):
    """Weather bridge configuration."""

    connection: Connection
    period: float = 1.0


class WeatherMetricConfiguration(MetricConfiguration):
    """Weather metric configuration."""

    city_name: str
    state_code: Optional[str] = None
    country_code: Optional[str] = None
    units: Literal["metric", "imperial"] = "metric"

    @property
    def q(self) -> str:
        """Query."""

        query: List[str] = [self.city_name]

        if self.state_code is not None:
            query += [self.state_code]
        if self.country_code is not None:
            query += [self.country_code]

        return ",".join(query)


class WeatherConfiguration(Configuration[WeatherBridgeConfiguration, WeatherMetricConfiguration]):
    """Weather configuration."""


class WeatherBridge(Bridge[WeatherConfiguration]):
    """Weather bridge."""

    async def _fetch(
        self, metric: WeatherMetricConfiguration, session: ClientSession
    ) -> Optional[Dict[str, Any]]:

        configuration = self.config.configuration
        connection = configuration.connection

        params = {
            "q": metric.configuration.q,
            "units": metric.configuration.units,
            "appid": connection.api_key,
        }
        try:
            async with session.get(f"{connection.base_url}/weather", params=params) as response:
                if not response.ok:
                    logger.error("Request error", metric=metric)
                    return None
                data = await response.json()
        except Exception:
            logger.exception("Request failed")
            return None

        try:
            value = data["main"]["temp"]
            timestamp = datetime.utcfromtimestamp(data["dt"]).isoformat() + "Z"
        except Exception:
            logger.exception("Unable to parse response")
            return None

        return {
            "name": metric.name,
            "data_type": metric.data_type,
            "asset_name": metric.asset_name,
            "timestamp": timestamp,
            "payload": {
                "value": value,
            },
        }

    async def reader(self, messages: Queue[Message]) -> None:
        """Reader loop."""

        configuration = self.config.configuration
        period = configuration.period

        metrics_map = self.config.metrics_map

        then = 0.0

        loop = asyncio.get_event_loop()

        async with ClientSession() as session:
            while True:
                now = loop.time()
                delay = max(period - (now - then), 0.0)
                await asyncio.sleep(delay)

                then = loop.time()
                tasks = [self._fetch(metric, session) for metric in metrics_map]

                for result in await asyncio.gather(*tasks):
                    if result is None:
                        continue
                    try:
                        message = Message.parse_obj(result)
                    except Exception:
                        logger.exception("Unable to create message")
                        continue

                    await messages.put(message)
