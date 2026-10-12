from datetime import date, datetime, time
from decimal import Decimal

from controllers.base_controller import BaseController
from dtos import SpendingDTO
from errors import ClientNotConfigured, InvalidParameter
from repositories import ClientConfigurationRepository, FeeRepository

ZERO = Decimal("0.00")


class SpendingController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.client_configuration_repository = ClientConfigurationRepository(self.context)
        self.fee_repository = FeeRepository(self.context)

    def get_by_client_key(self, client_key: str, filters: dict) -> dict:
        self.logger.debug(f"Somando o gasto da empresa {client_key}")

        from_date = self._parse_date("_from", filters["from"])
        to_date = self._parse_date("_to", filters["to"])

        if from_date > to_date:
            raise InvalidParameter(f"_from ({from_date.isoformat()}) is after _to ({to_date.isoformat()})")

        if self.client_configuration_repository.get_by_client_key(client_key) is None:
            raise ClientNotConfigured(client_key)

        from_datetime = datetime.combine(from_date, time.min)
        to_datetime = datetime.combine(to_date, time.max)
        rows = self.fee_repository.sum_by_month_and_fee_type(client_key, from_datetime, to_datetime)

        paid_amount = ZERO
        payable_amount = ZERO
        for _month, _fee_type, is_paid, amount in rows:
            if is_paid:
                paid_amount += amount
            else:
                payable_amount += amount

        months = self._group_by_month(rows)

        return SpendingDTO.client_key_and_spending(client_key, months, paid_amount, payable_amount)

    def _group_by_month(self, rows: list) -> list:
        amounts_by_month = {}
        for month, fee_type, _is_paid, amount in rows:
            month_label = month.strftime("%Y-%m")

            if month_label not in amounts_by_month:
                amounts_by_month[month_label] = {}

            amounts_by_fee_type = amounts_by_month[month_label]
            if fee_type not in amounts_by_fee_type:
                amounts_by_fee_type[fee_type] = ZERO
            amounts_by_fee_type[fee_type] += amount

        months = []
        for month_label, amounts_by_fee_type in amounts_by_month.items():
            fees = []
            for fee_type, amount in amounts_by_fee_type.items():
                fees.append({"fee_type": fee_type, "amount": amount})
            months.append({"month": month_label, "fees": fees})

        return months

    def _parse_date(self, parameter_name: str, raw_date: str) -> date:
        try:
            return date.fromisoformat(raw_date)
        except ValueError:
            raise InvalidParameter(f"{parameter_name} ({raw_date}) is not a real date")
