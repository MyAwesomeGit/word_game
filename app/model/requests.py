from pydantic import BaseModel, Field, validator


class GameCreateRequest(BaseModel):
    """Request model for game creation."""
    player1_name: str = Field(..., min_length=1, max_length=50)
    player2_name: str = Field(..., min_length=1, max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "player1_name": "Alice",
                "player2_name": "Bob"
            }
        }


class WordSubmitRequest(BaseModel):
    """Request model for word submission."""
    game_id: str
    player_name: str
    word: str

    @validator('word')
    def validate_word_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Word cannot be empty or whitespace')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "game_id": "abc12345",
                "player_name": "Alice",
                "word": "абрикос"
            }
        }
