from __future__ import annotations
from abc import abstractmethod, ABC

import kafkaesque_pylib as lib


class Tracer(ABC):

    @abstractmethod
    def __iter__(self) -> Tracer:
        pass

    @abstractmethod
    def __next__(self) -> lib.KafkaEsqueMessage:
        pass

    @abstractmethod
    def abort(self):
        pass
