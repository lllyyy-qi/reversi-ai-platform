from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import numpy as np
from typing import List, Optional
import time

from .ai_engine import ai_service, generate_actions_filter, update_chessboard, COLOR_BLACK, COLOR_WHITE, COLOR_NONE

app = FastAPI(title="Reversi AI Platform")

# 关键修复：允许所有来源，并允许携带凭证
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 数据模型
class UserLogin(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str


class MoveRequest(BaseModel):
    board: List[List[int]]
    player: int


class MoveResponse(BaseModel):
    move: Optional[List[int]] = None
    candidate_moves: List[List[int]]
    game_over: bool = False
    winner: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: str


# 临时用户存储
users = {}


@app.get("/")
async def root():
    return {"message": "Reversi AI Platform API"}


@app.post("/api/register", response_model=UserResponse)
async def register(user: UserCreate):
    print(f"注册尝试: {user.email}")  # 添加日志
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")

    users[user.email] = user.password
    print(f"当前用户: {users}")  # 添加日志
    return {
        "id": len(users),
        "email": user.email,
        "created_at": "2024-01-01T00:00:00"
    }


@app.post("/api/login")
async def login(user: UserLogin):
    print(f"登录尝试: {user.email}")  # 添加日志
    print(f"密码匹配: {users.get(user.email) == user.password}")  # 添加日志

    if user.email not in users or users[user.email] != user.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return {
        "access_token": "fake-token-12345",
        "token_type": "bearer"
    }


@app.get("/api/me")
async def get_me():
    # 简化版，总是返回第一个用户
    if not users:
        raise HTTPException(status_code=401, detail="No users")

    first_email = list(users.keys())[0]
    return {
        "id": 1,
        "email": first_email,
        "created_at": "2024-01-01T00:00:00"
    }


@app.post("/api/move", response_model=MoveResponse)
async def get_ai_move(request: MoveRequest):
    """获取AI的下一步移动"""
    board = np.array(request.board)
    player = request.player

    # 获取所有合法移动
    legal_moves = generate_actions_filter(board, player)
    legal_moves_list = [[int(r), int(c)] for r, c in legal_moves]

    if not legal_moves:
        # 检查游戏是否结束
        opponent_moves = generate_actions_filter(board, -player)
        game_over = not opponent_moves
        winner = None
        if game_over:
            black_count = np.sum(board == COLOR_BLACK)
            white_count = np.sum(board == COLOR_WHITE)
            if black_count > white_count:
                winner = COLOR_BLACK
            elif white_count > black_count:
                winner = COLOR_WHITE
            else:
                winner = 0

        return MoveResponse(
            move=None,
            candidate_moves=legal_moves_list,
            game_over=game_over,
            winner=winner
        )

    # 使用AI选择最佳移动
    ai = ai_service.create_ai("default")
    ai.chessboard = board
    ai.color = player
    ai.candidate_list = []

    # 调用AI决策
    ai.go(board)

    best_move = None
    if len(ai.candidate_list) > 1:
        best_move = ai.candidate_list[-1]
        best_move = [int(best_move[0]), int(best_move[1])]

    return MoveResponse(
        move=best_move,
        candidate_moves=legal_moves_list,
        game_over=False,
        winner=None
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)