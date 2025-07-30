
class KafkaEsqueClientConfig:

    def __init__(self,
                 message_poll_timeout: float = 5.0):
        self.message_poll_timeout = message_poll_timeout
