from typing import List

from models import Client


class ClientDTO:

    @staticmethod
    def obj_to_simplified_dict(client: Client) -> dict:
        dto = dict()
        dto["client_key"] = client.client_key
        dto["name"] = client.name
        dto["document_number"] = client.document_number
        dto["operation"] = client.operation
        dto["status"] = client.status.enumerator
        dto["created_at"] = client.created_at.isoformat()

        return dto

    @staticmethod
    def obj_to_dict(client: Client) -> dict:
        dto = ClientDTO.obj_to_simplified_dict(client)
        dto["status_events"] = []

        for status_event in client.status_events:
            status_event_dto = dict()
            status_event_dto["status"] = status_event.status.enumerator
            status_event_dto["created_at"] = status_event.created_at.isoformat()

            dto["status_events"].append(status_event_dto)

        return dto

    @staticmethod
    def list_obj_to_list_dict(clients_list: List[Client]) -> List[dict]:
        clients_dto = []

        for client in clients_list:
            clients_dto.append(ClientDTO.obj_to_simplified_dict(client))

        return clients_dto

    @staticmethod
    def only_obj_key_and_status(client: Client) -> dict:
        dto = dict()
        dto["client_key"] = client.client_key
        dto["status"] = client.status.enumerator

        return dto
