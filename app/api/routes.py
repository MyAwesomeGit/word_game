from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_game_service, get_game_repository
from model.requests import GameCreateRequest, WordSubmitRequest
from repositories.game_repository import GameRepositoryInterface
from services.game_service import GameService
from core.exceptions import GameNotFoundException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create-game")
async def create_game(
        game_data: GameCreateRequest,
        game_service: GameService = Depends(get_game_service),
        game_repository: GameRepositoryInterface = Depends(get_game_repository)
):
    """Create a new game."""
    game = game_service.create_game(
        player1_name=game_data.player1_name,
        player2_name=game_data.player2_name
    )

    game_repository.save(game)

    return {
        "game_id": game.id,
        "message": "Game created successfully"
    }


@router.post("/submit-word")
async def submit_word(
        word_data: WordSubmitRequest,
        game_service: GameService = Depends(get_game_service),
        game_repository: GameRepositoryInterface = Depends(get_game_repository)
):
    """Submit a word in the game."""
    game = game_repository.find_by_id(word_data.game_id)

    if not game:
        raise GameNotFoundException(word_data.game_id)

    # Validation will raise appropriate exceptions if invalid
    game_service.validate_word_submission(
        word=word_data.word,
        game=game,
        player_name=word_data.player_name
    )

    game_service.process_word_submission(
        word=word_data.word,
        game=game,
        player_name=word_data.player_name
    )

    game_repository.save(game)

    return {
        "status": "success",
        "message": f"Word '{word_data.word}' accepted",
        "next_player": game.current_player.name,
        "next_letter": game.last_letter,
        "scores": {
            game.player1.name: game.player1.score,
            game.player2.name: game.player2.score
        }
    }


@router.get("/game-state/{game_id}")
async def get_game_state(
        game_id: str,
        game_repository: GameRepositoryInterface = Depends(get_game_repository)
):
    """Get current game state."""
    game = game_repository.find_by_id(game_id)

    if not game:
        raise GameNotFoundException(game_id)

    return {
        "game_id": game.id,
        "current_player": game.current_player.name,
        "last_letter": game.last_letter,
        "used_words": game.get_recent_words(),
        "total_words": len(game.used_words),
        "scores": {
            game.player1.name: game.player1.score,
            game.player2.name: game.player2.score
        },
        "status": game.status
    }


@router.post("/end-game/{game_id}")
async def end_game(
        game_id: str,
        game_service: GameService = Depends(get_game_service),
        game_repository: GameRepositoryInterface = Depends(get_game_repository)
):
    """End the game and declare winner."""
    game = game_repository.find_by_id(game_id)

    if not game:
        raise GameNotFoundException(game_id)

    if game.status == "finished":
        raise HTTPException(status_code=400, detail="Game already finished")

    result = game_service.end_game(game)
    game_repository.save(game)

    return result


@router.get("/game-stats/{game_id}")
async def game_stats(
        game_id: str,
        game_service: GameService = Depends(get_game_service),
        game_repository: GameRepositoryInterface = Depends(get_game_repository)
):
    """Get detailed statistics for a specific game."""
    game = game_repository.find_by_id(game_id)

    if not game:
        raise GameNotFoundException(game_id)

    return game_service.get_game_stats(game)


@router.get("/health")
async def health_check(
        game_repository: GameRepositoryInterface = Depends(get_game_repository)
):
    """Health check endpoint."""
    active_games = len(game_repository.get_all_active_games())
    total_games = game_repository.get_total_games_count()

    return {
        "status": "healthy",
        "active_games": active_games,
        "total_games": total_games,
        "timestamp": datetime.now().isoformat()
    }
