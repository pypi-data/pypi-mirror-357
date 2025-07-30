from datetime import timedelta, datetime
from typing import Callable

import kafkaesque_pylib.deserializer as des
import kafkaesque_pylib as lib
import kafkaesque_pylib.tracer as tracer


class KafkaEsqueTopic:

    def __init__(self,
                 name: str,
                 number_of_partitions: int,
                 config: lib.KafkaEsqueConfig,
                 key_deserializer: Callable[[], des.Deserializer],
                 value_deserializer: Callable[[], des.Deserializer]):
        self.name = name
        self.number_of_partitions = number_of_partitions
        self.config = config
        self.key_deserializer = key_deserializer
        self.value_deserializer = value_deserializer

    def trace_all(self, partitions: [int] = None) -> tracer.Tracer:
        return tracer.AllTracer(self.name,
                                self.number_of_partitions,
                                partitions,
                                self.config,
                                self.key_deserializer(),
                                self.value_deserializer())

    def trace_newest(self, amount_per_partition: int, partitions: [int] = None) -> tracer.Tracer:
        return tracer.NewestTracer(self.name,
                                   amount_per_partition,
                                   self.number_of_partitions,
                                   partitions,
                                   self.config,
                                   self.key_deserializer(),
                                   self.value_deserializer())

    def trace_oldest(self, amount_per_partition: int, partitions: [int] = None) -> tracer.Tracer:
        return tracer.OldestTracer(self.name,
                                   amount_per_partition,
                                   self.number_of_partitions,
                                   partitions,
                                   self.config,
                                   self.key_deserializer(),
                                   self.value_deserializer())

    def trace_from_specific_offset(self, offset: int, amount_per_partition: int,
                                   partitions: [int] = None) -> tracer.Tracer:
        return tracer.SpecificOffsetTracer(self.name,
                                           offset,
                                           amount_per_partition,
                                           self.number_of_partitions,
                                           partitions,
                                           self.config,
                                           self.key_deserializer(),
                                           self.value_deserializer())

    def trace_continuously(self, partitions: [int] = None) -> tracer.Tracer:
        return tracer.ContinuousTracer(self.name,
                                       self.number_of_partitions,
                                       partitions,
                                       self.config,
                                       self.key_deserializer(),
                                       self.value_deserializer())

    def trace_by_time(self,
                      from_time: timedelta | datetime | str | None = None,
                      until_time: timedelta | datetime | str | None = None,
                      amount_per_partition: int | None = None,
                      partitions: [int] = None) -> tracer.Tracer:
        return tracer.TimeTracer(self.name,
                                 from_time,
                                 until_time,
                                 amount_per_partition,
                                 self.number_of_partitions,
                                 partitions,
                                 self.config,
                                 self.key_deserializer(),
                                 self.value_deserializer())

    def __str__(self) -> str:
        return f"{self.name}(partitions: {self.number_of_partitions})"
