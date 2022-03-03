"""MQTT Bridge."""

from __future__ import annotations

import asyncio
import sys
from abc import ABC, abstractmethod
from asyncio import CancelledError, Lock, Queue
from datetime import datetime, timezone
from itertools import groupby
from operator import attrgetter
from random import random
from ssl import SSLContext
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Tuple
from uuid import uuid4

import orjson
import structlog
from asyncio_mqtt import Client, MqttError
from orjson import OPT_SERIALIZE_NUMPY, OPT_SORT_KEYS
from pydantic import Field, ValidationError, validator
from pydantic.main import ErrorWrapper

from kelvin.sdk.app.bridge import (
    AuthenticationType,
    Bridge,
    BridgeConfiguration,
    BridgeError,
    Configuration,
    CredentialsType,
    MetricConfiguration,
    MetricMap,
)
from kelvin.sdk.app.types import TypedModel
from kelvin.sdk.datatype import Message, Model
from kelvin.sdk.datatype.utils import from_rfc3339_timestamp, to_rfc3339_timestamp
from kelvin.sdk.pubsub.types import QOS, Access

if sys.version_info >= (3, 8):
    from typing import Literal
else:  # pragma: no cover
    from typing_extensions import Literal  # type: ignore

logger = structlog.get_logger(__name__)


class MQTTBridgeError(BridgeError):
    """MQTT Bridge error."""


class Timestamp(Model):
    """Timestamp format."""

    __slots__ = ("_decoder", "_encoder")

    _decoder: Callable[[Timestamp, Any], int]
    _encoder: Callable[[Timestamp, int], Any]

    _CONVERTERS: Mapping[str, Tuple[Callable[[Any], int], Callable[[int], Any]]] = {
        "s": (
            lambda x: int(x * 1e9),
            lambda x: x / 1e9,
        ),
        "ms": (
            lambda x: int(x * 1e6),
            lambda x: x / 1e6,
        ),
        "ns": (
            lambda x: int(x),
            lambda x: x,
        ),
        "rfc3339": (
            lambda x: int(from_rfc3339_timestamp(x).timestamp() * 1e9),
            lambda x: to_rfc3339_timestamp(datetime.fromtimestamp(x / 1e9, timezone.utc)),
        ),
    }

    field_name: str
    format: Literal["s", "ms", "ns", "rfc3339"]

    def __init__(self, **kwargs: Any) -> None:
        """Initialise timestamp formatter."""

        super().__init__(**kwargs)

        decoder, encoder = self._CONVERTERS[self.format]

        object.__setattr__(self, "_decoder", decoder)
        object.__setattr__(self, "_encoder", encoder)

    def decode(self, data: Mapping[str, Any]) -> int:
        """Decode timestamp."""

        return self._decoder(data[self.field_name])

    def encode(self, time_of_validity: int) -> Any:
        """Encode timestamp."""

        return self._encoder(time_of_validity)


class PayloadType(Model, ABC):
    """Payload type."""

    @abstractmethod
    def decode(self, payload: bytes) -> Dict[str, Any]:
        """Decode payload."""

    @abstractmethod
    def encode(self, data: Mapping[str, Any]) -> bytes:
        """Encode payload."""

    __iter__: Callable[[], Iterator[str]]  # type: ignore


class JSONPayloadType(PayloadType):
    """JSON payload."""

    def decode(self, payload: bytes) -> Dict[str, Any]:
        """Decode payload."""

        try:
            return orjson.loads(payload)
        except orjson.JSONDecodeError as e:
            raise ValueError(e) from None

    def encode(self, data: Mapping[str, Any]) -> bytes:
        """Encode payload."""

        try:
            return orjson.dumps(data, option=OPT_SERIALIZE_NUMPY | OPT_SORT_KEYS)
        except orjson.JSONEncodeError as e:
            raise ValueError(e) from None


class PayloadMapping(Model):
    """Payload mapping."""

    external: str
    internal: str


class Payload(TypedModel[PayloadType]):
    """Payload base-class."""

    topic: str
    qos: QOS = QOS.AT_MOST_ONCE
    timestamp: Optional[Timestamp] = None
    type: Literal["json"] = "json"
    json_: Optional[JSONPayloadType] = Field(None, alias="json")

    def decode(self, payload: bytes) -> Dict[str, Any]:
        """Decode payload."""

        return self._.decode(payload)

    def encode(self, data: Mapping[str, Any]) -> bytes:
        """Encode payload."""

        return self._.encode(data)


class Connection(Model):
    """Connection configuration."""

    ip: str
    port: int = 1883
    client_id: Optional[str] = None
    keepalive: int = 60


class Authentication(TypedModel[AuthenticationType]):
    """Authentication configuration."""

    type: Literal["credentials"]
    credentials: Optional[CredentialsType] = None


class MQTTBridgeConfiguration(BridgeConfiguration):
    """MQTT bridge configuration."""

    connection: Connection
    authentication: Optional[Authentication]
    payloads: List[Payload]


class MQTTMetricConfiguration(MetricConfiguration):
    """MQTT metric configuration."""

    topic: str
    mapping: Optional[List[PayloadMapping]] = None


class MQTTConfiguration(Configuration[MQTTBridgeConfiguration, MQTTMetricConfiguration]):
    """MQTT configuration."""

    @validator("metrics_map")
    def validate_metric_map_topic(
        cls,
        value: List[MetricMap[MQTTMetricConfiguration]],
        values: Mapping[str, Any],
    ) -> List[MetricMap[MQTTMetricConfiguration]]:
        """Check topic exists in payloads."""

        if "configuration" not in values:
            return value

        payloads: List[Payload] = values["configuration"].payloads
        topics = {x.topic for x in payloads}

        errors: List[ErrorWrapper] = []

        for i, metric_map in enumerate(value):
            topic = metric_map.configuration.topic
            if topic not in topics:
                errors += [ErrorWrapper(ValueError(f"Topic {topic!r} not in payloads"), loc=(i,))]

        if errors:
            raise ValidationError(errors, model=cls) from None  # type: ignore

        return value


class MQTTBridge(Bridge[MQTTConfiguration]):
    """MQTT Bridge."""

    _client: Optional[Client] = None
    _lock: Lock

    def __init__(self, **kwargs: Any) -> None:
        """Initialise MQTT bridge."""

        super().__init__(**kwargs)

        self._lock = Lock()

    @property
    def client(self) -> Client:
        """MQTT client."""

        client = self._client

        if client is None:
            raise MQTTBridgeError("No client")

        return client

    async def init(self) -> None:
        """Initialise bridge resources prior to running."""

        connection = self.config.configuration.connection
        ip = connection.ip
        if "://" in ip:
            transport, _, hostname = ip.partition("://")
            if transport == "tcp":
                tls_context = None
            elif transport == "ssl":
                tls_context = SSLContext()
            else:
                raise ValueError(f"Unsupported transport {transport!r}") from None
        else:
            hostname = ip
            tls_context = None

        async with self._lock:
            client = self._client = Client(
                hostname=hostname,
                port=connection.port,
                client_id=connection.client_id or f"mqtt_bridge-{uuid4()}",
                keepalive=connection.keepalive,
                tls_context=tls_context,
            )

        min_interval, max_interval = 1.0, 32.0
        interval = 0.0

        while True:
            try:
                await client.connect()
            except MqttError as e:
                logger.error(f"Unable to initialise bridge: {e}")
                logger.info(f"Retrying in {interval} seconds")
                await asyncio.sleep(interval + random())  # nosec
                interval = min(max(2.0 * interval, min_interval), max_interval)
            else:
                break

        topics = [(x.topic, x.qos) for x in self.config.configuration.payloads]

        if topics:
            await client.subscribe(topics)

    async def stop(self) -> None:
        """Stop bridge."""

        async with self._lock:
            client = self._client

            if client is None:
                return

            try:
                await client.disconnect(timeout=1)
            except Exception:  # nosec
                pass

            self._client = None

    async def reader(self, messages: Queue[Message]) -> None:
        """Process inbound messages."""

        key = attrgetter("configuration.topic")
        payloads = {x.topic: x for x in self.config.configuration.payloads}
        topics = {
            topic: [(x, payloads[x.configuration.topic]) for x in group]
            for topic, group in groupby(sorted(self.config.metrics_map, key=key), key=key)
        }

        try:
            async with self.client.unfiltered_messages() as stream:
                async for x in stream:
                    try:
                        targets = topics.get(x.topic)
                        if targets is None:
                            logger.warning(f"Skipping unexpected topic {x.topic!r}")
                            continue

                        for metric, payload in targets:
                            if metric.access not in {Access.RW, Access.RO}:
                                logger.warning(f"Skipping non-readable message {x.topic!r}")
                                continue

                            data = payload.decode(x.payload)

                            result: Dict[str, Any] = {}

                            mapping = metric.configuration.mapping
                            if mapping is not None:
                                result.update((x.internal, data[x.external]) for x in mapping)
                            else:
                                result.update(data)

                            result["_"] = {
                                "name": metric.name,
                                "type": metric.data_type,
                                "asset_name": metric.asset_name,
                            }
                            if payload.timestamp is not None:
                                result["_"]["time_of_validity"] = payload.timestamp.decode(data)

                            message = Message.parse_obj(result)

                            await messages.put(message)

                    except Exception:
                        logger.exception("Failed", message=x)

        except CancelledError:
            logger.info("Stopping reader")
        except MqttError as e:
            raise MQTTBridgeError(f"Unable to receive messages: {e}") from None

    async def writer(self, messages: Queue[Message]) -> None:
        """Process outbound messages."""

        def key(x: MetricMap) -> Tuple[str, str, str]:
            return (str(x.name), str(x.data_type), str(x.asset_name))

        payloads = {x.topic: x for x in self.config.configuration.payloads}
        metrics = {
            metric_id: [(x, payloads[x.configuration.topic]) for x in group]
            for metric_id, group in groupby(sorted(self.config.metrics_map, key=key), key=key)
        }

        while True:
            try:
                message = await messages.get()
                header = message._
                metric_id = (header.name, header.type, header.asset_name or "")

                targets = metrics.get(metric_id)
                if targets is None:
                    logger.warning(f"Skipping unexpected message {metric_id!r}")
                    continue

                for metric, payload in targets:
                    if metric.access not in {Access.RW, Access.WO}:
                        logger.warning(f"Skipping non-writable message {metric_id!r}")
                        continue

                    result: Dict[str, Any] = {}

                    mapping = metric.configuration.mapping
                    if mapping is not None:
                        result.update((x.external, message[x.internal]) for x in mapping)
                    else:
                        result.update(message)

                    if payload.timestamp is not None:
                        result[payload.timestamp.field_name] = payload.timestamp.encode(
                            header.time_of_validity
                        )

                    asyncio.create_task(self.client.publish(payload.topic, payload.encode(result)))

            except CancelledError:
                logger.info("Stopping writer")
                break
            except Exception:
                logger.exception("Failed", message=message)
