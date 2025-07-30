from confluent_kafka import Consumer

import kafkaesque_pylib.deserializer as des
import kafkaesque_pylib.tracer.util as util
import kafkaesque_pylib.tracer as tracer
import kafkaesque_pylib as lib



class AllTracer(tracer.Tracer):

    def __init__(self,
                 name: str,
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

        self.consumer = None
        self.should_abort = False

    def __iter__(self) -> tracer.Tracer:
        if self.consumer is not None:
            return self
        self.consumer = util.ConsumerFactory.create(self.name, self.number_of_partitions, self.partitions, self.config)
        self.__seek(self.consumer)
        return self

    def __next__(self) -> lib.KafkaEsqueMessage:
        if self.should_abort:
            raise StopIteration
        msg = self.consumer.poll(self.config.client_config.message_poll_timeout)
        if msg is None:
            raise StopIteration
        if msg.error():
            raise StopIteration
        return util.MessageMapper.map(msg, self.key_deserializer, self.value_deserializer)

    def abort(self):
        self.should_abort = True

    def __del__(self):
        self.consumer.unassign()
        self.consumer.close()
        self.consumer = None

    @staticmethod
    def __seek(consumer: Consumer):
        assignment = consumer.assignment()
        offset_by_partition = {}
        for partition in assignment:
            (low, high) = consumer.get_watermark_offsets(partition)
            offset_by_partition[partition.partition] = low
        for partition in assignment:
            partition.offset = offset_by_partition[partition.partition]
            consumer.seek(partition)
