from typing import List

from models import Withdrawal, WithdrawalStatus

CLIENT_STATUS = {
    WithdrawalStatus.PENDING_CONFIRMATION: WithdrawalStatus.PENDING_CONFIRMATION,
    WithdrawalStatus.PENDING_FEE: WithdrawalStatus.COMPLETED,
    WithdrawalStatus.COMPLETED: WithdrawalStatus.COMPLETED,
    WithdrawalStatus.REVERSED: WithdrawalStatus.REVERSED,
}


class WithdrawalDTO:

    @staticmethod
    def obj_to_simplified_dict(withdrawal: Withdrawal) -> dict:
        dto = dict()
        dto["withdrawal_key"] = withdrawal.withdrawal_key
        dto["client_key"] = withdrawal.account.client_key
        dto["account_key"] = withdrawal.account.account_key
        dto["amount"] = str(withdrawal.amount)
        dto["status"] = withdrawal.status.enumerator
        dto["created_at"] = withdrawal.created_at.isoformat()

        return dto

    @staticmethod
    def list_obj_to_list_dict(withdrawals_list: List[Withdrawal]) -> List[dict]:
        withdrawals_list_dto = []

        for withdrawal in withdrawals_list:
            withdrawals_list_dto.append(WithdrawalDTO.obj_to_simplified_dict(withdrawal))

        return withdrawals_list_dto

    @staticmethod
    def obj_to_dict(withdrawal: Withdrawal) -> dict:
        dto = dict()
        dto["withdrawal_key"] = withdrawal.withdrawal_key
        dto["amount"] = str(withdrawal.amount)
        dto["status"] = withdrawal.status.enumerator
        dto["receiver_data"] = withdrawal.receiver_data
        dto["status_events"] = []

        for status_event in withdrawal.status_events:
            status_event_dto = dict()
            status_event_dto["status"] = status_event.status.enumerator
            status_event_dto["created_at"] = status_event.created_at.isoformat()

            dto["status_events"].append(status_event_dto)

        dto["created_at"] = withdrawal.created_at.isoformat()

        return dto

    @staticmethod
    def key_and_status(withdrawal: Withdrawal) -> dict:
        dto = dict()
        dto["withdrawal_key"] = withdrawal.withdrawal_key
        dto["status"] = CLIENT_STATUS[withdrawal.status.enumerator]

        return dto
