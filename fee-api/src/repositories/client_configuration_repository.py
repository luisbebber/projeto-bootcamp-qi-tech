from database import Context
from models import ClientConfiguration


class ClientConfigurationRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, client_key: str) -> ClientConfiguration:
        client_configuration = ClientConfiguration()
        client_configuration.client_key = client_key

        self.session.add(client_configuration)
        return client_configuration

    def get_by_client_key(self, client_key: str) -> ClientConfiguration:
        return (
            self.session.query(ClientConfiguration)
            .filter(ClientConfiguration.client_key == client_key)
            .first()
        )
