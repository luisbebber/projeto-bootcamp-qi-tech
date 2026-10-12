from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import ClientConfigurationController


class ClientConfigurationResource:

    def on_post(self, client_key: str) -> JSONResponse:
        controller = ClientConfigurationController()
        client_configuration = controller.create(client_key)

        return JSONResponse(
            content=jsonable_encoder(client_configuration),
            status_code=http_status.HTTP_201_CREATED,
        )
