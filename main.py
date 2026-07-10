from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

app = FastAPI(title="Word Game API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your iOS app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game state storage (in production, use a database)
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
        # Use the preceding letter
        if len(word) >= 2:
            return word[-2].lower()
    return last_letter


@app.post("/create-game")
async def create_game(game_data: GameCreate):
    """Create a new game"""
    import uuid
    game_id = str(uuid.uuid4())[:8]

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
        "created_at": datetime.now().isoformat()
    }

    return {"game_id": game_id, "message": "Game created successfully"}


@app.post("/submit-word")
async def submit_word(word_data: WordSubmit):
    """Submit a word in the game"""
    game = games.get(word_data.game_id)

    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game["status"] != "active":
        raise HTTPException(status_code=400, detail="Game is not active")

    if word_data.player_name != game["current_player"]:
        raise HTTPException(status_code=400, detail="Not your turn")

    word = word_data.word.lower().strip()

    # Check if word is valid
    if not word or len(word) < 2:
        raise HTTPException(status_code=400, detail="Word is too short")

    # Check if word is in dictionary (simplified check)
    if word not in COMMON_WORDS:
        # For testing, accept any word with 2+ letters
        if len(word) < 3:
            raise HTTPException(status_code=400, detail="Word is too short")

    # Check if word starts with the correct letter
    if game["last_letter"]:
        if word[0] != game["last_letter"]:
            raise HTTPException(
                status_code=400,
                detail=f"Word must start with letter '{game['last_letter']}'"
            )

    # Check if word was already used
    if word in game["used_words"]:
        raise HTTPException(status_code=400, detail="Word already used")

    # Add word to used words
    game["used_words"].append(word)

    # Update last letter for next word
    game["last_letter"] = get_valid_start_letter(word)

    # Update score
    if game["current_player"] == game["player1"]:
        game["player1_score"] += len(word)
    else:
        game["player2_score"] += len(word)

    # Switch players
    game["current_player"] = (
        game["player2"]
        if game["current_player"] == game["player1"]
        else game["player1"]
    )

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
        raise HTTPException(status_code=404, detail="Game not found")

    return {
        "game_id": game["id"],
        "current_player": game["current_player"],
        "last_letter": game["last_letter"],
        "used_words": game["used_words"][-10:],  # Last 10 words
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
        raise HTTPException(status_code=404, detail="Game not found")

    game["status"] = "finished"

    # Determine winner based on score
    if game["player1_score"] > game["player2_score"]:
        winner = game["player1"]
    elif game["player2_score"] > game["player1_score"]:
        winner = game["player2"]
    else:
        winner = "Ничья"

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
    return {"status": "healthy"}