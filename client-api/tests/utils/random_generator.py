import random
import string
from uuid import uuid4


class RandomGenerator:
    @staticmethod
    def generate_cnpj():
        alphabet = string.ascii_uppercase + string.digits
        cnpj = []
        for _ in range(8):
            cnpj.append(random.choice(alphabet))
        cnpj = cnpj + ["0", "0", "0", "1"]

        for _ in range(2):
            value = 0
            for i, c in enumerate(reversed(cnpj)):
                value += (ord(c) - 48) * (i % 8 + 2)

            digit = 11 - value % 11
            if digit < 10:
                cnpj.append(str(digit))
            else:
                cnpj.append("0")

        return "".join(cnpj)

    @staticmethod
    def generate_operation():
        return f"operation-{uuid4().hex[:12]}"
