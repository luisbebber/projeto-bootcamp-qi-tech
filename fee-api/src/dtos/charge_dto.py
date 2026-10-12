from models import Charge


class ChargeDTO:

    @staticmethod
    def obj_to_dict(charge: Charge) -> dict:
        dto = dict()
        dto["charge_key"] = charge.charge_key
        dto["month"] = charge.month.strftime("%Y-%m")
        dto["amount"] = str(charge.amount)
        dto["status"] = charge.status.enumerator

        return dto

    @staticmethod
    def obj_to_simplified_dict(charge: Charge) -> dict:
        dto = ChargeDTO.obj_to_dict(charge)
        dto["client_key"] = charge.client_key
        dto["created_at"] = charge.created_at.isoformat()

        return dto

    @staticmethod
    def key_and_status(charge: Charge) -> dict:
        dto = dict()
        dto["charge_key"] = charge.charge_key
        dto["status"] = charge.status.enumerator

        return dto

    @staticmethod
    def list_obj_to_list_dict(charges: list) -> list:
        dtos = []
        for charge in charges:
            dtos.append(ChargeDTO.obj_to_simplified_dict(charge))

        return dtos
