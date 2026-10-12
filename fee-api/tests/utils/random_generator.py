import random


class RandomGenerator:
    @staticmethod
    def generate_cpf():
        cpf = []
        for _ in range(9):
            cpf.append(random.randrange(10))

        for _ in range(2):
            value = 0
            for i, digit in enumerate(cpf):
                value += (len(cpf) + 1 - i) * digit
            value = value % 11

            if value > 1:
                cpf.append(11 - value)
            else:
                cpf.append(0)

        cpf_number = ""
        for digit in cpf:
            cpf_number += str(digit)

        cpf_number = f"{cpf_number[0:3]}.{cpf_number[3:6]}.{cpf_number[6:9]}-{cpf_number[9:11]}"
        return cpf_number

    @staticmethod
    def generate_cnpj():
        cnpj = []
        for _ in range(8):
            cnpj.append(random.randrange(10))
        cnpj = cnpj + [0, 0, 0, 1]

        for _ in range(2):
            value = 0
            for i, digit in enumerate(reversed(cnpj)):
                value += digit * (i % 8 + 2)

            check_digit = 11 - value % 11
            if check_digit < 10:
                cnpj.append(check_digit)
            else:
                cnpj.append(0)

        cnpj_number = ""
        for digit in cnpj:
            cnpj_number += str(digit)

        cnpj_number = (
            f"{cnpj_number[0:2]}.{cnpj_number[2:5]}.{cnpj_number[5:8]}/{cnpj_number[8:12]}-{cnpj_number[12:14]}"
        )

        return cnpj_number
