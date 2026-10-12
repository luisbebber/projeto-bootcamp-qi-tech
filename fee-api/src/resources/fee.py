from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import FeeController
from utils.schema_handler import SchemaHandler


class FeeResource:

    @SchemaHandler.validate("post_fee.json")
    def on_post(self, client_key: str, payload: dict) -> JSONResponse:
        controller = FeeController()
        fee = controller.create(client_key, payload)

        return JSONResponse(
            content=jsonable_encoder(fee),
            status_code=http_status.HTTP_201_CREATED,
        )

    def on_get_by_key(self, client_key: str, fee_key: str) -> JSONResponse:
        controller = FeeController()
        fee = controller.get_by_key(client_key, fee_key)

        return JSONResponse(
            content=jsonable_encoder(fee),
            status_code=http_status.HTTP_200_OK,
        )
