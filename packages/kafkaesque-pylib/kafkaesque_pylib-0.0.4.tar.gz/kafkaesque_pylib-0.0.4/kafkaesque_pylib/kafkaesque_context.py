from confluent_kafka.admin import AdminClient

import kafkaesque_pylib.deserializer as des
import kafkaesque_pylib as lib


class KafkaEsqueContext:

    def __init__(self, config: lib.KafkaEsqueConfig):
        self.config = config
        self.client = AdminClient({
            **config.cluster_config.get_boostrap_server_config(),
            **config.cluster_config.get_ssl_config()
        })

    def get_topics(self, key_type: str = None, value_type: str = None) -> [lib.KafkaEsqueTopic]:
        kafka_topics = self.client.list_topics().topics
        topics = []
        for name in kafka_topics:
            kafka_topic = kafka_topics[name]
            partitions = len(kafka_topic.partitions)

            cluster_config = self.config.cluster_config

            resolved_key_type = key_type or cluster_config.get_key_type(name) or 'string'
            resolved_value_type = value_type or cluster_config.get_value_type(name) or 'string'
            def key_deserializer(kt: str):
                resolver = des.DeserializerResolver(name, self.config)
                return lambda: resolver.resolve(kt, 'key')
            def value_deserializer(vt: str):
                resolver = des.DeserializerResolver(name, self.config)
                return lambda: resolver.resolve(vt, 'value')

            topic = lib.KafkaEsqueTopic(
                name,
                partitions,
                self.config,
                key_deserializer(resolved_key_type),
                value_deserializer(resolved_value_type)
            )
            topics.append(topic)
        return topics

    def get_topic(self, name: str, key_type: str = None, value_type: str = None) -> lib.KafkaEsqueTopic:
        topics = self.get_topics(key_type, value_type)
        matches = [t for t in topics if t.name == name]
        if len(matches) != 1:
            raise lib.KafkaEsqueException(f"Topic {name} not found")
        return matches[0]
