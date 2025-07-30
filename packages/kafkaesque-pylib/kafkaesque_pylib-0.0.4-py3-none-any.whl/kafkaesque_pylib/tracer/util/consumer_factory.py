from confluent_kafka import TopicPartition, Consumer, OFFSET_BEGINNING

import kafkaesque_pylib as lib


class ConsumerFactory:
    @staticmethod
    def create(name: str, number_of_partitions: int, partitions: [int], config: lib.KafkaEsqueConfig) -> Consumer:
        if partitions is None:
            topic_partitions = [TopicPartition(name, p, OFFSET_BEGINNING) for p in range(number_of_partitions)]
            topic_partitions.reverse()
        else:
            invalid_partitions = [p for p in partitions if p >= number_of_partitions]
            if len(invalid_partitions) > 0:
                raise lib.KafkaEsqueException(f"the following partitions do not exist: {invalid_partitions}")
            topic_partitions = [TopicPartition(name, p, OFFSET_BEGINNING) for p in partitions]
            topic_partitions.reverse()

        cluster_config = config.cluster_config
        consumer_config =  {
                'group.id': 'irrelevant',
                'enable.auto.commit': False
            }
        consumer = Consumer({
            **consumer_config,
            **cluster_config.get_boostrap_server_config(),
            **cluster_config.get_ssl_config(),
            **cluster_config.get_sasl_properties(),
            **cluster_config.get_schema_registry_auth_properties()
        })
        consumer.assign(topic_partitions)
        return consumer
