class ResponseUtils:

    @staticmethod
    def status_trail(client: dict) -> list:
        trail = []

        for status_event in client["status_events"]:
            trail.append(status_event["status"])

        return trail

    @staticmethod
    def client_keys(clients: list) -> list:
        client_keys = []

        for client in clients:
            client_keys.append(client["client_key"])

        return client_keys

    @staticmethod
    def client_keys_and_statuses(clients: list) -> list:
        pairs = []

        for client in clients:
            pairs.append((client["client_key"], client["status"]))

        return pairs
