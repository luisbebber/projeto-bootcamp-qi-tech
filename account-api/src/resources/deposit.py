from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import DepositController
from utils.schema_handler import SchemaHandler

DEFAULT_LIMIT = 10
DEFAULT_PAGE = 0


class DepositResource:

    @SchemaHandler.validate("post_deposit.json")
    def on_post(self, client_key: str, account_key: str, payload: dict) -> JSONResponse:
        controller = DepositController()
        deposit = controller.create(client_key, account_key, payload)

        return JSONResponse(
            content=jsonable_encoder(deposit),
            status_code=http_status.HTTP_201_CREATED,
        )

    @SchemaHandler.validate_query_params("get_deposits.json")
    def on_get_list(self, request: Request) -> JSONResponse:
        controller = DepositController()

        limit = int(request.query_params.get("limit", DEFAULT_LIMIT))
        page = int(request.query_params.get("page", DEFAULT_PAGE))

        filters = {"status": request.query_params.get("status")}

        deposits_page = controller.get_list(limit, page * limit, filters)

        page_envelope = {
            "data": deposits_page["deposits_list_dto"],
            "limit": limit,
            "page": page,
            "is_last_page": deposits_page["is_last_page"],
        }

        return JSONResponse(
            content=jsonable_encoder(page_envelope),
            status_code=http_status.HTTP_200_OK,
        )

    @SchemaHandler.validate("patch_deposit.json")
    def on_patch(self, client_key: str, deposit_key: str, payload: dict) -> JSONResponse:
        controller = DepositController()
        deposit = controller.complete(client_key, deposit_key)

        return JSONResponse(
            content=jsonable_encoder(deposit),
            status_code=http_status.HTTP_200_OK,
        )
