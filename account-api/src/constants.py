import os


SERVICE_ROOT = os.path.abspath(os.path.dirname(__file__))

SCHEMA_PATH = os.path.join(SERVICE_ROOT, "schemas")

APP_ENV = os.environ.get("APP_ENV", "local")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "bootcamp-api")

DATABASE_URL = os.environ.get("DATABASE_URL")
INTERNAL_TOKEN = os.environ.get("INTERNAL_TOKEN")

CLIENT_API_URL = os.environ.get("CLIENT_API_URL", "http://localhost:1080/client-api")
CLIENT_API_INTERNAL_TOKEN = os.environ.get("CLIENT_API_INTERNAL_TOKEN", "default_token")
FEE_API_URL = os.environ.get("FEE_API_URL", "http://localhost:1080/fee-api")
FEE_API_INTERNAL_TOKEN = os.environ.get("FEE_API_INTERNAL_TOKEN", "default_token")
SPI_API_URL = os.environ.get("SPI_API_URL", "http://localhost:1080/spi-api")
SPI_API_INTERNAL_TOKEN = os.environ.get("SPI_API_INTERNAL_TOKEN", "default_token")

CLIENT_API_TIMEOUT = int(os.environ.get("CLIENT_API_TIMEOUT", "5"))
FEE_API_TIMEOUT = int(os.environ.get("FEE_API_TIMEOUT", "5"))
SPI_API_TIMEOUT = int(os.environ.get("SPI_API_TIMEOUT", "5"))


class FeeType:

    TRANSFER = "transfer"
    ACCOUNT_OPENING = "account_opening"


BYPASS_ENDPOINTS = [
    "/",
    "/health_check",
]

REQUIRED_VARIABLES = ["DATABASE_URL", "INTERNAL_TOKEN"]


def check_variables():
    missing = []
    for name in REQUIRED_VARIABLES:
        if not globals().get(name):
            missing.append(name)

    if missing:
        raise EnvironmentError(
            f"Faltam variáveis de ambiente: {', '.join(missing)}. "
            "Rodando com 'docker compose up' elas já vêm preenchidas. "
            "Fora do Docker, copie o .env.example para .env."
        )
