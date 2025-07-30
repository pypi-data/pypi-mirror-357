import kafkaesque_pylib.deserializer as des
import kafkaesque_pylib as lib

class DeserializerResolver:

    def __init__(self, topic: str, config: lib.KafkaEsqueConfig):
        self.topic = topic
        self.config = config

    def resolve(self, deserializer_type: str, field: str) -> des.Deserializer:
        match deserializer_type.lower():
            case 'string':
                return des.StringDeserializer()
            case 'avro':
                return des.AvroDeserializer(self.topic, field, self.config)
            case _:
                raise lib.KafkaEsqueException('Invalid deserializer type ' + deserializer_type)
