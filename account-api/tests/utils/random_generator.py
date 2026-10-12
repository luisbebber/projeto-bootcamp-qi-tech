import random


class RandomGenerator:
    @staticmethod
    def generate_cpf():
        cpf = []
        for _ in range(9):
            cpf.append(random.randrange(10))

        for _ in range(2):
            value = 0
            for index, digit in enumerate(cpf):
                value = value + (len(cpf) + 1 - index) * digit

            remainder = value % 11
            if remainder > 1:
                cpf.append(11 - remainder)
            else:
                cpf.append(0)

        cpf_number = ""
        for digit in cpf:
            cpf_number = cpf_number + str(digit)

        return cpf_number

    @staticmethod
    def generate_cnpj():
        cnpj = []
        for _ in range(8):
            cnpj.append(random.randrange(10))

        cnpj.extend([0, 0, 0, 1])

        for _ in range(2):
            value = 0
            for index, digit in enumerate(reversed(cnpj)):
                value = value + digit * (index % 8 + 2)

            check_digit = 11 - value % 11
            if check_digit < 10:
                cnpj.append(check_digit)
            else:
                cnpj.append(0)

        cnpj_number = ""
        for digit in cnpj:
            cnpj_number = cnpj_number + str(digit)

        cnpj_number = (
            f"{cnpj_number[0:2]}.{cnpj_number[2:5]}.{cnpj_number[5:8]}/{cnpj_number[8:12]}-{cnpj_number[12:14]}"
        )

        return cnpj_number
