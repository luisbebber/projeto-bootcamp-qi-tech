from uuid import uuid4

from database import Context
from models import Client, ClientStatus, ClientStatusEvent


class ClientRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, client_data: dict) -> Client:
        client = Client()

        client.client_key = str(uuid4())
        client.name = client_data["name"]
        client.document_number = client_data["document_number"]
        client.operation = client_data["operation"]

        self.update_status(client, ClientStatus.ACTIVE)

        self.session.add(client)
        return client

    def update_status(self, client: Client, new_status_enumerator: str) -> None:
        new_status = self.get_status(new_status_enumerator)
        client.status = new_status

        new_status_event = ClientStatusEvent()
        new_status_event.status = new_status

        client.status_events.append(new_status_event)

    def get_by_key(self, client_key: str) -> Client:
        return (
            self.session.query(Client)
            .filter(Client.client_key == client_key)
            .first()
        )

    def get_by_key_for_update(self, client_key: str) -> Client:
        return (
            self.session.query(Client)
            .filter(Client.client_key == client_key)
            .with_for_update()
            .populate_existing()
            .first()
        )

    def list_page(self, document_number: str, limit: int, offset: int) -> list:
        query = self.session.query(Client)

        if document_number is not None:
            query = query.filter(Client.document_number == document_number)

        return (
            query
            .order_by(Client.created_at.desc(), Client.id.desc())
            .limit(limit + 1)
            .offset(offset)
            .all()
        )

    def get_by_document_number_and_operation(self, document_number: str, operation: str) -> Client:
        return (
            self.session.query(Client)
            .filter(Client.document_number == document_number)
            .filter(Client.operation == operation)
            .first()
        )

    def get_status(self, enumerator: str) -> ClientStatus:
        return (
            self.session.query(ClientStatus)
            .filter(ClientStatus.enumerator == enumerator)
            .one()
        )
