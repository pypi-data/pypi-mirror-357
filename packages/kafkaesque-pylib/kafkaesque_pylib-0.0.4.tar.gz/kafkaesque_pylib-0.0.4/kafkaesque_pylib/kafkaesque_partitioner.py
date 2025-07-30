from kafkaesque_pylib import KafkaEsqueTopic
from murmurhash2 import murmurhash2

class KafkaEsquePartitioner:

    @staticmethod
    def partitions_for(key, topic: KafkaEsqueTopic = None, number_of_partitions: int = None):
        if topic is not None:
            return [KafkaEsquePartitioner.__partition_for(key, topic.number_of_partitions)]
        if number_of_partitions is not None:
            return [KafkaEsquePartitioner.__partition_for(key, number_of_partitions)]
        return []

    @staticmethod
    def __partition_for(key: str, number_of_partitions: int):
        seed = 0x9747b28c
        mmhash = murmurhash2(key.encode('utf-8'), seed)

        # numbers greater than 2^31 would be negative in java, this is a correction for that
        if mmhash > pow(2, 31):
            mmhash = mmhash + (1 << 32)

        return abs(mmhash) % number_of_partitions
