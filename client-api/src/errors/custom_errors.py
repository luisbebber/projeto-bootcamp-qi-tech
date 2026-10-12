from errors import QIException


class InvalidDocumentNumber(QIException):

    code = "QIT001001"

    def __init__(self, document_number) -> None:
        title = "Invalid Document Number"
        http_status = 422
        description = f"The document number {document_number} is not a valid CNPJ."
        translation = "O CNPJ informado não é válido."
        super().__init__(title, self.code, http_status, description, translation)


class DuplicatedClient(QIException):

    code = "QIT001002"

    def __init__(self, document_number, operation) -> None:
        title = "Client already registered"
        http_status = 409
        description = f"There is already a client with the document number {document_number} and the operation {operation}."
        translation = "Já existe um cadastro com este CNPJ e esta operação."
        super().__init__(title, self.code, http_status, description, translation)


class NotFoundClient(QIException):

    code = "QIT001003"

    def __init__(self, client_key) -> None:
        title = "Client not found"
        http_status = 404
        description = f"Client with key {client_key} was not found."
        translation = f"O cliente com chave {client_key} não foi encontrado."
        super().__init__(title, self.code, http_status, description, translation)


class ClientAlreadyInStatus(QIException):

    code = "QIT001004"

    def __init__(self, client_key, status) -> None:
        title = "Client already in this status"
        http_status = 409
        description = f"Client with key {client_key} is already {status}."
        translation = f"O cliente com chave {client_key} já está com o status {status}."
        super().__init__(title, self.code, http_status, description, translation)
