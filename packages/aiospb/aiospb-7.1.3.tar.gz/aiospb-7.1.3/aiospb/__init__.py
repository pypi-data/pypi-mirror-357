import abc
import asyncio
import datetime
import logging
import time
from typing import AsyncGenerator, AsyncIterable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Clock(abc.ABC):
    @abc.abstractmethod
    def now(self) -> int:
        """Return current timestamp in ms"""

    @abc.abstractmethod
    def sleep(self, seconds: float):
        """Syncronous sleep for several seconds"""

    @abc.abstractmethod
    async def asleep(self, seconds: float):
        """Asyncronous sleep for several seconds"""

    @abc.abstractmethod
    def timestamp(self) -> int:
        """Return current timestamp in ms"""

    @abc.abstractmethod
    async def tick(self, interval_ms: int) -> AsyncIterable:
        """Raise every interval"""
        yield

    @abc.abstractmethod
    async def wait(
        self, tasks: list[asyncio.Task], for_milli_seconds: int
    ) -> set[asyncio.Task]:
        """Wait to execute a coroutine for a time"""


class UtcClock(Clock):
    def now(self) -> int:
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)

    def sleep(self, milli_seconds: int):
        time.sleep(milli_seconds / 1000)

    async def asleep(self, mili_seconds: int):
        await asyncio.sleep(mili_seconds / 1000)

    def timestamp(self) -> int:
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)

    async def tick(self, interval_ms: int):
        while True:
            next_ts = ((self.timestamp() // interval_ms) + 1) * interval_ms
            sleep = (next_ts - self.timestamp()) / 1000
            await asyncio.sleep(sleep)
            yield

    async def wait(
        self, tasks: list[asyncio.Task], for_milli_seconds
    ) -> set[asyncio.Task]:
        _, pendings = await asyncio.wait(tasks, timeout=for_milli_seconds / 1000)
        return pendings
