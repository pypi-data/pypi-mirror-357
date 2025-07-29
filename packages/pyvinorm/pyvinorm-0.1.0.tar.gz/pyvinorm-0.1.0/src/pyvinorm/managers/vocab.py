import logging
from typing import Dict
from threading import Lock, Thread


logger = logging.getLogger(__name__)


class Vocabulary:

    @staticmethod
    def from_file(file_path: str) -> "Vocabulary":
        """
        Load mappings from a file.

        :param file_path: Path to the file containing mappings.
        :return: An instance of Vocabulary with loaded data.
        """
        vocabulary = Vocabulary()
        vocabulary.__vocab = set()
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                word = line.strip()
                if word:
                    vocabulary.__vocab.add(word)
        return vocabulary

    def contains(self, word: str) -> bool:
        """
        Check if the vocabulary contains a specific word.

        :param word: The word to check.
        :return: True if the word exists, False otherwise.
        """
        return word in self.__vocab

    def get_all_words(self) -> set:
        """
        Get all words in the vocabulary.

        :return: A set of all words in the vocabulary.
        """
        return self.__vocab.copy()


class VocabularyManager:
    _registry = {}
    _lock = Lock()  # For thread-safety

    @classmethod
    def register_vocab(cls, name: str, vocab: Vocabulary):
        """
        Register a new vocabulary.

        :param name: The name of the vocabulary.
        :param vocab: An instance of Vocabulary to register.
        """
        with cls._lock:
            if name in cls._registry:
                logger.info(f"Vocabulary '{name}' is already registered.")
            cls._registry[name] = vocab

    @classmethod
    def get_vocab(cls, name: str) -> Vocabulary:
        """
        Retrieve a registered vocabulary by its name.

        :param name: The name of the vocabulary to retrieve.
        :return: The Vocabulary instance associated with the given name.
        :raises KeyError: If the vocabulary is not found.
        """
        with cls._lock:
            if name not in cls._registry:
                raise KeyError(f"Vocabulary '{name}' not found.")
            return cls._registry[name]
