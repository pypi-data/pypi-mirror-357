import confluent_kafka.schema_registry.avro as avro
from confluent_kafka.serialization import SerializationContext
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import MessageField

import kafkaesque_pylib.deserializer as des
import kafkaesque_pylib as lib


class AvroDeserializer(des.Deserializer):

    def __init__(self, topic: str, field: str, config: lib.KafkaEsqueConfig):
        self.topic = topic
        if field == 'key':
            self.field = MessageField.KEY
        elif field == 'value':
            self.field = MessageField.VALUE
        else:
            raise lib.KafkaEsqueException(f"invalid field type {field}")

        cluster_config = config.cluster_config
        schema_registry_client = SchemaRegistryClient({
            **cluster_config.get_schema_registry_config(),
            **cluster_config.get_schema_registry_auth_properties()
        })
        self.avro_deserializer = avro.AvroDeserializer(schema_registry_client)

    def deserialize(self, payload: bytes) -> dict | lib.KafkaEsqueError | None:
        if not payload:
            return None
        try:
            return self.avro_deserializer(payload, SerializationContext(self.topic, self.field))
        except Exception as e:
            return lib.KafkaEsqueError('Could not deserialize payload', payload, e)
