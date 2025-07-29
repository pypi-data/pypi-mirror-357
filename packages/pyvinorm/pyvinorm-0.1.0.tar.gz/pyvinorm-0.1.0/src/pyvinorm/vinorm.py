import importlib.resources as pkg_resources
import logging

import regex
from pyvinorm.patterns.handler import PatternHandler
from pyvinorm.managers import (
    MappingManager,
    Mapping,
    VocabularyManager,
    Vocabulary,
)
from pyvinorm.utils.string_utils import (
    remove_white_space,
    replace_nonvoice_symbols,
    contain_only_letters,
    read_letter_by_letter,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ViNormalizer:
    """Vietnamese text normalizer that convert text to its spoken form.

    :param bool regex_only: If True, only applies regex patterns without further normalization.
    :param bool keep_oov: If True, keeps out-of-vocabulary words as they are.
    :param bool keep_punctuation: If True, do not replace punctuation with dot or comma.
    :param bool downcase: If True, converts the text to lowercase after normalization.

    :return str: Normalized text in spoken form.
    """

    def __init__(
        self,
        regex_only: bool = False,
        keep_oov: bool = True,
        keep_punctuation: bool = False,
        downcase: bool = True,
    ):
        self.regex_only = regex_only
        self.keep_oov = keep_oov
        self.keep_punctuation = keep_punctuation
        self.downcase = downcase

        self.pattern_handler = PatternHandler()
        self.init_resources()

    def normalize(self, text: str) -> str:
        """
        Normalize the input text using defined patterns and mappings.
        """
        popular_vocab = VocabularyManager.get_vocab("Popular")
        acronym_mapping = MappingManager.get_mapping("Acronyms")
        teencode_mapping = MappingManager.get_mapping("Teencode")
        symbol_mapping = MappingManager.get_mapping("Symbol")
        lettersound_vn = MappingManager.get_mapping("LetterSoundVN")
        lettersound_en = MappingManager.get_mapping("LetterSoundEN")

        normalized_text = remove_white_space(text)

        # Step 1: Normalize text using regex patterns
        normalized_text = self.pattern_handler.normalize(normalized_text)

        if self.regex_only:
            normalized_text = remove_white_space(normalized_text)
            return normalized_text

        # Step 2: Check whether normalized text still contains parts
        # that aren't converted to spoken forms.
        normalized_text = replace_nonvoice_symbols(normalized_text, repl="")
        symbol_pattern = regex.compile(r"[^\w\d\s]")
        normalized_text = symbol_pattern.sub(
            lambda m: " " + m.group() + " ", normalized_text
        )

        result = ""
        for token in normalized_text.split():
            token_lower = token.lower()
            if popular_vocab.contains(token_lower):
                result += " " + token
            elif acronym_mapping.contains(token_lower):
                result += " " + acronym_mapping.get(token_lower)
            elif teencode_mapping.contains(token_lower):
                result += " " + teencode_mapping.get(token_lower)
            elif token in (".", "!", ":", "?"):
                result += " " + (token if self.keep_punctuation else ".")
            elif token in (",", ";", "/", "-"):
                result += " " + (token if self.keep_punctuation else ",")
            elif symbol_mapping.contains(token):
                result += " " + symbol_mapping.get(token)
            elif contain_only_letters(token, lettersound_vn):
                if self.keep_oov:
                    result += " " + token
                else:
                    result += read_letter_by_letter(token, lettersound_vn)
            else:
                result += " " + token

        # Step 3: Postprocess the result
        result = remove_white_space(result.lstrip())

        if self.downcase:
            result = result.lower()

        return result

    def init_resources(self):
        """
        Initialize mappings from files.
        """
        for resource in pkg_resources.contents("pyvinorm.resources.mapping"):
            if resource.endswith(".txt"):
                with pkg_resources.path("pyvinorm.resources.mapping", resource) as path:
                    mapping_name = resource[:-4]  # Remove the '.txt' extension
                    MappingManager.register_mapping(
                        mapping_name, Mapping.from_file(str(path))
                    )

        for resource in pkg_resources.contents("pyvinorm.resources.vocabulary"):
            if resource.endswith(".txt"):
                with pkg_resources.path(
                    "pyvinorm.resources.vocabulary", resource
                ) as path:
                    vocabulary_name = resource[:-4]  # Remove the '.txt' extension
                    VocabularyManager.register_vocab(
                        vocabulary_name, Vocabulary.from_file(str(path))
                    )
