import logging

logger = logging.getLogger(__name__)

from pyvinorm.utils import NumberConverter
from ..registry import register_pattern
from ..base import BasePattern


class BaseTimePattern(BasePattern):
    """
    Base class for time patterns.
    This class is used to handle time patterns in the text.
    It should be extended by specific time patterns.
    """

    def get_priority(self):
        # Since pattern of date time is at the format "dd/mm"
        # It often collides with other patterns such as
        # fraction or address which have more general regex patterns
        # so give these time patterns a higher priority
        return super().get_priority() + 50


@register_pattern
class TimePattern(BaseTimePattern):
    def get_regex_pattern(self):
        # This regex matches time formats like "10h30", "10h45 am"
        return r"(?i)\b(?:2[0-4]|10|[01]?[1-9])\s?[hg]\s?[0-5]?[0-9]\s?(?:am|pm|p)?\b(\s?-?)"

    def handle_match(self, matcher):
        match = matcher.group().lower()
        next_str = matcher.group(1).strip()
        match = match[:len(match) - len(next_str)]

        result = ""
        number = ""

        continuous_digits = False
        for i, c in enumerate(match):
            if c.isdigit():
                if continuous_digits:
                    number += c
                else:
                    number = c
                    continuous_digits = True
            else:
                if continuous_digits:
                    result += " " + NumberConverter.convert_number(number)
                    continuous_digits = False
                    number = ""

                match c:
                    case "h":
                        result += " giờ"
                    case "g":
                        result += " giờ"
                    case ":":
                        result += " giờ"
                    case "a":
                        if i + 1 < len(match) and match[i + 1] == "m":
                            result += " ây em"
                    case "p":
                        if i + 1 < len(match) and match[i + 1] == "m":
                            result += " pi em"
                        else:
                            result += " phút"
                    case "m":
                        pass
                    case _:
                        result += c

        if len(number) > 0:
            result += " " + NumberConverter.convert_number(number)
        if next_str == "-":
            result += " đến"

        return result.lstrip()


@register_pattern
class Time1Pattern(TimePattern):
    def get_regex_pattern(self):
        # This match hour without minutes like "10h", "10g", "10 g"
        return r"(?i)\b(?:2[0-4]|10|[01]?[1-9])\s?[hg]\b(\s?-?)"


@register_pattern
class Time2Pattern(BaseTimePattern):
    def get_regex_pattern(self):
        # This match time with hours, minutes & seconds in formats like
        # 12:23:30 or 12h23p30s
        return r"(?i)\b(?:2[0-4]|10|[01]?[1-9])\s?[:h]\s?[0-5]?[0-9]\s?(?:[:m]\s?[0-5]?[0-9]\s?s?)?\b(\s?-?)"

    def handle_match(self, matcher):
        match = matcher.group().lower()
        next_str = matcher.group(1).strip()
        match = match[:len(match) - len(next_str)]

        result = ""
        number = ""
        colon_count = 0

        continuous_digits = False
        for i, c in enumerate(match):
            if c.isdigit():
                if continuous_digits:
                    number += c
                else:
                    number = c
                    continuous_digits = True
            else:
                if continuous_digits:
                    result += " " + NumberConverter.convert_number(number)
                    continuous_digits = False
                    number = ""

                match c:
                    case "h":
                        result += " giờ"
                    case "m":
                        result += " phút"
                    case "s":
                        result += " giây"
                    case ":":
                        if colon_count == 0:
                            result += " giờ"
                        elif colon_count == 1:
                            result += " phút"
                        colon_count += 1
                    case _:
                        result += c

        if len(number) > 0:
            result += " " + NumberConverter.convert_number(number)
            if colon_count == 2:
                result += " giây"
        if next_str == "-":
            result += " đến"

        return result.lstrip()


@register_pattern
class DatePattern(BaseTimePattern):
    def get_regex_pattern(self):
        # This match date with slash / formats like "10/3/2023", "2/09/1945", "05 / 09 / 1890".
        return r"(?i)\b[0-3]?[0-9]\s?\/\s?[01]?\d\s?\/\s?[12]\d{3}\b"

    def handle_match(self, matcher):
        match = matcher.group().lower()
        result = ""
        number = ""
        continuous_digits = False
        delim_count = 0

        for c in match:
            if c.isdigit():
                if continuous_digits:
                    number += c
                else:
                    number = c
                    continuous_digits = True
            elif c in ["/", ".", "-"]:
                if continuous_digits:
                    result += " " + NumberConverter.convert_number(number)
                    continuous_digits = False
                    number = ""

                if delim_count == 0:
                    result += " tháng"
                elif delim_count == 1:
                    result += " năm"
                delim_count += 1
            elif c == " ":
                if continuous_digits:
                    result += " " + NumberConverter.convert_number(number)
                    continuous_digits = False
                    number = ""

                result += c
            else:
                raise ValueError(f"Invalid sequence. Sequence: {match}")

        result = result.lstrip() + " " + NumberConverter.convert_number(number)
        return result


@register_pattern
class Date1Pattern(DatePattern):
    def get_regex_pattern(self):
        # This match date with dash formats like "10-3-2023", "2-09-1945", "09 - 09 - 1890".
        return r"(?i)\b[0-3]?[0-9]\s?-\s?[01]?\d\s?-\s?[12]\d{3}\b"


@register_pattern
class Date2Pattern(DatePattern):
    def get_regex_pattern(self):
        # This match date with dot formats like "10.3.2023", "2.09.1945", "09 . 09 . 1890".
        return r"(?i)\b[0-3]?[0-9]\s?\.\s?[01]?\d\s?\.\s?[12]\d{3}\b"


@register_pattern
class DateFromToPattern(BaseTimePattern):
    def get_regex_pattern(self):
        # This match date formats like "từ 10- 20/3", "ngày 10-20.4"
        return r"(?i)(từ|ngày) [0-3]?[0-9]\s?-\s?[0-3]?[0-9][.\/][01]?\d\b"

    def handle_match(self, matcher):
        match = matcher.group().lower()
        result = ""
        number = ""
        continuous_digits = False
        prefix = ""
        is_met_digits = False

        for c in match:
            if c.isdigit():
                is_met_digits = True
                if continuous_digits:
                    number += c
                else:
                    number = c
                    continuous_digits = True
            elif not is_met_digits:
                prefix += c
            else:
                if continuous_digits:
                    result += " " + NumberConverter.convert_number(number)
                    continuous_digits = False
                    number = ""

                if c in ("/", "."):
                    result += " tháng"
                elif c == "-":
                    result += " đến"
                else:
                    result += c.strip()

        result = " ".join(
            (prefix.strip(), result.lstrip(), NumberConverter.convert_number(number))
        )
        return result.lstrip()


@register_pattern
class DateFromTo1Pattern(DateFromToPattern):
    def get_regex_pattern(self):
        # This match date formats like "từ 10/3 - 20/3", "ngày 10.4 - 20.4"
        return r"(?i)(từ|ngày) [0-3]?[0-9][.\/][01]?\d\s?(-|đến)\s?[0-3]?[0-9][.\/][01]?\d\b"


@register_pattern
class MonthFromToPattern(BaseTimePattern):
    def get_regex_pattern(self):
        # This match patterns like "từ 01-12.2023", "tháng 01-12/2023"
        return r"(?i)(từ|tháng) [01]?\d\s?-\s?[01]?\d[.\/][12]\d{3}\b"

    def handle_match(self, matcher):
        match = matcher.group().lower()
        result = ""
        number = ""
        continuous_digits = False
        prefix = ""
        is_met_digits = False

        for c in match:
            if c.isdigit():
                is_met_digits = True
                if continuous_digits:
                    number += c
                else:
                    number = c
                    continuous_digits = True
            elif not is_met_digits:
                prefix += c
            else:
                if continuous_digits:
                    result += " " + NumberConverter.convert_number(number)
                    continuous_digits = False
                    number = ""

                if c in ("/", "."):
                    result += " năm"
                elif c == "-":
                    result += " đến tháng"
                else:
                    result += c.strip()

        result = (
            prefix.strip()
            + " "
            + "tháng "
            + result
            + " "
            + NumberConverter.convert_number(number)
        )

        return result


@register_pattern
class MonthFromTo1Pattern(MonthFromToPattern):
    def get_regex_pattern(self):
        # This match patterns like "từ 01/2023 - 12/2023", "tháng 01.2023 đến 12.2023"
        return r"(?i)(từ|tháng) [01]?\d\s?[.\/]\s?[12]\d{3}\s?(-|đến)\s?[01]?\d\s?[.\/]\s?[12]\d{3}"


@register_pattern
class MonthPattern(BaseTimePattern):
    def get_regex_pattern(self):
        # This match patterns like "tháng 01. 2025", "tháng 12/2025"
        return r"(?i)tháng \d{1,2}\s?[\/.-]\s?\d{4}\b"

    def handle_match(self, matcher):
        match = matcher.group().lower()
        result = ""
        number = ""
        continuous_digits = False
        prefix = ""
        is_met_digits = False

        for c in match:
            if c.isdigit():
                is_met_digits = True
                if continuous_digits:
                    number += c
                else:
                    number = c
                    continuous_digits = True
            elif not is_met_digits:
                prefix += c
            else:
                if continuous_digits:
                    result += NumberConverter.convert_number(number)
                    continuous_digits = False
                    number = ""

                if c in ("/", ".", "-"):
                    result += " năm"

        result += " " + NumberConverter.convert_number(number)
        result = prefix + result.lstrip()

        return result


@register_pattern
class DateTimePattern(BaseTimePattern):
    def get_priority(self):
        # This pattern also collides with DatePattern, DateFromToPattern
        # so give it a lower priority
        return super().get_priority() - 1

    def get_regex_pattern(self):
        # This match patterns like "sáng 10/03", "hôm nay 18/06", "tối 20-6"
        return r"(?i)\b(ngày|sáng|trưa|chiều|tối|đêm|hôm|nay|hai|ba|tư|năm|sáu|bảy|nhật|qua|lúc|từ|đến|mùng|mồng)\s+[0-3]?[0-9]\s?[\/.-]\s?[01]?\d\b"

    def handle_match(self, matcher):
        match = matcher.group().lower()
        result = ""
        number = ""
        continuous_digits = False
        prefix = ""
        is_met_digits = False

        for c in match:
            if c.isdigit():
                is_met_digits = True
                if continuous_digits:
                    number += c
                else:
                    number = c
                    continuous_digits = True
            elif not is_met_digits:
                prefix += c
            else:
                if continuous_digits:
                    result += " " + NumberConverter.convert_number(number)
                    continuous_digits = False
                    number = ""

                if c in ("/", ".", "-"):
                    result += " tháng"

        result = " ".join(
            (prefix.strip(), result.lstrip(), NumberConverter.convert_number(number))
        )
        return result


@register_pattern
class FixAprilPattern(BaseTimePattern):
    def get_priority(self):
        # This should be run at last to fix the issue
        return super().get_priority() - 1

    def get_regex_pattern(self):
        return r"\btháng bốn\b"

    def handle_match(self, matcher):
        return "tháng tư"
