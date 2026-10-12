from fastapi import FastAPI

from constants import check_variables
from errors import register_error_handlers
from errors.base_error import error_verification
from middlewares import (
    register_internal_token_middleware,
    register_request_context_middleware,
    register_request_logger_middleware,
    register_session_manager_middleware,
)
from resources import (
    AccountResource,
    ClientConfigurationResource,
    DepositResource,
    HealthCheckResource,
    StatementResource,
    TransferResource,
    WithdrawalResource,
)
from utils.logger import setup_logging


def create_app() -> FastAPI:
    application = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    
    register_session_manager_middleware(application)
    register_internal_token_middleware(application)
    register_request_logger_middleware(application)
    register_request_context_middleware(application)


    health_check_resource = HealthCheckResource()
    client_configuration_resource = ClientConfigurationResource()
    account_resource = AccountResource()
    deposit_resource = DepositResource()
    withdrawal_resource = WithdrawalResource()
    transfer_resource = TransferResource()
    statement_resource = StatementResource()
    

    application.add_api_route("/", health_check_resource.on_get_home, methods=["GET"])
    application.add_api_route(
        "/health_check",
        health_check_resource.on_get_health_check,
        methods=["GET"]
    )

    application.add_api_route(
        "/client/{client_key}",
        client_configuration_resource.on_post,
        methods=["POST"],
    )
    application.add_api_route(
        "/client/{client_key}/account",
        account_resource.on_post,
        methods=["POST"],
    )
    application.add_api_route(
        "/client/{client_key}/account/{account_key}",
        account_resource.on_get_by_key,
        methods=["GET"],
    )
    application.add_api_route(
        "/client/{client_key}/account/{account_key}",
        account_resource.on_patch,
        methods=["PATCH"],
    )
    application.add_api_route(
        "/client/{client_key}/account/{account_key}/deposit",
        deposit_resource.on_post,
        methods=["POST"],
    )
    application.add_api_route(
        "/deposits",
        deposit_resource.on_get_list,
        methods=["GET"],
    )
    application.add_api_route(
        "/client/{client_key}/deposit/{deposit_key}",
        deposit_resource.on_patch,
        methods=["PATCH"],
    )
    application.add_api_route(
        "/client/{client_key}/account/{account_key}/withdrawal",
        withdrawal_resource.on_post,
        methods=["POST"],
    )
    application.add_api_route(
        "/client/{client_key}/withdrawal/{withdrawal_key}",
        withdrawal_resource.on_get_by_key,
        methods=["GET"],
    )
    application.add_api_route(
        "/withdrawals",
        withdrawal_resource.on_get_list,
        methods=["GET"],
    )
    application.add_api_route(
        "/client/{client_key}/withdrawal/{withdrawal_key}",
        withdrawal_resource.on_patch,
        methods=["PATCH"],
    )
    application.add_api_route(
        "/client/{client_key}/transfer",
        transfer_resource.on_post,
        methods=["POST"],
    )
    application.add_api_route(
        "/client/{client_key}/account/{account_key}/statement",
        statement_resource.on_get_list,
        methods=["GET"],
    )
    application.add_api_route(
        "/client/{client_key}/accounts",
        account_resource.on_get_list,
        methods=["GET"],
    )

    register_error_handlers(application)

    return application


def main() -> FastAPI:
    check_variables()
    error_verification()
    setup_logging()

    return create_app()


app = main()
