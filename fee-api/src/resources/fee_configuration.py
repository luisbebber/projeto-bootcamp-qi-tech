from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import FeeConfigurationController
from utils.schema_handler import SchemaHandler


class FeeConfigurationResource:

    @SchemaHandler.validate("post_fee_configuration.json")
    def on_post(self, client_key: str, payload: dict) -> JSONResponse:
        controller = FeeConfigurationController()
        fees = controller.create(client_key, payload)

        return JSONResponse(
            content=jsonable_encoder(fees),
            status_code=http_status.HTTP_201_CREATED,
        )

    def on_get(self, client_key: str) -> JSONResponse:
        controller = FeeConfigurationController()
        fees = controller.get_by_client_key(client_key)

        return JSONResponse(
            content=jsonable_encoder(fees),
            status_code=http_status.HTTP_200_OK,
        )

    @SchemaHandler.validate("patch_fee_configuration.json")
    def on_patch(self, client_key: str, payload: dict) -> JSONResponse:
        controller = FeeConfigurationController()
        fees = controller.update(client_key, payload)

        return JSONResponse(
            content=jsonable_encoder(fees),
            status_code=http_status.HTTP_200_OK,
        )
