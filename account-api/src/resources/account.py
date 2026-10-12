from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import AccountController
from utils.schema_handler import SchemaHandler

DEFAULT_LIMIT = 10
DEFAULT_PAGE = 0


class AccountResource:

    @SchemaHandler.validate("post_account.json")
    def on_post(self, client_key: str, payload: dict) -> JSONResponse:
        controller = AccountController()
        account = controller.create(client_key, payload)

        return JSONResponse(
            content=jsonable_encoder(account),
            status_code=http_status.HTTP_201_CREATED,
        )

    @SchemaHandler.validate("patch_account.json")
    def on_patch(self, client_key: str, account_key: str, payload: dict) -> JSONResponse:
        controller = AccountController()
        account = controller.close(client_key, account_key)

        return JSONResponse(
            content=jsonable_encoder(account),
            status_code=http_status.HTTP_200_OK,
        )

    @SchemaHandler.validate_query_params("get_accounts.json")
    def on_get_list(self, client_key: str, request: Request) -> JSONResponse:
        controller = AccountController()

        limit = int(request.query_params.get("limit", DEFAULT_LIMIT))
        page = int(request.query_params.get("page", DEFAULT_PAGE))

        accounts_page = controller.get_list(client_key, limit, page * limit)

        page_envelope = {
            "data": accounts_page["accounts_list_dto"],
            "limit": limit,
            "page": page,
            "is_last_page": accounts_page["is_last_page"],
        }

        return JSONResponse(
            content=jsonable_encoder(page_envelope),
            status_code=http_status.HTTP_200_OK,
        )

    def on_get_by_key(self, client_key: str, account_key: str) -> JSONResponse:
        controller = AccountController()
        account = controller.get_by_key(client_key, account_key)

        return JSONResponse(
            content=jsonable_encoder(account),
            status_code=http_status.HTTP_200_OK,
        )
