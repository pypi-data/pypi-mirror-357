import logging

logger = logging.getLogger(__name__)

from pyvinorm.utils import NumberConverter
from pyvinorm.managers import MappingManager, VocabularyManager, Mapping
from ..registry import register_pattern
from ..base import BasePattern


class BaseSpecialPattern(BasePattern):
    """
    Base class for special patterns.
    """

    def get_priority(self):
        # Since special patterns are usually used for specific cases,
        # assign them a higher priority than regular patterns.
        return super().get_priority() + 90


@register_pattern
class PhoneNumberPattern(BaseSpecialPattern):
    def get_regex_pattern(self):
        # This matches formats like:
        # +84 123 456 7890, +1.800.555.1234
        return (
            r"([^(\w|\d|\.)]|^)((\+\d{1,3})|0)[-\s.]?\d{1,3}[-\s.]?\d{3}[-\s.]?\d{4}\b"
        )

    def handle_match(self, matcher):
        match = matcher.group()
        prefix = matcher.group(1)  # The character before the phone number
        match = match[len(prefix):]
        result = ""

        for c in match:
            if c == "+":
                result += " cộng"
            elif c in ".:-()":
                pass  # ignore separators
            elif c.isdigit():
                result += " " + NumberConverter.convert_number(c)
            else:
                result += " " + c

        return prefix + result.lstrip()


@register_pattern
class PhoneNumber1Pattern(PhoneNumberPattern):
    def get_regex_pattern(self):
        # This matches formats like:
        # +84 123 45 67 89, 0 123 45 67 89
        return r"([^(\w|\d|\.)]|^)((\+\d{1,3})|0)[-\s.]?\d{2,3}[-\s.]?\d{2}[-\s.]?\d{2}[-\s.]?\d{2}\b"


@register_pattern
class PhoneNumber2Pattern(PhoneNumberPattern):
    def get_regex_pattern(self):
        # This matches formats like:
        # +84 12 34 56 789
        return r"([^(\w|\d|\.)]|^)((\+\d{1,3})|0)[-\s.]?\d{1,3}[-\s.]?\d{1,2}[-\s.]?\d{2,3}[-\s.]?\d{3}\b"


@register_pattern
class PhoneNumber3Pattern(PhoneNumberPattern):
    def get_regex_pattern(self):
        # This matches hotline phone numbers like:
        # 1900 1234, 1900.0606.0909
        return r"\b1[89]00[\s\.]?[\d\s\.]{4,8}\b"


@register_pattern
class EmailPattern(BaseSpecialPattern):
    def get_regex_pattern(self):
        return r"[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"

    def handle_match(self, matcher):
        # TODO: This is a work-in-progress implementation.
        logger.warning("EmailPattern is WIP. It may not handle all cases correctly.")
        lettersound_en = MappingManager.get_mapping("LetterSoundEN")
        domain_mapping = MappingManager.get_mapping("Domain")

        match = matcher.group().lower()
        result = ""

        name, domain = match.split("@")
        provider, domains = domain.split(".", maxsplit=1)

        for c in name:
            if c.isdigit():
                result += " " + NumberConverter.convert_number(c)
            else:
                result += " " + lettersound_en.get(c, c)

        result += " a còng"
        result += " " + provider

        for d in domains.split("."):
            result += " chấm"
            if d.isdigit():
                for digit in d:
                    result += " " + NumberConverter.convert_number(digit)
            else:
                result += " " + domain_mapping.get(d, d)

        return result.lstrip()


@register_pattern
class WebsitePattern(BaseSpecialPattern):
    def get_regex_pattern(self):
        return r"(?i)\b(https?:\/\/|ftp:\/\/|www\.|[^\s:=]+@www\.)?((\w+)\.)+(?:com|au\.uk|co\.in|net|org|info|coop|int|co\.uk|org\.uk|ac\.uk|uk)([\.\/][^\s]*)*([^(w|\d)]|$)"

    def handle_match(self, matcher):
        lettersound_mapping = Mapping.combine(
            MappingManager.get_mapping("LetterSoundVN"),
            MappingManager.get_mapping("Symbol"),
        )
        domain_mapping = MappingManager.get_mapping("Domain")

        match = matcher.group().lower()
        protocol = matcher.group(1)
        domain = match[len(protocol) :]

        result = ""
        for c in protocol:
            match c:
                case ":":
                    result += " hai chấm"
                case "/":
                    result += " gạch chéo"
                case _:
                    result += " " + lettersound_mapping.get(c, c)

        continuous = False
        subdomain = ""
        for c in domain:
            if c in ".:/":
                if continuous:
                    result += " " + self._try_convert_to_spoken(
                        subdomain, domain_mapping, lettersound_mapping
                    )
                    subdomain = ""
                    continuous = False

                if c == ".":
                    result += " chấm"
                elif c == ":":
                    result += " hai chấm"
                elif c == "/":
                    result += " gạch chéo"
            else:
                subdomain += c
                continuous = True
        if continuous:
            result += " " + self._try_convert_to_spoken(
                subdomain, domain_mapping, lettersound_mapping
            )
        
        return result.lstrip()

    def _try_convert_to_spoken(
        self,
        subdomain: str,
        domain_mapping: Mapping,
        lettersound_mapping: Mapping,
    ):
        if domain_mapping.contains(subdomain):
            return domain_mapping.get(subdomain)
        else:  # read subdomain as letters
            spoken_subdomain = ""
            for char in subdomain:
                if char.isdigit():
                    spoken_subdomain += " " + NumberConverter.convert_number(char)
                else:
                    spoken_subdomain += " " + lettersound_mapping.get(char, char)
            return spoken_subdomain.lstrip()


@register_pattern
class Website1Pattern(WebsitePattern):
    def get_regex_pattern(self):
        # This matches URLs with IP addresses as hostnames
        # For example: https://192.168.1.1, ftp://user:pass@192.168.1.1:212
        return r"(?i)\b((https?:\/\/|ftp:\/\/|sftp:\/\/|www\.|[^\s:=]+@www\.))(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\d]+-[a-z\d])*[a-z\d]+)(?:\.(?:[a-z\d]+-?)*[a-z\d]+)*(?:\.(?:[a-z]{2,})))(?::\d{2,5})?(?:\/[^\s]*)?([^(w|\d)]|$)"


@register_pattern
class FootballUnderAgePattern(BaseSpecialPattern):
    def get_regex_pattern(self):
        # This matches football under the age patterns like:
        # "U19", "U21", "U23", "U17"
        return r"(?i)\b[u][.]?\d{2}\b"

    def handle_match(self, matcher):
        match = matcher.group()
        age = match[-2:]  # Get the last two digits
        prefix = match[0]

        result = prefix + " " + NumberConverter.convert_number(age)
        return result

@register_pattern
class FootballTeamPattern(BaseSpecialPattern):
    def get_regex_pattern(self):
        return r"(?i)[đ]ội hình \b\d\s?-\s?\d\s?-\s?\d(-\s?\d)?\b"

    def handle_match(self, matcher):
        match = matcher.group()
        result = ""
        number = ""
        continuous_digits = False

        for c in match:
            if c.isdigit():
                number += c
                continuous_digits = True
            else:
                if continuous_digits:
                    result += NumberConverter.convert_number(number)
                    number = ""
                    continuous_digits = False
                
                if c in "-|":
                    result += " "
                else:
                    result += c
        
        if len(number) > 0:
            result = result.strip() + " " + NumberConverter.convert_number(number)
        return result

@register_pattern
class FootballScorePattern(BaseSpecialPattern):
    def get_regex_pattern(self):
        return r"(?i)tỉ số \b\d{1,2}\s?[-|]\s?\d{1,2}\b"

    def handle_match(self, matcher):
        match = matcher.group()
        result = ""
        number = ""
        continuous_digits = False

        for c in match:
            if c.isdigit():
                number += c
                continuous_digits = True
            else:
                if continuous_digits:
                    result += NumberConverter.convert_number(number)
                    number = ""
                    continuous_digits = False
                
                if c in "-|":
                    result += " "
                else:
                    result += c
        
        if len(number) > 0:
            result = result.strip() + " " + NumberConverter.convert_number(number)
        return result
    
@register_pattern
class FootballScore1Pattern(FootballScorePattern):
    def get_regex_pattern(self):
        return r"(?i)[h]ạ\s(\w+(\s)?){1,4}\d{1,2}\s?[-|]\s?\d{1,2}\b"
