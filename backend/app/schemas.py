from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Game schemas
class GameBase(BaseModel):
    game_type: str
    player_color: Optional[int] = None
    moves: List[tuple]
    result: str
    final_board: List[List[int]]


class GameCreate(GameBase):
    pass


class Game(GameBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Move schemas
class MoveRequest(BaseModel):
    board: List[List[int]]
    player: int  # -1 or 1


class MoveResponse(BaseModel):
    move: Optional[tuple] = None
    candidate_moves: List[tuple]
    game_over: bool = False
    winner: Optional[int] = None


class AIVersusAIRequest(BaseModel):
    black_ai_params: Optional[dict] = None
    white_ai_params: Optional[dict] = None
    delay: float = 0.5  # 每一步的延迟，用于观战


class Token(BaseModel):
    access_token: str
    token_type: str