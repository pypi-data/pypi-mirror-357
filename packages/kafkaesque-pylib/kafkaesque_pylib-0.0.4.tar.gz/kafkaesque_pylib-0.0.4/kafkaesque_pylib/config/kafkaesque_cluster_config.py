from pathlib import Path
import yaml

class KafkaEsqueClusterConfig:

    def __init__(self,
                 folder: Path | None,
                 bootstrapServers: str,
                 schemaRegistry: str = None,
                 schemaRegistryBasicAuthUserInfo: str = None,
                 schemaRegistryAuthConfig: str = None,
                 schemaRegistryAuthMode: str = None,
                 schemaRegistryUseSsl: bool = None,
                 sslEnabled: bool = None,
                 keyStoreLocation: str = None,
                 keyStorePassword: str = None,
                 trustStoreLocation: str = None,
                 trustStorePassword: str = None,
                 saslSecurityProtocol: str = None,
                 saslMechanism: str = None,
                 saslClientCallbackHandlerClass: str = None,
                 saslJaasConfig: str = None,
                 kafkaConnectUrl: str = None,
                 kafkaConnectBasicAuthUser: str = None,
                 kafkaConnectBasicAuthPassword: str = None,
                 kafkaConnectUseSsl: str = bool,
                 suppressSslEndPointIdentification: str = bool,
                 certPathValidationSuppressed: str = bool,
                 identifier: str = None
                 ):

        self.folder = folder
        self.bootstrap_servers = bootstrapServers
        self.schema_registry = schemaRegistry
        self.schema_registry_basic_auth_user_info = schemaRegistryBasicAuthUserInfo
        self.schema_registry_auth_config = schemaRegistryAuthConfig
        self.schema_registry_auth_mode = schemaRegistryAuthMode
        self.schema_registry_use_ssl = schemaRegistryUseSsl
        self.ssl_enabled = sslEnabled
        self.key_store_location = keyStoreLocation
        self.key_store_password = keyStorePassword
        self.trust_store_location = trustStoreLocation
        self.trust_store_password = trustStorePassword
        self.sasl_security_protocol = saslSecurityProtocol
        self.sasl_mechanism = saslMechanism
        self.sasl_client_callback_handler_class = saslClientCallbackHandlerClass
        self.sasl_jaas_config = saslJaasConfig
        self.kafka_connect_url = kafkaConnectUrl
        self.kafka_connect_basic_auth_user = kafkaConnectBasicAuthUser
        self.kafka_connect_basic_auth_password = kafkaConnectBasicAuthPassword
        self.kafka_connect_use_ssl = kafkaConnectUseSsl
        self.suppress_sll_end_point_identification = suppressSslEndPointIdentification
        self.cert_path_validation_suppressed = certPathValidationSuppressed,
        self.identifier = identifier
        self.topics_config = None
        self.settings = None

    def get_boostrap_server_config(self) -> dict[str, str]:
        return {
            'bootstrap.servers': self.bootstrap_servers
        }

    def get_schema_registry_config(self) -> dict[str, str]:
        config = {}
        if not self.schema_registry:
            return config
        config['url'] = self.schema_registry

        if not self.schema_registry.lower().startswith('https:'):
            return config

        config['security.protocol'] = 'SSL'
        if self.suppress_sll_end_point_identification:
            config['ssl.endpoint.identification.algorithm'] = ''
        if self.key_store_location:
            store_location = self.folder / self.key_store_location
            if store_location.exists():
                # TODO convert jks stores to p12
                config['ssl.keystore.location'] = str(store_location.absolute())
                if self.key_store_password:
                    config['ssl.keystore.password'] = self.key_store_password

        # TODO figure out how to convert truststore into a compatible format
        config['enable.ssl.certificate.verification'] = 'false'
        # if self.trust_store_location:
        #     store_location = self.folder / self.trust_store_location
        #     if store_location.exists():
        #         config['ssl.truststore.location'] = str(store_location.absolute())
        #         if self.trust_store_password:
        #             config['ssl.truststore.password'] = self.trust_store_password
        return config

    def get_ssl_config(self) -> dict[str, str]:
        config = {}
        if not self.ssl_enabled:
            return config

        config['security.protocol'] = 'SSL'
        if self.suppress_sll_end_point_identification:
            config['ssl.endpoint.identification.algorithm'] = ''

        if self.key_store_location:
            store_location = self.folder / self.key_store_location
            if store_location.exists():
                # TODO convert jks stores to p12
                config['ssl.keystore.location'] = str(store_location.absolute())
                if self.key_store_password:
                    config['ssl.keystore.password'] = self.key_store_password

        # TODO figure out how to convert truststore into a compatible format
        config['enable.ssl.certificate.verification'] = 'false'
        # if self.trust_store_location:
        #     store_location = self.folder / self.trust_store_location
        #     if store_location.exists():
        #         config['ssl.truststore.location'] = str(store_location.absolute())
        #         if self.trust_store_password:
        #             config['ssl.truststore.password'] = self.trust_store_password
        return config

    def get_sasl_properties(self) -> dict[str, str]:
        config = {}
        if self.sasl_security_protocol:
            config['security.protocol'] = self.sasl_security_protocol
        if self.sasl_mechanism:
            config['sasl.mechanism'] = self.sasl_mechanism
        if self.sasl_jaas_config:
            config['sasl.jaas.config"'] = self.sasl_jaas_config
        if self.sasl_client_callback_handler_class:
            config['sasl.client.callback.handler.class'] = self.sasl_client_callback_handler_class
        return config

    def get_schema_registry_auth_properties(self) -> dict[str, str]:
        config = {}
        if 'BASIC' == self.schema_registry_auth_mode:
            config['basic.auth.credentials.source'] = 'USER_INFO'
            config['basic.auth.user.info'] = self.schema_registry_auth_config
        elif 'TOKEN' == self.schema_registry_auth_mode:
            config['bearer.auth.credentials.source'] = 'STATIC_TOKEN'
            config['bearer.auth.token'] = self.schema_registry_auth_config
        return config

    def get_key_type(self, topic):
        topic_config = self.__get_topic_config(topic)
        if topic_config:
            return topic_config['keyType']
        settings = self.__get_settings()
        if settings:
            return settings['default.key.messagetype']
        return None

    def get_value_type(self, topic):
        topic_config = self.__get_topic_config(topic)
        if topic_config:
            return topic_config['valueType']
        settings = self.__get_settings()
        if settings:
            return settings['default.value.messagetype']
        return None

    def __get_settings(self):
        if self.folder is None:
            return None
        if self.settings is None:
            settings_path = self.folder / '../settings.yaml'
            with open(settings_path, 'r') as file:
                try:
                    self.settings = yaml.safe_load(file)
                except yaml.YAMLError:
                    return None
        return self.settings

    def __get_topic_config(self, topic):
        if self.folder is None:
            return None
        if self.topics_config is None:
            topics_config_path = self.folder / 'topics.yaml'
            with open(topics_config_path, 'r') as file:
                try:
                    loaded_config = yaml.safe_load(file)
                except yaml.YAMLError:
                    return None
            self.topics_config = {}
            for config in loaded_config:
                name = config['name']
                if name is None:
                    continue
                self.topics_config[name] = config
        if topic not in self.topics_config:
            return None
        return self.topics_config[topic]
