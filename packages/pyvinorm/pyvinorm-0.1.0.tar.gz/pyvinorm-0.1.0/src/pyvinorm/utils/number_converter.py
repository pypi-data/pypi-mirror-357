class NumberConverter:
    """
    Convert numbers for spoken form.
    """

    DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

    @staticmethod
    def _convert_number_lt_hundred(number: str):
        # n < 10
        if len(number) == 1:
            return NumberConverter.DIGITS[int(number)]

        assert len(number) == 2
        # 10 <= n < 20
        if number[0] == "1":
            if number[1] == "0":
                return "mười"
            elif number[1] == "5":
                return "mười lăm"
            else:
                return "mười " + NumberConverter.DIGITS[int(number[1])]

        # 20 <= n < 99
        result = NumberConverter.DIGITS[int(number[0])] + " mươi"
        match number[1]:
            # n = 20, 30, ..., 90
            case "0":
                return result
            # n = 21, 31, ..., 91
            case "1":
                return result + " mốt"
            # n = 24, 34, ..., 94
            case "4":
                return result + " tư"
            # n = 25, 35, ..., 95
            case "5":
                return result + " lăm"
            case _:
                return result + " " + NumberConverter.DIGITS[int(number[1])]

    @staticmethod
    def _convert_number_lt_thousand(number: str):
        if len(number) < 3:
            return NumberConverter._convert_number_lt_hundred(number)
        result = NumberConverter.DIGITS[int(number[0])] + " trăm"

        # n = 000, 100, ..., 900
        if number[1] == "0" and number[2] == "0":
            if number[0] == "0":
                return ""
            else:
                return result
        elif number[1] == "0":
            result += " linh "
            match number[2]:
                case "0":
                    raise ValueError(f"Unexpected error. Number: {number}")
                case "5":
                    return result + "lăm"
                case _:
                    return result + NumberConverter.DIGITS[int(number[2])]
        else:
            return result + " " + NumberConverter._convert_number_lt_hundred(number[1:])

    @staticmethod
    def _convert_number_lq_milion(number: str):
        if len(number) < 4:
            return NumberConverter._convert_number_lt_thousand(number)

        split_index = len(number) % 3
        if split_index == 0:
            split_index = 3

        first_part = NumberConverter._convert_number_lq_milion(number[:split_index])
        second_part = NumberConverter._convert_number_lq_milion(number[split_index:])

        if len(first_part) == 0 and len(second_part) == 0:
            return ""

        hang_index = (len(number) - split_index) // 3 - 1
        hang = "nghìn" if hang_index == 0 else "triệu"

        if len(first_part) == 0:
            return " ".join((NumberConverter.DIGITS[0], hang, second_part))
        if len(second_part) == 0:
            return first_part + " " + hang
        return " ".join((first_part, hang, second_part))

    @staticmethod
    def _convert_arbitrary_number(number: str):
        if len(number) < 10:
            return NumberConverter._convert_number_lq_milion(number)
        split_index = len(number) % 9
        if split_index == 0:
            split_index = 9
        first_part = NumberConverter._convert_number_lq_milion(number[:split_index])
        second_part = NumberConverter._convert_arbitrary_number(number[split_index:])
        if len(first_part) == 0 and len(second_part) == 0:
            return ""

        hang = " tỷ" * ((len(number) - split_index) // 9)
        if len(second_part) == 0:
            return first_part + hang
        else:
            return first_part + hang + " " + second_part

    @staticmethod
    def strip_leading_zeros(number: str):
        return number.lstrip("0")

    @staticmethod
    def _convert_number(number: str):
        if len(number) == 0:
            raise ValueError("Number cannot be empty")
        if not number.isdigit():
            raise ValueError(f"Invalid number {number}")
        if number == "0":
            return NumberConverter.DIGITS[0]

        result = NumberConverter.strip_leading_zeros(number)

        if len(result) == 0:
            raise ValueError(
                f"Number contains only zeros is not valid! Number: {number}"
            )

        if len(result) > 15:
            # Convert to per digit spoken form
            return " ".join(NumberConverter.DIGITS[int(digit)] for digit in result)

        result = NumberConverter._convert_arbitrary_number(result)
        return result

    @staticmethod
    def convert_number(number: str):
        if len(number) == 0:
            raise ValueError("Number cannot be empty")

        prefix = ""
        signed_number = number
        if number[0] == "-":
            prefix = "âm "
            number = number[1:]
        elif number[0] == "+":
            prefix = "dương "
            number = number[1:]

        try:
            result = prefix + NumberConverter._convert_number(number)
            return result
        except ValueError as e:
            raise ValueError(f"Failed to convert number '{signed_number}': {e}")

    @staticmethod
    def convert_decimal(
        number: str, decimal_delimiter: str = ",", thousands_delimiter: str = "."
    ):
        """
        Convert a decimal number to its spoken form.

        :param number: The decimal number as a string.
        :param decimal_delimiter: The character used to separate the integer and decimal parts.
        :param thousands_delimiter: The character used to separate thousands.
        :return: The spoken form of the decimal number.
        """
        assert (
            decimal_delimiter != thousands_delimiter
        ), "Decimal and thousands delimiters must be different"

        parts = number.split(decimal_delimiter)
        if len(parts) == 1:
            # No decimal part, just convert the integer part
            return NumberConverter.convert_number(
                parts[0].replace(thousands_delimiter, "")
            )
        elif len(parts) != 2:
            raise ValueError(f"Invalid decimal number format: {number}")
        elif not parts[1].isdigit():
            raise ValueError(f"Invalid decimal part: {parts[1]} in {number}")

        integer_part, decimal_part = parts
        integer_part = integer_part.replace(thousands_delimiter, "")

        spoken_integer = NumberConverter.convert_number(integer_part)
        spoken_decimal = " phẩy " + " ".join(
            NumberConverter.DIGITS[int(digit)] for digit in decimal_part
        )

        return spoken_integer + spoken_decimal

    @staticmethod
    def decimal_to_roman(number: int):
        roman_numerals = [
            ("M", 1000),
            ("CM", 900),
            ("D", 500),
            ("CD", 400),
            ("C", 100),
            ("XC", 90),
            ("L", 50),
            ("XL", 40),
            ("X", 10),
            ("IX", 9),
            ("V", 5),
            ("IV", 4),
            ("I", 1),
        ]
        result = ""
        for roman, value in roman_numerals:
            while number >= value:
                result += roman
                number -= value
        return result

    @staticmethod
    def roman_to_decimal(roman: str) -> int:
        """
        Convert a Roman numeral to a decimal number.

        :param roman: The Roman numeral string.
        :return: The decimal equivalent of the Roman numeral.
        :raises ValueError: If the input is not a valid Roman numeral.
        """
        roman2int = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

        roman = roman.upper()  # Normalize to uppercase
        if not all(char in roman2int for char in roman):
            raise ValueError("Invalid Roman numeral: contains invalid characters.")

        # Check for invalid patterns
        valid_subtractions = {"IV", "IX", "XL", "XC", "CD", "CM"}
        for i, char in enumerate(roman):
            if i > 0 and roman2int[char] > roman2int[roman[i - 1]]:
                if roman[i - 1 : i + 1] not in valid_subtractions:
                    raise ValueError(
                        f"Invalid Roman numeral: incorrect subtraction at '{roman[i - 1:i + 1]}'."
                    )
            if i >= 3 and char in ("I", "X", "M") and roman[i - 3 : i + 1] == char * 4:
                raise ValueError(
                    f"Invalid Roman numeral: too many consecutive '{char}'s."
                )
            if i >= 1 and char in ("V", "L", "D") and roman[i - 1 : i + 1] == char * 2:
                raise ValueError(
                    f"Invalid Roman numeral: too many consecutive '{char}'s."
                )

        total = 0
        prev_value = 0
        for char in reversed(roman):
            value = roman2int[char]
            if value < prev_value:
                total -= value
            else:
                total += value
            prev_value = value

        return total
