from models import Transfer


class TransferDTO:

    @staticmethod
    def only_obj_key(transfer: Transfer) -> dict:
        dto = dict()
        dto["transfer_key"] = transfer.transfer_key

        return dto
