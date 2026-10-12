from tests.utils.random_generator import RandomGenerator


class PayloadGenerator:

    @staticmethod
    def create_client_payload(
        name: str = None,
        document_number: str = None,
        operation: str = None,
    ) -> dict:
        if name is None:
            name = "Uber do Brasil Tecnologia Ltda"

        if document_number is None:
            document_number = RandomGenerator.generate_cnpj()

        if operation is None:
            operation = RandomGenerator.generate_operation()

        return {
            "name": name,
            "document_number": document_number,
            "operation": operation,
        }

    @staticmethod
    def create_client_status_payload(status: str = "inactivated") -> dict:
        return {"status": status}
