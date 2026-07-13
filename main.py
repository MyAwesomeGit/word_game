from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import logging
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('word_game.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Word Game API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game state storage
games: Dict[str, dict] = {}


class GameCreate(BaseModel):
    player1_name: str
    player2_name: str


class WordSubmit(BaseModel):
    game_id: str
    player_name: str
    word: str


class GameState(BaseModel):
    game_id: str
    current_player: str
    last_letter: str
    used_words: List[str]
    player1_score: int
    player2_score: int
    status: str
    winner: Optional[str] = None


# Load dictionary (simplified - in production, use a real dictionary)
COMMON_WORDS = set([
    "абрикос", "автомобиль", "арбуз", "банан", "береза", "волк", "город",
    "дом", "дерево", "енот", "еж", "жираф", "жук", "зонт", "заяц",
    "иголка", "икра", "йогурт", "кот", "корова", "лес", "лиса", "луна",
    "мама", "медведь", "нос", "небо", "осел", "орел", "папа", "поле",
    "река", "рыба", "собака", "слон", "слово", "тигр", "утка", "ухо",
    "флаг", "хлеб", "цветок", "чай", "черепаха", "шкаф", "щенок",
    "экран", "юла", "яблоко", "якорь", "ящерица"
])

# Letters that rarely end words (no common words start with these)
HARD_ENDINGS = set(['ъ', 'ы', 'ь'])


def get_valid_start_letter(word: str) -> str:
    """Get the letter that the next word should start with"""
    last_letter = word[-1].lower()
    if last_letter in HARD_ENDINGS:
        if len(word) >= 2:
            return word[-2].lower()
    return last_letter


@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("WORD GAME API STARTED")
    logger.info(f"Server time: {datetime.now().isoformat()}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    active_games = len([g for g in games.values() if g["status"] == "active"])
    logger.info("=" * 60)
    logger.info("WORD GAME API SHUTTING DOWN")
    logger.info(f"Active games at shutdown: {active_games}")
    logger.info(f"Total games created: {len(games)}")
    logger.info("=" * 60)


@app.post("/create-game")
async def create_game(game_data: GameCreate):
    """Create a new game"""
    game_id = str(uuid.uuid4())[:8]

    logger.info("=" * 60)
    logger.info("NEW GAME CREATED")
    logger.info(f"Game ID: {game_id}")
    logger.info(f"Player 1: {game_data.player1_name}")
    logger.info(f"Player 2: {game_data.player2_name}")
    logger.info(f"Start time: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    games[game_id] = {
        "id": game_id,
        "player1": game_data.player1_name,
        "player2": game_data.player2_name,
        "current_player": game_data.player1_name,
        "used_words": [],
        "last_letter": None,
        "player1_score": 0,
        "player2_score": 0,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "word_history": []  # Store all words with timestamps and players
    }

    return {"game_id": game_id, "message": "Game created successfully"}


@app.post("/submit-word")
async def submit_word(word_data: WordSubmit):
    """Submit a word in the game"""
    game = games.get(word_data.game_id)

    if not game:
        logger.warning(f"WORD SUBMISSION FAILED - Game not found: {word_data.game_id}")
        raise HTTPException(status_code=404, detail="Game not found")

    if game["status"] != "active":
        logger.warning(f"WORD SUBMISSION FAILED - Game {word_data.game_id} is not active (status: {game['status']})")
        raise HTTPException(status_code=400, detail="Game is not active")

    if word_data.player_name != game["current_player"]:
        logger.warning(
            f"WORD SUBMISSION FAILED - Wrong turn. Expected: {game['current_player']}, Got: {word_data.player_name}")
        raise HTTPException(status_code=400, detail="Not your turn")

    word = word_data.word.lower().strip()
    timestamp = datetime.now().isoformat()

    logger.info(f"WORD SUBMISSION - Game: {word_data.game_id}, Player: {word_data.player_name}, Word: '{word}'")

    # Check if word is valid
    if not word or len(word) < 2:
        logger.warning(f"WORD REJECTED - Too short: '{word}'")
        raise HTTPException(status_code=400, detail="Word is too short")

    # Check if word is in dictionary (simplified check)
    if word not in COMMON_WORDS:
        if len(word) < 3:
            logger.warning(f"WORD REJECTED - Too short (not in dictionary): '{word}'")
            raise HTTPException(status_code=400, detail="Word is too short")

    # Check if word starts with the correct letter
    if game["last_letter"]:
        if word[0] != game["last_letter"]:
            logger.warning(
                f"WORD REJECTED - Wrong starting letter. Required: '{game['last_letter']}', Got: '{word[0]}'")
            raise HTTPException(
                status_code=400,
                detail=f"Word must start with letter '{game['last_letter']}'"
            )

    # Check if word was already used
    if word in game["used_words"]:
        logger.warning(f"WORD REJECTED - Already used: '{word}'")
        raise HTTPException(status_code=400, detail="Word already used")

    # Add word to used words
    game["used_words"].append(word)
    game["word_history"].append({
        "word": word,
        "player": word_data.player_name,
        "timestamp": timestamp,
        "score_added": len(word)
    })

    # Update last letter for next word
    game["last_letter"] = get_valid_start_letter(word)

    # Update score
    if game["current_player"] == game["player1"]:
        game["player1_score"] += len(word)
        logger.info(f"SCORE UPDATE - {game['player1']}: +{len(word)} points (total: {game['player1_score']})")
    else:
        game["player2_score"] += len(word)
        logger.info(f"SCORE UPDATE - {game['player2']}: +{len(word)} points (total: {game['player2_score']})")

    # Switch players
    previous_player = game["current_player"]
    game["current_player"] = (
        game["player2"]
        if game["current_player"] == game["player1"]
        else game["player1"]
    )

    logger.info(f"TURN SWITCH - {previous_player} → {game['current_player']}")
    logger.info(f"NEXT LETTER REQUIRED: '{game['last_letter']}'")
    logger.info(f"TOTAL WORDS: {len(game['used_words'])}")
    logger.info("-" * 40)

    return {
        "status": "success",
        "message": f"Word '{word}' accepted",
        "next_player": game["current_player"],
        "next_letter": game["last_letter"],
        "scores": {
            game["player1"]: game["player1_score"],
            game["player2"]: game["player2_score"]
        }
    }


@app.get("/game-state/{game_id}")
async def get_game_state(game_id: str):
    """Get current game state"""
    game = games.get(game_id)
    if not game:
        logger.warning(f"GAME STATE REQUEST - Game not found: {game_id}")
        raise HTTPException(status_code=404, detail="Game not found")

    logger.info(f"GAME STATE REQUEST - Game: {game_id}, Status: {game['status']}")

    return {
        "game_id": game["id"],
        "current_player": game["current_player"],
        "last_letter": game["last_letter"],
        "used_words": game["used_words"][-10:],
        "total_words": len(game["used_words"]),
        "scores": {
            game["player1"]: game["player1_score"],
            game["player2"]: game["player2_score"]
        },
        "status": game["status"]
    }


@app.post("/end-game/{game_id}")
async def end_game(game_id: str):
    """End the game and declare winner"""
    game = games.get(game_id)
    if not game:
        logger.warning(f"GAME END ATTEMPT - Game not found: {game_id}")
        raise HTTPException(status_code=404, detail="Game not found")

    if game["status"] == "finished":
        logger.warning(f"GAME END ATTEMPT - Game already finished: {game_id}")
        raise HTTPException(status_code=400, detail="Game already finished")

    logger.info("=" * 60)
    logger.info(f"GAME ENDING - Game ID: {game_id}")
    logger.info(f"Duration: {datetime.now().isoformat()} - {game['created_at']}")

    # Calculate game duration
    start_time = datetime.fromisoformat(game["created_at"])
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Total game time: {duration}")

    game["status"] = "finished"

    # Determine winner based on score
    if game["player1_score"] > game["player2_score"]:
        winner = game["player1"]
    elif game["player2_score"] > game["player1_score"]:
        winner = game["player2"]
    else:
        winner = "Ничья"

    logger.info(
        f"FINAL SCORES - {game['player1']}: {game['player1_score']}, {game['player2']}: {game['player2_score']}")
    logger.info(f"WINNER: {winner}")
    logger.info(f"TOTAL WORDS PLAYED: {len(game['used_words'])}")
    logger.info(f"WORD HISTORY:")

    # Log complete word history
    for i, entry in enumerate(game["word_history"], 1):
        logger.info(f"  {i}. {entry['word']} ({entry['player']}) - +{entry['score_added']} pts - {entry['timestamp']}")

    logger.info("=" * 60)

    return {
        "status": "finished",
        "winner": winner,
        "final_scores": {
            game["player1"]: game["player1_score"],
            game["player2"]: game["player2_score"]
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    active_games = len([g for g in games.values() if g["status"] == "active"])
    total_games = len(games)

    logger.info(f"HEALTH CHECK - Active games: {active_games}, Total games: {total_games}")
    return {
        "status": "healthy",
        "active_games": active_games,
        "total_games": total_games,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/game-stats/{game_id}")
async def game_stats(game_id: str):
    """Get detailed statistics for a specific game"""
    game = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    logger.info(f"STATS REQUEST - Game: {game_id}")

    return {
        "game_id": game["id"],
        "created_at": game["created_at"],
        "status": game["status"],
        "player1": {
            "name": game["player1"],
            "score": game["player1_score"],
            "words_count": len([w for w in game["word_history"] if w["player"] == game["player1"]])
        },
        "player2": {
            "name": game["player2"],
            "score": game["player2_score"],
            "words_count": len([w for w in game["word_history"] if w["player"] == game["player2"]])
        },
        "total_words": len(game["used_words"]),
        "word_list": game["word_history"]
    }
