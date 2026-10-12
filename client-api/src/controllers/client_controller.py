from controllers.base_controller import BaseController
from dtos import ClientDTO
from errors import ClientAlreadyInStatus, DuplicatedClient, InvalidDocumentNumber, NotFoundClient
from repositories import ClientRepository
from utils.document_number import is_valid_cnpj


class ClientController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.client_repository = ClientRepository(self.context)

    def create(self, client_data: dict) -> dict:
        self.logger.debug(f"Cadastrando a operação {client_data['operation']}")

        document_number = client_data["document_number"]
        operation = client_data["operation"]

        if not is_valid_cnpj(document_number):
            raise InvalidDocumentNumber(document_number)

        if self.client_repository.get_by_document_number_and_operation(document_number, operation) is not None:
            raise DuplicatedClient(document_number, operation)

        client = self.client_repository.create(client_data)

        client_dto = ClientDTO.only_obj_key_and_status(client)
        self.session.commit()

        return client_dto

    def get_by_key(self, client_key: str) -> dict:
        self.logger.debug(f"Buscando a empresa {client_key}")

        client = self.client_repository.get_by_key(client_key)
        if client is None:
            raise NotFoundClient(client_key)

        return ClientDTO.obj_to_dict(client)

    def get_list(self, document_number: str, limit: int, offset: int) -> dict:
        self.logger.debug("Listando as empresas")

        clients_list = self.client_repository.list_page(document_number, limit, offset)

        is_last_page = True
        if len(clients_list) > limit:
            is_last_page = False
            clients_list = clients_list[:-1]

        return {
            "clients_list_dto": ClientDTO.list_obj_to_list_dict(clients_list),
            "is_last_page": is_last_page,
        }

    def update_status(self, client_key: str, new_status: str) -> dict:
        self.logger.debug(f"Mudando a empresa {client_key} para {new_status}")

        client = self.client_repository.get_by_key_for_update(client_key)
        if client is None:
            raise NotFoundClient(client_key)

        if client.status.enumerator == new_status:
            raise ClientAlreadyInStatus(client_key, new_status)

        self.client_repository.update_status(client, new_status)

        client_dto = ClientDTO.only_obj_key_and_status(client)
        self.session.commit()

        return client_dto
