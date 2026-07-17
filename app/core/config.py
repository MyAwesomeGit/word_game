from dataclasses import dataclass, field
from typing import Set


@dataclass(frozen=True)
class GameConfig:
    """Application configuration constants."""
    MIN_WORD_LENGTH: int = 2
    MIN_DICTIONARY_WORD_LENGTH: int = 3
    HARD_ENDINGS: Set[str] = field(default_factory=lambda: {'ъ', 'ы', 'ь'})
    MAX_RECENT_WORDS_DISPLAY: int = 10
    GAME_ID_LENGTH: int = 8
