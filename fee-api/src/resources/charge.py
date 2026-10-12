from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import ChargeController
from utils.schema_handler import SchemaHandler

DEFAULT_LIMIT = 10
DEFAULT_PAGE = 0


class ChargeResource:

    @SchemaHandler.validate("post_charge.json")
    def on_post(self, client_key: str, payload: dict) -> JSONResponse:
        controller = ChargeController()
        charge = controller.create(client_key, payload)

        return JSONResponse(
            content=jsonable_encoder(charge),
            status_code=http_status.HTTP_201_CREATED,
        )

    @SchemaHandler.validate("patch_charge.json")
    def on_patch(self, client_key: str, charge_key: str, payload: dict) -> JSONResponse:
        controller = ChargeController()
        charge = controller.update(client_key, charge_key, payload)

        return JSONResponse(
            content=jsonable_encoder(charge),
            status_code=http_status.HTTP_200_OK,
        )

    def on_get_by_key(self, client_key: str, charge_key: str) -> JSONResponse:
        controller = ChargeController()
        charge = controller.get_by_key(client_key, charge_key)

        return JSONResponse(
            content=jsonable_encoder(charge),
            status_code=http_status.HTTP_200_OK,
        )

    @SchemaHandler.validate_query_params("get_charges.json")
    def on_get_list(self, client_key: str, request: Request) -> JSONResponse:
        controller = ChargeController()

        limit = int(request.query_params.get("limit", DEFAULT_LIMIT))
        page = int(request.query_params.get("page", DEFAULT_PAGE))

        filters = {"status": request.query_params.get("status")}

        charges_page = controller.get_list(client_key, limit, page * limit, filters)

        page_envelope = {
            "data": charges_page["charges_list_dto"],
            "limit": limit,
            "page": page,
            "is_last_page": charges_page["is_last_page"],
        }

        return JSONResponse(
            content=jsonable_encoder(page_envelope),
            status_code=http_status.HTTP_200_OK,
        )
