from os import environ

from tests.utils.requisition import ClientRequisition, BaseConnectorResponse


INTERNAL_TOKEN = environ.get("INTERNAL_TOKEN", "default_token")


class RequestGenerator:
    @staticmethod
    def POST_client_configuration(client_key: str) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST",
            f"/client/{client_key}",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def POST_deposit(client_key: str, account_key: str, deposit_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST",
            f"/client/{client_key}/account/{account_key}/deposit",
            payload=deposit_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def POST_withdrawal(client_key: str, account_key: str, withdrawal_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST",
            f"/client/{client_key}/account/{account_key}/withdrawal",
            payload=withdrawal_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_withdrawal(client_key: str, withdrawal_key: str) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/client/{client_key}/withdrawal/{withdrawal_key}",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def POST_transfer(client_key: str, transfer_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST",
            f"/client/{client_key}/transfer",
            payload=transfer_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_statement(client_key: str, account_key: str, params: dict = None) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/client/{client_key}/account/{account_key}/statement",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
            query_params=params,
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_deposits(params: dict = None) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET", "/deposits", headers={"INTERNAL-TOKEN": INTERNAL_TOKEN}, query_params=params
        )
        return response.response_status, response.response_json

    @staticmethod
    def PATCH_deposit(client_key: str, deposit_key: str, status_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "PATCH",
            f"/client/{client_key}/deposit/{deposit_key}",
            payload=status_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_withdrawals(params: dict = None) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET", "/withdrawals", headers={"INTERNAL-TOKEN": INTERNAL_TOKEN}, query_params=params
        )
        return response.response_status, response.response_json

    @staticmethod
    def PATCH_withdrawal(client_key: str, withdrawal_key: str, status_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "PATCH",
            f"/client/{client_key}/withdrawal/{withdrawal_key}",
            payload=status_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def PATCH_account(client_key: str, account_key: str, status_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "PATCH",
            f"/client/{client_key}/account/{account_key}",
            payload=status_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_account(client_key: str, account_key: str) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/client/{client_key}/account/{account_key}",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_accounts(client_key: str, params: dict = None) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/client/{client_key}/accounts",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
            query_params=params,
        )
        return response.response_status, response.response_json

    @staticmethod
    def POST_account(client_key: str, account_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST",
            f"/client/{client_key}/account",
            payload=account_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json
