from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class GameStatus(str, Enum):
    """Game status enumeration."""
    ACTIVE = "active"
    FINISHED = "finished"


class GameResult(str, Enum):
    """Game result enumeration."""
    DRAW = "Ничья"


@dataclass
class WordEntry:
    """Represents a single word submission."""
    word: str
    player: str
    timestamp: str
    score_added: int


@dataclass
class Player:
    """Represents a player in the game."""
    name: str
    score: int = 0

    @property
    def words_count(self) -> int:
        # This will be calculated by the game service
        return 0


@dataclass
class Game:
    """Core game entity."""
    id: str
    player1: Player
    player2: Player
    current_player: Player
    used_words: List[str] = field(default_factory=list)
    last_letter: Optional[str] = None
    status: GameStatus = GameStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    word_history: List[WordEntry] = field(default_factory=list)

    @property
    def player1_score(self) -> int:
        return self.player1.score

    @player1_score.setter
    def player1_score(self, value: int) -> None:
        self.player1.score = value

    @property
    def player2_score(self) -> int:
        return self.player2.score

    @player2_score.setter
    def player2_score(self, value: int) -> None:
        self.player2.score = value

    def switch_turn(self) -> None:
        """Switch current player."""
        self.current_player = (
            self.player2 if self.current_player == self.player1
            else self.player1
        )

    def add_word(self, word_entry: WordEntry) -> None:
        """Add a word to the game history."""
        self.used_words.append(word_entry.word)
        self.word_history.append(word_entry)

        if word_entry.player == self.player1.name:
            self.player1.score += word_entry.score_added
        else:
            self.player2.score += word_entry.score_added

    def get_winner(self) -> str:
        """Determine the winner based on scores."""
        if self.player1.score > self.player2.score:
            return self.player1.name
        elif self.player2.score > self.player1.score:
            return self.player2.name
        return GameResult.DRAW

    def get_recent_words(self, count: int = 10) -> List[str]:
        """Get the most recent used words."""
        return self.used_words[-count:]
