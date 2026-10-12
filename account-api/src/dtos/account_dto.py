from typing import List

from models import Account


class AccountDTO:

    @staticmethod
    def obj_to_simplified_dict(account: Account) -> dict:
        dto = dict()
        dto["account_key"] = account.account_key
        dto["name"] = account.name
        dto["document_number"] = account.document_number
        dto["balance"] = str(account.balance)
        dto["status"] = account.status.enumerator
        dto["created_at"] = account.created_at.isoformat()

        return dto

    @staticmethod
    def obj_to_dict(account: Account) -> dict:
        dto = AccountDTO.obj_to_simplified_dict(account)
        dto["status_events"] = []

        for status_event in account.status_events:
            status_event_dto = dict()
            status_event_dto["status"] = status_event.status.enumerator
            status_event_dto["created_at"] = status_event.created_at.isoformat()

            dto["status_events"].append(status_event_dto)

        return dto

    @staticmethod
    def list_obj_to_list_dict(accounts_list: List[Account]) -> List[dict]:
        accounts_list_dto = []

        for account in accounts_list:
            accounts_list_dto.append(AccountDTO.obj_to_simplified_dict(account))

        return accounts_list_dto

    @staticmethod
    def only_obj_key_and_status(account: Account) -> dict:
        dto = dict()
        dto["account_key"] = account.account_key
        dto["status"] = account.status.enumerator

        return dto
