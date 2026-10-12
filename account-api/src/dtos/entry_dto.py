from typing import List

from models import Entry


class EntryDTO:

    @staticmethod
    def obj_to_simplified_dict(entry: Entry) -> dict:
        dto = dict()
        dto["type"] = entry.type.enumerator
        dto["amount"] = str(entry.amount)
        dto["balance_after"] = str(entry.balance_after)
        dto["created_at"] = entry.created_at.isoformat()

        return dto

    @staticmethod
    def list_obj_to_list_dict(entries_list: List[Entry]) -> List[dict]:
        entries_list_dto = []

        for entry in entries_list:
            entries_list_dto.append(EntryDTO.obj_to_simplified_dict(entry))

        return entries_list_dto
