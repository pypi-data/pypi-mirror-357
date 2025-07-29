import logging

from typing import Dict, Optional
from threading import Lock, Thread

logger = logging.getLogger(__name__)

class Mapping:

    @staticmethod
    def from_file(file_path: str, delimiter: str = "#") -> "Mapping":
        """
        Load mappings from a file.

        :param file_path: Path to the file containing mappings.
        :return: An instance of Mapping with loaded data.
        """
        mapping = Mapping()
        mapping.__map = {}
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                key, value = line.strip().split(delimiter)
                mapping.__map[key] = value
        return mapping
    
    @staticmethod
    def combine(*mappings: "Mapping") -> "Mapping":
        """
        Combine multiple Mapping instances into one.

        :param mappings: Mapping instances to combine.
        :return: A new Mapping instance containing all mappings.
        """
        combined = Mapping()
        combined.__map = {}
        for mapping in mappings:
            combined.__map.update(mapping.__map)
        return combined

    def get(self, key: str, default: Optional[str] = None, raise_error: bool = True) -> str:
        """
        Get the value for a given key.

        :param key: The key to look up.
        :return: The corresponding value or None if not found.
        """
        if default is not None:
            raise_error = False
        return self.__map[key] if raise_error else self.__map.get(key, default)

    def contains(self, key: str) -> bool:
        """
        Check if the mapping contains a specific key.

        :param key: The key to check.
        :return: True if the key exists, False otherwise.
        """
        return key in self.__map


class MappingManager:
    _registry = {}
    _lock = Lock()  # For thread-safety

    @classmethod
    def register_mapping(cls, name: str, mapping: Mapping):
        """
        Register a new mapping.

        :param name: The name of the mapping.
        :param mapping: An instance of Mapping to register.
        """
        with cls._lock:
            if name in cls._registry:
                logger.info(f"Mapping '{name}' is already registered.")
            cls._registry[name] = mapping

    @classmethod
    def get_mapping(cls, name: str) -> Mapping:
        """
        Retrieve a registered mapping by its name.

        :param name: The name of the mapping to retrieve.
        :return: The Mapping instance associated with the given name.
        :raises KeyError: If the mapping is not found.
        """
        with cls._lock:
            if name not in cls._registry:
                raise KeyError(f"Mapping '{name}' not found.")
            return cls._registry[name]
