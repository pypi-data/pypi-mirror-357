from datetime import datetime

from kafkaesque_pylib import KafkaEsqueError


class KafkaEsqueMessage:
    def __init__(self,
                 key: str | dict | KafkaEsqueError | None,
                 value: str | dict | KafkaEsqueError | None,
                 header: dict[str, str],
                 timestamp: datetime,
                 partition: int,
                 offset: int):
        self.key = key
        self.value = value
        self.header = header
        self.timestamp = timestamp
        self.partition = partition
        self.offset = offset

    def is_erroneous(self):
        return self.key_is_erroneous() | self.value_is_erroneous()

    def key_is_erroneous(self):
        return isinstance(self.key, KafkaEsqueError)

    def value_is_erroneous(self):
        return isinstance(self.value, KafkaEsqueError)

    def is_tombstone(self):
        return self.value is None

    def __str__(self):
        return f"Timestamp={self.timestamp.isoformat()} Partition={self.partition} Offset={self.offset} Key={self.key} Value={self.value}"
