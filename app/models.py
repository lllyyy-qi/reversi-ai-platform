from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    games = relationship("Game", back_populates="user")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_type = Column(String)  # "human_vs_ai" 或 "ai_vs_ai"
    player_color = Column(Integer)  # -1 for black, 1 for white
    result = Column(String)  # "win", "loss", "draw"
    moves = Column(JSON)  # 存储每一步的落子
    final_board = Column(JSON)  # 最终棋盘状态
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="games")