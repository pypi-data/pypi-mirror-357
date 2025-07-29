import regex


class BasePattern:
    def get_regex_pattern(self) -> str:
        """
        Get the regex pattern.

        :return: The regex pattern string.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def handle_match(self, matcher: regex.Match) -> str:
        """
        Handle the match found by the regex pattern.

        :param matcher: The re.Match object containing the match.
        :return: The string to replace the matched text.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_priority(self) -> int:
        """
        Get the priority of the pattern.

        :return: An integer representing the priority.
        """
        return 0
