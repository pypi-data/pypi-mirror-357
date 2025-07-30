from datetime import timedelta, datetime

import isodate
from confluent_kafka import Consumer, TopicPartition
from isodate import ISO8601Error

import kafkaesque_pylib.tracer as tracer
import kafkaesque_pylib.tracer.util as util
import kafkaesque_pylib.deserializer as des
import kafkaesque_pylib as lib


class TimeTracer(tracer.Tracer):

    def __init__(self,
                 name: str,
                 from_time: timedelta | datetime | str | None,
                 until_time: timedelta | datetime | str | None,
                 amount_per_partition: int | None,
                 number_of_partitions: int,
                 partitions: [int],
                 config: lib.KafkaEsqueConfig,
                 key_deserializer: des.Deserializer,
                 value_deserializer: des.Deserializer):
        self.name = name
        self.number_of_partitions = number_of_partitions
        self.partitions = partitions
        self.config = config
        self.key_deserializer = key_deserializer
        self.value_deserializer = value_deserializer

        self.from_time = self.__to_timestamp(from_time)
        self.until_time = self.__to_timestamp(until_time)
        self.amount_per_partition = amount_per_partition

        self.consumer = None
        self.should_abort = False
        self.count = {}

    def __iter__(self) -> tracer.Tracer:
        if self.consumer is not None:
            return self
        self.consumer = util.ConsumerFactory.create(self.name, self.number_of_partitions, self.partitions, self.config)
        self.__seek(self.consumer, self.from_time)
        return self

    def __next__(self) -> lib.KafkaEsqueMessage:
        if self.should_abort:
            raise StopIteration
        msg = self.consumer.poll(self.config.client_config.message_poll_timeout)
        if msg is None:
            raise StopIteration
        if msg.error():
            raise StopIteration

        partition = msg.partition()
        timestamp = datetime.fromtimestamp(msg.timestamp()[-1] / 1000.0)
        if self.amount_per_partition is not None:
            if partition not in self.count:
                self.count[partition] = 0
            self.count[partition] += 1
            if self.count[partition] >= self.amount_per_partition:
                self.consumer.incremental_unassign([TopicPartition(self.name, partition)])
                return util.MessageMapper.map(msg, self.key_deserializer, self.value_deserializer)

        if self.until_time is not None:
            if self.until_time < timestamp:
                self.consumer.incremental_unassign([TopicPartition(self.name, partition)])
                return self.__next__()

        return util.MessageMapper.map(msg, self.key_deserializer, self.value_deserializer)

    def abort(self):
        self.should_abort = True

    def __del__(self):
        self.consumer.unassign()
        self.consumer.close()
        self.consumer = None

    @staticmethod
    def __seek(consumer: Consumer, from_time: datetime):
        if from_time is None:
            return
        assignment = consumer.assignment()

        search_partitions = [TopicPartition(p.topic, p.partition, int(from_time.timestamp() * 1000)) for p in
                             assignment]

        offset_partitions = consumer.offsets_for_times(search_partitions)
        offset_by_partition = {}
        for partition in offset_partitions:
            offset_by_partition[partition.partition] = partition.offset

        for partition in assignment:
            partition.offset = offset_by_partition[partition.partition]
            if partition.offset < 0:
                continue
            consumer.seek(partition)

    @staticmethod
    def __to_timestamp(time: timedelta | datetime | str):
        if time is None:
            return None
        if isinstance(time, str):
            if TimeTracer.__is_duration(time):
                duration = isodate.parse_duration(time)
                return datetime.now() - duration
            elif TimeTracer.__is_datetime(time):
                return isodate.parse_datetime(time)
            else:
                raise lib.KafkaEsqueException(f"Cannot interpret time '{time}'")
        if isinstance(time, timedelta):
            return datetime.now() - time
        return time

    @staticmethod
    def __is_duration(text: str):
        try:
            isodate.parse_duration(text)
            return True
        except ISO8601Error:
            return False

    @staticmethod
    def __is_datetime(text: str):
        try:
            isodate.parse_datetime(text)
            return True
        except ISO8601Error:
            return False
