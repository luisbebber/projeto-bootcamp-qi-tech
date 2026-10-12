from datetime import datetime

from controllers.base_controller import BaseController
from dtos import EntryDTO
from errors import InvalidParameter, NotFoundAccount
from repositories import AccountRepository, EntryRepository


class StatementController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.entry_repository = EntryRepository(self.context)

    def get_list(self, client_key: str, account_key: str, limit: int, offset: int, filters: dict) -> dict:
        self.logger.debug(f"Listando o extrato da conta {account_key} da empresa {client_key}")

        from_datetime = self._parse_datetime("_from", filters.get("from"))
        to_datetime = self._parse_datetime("_to", filters.get("to"))

        if from_datetime is not None and to_datetime is not None and from_datetime > to_datetime:
            raise InvalidParameter(f"_from ({from_datetime.isoformat()}) is after _to ({to_datetime.isoformat()})")

        account = self.account_repository.get_by_key(client_key, account_key)
        if account is None:
            raise NotFoundAccount(account_key)

        entries_list = self.entry_repository.list_page(account, limit, offset, from_datetime, to_datetime)

        is_last_page = True
        if len(entries_list) > limit:
            is_last_page = False
            entries_list = entries_list[:-1]

        return {
            "entries_list_dto": EntryDTO.list_obj_to_list_dict(entries_list),
            "is_last_page": is_last_page,
        }

    def _parse_datetime(self, parameter_name: str, raw_datetime: str) -> datetime:
        if raw_datetime is None:
            return None

        try:
            return datetime.fromisoformat(raw_datetime)
        except ValueError:
            raise InvalidParameter(f"{parameter_name} ({raw_datetime}) is not a real date and time")
