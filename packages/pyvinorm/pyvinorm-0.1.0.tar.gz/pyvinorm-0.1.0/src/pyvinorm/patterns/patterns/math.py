import logging

logger = logging.getLogger(__name__)

from pyvinorm.utils import NumberConverter
from pyvinorm.managers import MappingManager
from ..registry import register_pattern
from ..base import BasePattern


@register_pattern
class DecimalVNPattern(BasePattern):
    def get_priority(self):
        return super().get_priority() + 10

    def get_regex_pattern(self):
        # This pattern matches decimal numbers with thousands separators.
        # For example: "1.234,56", "12.345,67", "123.456,78"
        return r"(?i)(\s|^)-?\d+(\.\d{3})+(,\d+)?(:?\b|$)"

    def handle_match(self, matcher):
        match = matcher.group()
        prefix = matcher.group(1)
        match = match[len(prefix):]  # Remove the prefix (space or start of string)

        return prefix + NumberConverter.convert_decimal(
            number=match, decimal_delimiter=",", thousands_delimiter="."
        )


@register_pattern
class DecimalUSPattern(DecimalVNPattern):
    def get_regex_pattern(self):
        return r"(?i)(\s|^)-?\d+(,\d{3})+(\.\d+)?(:?\b|$)"

    def handle_match(self, matcher):
        match = matcher.group()
        prefix = matcher.group(1)
        match = match[len(prefix):]  # Remove the prefix (space or start of string)

        return prefix + NumberConverter.convert_decimal(
            number=match, decimal_delimiter=".", thousands_delimiter=","
        )


@register_pattern
class DecimalVN1Pattern(DecimalVNPattern):
    def get_regex_pattern(self):
        return r"(?i)(\s|^)-?\d+(,\d+)(:?\b|$)"


@register_pattern
class DecimalUS1Pattern(DecimalUSPattern):
    def get_regex_pattern(self):
        return r"(?i)(\s|^)-?\d+(\.\d+)(:?\b|$)"


@register_pattern
class RomanPattern(BasePattern):
    def get_regex_pattern(self):
        return r"(?i)(\b|^)(thứ|lần|kỷ|kỉ|kì|kỳ|khóa)\s+[V|I|X]{1,5}(\b|$)"

    def handle_match(self, matcher):
        match = matcher.group()
        prefix, roman_numeral = match.split()
        result = (
            prefix
            + " "
            + NumberConverter.convert_number(
                str(NumberConverter.roman_to_decimal(roman_numeral.upper()))
            )
        )
        return result

class BaseMeasurementPattern(BasePattern):
    def get_priority(self):
        # These patterns be collide with decimal patterns
        # so we set a higher priority to ensure they are matched first
        return super().get_priority() + 20

@register_pattern
class MeasurementVNPattern(BaseMeasurementPattern):
    def get_priority(self):
        # Could be collide with DecimalVNPattern
        # so we set a higher priority to ensure it is matched first
        return super().get_priority() + 20

    def get_regex_pattern(self):
        return r"(?i)\b(\d+(?:\.\d{3})+(?:,\d+)?)\s?([°|\p{Alphabetic}]+[2|3]?)(?:\/(\p{Alphabetic}+[2|3]?))?(?:\b|$)"

    def handle_match(self, matcher):
        unit_mapping = MappingManager.get_mapping("BaseUnit")
        number = matcher.group(1)
        result = NumberConverter.convert_decimal(
            number, decimal_delimiter=",", thousands_delimiter="."
        )

        unit = matcher.group(2)
        if unit_mapping.contains(unit):
            result += " " + unit_mapping.get(unit)
        else:
            raise ValueError(
                f"Unit '{unit}' not found in mapping. Please check the unit mapping."
            )

        unit2 = matcher.group(3)
        if unit2:
            result += " trên"
            if unit_mapping.contains(unit2):
                result += " " + unit_mapping.get(unit2)
            else:
                raise ValueError(
                    f"Unit '{unit2}' not found in mapping. Please check the unit mapping."
                )
        return result


@register_pattern
class MeasurementUSPattern(BaseMeasurementPattern):
    def get_priority(self):
        # Could be collide with DecimalUSPattern
        # so we set a higher priority to ensure it is matched first
        return super().get_priority() + 20

    def get_regex_pattern(self):
        return r"(?i)\b(\d+(?:,\d{3})+(?:\.\d+)?)\s?([°|\p{Alphabetic}]+[2|3]?)(?:\/(\p{Alphabetic}+[2|3]?))?(?:\b|$)(-?)"

    def handle_match(self, matcher):
        unit_mapping = MappingManager.get_mapping("BaseUnit")
        number = matcher.group(1)
        result = NumberConverter.convert_decimal(
            number, decimal_delimiter=".", thousands_delimiter=","
        )

        unit = matcher.group(2)
        if unit_mapping.contains(unit):
            result += " " + unit_mapping.get(unit)
        else:
            raise ValueError(
                f"Unit '{unit}' not found in mapping. Please check the unit mapping."
            )

        unit2 = matcher.group(3)
        if unit2:
            result += " trên"
            if unit_mapping.contains(unit2):
                result += " " + unit_mapping.get(unit2)
            else:
                raise ValueError(
                    f"Unit '{unit2}' not found in mapping. Please check the unit mapping."
                )

        if matcher.group(4).strip() == "-":
            result += " đến"
        return result


@register_pattern
class MeasurementVN1Pattern(MeasurementVNPattern):
    def get_regex_pattern(self):
        return r"(?i)\b(\d+(?:,\d+))\s?([°|\p{Alphabetic}]+[2|3]?)(?:\/(\p{Alphabetic}+[2|3]?))?(?:\b|$)(-?)"


@register_pattern
class MeasurementUS1Pattern(MeasurementUSPattern):
    def get_regex_pattern(self):
        # return r"(?i)\b(\d+(?:\.\d+)?)\s?([°|\p{Alphabetic}]+[2|3]?)(?:\/(\p{Alphabetic}+[2|3]?))?(?:\b|$)(-?)"
        return r"(?i)\b(\d+(?:\.\d+)?)\s?([°|\p{Alphabetic}]+[2|3]?)(?:\/(\p{Alphabetic}+[2|3]?))?(?:\b|$)(\s?-?)"


@register_pattern
class MeasurementOtherVNPattern(BaseMeasurementPattern):
    def get_priority(self):
        return super().get_priority() + 20

    def get_regex_pattern(self):
        return r"(?i)(?:\b|^)(\d+(?:\.\d{3})+(?:,\d+)?)\s?(\%|\$|฿|₱|₭|₩|¥|€|£|Ω)(\s-|$|-|\s)"

    def handle_match(self, matcher):
        unit_mapping = MappingManager.get_mapping("CurrencyUnit")
        number = matcher.group(1)
        result = NumberConverter.convert_decimal(
            number, decimal_delimiter=",", thousands_delimiter="."
        )

        if matcher.groupCount() > 1:
            unit = matcher.group(2)
            if unit_mapping.contains(unit):
                result += " " + unit_mapping.get(unit)

        if matcher.group(3).strip() == "-":
            result += " đến"

        return result


@register_pattern
class MeasurementOtherUSPattern(BaseMeasurementPattern):
    def get_regex_pattern(self):
        return r"(?i)(?:\b|^)(\d+(?:,\d{3})+(?:\.\d+)?)\s?(\%|\$|฿|₱|₭|₩|¥|€|£|Ω)(\s-|$|-|\s)"

    def handle_match(self, matcher):
        unit_mapping = MappingManager.get_mapping("CurrencyUnit")
        number = matcher.group(1)
        result = NumberConverter.convert_decimal(
            number, decimal_delimiter=".", thousands_delimiter=","
        )

        if matcher.groupCount() > 1:
            unit = matcher.group(2)
            if unit_mapping.contains(unit):
                result += " " + unit_mapping.get(unit)

        if matcher.group(3).strip() == "-":
            result += " đến"

        return result


@register_pattern
class MeasurementOtherVN1Pattern(MeasurementOtherVNPattern):
    def get_regex_pattern(self):
        return r"(?i)(?:\b|^)(\d+(?:,\d+))\s?(\%|\$|฿|₱|₭|₩|¥|€|£|Ω)(\s-|$|-|\s)"


@register_pattern
class MeasurementOtherUS1Pattern(MeasurementOtherUSPattern):
    def get_regex_pattern(self):
        return r"(?i)(?:\b|^)(\d+(?:\.\d+)?)\s?(\%|\$|฿|₱|₭|₩|¥|€|£|Ω)(\s-|$|-|\s)"
