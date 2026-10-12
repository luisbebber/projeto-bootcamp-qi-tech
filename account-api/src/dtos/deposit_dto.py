from typing import List

from models import Deposit


class DepositDTO:

    @staticmethod
    def obj_to_simplified_dict(deposit: Deposit) -> dict:
        dto = dict()
        dto["deposit_key"] = deposit.deposit_key
        dto["client_key"] = deposit.account.client_key
        dto["account_key"] = deposit.account.account_key
        dto["amount"] = str(deposit.amount)
        dto["status"] = deposit.status.enumerator
        dto["created_at"] = deposit.created_at.isoformat()

        return dto

    @staticmethod
    def list_obj_to_list_dict(deposits_list: List[Deposit]) -> List[dict]:
        deposits_list_dto = []

        for deposit in deposits_list:
            deposits_list_dto.append(DepositDTO.obj_to_simplified_dict(deposit))

        return deposits_list_dto

    @staticmethod
    def key_and_status(deposit: Deposit) -> dict:
        dto = dict()
        dto["deposit_key"] = deposit.deposit_key
        dto["status"] = deposit.status.enumerator

        return dto

    @staticmethod
    def key_and_balance_after(deposit: Deposit, balance_after) -> dict:
        dto = dict()
        dto["deposit_key"] = deposit.deposit_key
        dto["balance_after"] = str(balance_after)

        return dto
