import asyncio
import logging
from typing import Any

import aiomqtt
from aiomqtt.exceptions import MqttError as AioMqttError

from aiospb.mqtt.encoding.protobuf.core import EncodingError

from . import MqttClient, MqttConfig, MqttError, SpbMessage, Topic, Will
from .encoding import JsonEncoder, ProtobufEncoder

logger = logging.getLogger(__name__)


class PahoMqttClient(MqttClient):
    def __init__(
        self,
        config: MqttConfig,
    ):
        self._config = config

        self._client = None
        self._json_encoder = JsonEncoder()
        self._protobuf_encoder = ProtobufEncoder()
        self._is_host = None

    async def connect(self, component_name: str, will: Will):
        payload = self._encode_message(will.message)
        will_ = aiomqtt.Will(
            will.message.topic.value, payload, qos=will.qos, retain=will.retain
        )

        tls_pars = None
        if self._config.ca_cert:
            tls_pars = aiomqtt.TLSParameters(
                ca_certs=self._config.deploy_certificate_file()
            )

        username, password = self._config.login_info()
        self._client = aiomqtt.Client(
            self._config.hostname,
            self._config.port,
            identifier=component_name,
            username=username,
            password=password,
            will=will_,
            protocol=aiomqtt.ProtocolVersion.V5,
            tls_params=tls_pars,
            clean_start=True,
            keepalive=self._config.keepalive,
        )

        try:
            await asyncio.wait_for(self._client.__aenter__(), timeout=30)
        except Exception as e:
            logger.info(
                f"Detecting exception when trying to connect, diconnecting cleanly"
            )
            await self._disconnect_with_error(e)

    @property
    def keepalive(self) -> float:
        return self._config.keepalive

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    def _encode_message(self, message: SpbMessage) -> bytes:
        if message.topic.value.startswith("spBv1.0/STATE/"):
            return self._json_encoder.encode(message.payload)

        return self._protobuf_encoder.encode(message.payload)

    async def publish(self, message: SpbMessage, qos: int, retain: bool):
        if self._client is None:
            raise RuntimeError("Client not connected to Mqtt Server")

        attempts = 0
        while True:
            try:
                await self._client.publish(
                    message.topic.value,
                    self._encode_message(message),
                    qos=qos,
                    retain=retain,
                    timeout=10.0,
                )
                return
            except asyncio.TimeoutError:
                attempts += 1
                logger.warning(
                    f"Failure by timeout publishing to {message.topic.value}, attempt {attempts}"
                )
                if attempts > 3:
                    await self._disconnect_with_error(
                        TimeoutError(
                            f"After 3 attempts not possible to publish to {message.topic.value}"
                        )
                    )
            except EncodingError as e:
                logger.warning(
                    f"Lost message publishing {message} by error when encoding"
                )
                logger.exception(e)
                return
            except Exception as e:
                logger.error(
                    f"Disconnecting by failure at publishing to {message.topic.value}!!!..."
                )
                await self._disconnect_with_error(e)

    async def subscribe(self, topic: str, qos: int):
        if self._client is None:
            raise RuntimeError("Client not connected to Mqtt Server")

        try:
            await self._client.subscribe(topic, qos=qos)
        except Exception as e:
            await self._disconnect_with_error(e)

    async def deliver_message(self) -> SpbMessage:
        if self._client is None:
            raise RuntimeError("Mqtt client is not connected")

        trys = 0

        while True:
            try:
                message = await anext(self._client.messages)
                break
            except AioMqttError as e:
                if trys < 3:
                    logger.warning(
                        f"Error while delivering messages, tried {trys} times"
                    )
                    logger.exception(e)
                    trys += 1
                    await asyncio.sleep(0.1)
                    logger.info("Increasing trys")
                else:
                    logger.error(
                        f"Disconnecting by MqttError from aiomqtt after {trys} intents"
                    )
                    await self._disconnect_with_error(e)
            except Exception as e:
                logger.error(
                    "Disconnecting by unhandled exception when delivering message"
                )
                await self._disconnect_with_error(e)

        # if type(message.payload) is not bytes:
        #     raise ValueError(f"Message should be bytes {message.payload}")

        if message.topic.value.startswith("spBv1.0/STATE/"):
            return SpbMessage(
                Topic(message.topic.value), self._json_encoder.decode(message.payload)
            )

        message = SpbMessage(
            Topic(message.topic.value), self._protobuf_encoder.decode(message.payload)
        )

        return message

    async def _disconnect_with_error(self, e: Exception):
        try:
            logger.error("Inside disconnection process")
            logger.exception(e)
            await self.disconnect()
        except Exception:
            pass
        finally:
            raise MqttError() from e

    async def disconnect(self):
        if self._client is None:
            return
        await self._client.__aexit__(None, None, None)
        self._client = None
