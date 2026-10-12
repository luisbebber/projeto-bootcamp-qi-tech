from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RandomGenerator, RequestGenerator
from tests.utils.mock_generator import FeeApiMock
from tests.utils.mock_utils import Mock


class TestAccountCreate:

    def test_opens_account(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_account_payload()
        status, response = RequestGenerator.POST_account(client_key, payload)

        assert status == 201
        account_key = response["account_key"]
        assert response == {"account_key": account_key, "status": "active"}

        received_requests = Mock().retrieve_requests("POST", f"/fee-api/client/{client_key}/fee")
        assert len(received_requests) == 1
        assert received_requests[0]["body"]["json"] == {
            "fee_type": "account_opening",
            "idempotency_key": payload["idempotency_key"],
        }

        sent_token = received_requests[0]["headers"]["INTERNAL-TOKEN"]
        assert len(sent_token) == 1
        assert sent_token[0] != ""

    def test_schema_refuses_malformed_body(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        FeeApiMock.POST_fee(client_key)

        status, response = RequestGenerator.POST_account(client_key, {})
        assert status == 400
        assert response["code"] == "QIT000001"

        payload = PayloadGenerator.create_account_payload()
        payload["campo_que_nao_existe"] = 1
        status, response = RequestGenerator.POST_account(client_key, payload)
        assert status == 400
        assert response["code"] == "QIT000001"

        crooked_fields = [
            ("name", ""),
            ("name", "a" * 256),
            ("document_number", "1234567890"),
            ("document_number", "123456789012"),
            ("document_number", "529.982.247-25"),
            ("document_number", "abcdefghijk"),
            ("idempotency_key", "isto-nao-e-um-uuid"),
            ("idempotency_key", ""),
        ]
        for field, crooked_value in crooked_fields:
            payload = PayloadGenerator.create_account_payload()
            payload[field] = crooked_value

            status, response = RequestGenerator.POST_account(client_key, payload)

            assert status == 400, f"o campo '{field}' aceitou o valor '{crooked_value}'"
            assert response["code"] == "QIT000001"

        received_requests = Mock().retrieve_requests("POST", f"/fee-api/client/{client_key}/fee")
        assert received_requests == []

    def test_refuses_invalid_document_number(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_account_payload(document_number="11122233344")
        status, response = RequestGenerator.POST_account(client_key, payload)
        assert status == 422
        assert response["code"] == "QIT001007"

        received_requests = Mock().retrieve_requests("POST", f"/fee-api/client/{client_key}/fee")
        assert received_requests == []

    def test_refuses_unconfigured_client(self):
        Mock().clear()

        client_key = str(uuid4())
        FeeApiMock.POST_fee(client_key)

        status, response = RequestGenerator.POST_account(client_key, PayloadGenerator.create_account_payload())
        assert status == 404
        assert response["code"] == "QIT001008"

        received_requests = Mock().retrieve_requests("POST", f"/fee-api/client/{client_key}/fee")
        assert received_requests == []

    def test_refuses_second_active_account_with_same_document_number(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        document_number = RandomGenerator.generate_cpf()

        ObjectGenerator.create_account(client_key, document_number=document_number)

        payload = PayloadGenerator.create_account_payload(document_number=document_number)
        status, response = RequestGenerator.POST_account(client_key, payload)
        assert status == 409
        assert response["code"] == "QIT001009"

        received_requests = Mock().retrieve_requests("POST", f"/fee-api/client/{client_key}/fee")
        assert len(received_requests) == 1

    def test_same_document_number_in_another_client_is_allowed(self):
        Mock().clear()
        first_client_key = ObjectGenerator.configure_client()
        second_client_key = ObjectGenerator.configure_client()
        document_number = RandomGenerator.generate_cpf()

        first_account = ObjectGenerator.create_account(first_client_key, document_number=document_number)
        second_account = ObjectGenerator.create_account(second_client_key, document_number=document_number)

        assert first_account["account_key"] != second_account["account_key"]

    def test_retry_with_same_idempotency_key_returns_original_response(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        FeeApiMock.POST_fee(client_key)

        payload = PayloadGenerator.create_account_payload()
        first_status, first_response = RequestGenerator.POST_account(client_key, payload)
        assert first_status == 201

        second_status, second_response = RequestGenerator.POST_account(client_key, payload)
        assert second_status == 201
        assert second_response == first_response

        received_requests = Mock().retrieve_requests("POST", f"/fee-api/client/{client_key}/fee")
        assert len(received_requests) == 1

    def test_fee_api_refusal_changes_nothing(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        document_number = RandomGenerator.generate_cpf()

        FeeApiMock.POST_fee_not_found(client_key)
        payload = PayloadGenerator.create_account_payload(document_number=document_number)
        status, response = RequestGenerator.POST_account(client_key, payload)
        assert status == 502
        assert response["code"] == "QIT001006"

        Mock().clear()
        retry_payload = PayloadGenerator.create_account_payload(document_number=document_number)
        FeeApiMock.POST_fee(client_key)

        status, _response = RequestGenerator.POST_account(client_key, retry_payload)
        assert status == 201

    def test_fee_api_without_answer_changes_nothing(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        document_number = RandomGenerator.generate_cpf()

        FeeApiMock.POST_fee_connection_dropped(client_key)
        payload = PayloadGenerator.create_account_payload(document_number=document_number)
        status, response = RequestGenerator.POST_account(client_key, payload)
        assert status == 502
        assert response["code"] == "QIT001006"

        Mock().clear()
        FeeApiMock.POST_fee(client_key)
        retry_payload = PayloadGenerator.create_account_payload(document_number=document_number)

        status, _response = RequestGenerator.POST_account(client_key, retry_payload)
        assert status == 201

    def test_closed_account_lets_person_open_another(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        document_number = RandomGenerator.generate_cpf()

        old_account_key = ObjectGenerator.create_account(client_key, document_number=document_number)["account_key"]
        ObjectGenerator.close_account(client_key, old_account_key)

        new_account_key = ObjectGenerator.create_account(client_key, document_number=document_number)["account_key"]
        assert new_account_key != old_account_key
