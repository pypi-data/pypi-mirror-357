"""A MQTT Server can not warrant that host application would recieve the node messages
in the same order is sent. If not, standards rules a rebirth"""
import logging

from aiospb import Clock
from aiospb.mqtt import NodePayload, SpbMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NodeMessageSorter:
    def __init__(
        self,
        node_name: str,
        clock: Clock,
        reorder_time: float = 2.0,  # in s
    ):
        self._node_name = node_name
        self._clock = clock
        self._reorder_time = reorder_time

        self._seq = -1
        self._bd_seq = 0
        self._messages = {}
        self._timeout_ts = 0

    def register_message(self, message: SpbMessage):
        if type(message.payload) is not NodePayload:
            return

        if message.is_a("NCMD"):
            return

        if message.is_a("NDATA") and self._seq == -1:
            logger.warning(f"Lost NDATA at {self._node_name} by lack of birth")

        if message.is_a("NDEATH"):
            if message.payload.metrics[0].value == self._bd_seq:
                self._messages[None] = message
            else:
                logger.warning(
                    f"Recieved NDEATH with out of bd_seq at {self._node_name}!!"
                )
            return

        if message.is_a("NBIRTH"):
            bd_seq = None
            for metric in message.payload.metrics:
                if metric.name == "bdSeq":
                    bd_seq = metric.value
            if bd_seq is None:
                raise ValueError(
                    f"Birth from {self._node_name} has not bdSeq metric at {self._node_name}!!"
                )
            self._bd_seq = bd_seq

            self._clear_message_buffer("rebirth")
            self._seq = message.payload.seq

        self._messages[message.payload.seq] = message

    def nexts(self) -> list[SpbMessage]:
        output = []
        while self._messages:
            if self._seq in self._messages:
                output.append(self._messages.pop(self._seq))
                self._seq = 0 if self._seq == 255 else self._seq + 1
            elif None in self._messages:  # Recieved death certificate
                message = self._messages.pop(None)
                output.append(message)
                self._clear_message_buffer("death")
                self._seq = -1  # Until new session no next data will be sent
            else:
                if self._clock.timestamp() > self._timeout_ts:
                    logger.warning(f"Sequence out of time at {self._node_name}")
                    self._clear_message_buffer("timeout")
                    raise TimeoutError()  # Client would send a rebirth request
                break
            self._timeout_ts = self._clock.timestamp() + self._reorder_time * 1000
        return output

    def _clear_message_buffer(self, when):
        if len(self._messages) == 0:
            return

        logger.warning(f"Lost {len(self._messages)} at {self._node_name} when {when}")
        self._messages.clear()
