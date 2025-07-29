import logging

from pyvinorm.managers import MappingManager, VocabularyManager
from pyvinorm.utils import NumberConverter

from ..registry import register_pattern
from ..base import BasePattern

logger = logging.getLogger(__name__)


@register_pattern
class PoliticalDivisionPattern(BasePattern):
    def get_regex_pattern(self):
        return r"(?i)\b(kp|q|p|h|tx|tp|x)\s?[.]\s?"

    def handle_match(self, matcher):
        match = matcher.group()
        prefix = matcher.group(1)
        expanded_prefix = self._expand_prefix(prefix)
        dot_index = match.index(".", len(prefix))

        if dot_index != -1:
            return expanded_prefix + " " + match[(dot_index + 1) :]
        else:
            return expanded_prefix + match[len(prefix) :]

    def _expand_prefix(self, prefix: str):
        match prefix:
            case "kp":
                return "khu phố"
            case "q":
                return "quận"
            case "p":
                return "phường"
            case "h":
                return "huyện"
            case "tx":
                return "thị xã"
            case "tp":
                return "thành phố"
            case "x":
                return "xã"
            case _:
                logging.debug(f"Failed to expand unknown prefix. Prefix: {prefix}")
                return prefix


@register_pattern
class StreetPattern(BasePattern):
    def get_regex_pattern(self):
        return r"(?i)\b(đường|số|số nhà|nhà|địa chỉ|tọa lạc|xã|thôn|ấp|khu phố|căn hộ|cư xá|Đ\/c)[\s:]\s?[^\s]*\d[^\s]*(\b|$)"

    def handle_match(self, matcher):
        match = matcher.group()
        prefix = matcher.group(1)
        # The main part contains the digist and symbol for the street
        mainPart = match[len(prefix) :]
        # Check continuous digits construct a whole number
        continuous_digits = False
        result = ""
        number = ""
        lettersound_mapping = MappingManager.get_mapping("LetterSoundVN")

        for c in mainPart:
            if c.isdigit():
                if continuous_digits:
                    number += c
                else:
                    if c == "0":
                        # Skip leading zero
                        result += " không"
                        number = ""
                    else:
                        number = c
                        continuous_digits = True
            else:
                if continuous_digits:
                    continuous_digits = False
                    result += " " + NumberConverter.convert_number(number)
                    number = ""

                match c:
                    case "/":
                        result += " trên"
                    case "-":
                        result += " " + c
                    case " ":
                        result += c
                    case _:
                        result += " " + lettersound_mapping.get(c, c)

        if len(number) > 0:
            # If there is a number left, convert it to words
            result += " " + NumberConverter.convert_number(number)
        return prefix + " " + result.lstrip()


@register_pattern
class OfficePattern(BasePattern):
    def get_regex_pattern(self):
        return r"(?i)(phòng|lớp|đơn vị)\s[^\s]*\d[^\s]*(\b|$)"

    def handle_match(self, matcher):
        match = matcher.group()
        prefix = matcher.group(1)
        # The main part contains the digist and symbol of the office
        main_part = match[len(prefix) :]
        continuous_digits = False
        result = ""
        number = ""
        lettersound_mapping = MappingManager.get_mapping("LetterSoundVN")

        for c in main_part:
            if c.isdigit():
                if continuous_digits:
                    number += c
                else:
                    if c == "0":
                        continuous_digits = False
                        result += " không"
                        number = ""
                    else:
                        number = c
                        continuous_digits = True
            else:
                if continuous_digits:
                    # If there is a number before the slash, convert it to words
                    continuous_digits = False
                    result += " " + NumberConverter.convert_number(number)
                    number = ""

                match c:
                    case "/":
                        result += " trên"
                    case "-":
                        result += " " + c
                    case " ":
                        result += c
                    case _:
                        result += " " + lettersound_mapping.get(c, c)

        if len(number) > 0:
            # If there is a number left, convert it to words
            result += " " + NumberConverter.convert_number(number)
        return prefix + " " + result.lstrip()


@register_pattern
class CodeNumberPattern(BasePattern):
    def get_regex_pattern(self):
        return r"(?i)(\b|^)[^\s]*\d[^\s]*\b"

    def handle_match(self, matcher):
        match = matcher.group()
        result = ""
        number = ""
        pop_word = ""
        continuous_digits = False
        contiguous_lowercase_pop = False

        # TODO: This implement seems ambiguous
        lettersound_mapping = MappingManager.get_mapping("LetterSoundVN")

        for c in match:
            if c.isdigit():
                if continuous_digits:
                    number += c
                else:
                    if c == "0":
                        continuous_digits = False
                        result += " không"
                        number = ""
                    else:
                        number = c
                        continuous_digits = True

                if contiguous_lowercase_pop:
                    # If we are in a contiguous lowercase popular word, we need to reset it
                    contiguous_lowercase_pop = False
                    result += " " + pop_word
                    pop_word = ""
            elif lettersound_mapping.contains(c):
                if continuous_digits:
                    continuous_digits = False
                    result += " " + self._number_to_spoken(number)
                    number = ""

                if contiguous_lowercase_pop:
                    pop_word += c
                else:
                    pop_word = c
                    contiguous_lowercase_pop = True
            else:
                if continuous_digits:
                    continuous_digits = False
                    result += " " + self._number_to_spoken(number)
                    number = ""

                if contiguous_lowercase_pop:
                    contiguous_lowercase_pop = False
                    result += " " + pop_word
                    pop_word = ""

                match c:
                    case "/":
                        result += " trên"
                    case ".":
                        result += " chấm"
                    case "-":
                        result += " " + c
                    case " ":
                        result += c
                    case _:
                        result += " " + lettersound_mapping.get(c, c)

        if len(number) > 0:
            result += " " + self._number_to_spoken(number)
        if len(pop_word) > 0:
            result += " " + " ".join([lettersound_mapping.get(c, c) for c in pop_word])

        return result.lstrip()

    def _number_to_spoken(self, number: str):
        """
        Convert a number to its spoken form.

        :param number: The number to convert.
        :return: The spoken form of the number.
        """
        if len(number) <= 4:
            return NumberConverter.convert_number(number)
        else:
            return " ".join(NumberConverter.convert_number(digit) for digit in number)
