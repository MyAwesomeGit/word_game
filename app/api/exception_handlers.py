from fastapi import Request
from fastapi.responses import JSONResponse
from core.exceptions import (
    GameNotFoundException,
    GameNotActiveException,
    InvalidTurnException,
    WordValidationException
)
import logging

logger = logging.getLogger(__name__)


async def game_not_found_handler(request: Request, exc: GameNotFoundException):
    """Handle GameNotFoundException."""
    logger.warning(f"Game not found: {exc.game_id}")
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "game_id": exc.game_id}
    )


async def game_not_active_handler(request: Request, exc: GameNotActiveException):
    """Handle GameNotActiveException."""
    logger.warning(f"Game not active: {exc.game_id} (status: {exc.status})")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "game_id": exc.game_id, "status": exc.status}
    )


async def invalid_turn_handler(request: Request, exc: InvalidTurnException):
    """Handle InvalidTurnException."""
    logger.warning(f"Invalid turn: {exc.player_name} (current: {exc.current_player})")
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "current_player": exc.current_player
        }
    )


async def word_validation_handler(request: Request, exc: WordValidationException):
    """Handle WordValidationException."""
    logger.warning(f"Word validation failed: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(GameNotFoundException, game_not_found_handler)
    app.add_exception_handler(GameNotActiveException, game_not_active_handler)
    app.add_exception_handler(InvalidTurnException, invalid_turn_handler)
    app.add_exception_handler(WordValidationException, word_validation_handler)
