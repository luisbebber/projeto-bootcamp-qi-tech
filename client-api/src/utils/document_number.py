CNPJ_LENGTH = 14

FIRST_CHECK_DIGIT_WEIGHTS = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
SECOND_CHECK_DIGIT_WEIGHTS = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


def is_valid_cnpj(document_number: str) -> bool:
    if len(document_number) != CNPJ_LENGTH:
        return False

    values = []
    for character in document_number:
        values.append(ord(character) - 48)

    all_values_are_equal = True
    for value in values:
        if value != values[0]:
            all_values_are_equal = False
            break

    if all_values_are_equal:
        return False

    check_digit_rules = [
        (12, FIRST_CHECK_DIGIT_WEIGHTS),
        (13, SECOND_CHECK_DIGIT_WEIGHTS),
    ]

    for position, weights in check_digit_rules:
        total = 0

        for index in range(position):
            total = total + values[index] * weights[index]

        remainder = total % 11

        if remainder < 2:
            expected_digit = 0
        else:
            expected_digit = 11 - remainder

        if values[position] != expected_digit:
            return False

    return True
