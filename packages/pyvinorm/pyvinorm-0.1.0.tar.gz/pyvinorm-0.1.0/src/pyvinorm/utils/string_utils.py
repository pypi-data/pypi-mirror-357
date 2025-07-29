import re
from pyvinorm.managers import MappingManager, Mapping


def remove_white_space(text: str) -> str:
    """
    Remove extra white spaces from the text.
    """
    return " ".join(text.split())


def replace_nonvoice_symbols(text: str, repl: str = "") -> str:
    """
    Remove non-voice symbols from the text.
    """
    # Define a regex pattern to match non-voice symbols
    pattern = re.compile(r"(“|”|\.\.\.|\"|\'|\{|\}|\[|\]|\(|\))")
    return pattern.sub(repl, text)


def contain_only_letters(text: str, letter_mapping: Mapping) -> bool:
    for c in text.lower():
        if not letter_mapping.contains(c):
            return False
    return True


def read_letter_by_letter(text: str, lettersound_mapping: Mapping) -> str:
    """
    Read the text letter by letter using the provided lettersound mapping.
    """
    result = ""
    for char in text.lower():
        if lettersound_mapping.contains(char):
            result += " " + lettersound_mapping.get(char, char)
    return result.lstrip()
