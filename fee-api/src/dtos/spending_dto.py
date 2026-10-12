from decimal import Decimal
from typing import List


class SpendingDTO:

    @staticmethod
    def client_key_and_spending(client_key: str, months: List[dict], paid_amount: Decimal, payable_amount: Decimal) -> dict:
        dto = dict()
        dto["client_key"] = client_key

        dto["months"] = []
        for month in months:
            fees = []
            for fee in month["fees"]:
                fees.append({"fee_type": fee["fee_type"], "amount": str(fee["amount"])})
            dto["months"].append({"month": month["month"], "fees": fees})

        dto["paid_amount"] = str(paid_amount)
        dto["payable_amount"] = str(payable_amount)

        return dto
