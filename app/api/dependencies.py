from functools import lru_cache

from core.config import GameConfig
from repositories.game_repository import InMemoryGameRepository, GameRepositoryInterface
from services.game_service import GameService
from services.word_service import (
    InMemoryDictionaryProvider,
    WordValidator,
    WordProcessor
)


# Pre-populated dictionary
COMMON_WORDS = set([
    "абрикос", "автомобиль", "арбуз", "банан", "береза", "волк", "город",
    "дом", "дерево", "енот", "еж", "жираф", "жук", "зонт", "заяц",
    "иголка", "икра", "йогурт", "кот", "корова", "лес", "лиса", "луна",
    "мама", "медведь", "нос", "небо", "осел", "орел", "папа", "поле",
    "река", "рыба", "собака", "слон", "слово", "тигр", "утка", "ухо",
    "флаг", "хлеб", "цветок", "чай", "черепаха", "шкаф", "щенок",
    "экран", "юла", "яблоко", "якорь", "ящерица"
])


@lru_cache()
def get_config() -> GameConfig:
    """Get application configuration."""
    return GameConfig()


@lru_cache()
def get_dictionary_provider() -> InMemoryDictionaryProvider:
    """Get dictionary provider with pre-populated words."""
    return InMemoryDictionaryProvider(words=COMMON_WORDS)


@lru_cache()
def get_word_validator() -> WordValidator:
    """Get word validator instance."""
    config = get_config()
    dictionary = get_dictionary_provider()
    return WordValidator(dictionary, config)


@lru_cache()
def get_word_processor() -> WordProcessor:
    """Get word processor instance."""
    config = get_config()
    return WordProcessor(config)


@lru_cache()
def get_game_repository() -> GameRepositoryInterface:
    """Get game repository instance."""
    return InMemoryGameRepository()


@lru_cache()
def get_game_service() -> GameService:
    """Get game service instance."""
    config = get_config()
    word_validator = get_word_validator()
    word_processor = get_word_processor()
    return GameService(
        word_validator=word_validator,
        word_processor=word_processor,
        game_id_length=config.GAME_ID_LENGTH
    )