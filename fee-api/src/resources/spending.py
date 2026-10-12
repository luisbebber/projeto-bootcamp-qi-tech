from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import SpendingController
from utils.schema_handler import SchemaHandler


class SpendingResource:

    @SchemaHandler.validate_query_params("get_spending.json")
    def on_get(self, client_key: str, request: Request) -> JSONResponse:
        controller = SpendingController()

        filters = {
            "from": request.query_params.get("_from"),
            "to": request.query_params.get("_to"),
        }
        spending = controller.get_by_client_key(client_key, filters)

        return JSONResponse(
            content=jsonable_encoder(spending),
            status_code=http_status.HTTP_200_OK,
        )
