from models import ClientConfiguration


class ClientConfigurationDTO:

    @staticmethod
    def only_obj_key(client_configuration: ClientConfiguration) -> dict:
        dto = dict()
        dto["client_key"] = client_configuration.client_key

        return dto
