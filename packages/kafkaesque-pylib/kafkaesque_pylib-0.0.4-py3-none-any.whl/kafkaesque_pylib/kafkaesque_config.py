import json
from pathlib import Path

from kafkaesque_pylib import KafkaEsqueException
from kafkaesque_pylib.config import KafkaEsqueClusterConfig, KafkaEsqueClientConfig


class KafkaEsqueConfig:

    def __init__(self, cluster_config: KafkaEsqueClusterConfig, client_config: KafkaEsqueClientConfig):
        self.cluster_config = cluster_config
        self.client_config = client_config

    @staticmethod
    def get(cluster_name: str, clusters_file=None, client_config: KafkaEsqueClientConfig = KafkaEsqueClientConfig()):
        return KafkaEsqueConfig(
            KafkaEsqueConfig.get_custer_config(cluster_name, clusters_file),
            client_config
        )

    @staticmethod
    def get_custer_config(cluster_name: str, clusters_file=None):
        if clusters_file is None:
            clusters_path = Path.home() / '.kafkaesque' / 'clusters.json'
        else:
            clusters_path = Path(clusters_file)

        if not Path.exists(clusters_path):
            raise KafkaEsqueException(f"Could not find KafkaEsqueConfig")

        with open(clusters_path, 'r') as file:
            clusters = json.load(file)['clusterConfigs']

        for i in range(len(clusters)):
            cluster = clusters[i]
            identifier = cluster['identifier']
            if cluster_name == identifier:
                return KafkaEsqueClusterConfig(clusters_path.parent / identifier, **cluster)
        raise KafkaEsqueException(f"No cluster with name '{cluster_name}' found")
