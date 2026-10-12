from errors import QIException


class ClientAlreadyConfigured(QIException):

    code = "QIT001001"

    def __init__(self, client_key) -> None:
        title = "Client already configured"
        http_status = 409
        description = f"Client with key {client_key} already has fees registered."
        translation = f"O cliente com chave {client_key} já tem taxas cadastradas."
        super().__init__(title, self.code, http_status, description, translation)


class ClientNotFound(QIException):

    code = "QIT001002"

    def __init__(self, client_key) -> None:
        title = "Client not found"
        http_status = 404
        description = f"Client with key {client_key} was not found."
        translation = f"O cliente com chave {client_key} não foi encontrado."
        super().__init__(title, self.code, http_status, description, translation)


class ClientNotActive(QIException):

    code = "QIT001003"

    def __init__(self, client_key, client_status) -> None:
        title = "Client not active"
        http_status = 409
        description = f"Client with key {client_key} has status {client_status}, and it must be active."
        translation = f"O cliente com chave {client_key} está {client_status} e precisa estar active."
        super().__init__(title, self.code, http_status, description, translation)


class ClientNotConfigured(QIException):

    code = "QIT001005"

    def __init__(self, client_key) -> None:
        title = "Client not configured"
        http_status = 404
        description = f"Client with key {client_key} has no fees registered."
        translation = f"O cliente com chave {client_key} não tem taxas cadastradas."
        super().__init__(title, self.code, http_status, description, translation)


class NotFoundFee(QIException):

    code = "QIT001006"

    def __init__(self, fee_key) -> None:
        title = "Fee not found"
        http_status = 404
        description = f"Fee with key {fee_key} was not found."
        translation = f"A taxa com chave {fee_key} não foi encontrada."
        super().__init__(title, self.code, http_status, description, translation)


class FeeConfigurationNotChanged(QIException):

    code = "QIT001007"

    def __init__(self, client_key) -> None:
        title = "Fee configuration not changed"
        http_status = 409
        description = f"None of the amounts differs from the active fees of client {client_key}."
        translation = f"Nenhum dos valores é diferente das taxas ativas do cliente {client_key}."
        super().__init__(title, self.code, http_status, description, translation)


class MonthNotEnded(QIException):

    code = "QIT001008"

    def __init__(self, month) -> None:
        title = "Month not ended"
        http_status = 422
        description = f"Month {month} has not ended yet, so it cannot be closed."
        translation = f"O mês {month} ainda não terminou e não pode ser fechado."
        super().__init__(title, self.code, http_status, description, translation)


class MonthBeforeConfiguration(QIException):

    code = "QIT001009"

    def __init__(self, month, client_key) -> None:
        title = "Month before configuration"
        http_status = 422
        description = f"Month {month} is before client {client_key} was configured."
        translation = f"O mês {month} é anterior ao cadastro do cliente {client_key}."
        super().__init__(title, self.code, http_status, description, translation)


class NotFoundCharge(QIException):

    code = "QIT001010"

    def __init__(self, charge_key) -> None:
        title = "Charge not found"
        http_status = 404
        description = f"Charge with key {charge_key} was not found."
        translation = f"A cobrança com chave {charge_key} não foi encontrada."
        super().__init__(title, self.code, http_status, description, translation)


class ChargeNotPending(QIException):

    code = "QIT001011"

    def __init__(self, charge_key, charge_status) -> None:
        title = "Charge not pending payment"
        http_status = 409
        description = f"Charge with key {charge_key} has status {charge_status}, and it must be pending_payment."
        translation = f"A cobrança com chave {charge_key} está {charge_status} e precisa estar pending_payment."
        super().__init__(title, self.code, http_status, description, translation)


class MonthAlreadyClosed(QIException):

    code = "QIT001012"

    def __init__(self, month, client_key) -> None:
        title = "Month already closed"
        http_status = 409
        description = f"Month {month} of client {client_key} already has a charge."
        translation = f"O mês {month} do cliente {client_key} já tem uma cobrança."
        super().__init__(title, self.code, http_status, description, translation)


class ClientApiUnavailable(QIException):

    code = "QIT001004"

    def __init__(self) -> None:
        title = "Client API unavailable"
        http_status = 502
        description = "The client-api did not answer with a usable response."
        translation = "A client-api não respondeu de forma utilizável. Tente novamente mais tarde."
        super().__init__(title, self.code, http_status, description, translation)
