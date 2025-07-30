from datetime import datetime

import kafkaesque_pylib.deserializer as des
import kafkaesque_pylib as lib


class MessageMapper:

    @staticmethod
    def map(msg, key_deserializer: des.Deserializer, value_deserializer: des.Deserializer) -> lib.KafkaEsqueMessage:

        headers = {}
        if msg.headers() is not None:
            for kv in msg.headers():
                headers[kv[0]] = str(kv[1])
        return lib.KafkaEsqueMessage(
            key_deserializer.deserialize(msg.key()),
            value_deserializer.deserialize(msg.value()),
            headers,
            datetime.fromtimestamp(msg.timestamp()[-1] / 1000.0),
            msg.partition(),
            msg.offset()
        )
