from decimal import Decimal
from uuid import uuid4

from database import Context
from models import ClientConfiguration, FeeConfiguration, FeeConfigurationStatus, FeeConfigurationStatusEvent, FeeType

TWO_PLACES = Decimal("0.01")


class FeeConfigurationRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, client_configuration: ClientConfiguration, fee_type_enumerator: str, amount: str) -> FeeConfiguration:
        fee_configuration = FeeConfiguration()

        fee_configuration.fee_configuration_key = str(uuid4())
        fee_configuration.client_configuration = client_configuration
        fee_configuration.fee_type = self.get_fee_type(fee_type_enumerator)

        fee_configuration.amount = Decimal(amount).quantize(TWO_PLACES)

        self.update_status(fee_configuration, FeeConfigurationStatus.ACTIVE)

        self.session.add(fee_configuration)
        return fee_configuration

    def update_status(self, fee_configuration: FeeConfiguration, new_status_enumerator: str) -> None:
        new_status = self.get_status(new_status_enumerator)
        fee_configuration.status = new_status

        new_status_event = FeeConfigurationStatusEvent()
        new_status_event.status = new_status

        fee_configuration.status_events.append(new_status_event)

    def list_active_by_client_key(self, client_key: str) -> list:
        return (
            self.session.query(FeeConfiguration)
            .join(FeeConfiguration.status)
            .filter(FeeConfiguration.client_key == client_key)
            .filter(FeeConfigurationStatus.enumerator == FeeConfigurationStatus.ACTIVE)
            .order_by(FeeConfiguration.fee_type_id)
            .all()
        )

    def list_active_by_client_key_for_update(self, client_key: str) -> list:
        return (
            self.session.query(FeeConfiguration)
            .join(FeeConfiguration.status)
            .filter(FeeConfiguration.client_key == client_key)
            .filter(FeeConfigurationStatus.enumerator == FeeConfigurationStatus.ACTIVE)
            .order_by(FeeConfiguration.id)
            .with_for_update()
            .all()
        )

    def get_active_by_client_key_and_fee_type(self, client_key: str, fee_type_enumerator: str) -> FeeConfiguration:
        return (
            self.session.query(FeeConfiguration)
            .join(FeeConfiguration.status)
            .join(FeeConfiguration.fee_type)
            .filter(FeeConfiguration.client_key == client_key)
            .filter(FeeType.enumerator == fee_type_enumerator)
            .filter(FeeConfigurationStatus.enumerator == FeeConfigurationStatus.ACTIVE)
            .first()
        )

    def get_fee_type(self, enumerator: str) -> FeeType:
        return (
            self.session.query(FeeType)
            .filter(FeeType.enumerator == enumerator)
            .first()
        )

    def get_status(self, enumerator: str) -> FeeConfigurationStatus:
        return (
            self.session.query(FeeConfigurationStatus)
            .filter(FeeConfigurationStatus.enumerator == enumerator)
            .first()
        )
