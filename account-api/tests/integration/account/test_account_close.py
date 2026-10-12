from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator
from tests.utils.checks import values_of
from tests.utils.mock_generator import FeeApiMock, SpiApiMock
from tests.utils.mock_utils import Mock


class TestAccountClose:

    def test_closes_account(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]

        payload = PayloadGenerator.create_account_status_payload()
        status, response = RequestGenerator.PATCH_account(client_key, account_key, payload)
        assert status == 200
        assert response == {"account_key": account_key, "status": "closed"}

        status, response = RequestGenerator.GET_account(client_key, account_key)
        assert status == 200
        assert response["status"] == "closed"
        assert values_of(response["status_events"], "status") == ["active", "closed"]

    def test_refuses_closing_already_closed_account(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]
        ObjectGenerator.close_account(client_key, account_key)

        payload = PayloadGenerator.create_account_status_payload()
        status, response = RequestGenerator.PATCH_account(client_key, account_key, payload)
        assert status == 409
        assert response["code"] == "QIT001011"

        _status, response = RequestGenerator.GET_account(client_key, account_key)
        assert values_of(response["status_events"], "status") == ["active", "closed"]

    def test_refuses_unknown_account_key(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()

        payload = PayloadGenerator.create_account_status_payload()
        status, response = RequestGenerator.PATCH_account(client_key, "00000000-0000-0000-0000-000000000000", payload)
        assert status == 404
        assert response["code"] == "QIT001010"

    def test_refuses_account_of_another_client(self):
        Mock().clear()
        owner_client_key = ObjectGenerator.configure_client()
        other_client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(owner_client_key)["account_key"]

        payload = PayloadGenerator.create_account_status_payload()
        status, response = RequestGenerator.PATCH_account(other_client_key, account_key, payload)
        assert status == 404
        assert response["code"] == "QIT001010"

        _status, response = RequestGenerator.GET_account(owner_client_key, account_key)
        assert response["status"] == "active"

    def test_schema_refuses_malformed_body(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]

        crooked_payloads = [
            {},
            {"status": "active"},
            {"status": "CLOSED"},
            {"status": 1},
            {"status": "closed", "campo_que_nao_existe": 1},
        ]
        for payload in crooked_payloads:
            status, response = RequestGenerator.PATCH_account(client_key, account_key, payload)

            assert status == 400, f"o corpo {payload} foi aceito"
            assert response["code"] == "QIT000001"

        _status, response = RequestGenerator.GET_account(client_key, account_key)
        assert response["status"] == "active"

    def test_refuses_closing_account_with_balance(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]
        ObjectGenerator.create_deposit(client_key, account_key, amount="10.00")

        payload = PayloadGenerator.create_account_status_payload()
        status, response = RequestGenerator.PATCH_account(client_key, account_key, payload)
        assert status == 422
        assert response["code"] == "QIT001014"

        _status, response = RequestGenerator.GET_account(client_key, account_key)
        assert response["status"] == "active"
        assert response["balance"] == "10.00"

    def test_refuses_closing_account_with_pending_withdrawal(self):
        Mock().clear()
        client_key = ObjectGenerator.configure_client()
        account_key = ObjectGenerator.create_account(client_key)["account_key"]
        ObjectGenerator.create_deposit(client_key, account_key, amount="50.00")

        FeeApiMock.POST_fee(client_key)
        SpiApiMock.POST_withdrawal_pending()
        payload = PayloadGenerator.create_withdrawal_payload(amount="50.00")
        status, _response = RequestGenerator.POST_withdrawal(client_key, account_key, payload)
        assert status == 202

        payload = PayloadGenerator.create_account_status_payload()
        status, response = RequestGenerator.PATCH_account(client_key, account_key, payload)
        assert status == 409
        assert response["code"] == "QIT001016"

        _status, response = RequestGenerator.GET_account(client_key, account_key)
        assert response["status"] == "active"
