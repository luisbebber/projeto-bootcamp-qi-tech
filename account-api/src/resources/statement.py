from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import StatementController
from utils.schema_handler import SchemaHandler

DEFAULT_LIMIT = 10
DEFAULT_PAGE = 0


class StatementResource:

    @SchemaHandler.validate_query_params("get_statement.json")
    def on_get_list(self, client_key: str, account_key: str, request: Request) -> JSONResponse:
        controller = StatementController()

        limit = int(request.query_params.get("limit", DEFAULT_LIMIT))
        page = int(request.query_params.get("page", DEFAULT_PAGE))

        filters = {
            "from": request.query_params.get("_from"),
            "to": request.query_params.get("_to"),
        }

        statement_page = controller.get_list(client_key, account_key, limit, page * limit, filters)

        page_envelope = {
            "data": statement_page["entries_list_dto"],
            "limit": limit,
            "page": page,
            "is_last_page": statement_page["is_last_page"],
        }

        return JSONResponse(
            content=jsonable_encoder(page_envelope),
            status_code=http_status.HTTP_200_OK,
        )
