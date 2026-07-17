from typing import Optional, Protocol, Set

from core.config import GameConfig


class DictionaryProvider(Protocol):
    """Protocol for dictionary providers (Dependency Inversion)."""

    def get_valid_words(self) -> Set[str]:
        ...


class InMemoryDictionaryProvider:
    """Simple in-memory dictionary implementation."""

    def __init__(self, words: Optional[Set[str]] = None):
        self._words = words or set()

    def get_valid_words(self) -> Set[str]:
        return self._words


class WordValidator:
    """Handles word validation logic (SRP)."""

    def __init__(
            self,
            dictionary: DictionaryProvider,
            config: GameConfig
    ):
        self._dictionary = dictionary
        self._config = config

    def is_valid_length(self, word: str) -> bool:
        """Check if word meets minimum length requirements."""
        return len(word) >= self._config.MIN_WORD_LENGTH

    def is_in_dictionary(self, word: str) -> bool:
        """Check if word exists in dictionary."""
        valid_words = self._dictionary.get_valid_words()

        if word in valid_words:
            return True

        # Allow short words if they meet minimum criteria
        return len(word) >= self._config.MIN_DICTIONARY_WORD_LENGTH

    def has_valid_start_letter(
            self,
            word: str,
            expected_letter: Optional[str]
    ) -> bool:
        """Check if word starts with the expected letter."""
        if expected_letter is None:
            return True
        return word[0] == expected_letter


class WordProcessor:
    """Handles word processing and letter extraction (SRP)."""

    def __init__(self, config: GameConfig):
        self._config = config

    def get_next_start_letter(self, word: str) -> str:
        """Get the letter that the next word should start with."""
        last_letter = word[-1].lower()

        if last_letter in self._config.HARD_ENDINGS and len(word) >= 2:
            return word[-2].lower()

        return last_letter

    def normalize_word(self, word: str) -> str:
        """Normalize word for comparison."""
        return word.lower().strip()
