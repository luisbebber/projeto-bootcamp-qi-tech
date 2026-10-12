from errors import QIException


class ClientAlreadyConfigured(QIException):

    code = "QIT001001"

    def __init__(self, client_key) -> None:
        title = "Client already configured"
        http_status = 409
        description = f"Client with key {client_key} is already configured."
        translation = f"O cliente com chave {client_key} já está configurado."
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


class ClientWithoutFees(QIException):

    code = "QIT001004"

    def __init__(self, client_key) -> None:
        title = "Client without fees"
        http_status = 409
        description = f"Client with key {client_key} has no fees registered in the fee-api."
        translation = f"O cliente com chave {client_key} não tem taxas cadastradas na fee-api."
        super().__init__(title, self.code, http_status, description, translation)


class ClientApiUnavailable(QIException):

    code = "QIT001005"

    def __init__(self) -> None:
        title = "Client API unavailable"
        http_status = 502
        description = "The client-api did not answer with a usable response."
        translation = "A client-api não respondeu de forma utilizável. Tente novamente mais tarde."
        super().__init__(title, self.code, http_status, description, translation)


class FeeApiUnavailable(QIException):

    code = "QIT001006"

    def __init__(self) -> None:
        title = "Fee API unavailable"
        http_status = 502
        description = "The fee-api did not answer with a usable response."
        translation = "A fee-api não respondeu de forma utilizável. Tente novamente mais tarde."
        super().__init__(title, self.code, http_status, description, translation)


class InvalidDocumentNumber(QIException):

    code = "QIT001007"

    def __init__(self, document_number) -> None:
        title = "Invalid Document Number"
        http_status = 422
        description = f"The document number {document_number} is not a valid CPF."
        translation = "O CPF informado não é válido."
        super().__init__(title, self.code, http_status, description, translation)


class ClientNotConfigured(QIException):

    code = "QIT001008"

    def __init__(self, client_key) -> None:
        title = "Client not configured"
        http_status = 404
        description = f"Client with key {client_key} is not configured."
        translation = f"O cliente com chave {client_key} não está configurado."
        super().__init__(title, self.code, http_status, description, translation)


class ActiveAccountAlreadyExists(QIException):

    code = "QIT001009"

    def __init__(self, document_number) -> None:
        title = "Active account already exists"
        http_status = 409
        description = f"There is already an active account for the document number {document_number} in this client."
        translation = "Já existe uma conta ativa para este CPF nesta empresa."
        super().__init__(title, self.code, http_status, description, translation)


class NotFoundAccount(QIException):

    code = "QIT001010"

    def __init__(self, account_key) -> None:
        title = "Account not found"
        http_status = 404
        description = f"Account with key {account_key} was not found."
        translation = f"A conta com chave {account_key} não foi encontrada."
        super().__init__(title, self.code, http_status, description, translation)


class AccountAlreadyClosed(QIException):

    code = "QIT001011"

    def __init__(self, account_key) -> None:
        title = "Account already closed"
        http_status = 409
        description = f"Account with key {account_key} is already closed."
        translation = f"A conta com chave {account_key} já está fechada."
        super().__init__(title, self.code, http_status, description, translation)


class ZeroAmount(QIException):

    code = "QIT001012"

    def __init__(self) -> None:
        title = "Zero amount"
        http_status = 422
        description = "The amount must be greater than zero."
        translation = "O valor precisa ser maior que zero."
        super().__init__(title, self.code, http_status, description, translation)


class AccountClosed(QIException):

    code = "QIT001013"

    def __init__(self, account_key) -> None:
        title = "Account closed"
        http_status = 409
        description = f"Account with key {account_key} is closed."
        translation = f"A conta com chave {account_key} está fechada."
        super().__init__(title, self.code, http_status, description, translation)


class AccountHasBalance(QIException):

    code = "QIT001014"

    def __init__(self, account_key) -> None:
        title = "Account has balance"
        http_status = 422
        description = f"Account with key {account_key} has a balance and cannot be closed."
        translation = f"A conta com chave {account_key} ainda tem saldo e não pode ser fechada."
        super().__init__(title, self.code, http_status, description, translation)


class InsufficientBalance(QIException):

    code = "QIT001015"

    def __init__(self, account_key) -> None:
        title = "Insufficient balance"
        http_status = 422
        description = f"Account with key {account_key} does not have enough balance."
        translation = f"A conta com chave {account_key} não tem saldo suficiente."
        super().__init__(title, self.code, http_status, description, translation)


class AccountHasPendingWithdrawal(QIException):

    code = "QIT001016"

    def __init__(self, account_key) -> None:
        title = "Account has a pending withdrawal"
        http_status = 409
        description = f"Account with key {account_key} has a withdrawal waiting for confirmation."
        translation = f"A conta com chave {account_key} tem um saque aguardando confirmação."
        super().__init__(title, self.code, http_status, description, translation)


class NotFoundWithdrawal(QIException):

    code = "QIT001017"

    def __init__(self, withdrawal_key) -> None:
        title = "Withdrawal not found"
        http_status = 404
        description = f"Withdrawal with key {withdrawal_key} was not found."
        translation = f"O saque com chave {withdrawal_key} não foi encontrado."
        super().__init__(title, self.code, http_status, description, translation)


class SameAccountTransfer(QIException):

    code = "QIT001018"

    def __init__(self, account_key) -> None:
        title = "Same account transfer"
        http_status = 422
        description = f"The origin and the destination are the same account ({account_key})."
        translation = "A conta de origem e a de destino são a mesma."
        super().__init__(title, self.code, http_status, description, translation)


class NotFoundDeposit(QIException):

    code = "QIT001019"

    def __init__(self, deposit_key) -> None:
        title = "Deposit not found"
        http_status = 404
        description = f"Deposit with key {deposit_key} was not found."
        translation = f"O depósito com chave {deposit_key} não foi encontrado."
        super().__init__(title, self.code, http_status, description, translation)


class DepositNotPendingFee(QIException):

    code = "QIT001020"

    def __init__(self, deposit_key, deposit_status) -> None:
        title = "Deposit is not pending fee"
        http_status = 409
        description = f"Deposit with key {deposit_key} has status {deposit_status}, and it must be pending_fee."
        translation = f"O depósito com chave {deposit_key} está {deposit_status} e precisa estar pending_fee."
        super().__init__(title, self.code, http_status, description, translation)


class WithdrawalCannotChangeStatus(QIException):

    code = "QIT001021"

    def __init__(self, withdrawal_key, old_status, new_status) -> None:
        title = "Withdrawal cannot change status"
        http_status = 409
        description = f"Withdrawal with key {withdrawal_key} has status {old_status} and cannot go to {new_status}."
        translation = f"O saque com chave {withdrawal_key} está {old_status} e não pode ir para {new_status}."
        super().__init__(title, self.code, http_status, description, translation)
