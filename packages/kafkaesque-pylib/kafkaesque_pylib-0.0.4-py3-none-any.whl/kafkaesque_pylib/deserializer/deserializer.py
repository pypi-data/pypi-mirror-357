from abc import ABC, abstractmethod

from kafkaesque_pylib import KafkaEsqueError


class Deserializer(ABC):

    @abstractmethod
    def deserialize(self, payload: bytes) -> str | dict | KafkaEsqueError | None:
        pass
