from typing import List

from models import FeeConfiguration


class FeeConfigurationDTO:

    @staticmethod
    def obj_to_simplified_dict(fee_configuration: FeeConfiguration) -> dict:
        dto = dict()
        dto["fee_type"] = fee_configuration.fee_type.enumerator
        dto["amount"] = str(fee_configuration.amount)
        dto["status"] = fee_configuration.status.enumerator

        return dto

    @staticmethod
    def client_key_and_fees(client_key: str, fee_configurations: List[FeeConfiguration]) -> dict:
        dto = dict()
        dto["client_key"] = client_key
        fees = []
        for fee_configuration in fee_configurations:
            fees.append(FeeConfigurationDTO.obj_to_simplified_dict(fee_configuration))
        dto["fees"] = fees

        return dto
