
class KafkaEsqueError:

    def __init__(self, message: str, payload: bytes, cause: Exception):
        self.message = message
        self.payload = payload
        self.cause = cause

    def __str__(self):
        return f"Message={self.message} Payload={self.payload} Cause={self.cause}"
