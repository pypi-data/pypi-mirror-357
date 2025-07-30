import abc
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Self

from .. import Clock, UtcClock
from ..data import DataType, Metric, PropertySet, PropertyValue, Quality, ValueType

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass(frozen=True)
class MetricCore:
    """Metric data, stable for a session"""

    name: str
    data_type: DataType
    properties: PropertySet = field(default_factory=PropertySet)
    alias: int = 0
    is_transient: bool = False

    def create_metric(
        self, value: ValueType, timestamp: int, quality: Quality | None = None
    ) -> Metric:
        """Create metric from the metric core"""
        props = self.properties
        if quality is not None:
            props_data = self.properties.as_dict()
            props_data["Quality"] = {"value": quality.value, "dataType": "Int32"}
            props = PropertySet.from_dict(props_data)

        return Metric(
            timestamp,
            value,
            self.data_type,
            self.alias,
            self.name,
            props,
            self.is_transient,
        )

    # @classmethod
    # def from_dict(cls, dump: dict[str, Any]) -> Self:
    #     datatype = (
    #         DataType(dump["dataType"])
    #         if type(dump["dataType"]) is int
    #         else DataType[dump["dataType"]]
    #     )
    #     properties = (
    #         PropertySet.from_dict(dump["properties"])
    #         if "properties" in dump
    #         else PropertySet()
    #     )
    #     return cls(
    #         dump["name"],
    #         datatype,
    #         properties,
    #         dump.get("alias", 0),
    #         dump.get("is_transient", False),
    #     )


class MetricNotFound(Exception):
    """Metric not found when reading or writing by the MetricNet"""


class MetricsNet(abc.ABC):
    # @abc.abstractmethod
    # async def smap(self) -> dict[str, int]:
    #     """List all name of metrics available and their aliases, 0 it does not have"""

    @abc.abstractmethod
    async def get_metric_cores(self, filter: str = "") -> list[MetricCore]:
        """List available metrics in the net with all its properties"""

    @abc.abstractmethod
    async def read_value(self, metric_name: str = "", alias: int = 0) -> ValueType:
        """Read a value to a metric"""

    @abc.abstractmethod
    async def write_value(
        self, value: ValueType, metric_name: str = "", alias: int = 0
    ):
        """Write a value to a metric"""


@dataclass
class Sample:
    timestamp: int
    value: ValueType
    quality: Quality


@dataclass
class Reading:
    data_type: DataType
    quality: Quality
    value: ValueType = None
    alias: int = 0
    name: str = ""

    def compare(self, sample: Sample) -> Metric | None:
        if sample.quality == self.quality and sample.value == self.value:
            return

        props = (
            PropertySet()
            if self.quality == sample.quality
            else PropertySet(
                ("Quality",), (PropertyValue(sample.quality.value, DataType.Int32),)
            )
        )

        name = "" if self.alias else self.name
        return Metric(
            sample.timestamp, sample.value, self.data_type, self.alias, name, props
        )

    def update(self, change: Metric) -> Self:
        """Generate a new reading from the change information of metric"""
        quality = (
            Quality(change.properties["Quality"].value)
            if "Quality" in change.properties
            else self.quality
        )
        return self.__class__(
            self.data_type, quality, change.value, self.alias, self.name
        )


class ScanSchedule:
    def __init__(
        self, net: MetricsNet, scan_rate: int, queue: asyncio.Queue, clock: Clock
    ):
        self._scan_rate = scan_rate
        self._net = net
        self._clock = clock
        self._task = None
        self._readings = []
        self._continue = True
        self._queue = queue

    @property
    def scan_rate(self) -> int:
        return self._scan_rate

    @scan_rate.setter
    def scan_rate(self, value: int):
        if self._task:
            self._task.cancel()

        self._scan_rate = value

    def add_reading(self, value: Reading):
        self._readings.append(value)

    async def _read(self, reading: Reading) -> Sample:
        if not reading.alias and not reading.name:
            raise ValueError("Metric Name and alias can not be null at the same time")
        try:
            value = await self._net.read_value(reading.name)
            return Sample(self._clock.timestamp(), value, Quality.GOOD)
        except asyncio.CancelledError:
            return Sample(self._clock.timestamp(), None, Quality.STALE)
        except Exception as e:
            logger.error(
                f"Exception when scanning metric {reading.name}:{reading.alias}: {e.__class__.__name__}({e})"
            )
            return Sample(self._clock.timestamp(), None, Quality.BAD)

    async def _read_metrics(self):
        reads = [asyncio.create_task(self._read(reading)) for reading in self._readings]

        try:
            pending = await self._clock.wait(reads, int(self._scan_rate * 0.8))
        except asyncio.CancelledError as e:
            for read in reads:
                if not read.done():
                    read.cancel()
            raise e

        if pending:
            logger.warning(f"{len(pending)} metrics are in STALE quality when scanning")
            for reading, read in zip(self._readings, reads):
                if not read.done():
                    logger.warning(f"Metric {reading.name}:{reading.alias} is STALE")

        for read in pending:
            read.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

        changes = []
        for index, read in enumerate(reads):
            change = self._readings[index].compare(read.result())
            if change:
                changes.append(change)
                self._readings[index] = self._readings[index].update(change)

        if changes:
            self._queue.put_nowait(sorted(changes, key=lambda change: change.timestamp))

    def start(self):
        if self._task:
            self._task.cancel()

        if not self._readings:
            return

        if self.scan_rate > 0:
            self._task = asyncio.create_task(self._scan())

    async def _scan(self):
        if self._scan_rate == 0:  # There is no scanning process if scan_rate=0!!!
            return

        async for _ in self._clock.tick(self._scan_rate):
            await self._read_metrics()

    def update_reading(self, sample: Sample, alias: int, name: str) -> bool:
        for index, reading in enumerate(self._readings):
            if (alias and reading.alias == alias) or name == reading.name:
                metric = reading.compare(sample)
                if metric:
                    self._readings[index] = reading.update(metric)
                return True
        return False

    async def stop(self):
        """Stop schedule tasks"""

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


class Scanner:
    def __init__(
        self,
        metrics_net: MetricsNet,
        clock: Clock | None = None,
    ):
        self._net = metrics_net
        self._clock = clock or UtcClock()
        self._scan_rate = 60000

        self._queue = asyncio.Queue()
        self._schedules = []

    @property
    def scan_rate(self) -> int:
        return self._scan_rate

    async def deliver_changes(self, timeout: float = 0.0) -> list[Metric]:
        """Return last changes"""
        if timeout:
            try:
                return await asyncio.wait_for(self._queue.get(), timeout=timeout)
            except TimeoutError:
                return []
        return await self._queue.get()

    async def _read(self, metric_name: str) -> Sample:
        try:
            value = await self._net.read_value(metric_name)
            return Sample(self._clock.timestamp(), value, Quality.GOOD)
        except asyncio.CancelledError:
            logger.warning(f"Metric {metric_name} is STALE")
            return Sample(self._clock.timestamp(), None, Quality.STALE)
        except Exception as e:
            logger.warning(f"Error reading metric {metric_name} by {e}")
            return Sample(self._clock.timestamp(), None, Quality.BAD)

    async def _read_births(self) -> list[Metric]:
        cores = await self._net.get_metric_cores()
        for core in cores:
            if not core.name and not core.alias:
                raise ValueError("There is a metric without alias and without name")

        reads = [asyncio.create_task(self._read(core.name)) for core in cores]
        pending = await self._clock.wait(reads, self.scan_rate)
        if pending:
            logger.warning(f"{len(pending)} metrics are in STALE quality when birth")

        for reading in pending:
            reading.cancel()
        await asyncio.gather(*pending, return_exceptions=True)

        births = []
        for core, read in zip(cores, reads):
            sample = read.result()
            births.append(
                core.create_metric(sample.value, sample.timestamp, sample.quality)
            )

        return births

    async def start(self) -> list[Metric]:
        ts = self._clock.timestamp()
        try:
            value = await self._net.read_value("Node Control/Scan Rate")
            assert type(value) is int
            self._scan_rate = value
        except Exception:
            pass

        births = [
            Metric(ts, False, DataType.Boolean, name="Node Control/Reboot"),
            Metric(ts, False, DataType.Boolean, name="Node Control/Rebirth"),
            Metric(ts, self._scan_rate, DataType.Int64, name="Node Control/Scan Rate"),
        ]

        read = await self._read_births()
        for r in read:
            if r.name == "Node Control/Scan Rate" and type(r.value) is int:
                r.properties = PropertySet()
                self._scan_rate = r.value
                logger.info(f"Found scan rate from metrics, setting {self._scan_rate}")
                births[2] = r

        schedules = {}
        while read:
            birth = read.pop()
            if birth.name == "Node Control/Scan Rate":
                continue

            births.append(birth)
            if "Properties/" in birth.name:  # Properties will not be scanned
                continue

            scan_rate = self._scan_rate
            if "scan_rate" in birth.properties:
                scan_rate = birth.properties["scan_rate"].value
                if type(scan_rate) is not int:
                    raise ValueError(f"Scan rate can not be of type {type(scan_rate)}")

                if scan_rate == 0:  # No scan this metric
                    continue

            if scan_rate not in schedules:
                schedules[scan_rate] = ScanSchedule(
                    self._net, scan_rate, self._queue, self._clock
                )

            quality = birth.properties.get("Quality", 192)
            schedules[scan_rate].add_reading(
                Reading(
                    birth.data_type,
                    Quality(quality if type(quality) is int else 192),
                    birth.value,
                    alias=birth.alias,
                    name=birth.name,
                )
            )

        self._schedules = []
        for schedule in schedules.values():
            schedule.start()
            self._schedules.append(schedule)

        return births

    async def stop(self):
        """Stop all next scanning tasks"""
        for schedule in self._schedules:
            await schedule.stop()

        await asyncio.gather(
            *[schedule.stop() for schedule in self._schedules], return_exceptions=True
        )

    async def _set_scan_rate(self, value: int):
        for schedule in self._schedules:
            if schedule.scan_rate == self._scan_rate:
                await schedule.stop()
                schedule.scan_rate = value
                schedule.start()
        self._scan_rate = value

    async def execute_command(self, metric: Metric) -> Metric:
        """execute a command, writing metric to the net"""

        if metric.name == "Node Control/Scan Rate":
            if type(metric.value) is not int:
                raise ValueError(f"Metric {metric.name} has not type integer")
            await self._set_scan_rate(metric.value)
            try:
                await self._net.write_value(metric.value, metric_name=metric.name)
            except Exception:
                pass

            return Metric(
                self._clock.timestamp(),
                metric.value,
                DataType.Int32,
                name="Node Control/Scan Rate",
            )

        try:
            await self._net.write_value(
                metric.value, metric_name=metric.name, alias=metric.alias
            )
            sample = Sample(self._clock.timestamp(), metric.value, Quality.GOOD)
        except asyncio.CancelledError:
            sample = Sample(self._clock.timestamp(), metric.value, Quality.STALE)
        except Exception as e:
            sample = Sample(self._clock.timestamp(), metric.value, Quality.BAD)
            logger.error(
                f"Writing {metric.value} to metric '{metric.name}:{metric.alias}'"
            )
            logger.exception(e)

        for schedule in self._schedules:
            if schedule.update_reading(sample, alias=metric.alias, name=metric.name):
                break

        return Metric(
            sample.timestamp,
            metric.value,
            metric.data_type,
            metric.alias,
            metric.name,
            properties=PropertySet.from_dict(
                {"Quality": {"value": sample.quality.value, "dataType": "Int32"}}
            ),
        )
