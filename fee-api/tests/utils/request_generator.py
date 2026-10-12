from os import environ

from tests.utils.requisition import ClientRequisition, BaseConnectorResponse


INTERNAL_TOKEN = environ.get("INTERNAL_TOKEN", "default_token")


class RequestGenerator:

    @staticmethod
    def POST_fee_configuration(client_key: str, fee_configuration_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST",
            f"/client/{client_key}/fee_configuration",
            payload=fee_configuration_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def POST_fee(client_key: str, fee_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST",
            f"/client/{client_key}/fee",
            payload=fee_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_fee(client_key: str, fee_key: str) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/client/{client_key}/fee/{fee_key}",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_fee_configuration(client_key: str) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/client/{client_key}/fee_configuration",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def PATCH_fee_configuration(client_key: str, fee_configuration_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "PATCH",
            f"/client/{client_key}/fee_configuration",
            payload=fee_configuration_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_spending(client_key: str, query_params: dict = None) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/client/{client_key}/spending",
            query_params=query_params,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def POST_charge(client_key: str, charge_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST",
            f"/client/{client_key}/charge",
            payload=charge_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def PATCH_charge(client_key: str, charge_key: str, charge_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "PATCH",
            f"/client/{client_key}/charge/{charge_key}",
            payload=charge_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_charges(client_key: str, query_params: dict = None) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/client/{client_key}/charge",
            query_params=query_params,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

    @staticmethod
    def GET_charge(client_key: str, charge_key: str) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/client/{client_key}/charge/{charge_key}",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json
