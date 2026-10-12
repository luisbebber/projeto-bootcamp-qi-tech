from models import Fee


class FeeDTO:

    @staticmethod
    def only_obj_key(fee: Fee) -> dict:
        dto = dict()
        dto["fee_key"] = fee.fee_key

        return dto

    @staticmethod
    def obj_to_dict(fee: Fee) -> dict:
        dto = dict()
        dto["fee_key"] = fee.fee_key
        dto["client_key"] = fee.client_key
        dto["fee_type"] = fee.fee_type.enumerator
        dto["amount"] = str(fee.amount)
        dto["idempotency_key"] = fee.idempotency_key
        dto["charge_key"] = None
        if fee.charge is not None:
            dto["charge_key"] = fee.charge.charge_key
        dto["created_at"] = fee.created_at.isoformat()

        return dto
