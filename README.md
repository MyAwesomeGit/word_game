# Word Game (backend)

⚠️ **NOTICE:** This project is currently under active development. Features, APIs, and structure are subject to change. Not recommended for production use at this stage.

A full-stack two-player word game where players take turns entering words that begin with the last letter of the previous word. The project consists of an iOS client built with SwiftUI and a Python backend powered by FastAPI.

## Gameplay

- Two players create a game session
- Players alternate submitting words
- Each new word must start with the last letter of the previous word
- Points are awarded based on word length
- Smart handling of words ending with ъ, ы, ь (uses the preceding letter)
- The game tracks scores, used words, and declares a winner

## Tech Stack

- Python 3.13: Runtime
- FastAPI: Web framework
- Pydantic: Data validation
- Uvicorn: ASGI server
- Docker: Containerization

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/create-game` | Create a new game session |
| POST | `/submit-word` | Submit a word for the current player |
| GET | `/game-state/{game_id}` | Get current game state |
| POST | `/end-game/{game_id}` | End the game and declare a winner |
| GET | `/health` | Health check endpoint |
| GET | `/game-stats/{game_id}` | Get detailed game statistics |

## Logging & Monitoring

The backend includes comprehensive logging for debugging and game monitoring:

### Log Output
All logs are written to both console and `word_game.log` file with timestamps:

2024-07-13 14:30:15,123 - INFO - NEW GAME CREATED  
2024-07-13 14:30:15,123 - INFO - Game ID: a1b2c3d4  
2024-07-13 14:30:15,123 - INFO - Player 1: Alice  
2024-07-13 14:30:15,123 - INFO - Player 2: Bob  
2024-07-13 14:30:15,123 - INFO - Start time: 2024-07-13T14:30:15.123456

## Setup

- Clone the repository:
```bash

```
- Install dependencies:
```bash
pip install -r requirements.txt
```
- Run the server:
```bash
uvicorn main:app --reload --log-level info
```
- Access the API at:
```bash
http://localhost:8000
```
