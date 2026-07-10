# Word Game (backend)

⚠️ NOTICE: This project is currently under active development. Features, APIs, and structure are subject to change. Not recommended for production use at this stage.

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

- POST	/create-game	
- POST	/submit-word
- GET	/game-state/{game_id}
- POST	/end-game/{game_id}
- GET	/health