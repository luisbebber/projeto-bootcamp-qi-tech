from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import WithdrawalController
from utils.schema_handler import SchemaHandler

DEFAULT_LIMIT = 10
DEFAULT_PAGE = 0


class WithdrawalResource:

    @SchemaHandler.validate("post_withdrawal.json")
    def on_post(self, client_key: str, account_key: str, payload: dict) -> JSONResponse:
        controller = WithdrawalController()
        withdrawal = controller.create(client_key, account_key, payload)

        if withdrawal["status"] == "pending_confirmation":
            response_status = http_status.HTTP_202_ACCEPTED
        else:
            response_status = http_status.HTTP_201_CREATED

        return JSONResponse(
            content=jsonable_encoder(withdrawal),
            status_code=response_status,
        )

    def on_get_by_key(self, client_key: str, withdrawal_key: str) -> JSONResponse:
        controller = WithdrawalController()
        withdrawal = controller.get_by_key(client_key, withdrawal_key)

        return JSONResponse(
            content=jsonable_encoder(withdrawal),
            status_code=http_status.HTTP_200_OK,
        )

    @SchemaHandler.validate_query_params("get_withdrawals.json")
    def on_get_list(self, request: Request) -> JSONResponse:
        controller = WithdrawalController()

        limit = int(request.query_params.get("limit", DEFAULT_LIMIT))
        page = int(request.query_params.get("page", DEFAULT_PAGE))

        filters = {"status": request.query_params.get("status")}

        withdrawals_page = controller.get_list(limit, page * limit, filters)

        page_envelope = {
            "data": withdrawals_page["withdrawals_list_dto"],
            "limit": limit,
            "page": page,
            "is_last_page": withdrawals_page["is_last_page"],
        }

        return JSONResponse(
            content=jsonable_encoder(page_envelope),
            status_code=http_status.HTTP_200_OK,
        )

    @SchemaHandler.validate("patch_withdrawal.json")
    def on_patch(self, client_key: str, withdrawal_key: str, payload: dict) -> JSONResponse:
        controller = WithdrawalController()
        withdrawal = controller.resolve(client_key, withdrawal_key, payload["status"])

        return JSONResponse(
            content=jsonable_encoder(withdrawal),
            status_code=http_status.HTTP_200_OK,
        )
