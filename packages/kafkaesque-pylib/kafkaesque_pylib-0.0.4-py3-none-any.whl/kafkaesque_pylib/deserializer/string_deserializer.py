import kafkaesque_pylib.deserializer as des
import kafkaesque_pylib as lib

class StringDeserializer(des.Deserializer):

    def deserialize(self, payload: bytes) -> str | lib.KafkaEsqueError | None:
        if not payload:
            return None
        try:
            return payload.decode('utf-8')
        except Exception as e:
            return lib.KafkaEsqueError('Could not deserialize payload', payload, e)
