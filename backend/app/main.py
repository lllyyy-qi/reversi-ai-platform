from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import numpy as np
import asyncio
import concurrent.futures
import time
from typing import List, Optional

from .ai_engine import ai_service, generate_actions_filter, update_chessboard, COLOR_BLACK, COLOR_WHITE, COLOR_NONE

app = FastAPI(title="Reversi AI Platform")

# CORS 允许 5173 和 5174
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 数据模型 ==========
class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str

class MoveRequest(BaseModel):
    board: List[List[int]]
    player: int
    move: Optional[List[int]] = None  # 如果有值，表示玩家落子；否则 AI 选择

class MoveResponse(BaseModel):
    board: List[List[int]]            # 执行后的棋盘
    move: Optional[List[int]] = None  # AI 选择的移动（如果是 AI 移动）
    candidate_moves: List[List[int]]  # 下一玩家的合法移动
    game_over: bool = False
    winner: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: str

# ========== 临时用户存储 ==========
users = {}

# ========== API 端点 ==========
@app.get("/")
async def root():
    return {"message": "Reversi AI Platform API"}

@app.post("/api/register", response_model=UserResponse)
async def register(user: UserCreate):
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    users[user.email] = user.password
    return {"id": len(users), "email": user.email, "created_at": "2024-01-01T00:00:00"}

@app.post("/api/login")
async def login(user: UserLogin):
    if user.email not in users or users[user.email] != user.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": "fake-token-12345", "token_type": "bearer"}

@app.get("/api/me")
async def get_me():
    if not users:
        raise HTTPException(status_code=401, detail="No users")
    first_email = list(users.keys())[0]
    return {"id": 1, "email": first_email, "created_at": "2024-01-01T00:00:00"}

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "timestamp": time.time()}

@app.post("/api/legal_moves", response_model=List[List[int]])
async def get_legal_moves(data: dict):
    """只返回合法移动，不改变棋盘"""
    board = np.array(data["board"])
    player = data["player"]
    legal = generate_actions_filter(board, player)
    return [[int(r), int(c)] for r, c in legal]


@app.post("/api/move", response_model=MoveResponse)
async def move(request: MoveRequest):
    board = np.array(request.board)
    player = request.player
    user_move = request.move

    try:
        # 如果提供了 user_move，则应用玩家移动
        if user_move is not None:
            r, c = user_move
            # 验证合法性
            legal_moves = generate_actions_filter(board, player)
            if (r, c) not in legal_moves:
                raise HTTPException(status_code=400, detail="Illegal move")
            # 应用移动
            update_chessboard(board, (r, c), player)
            move_made = user_move
            print(f"玩家移动: ({r}, {c})")
        else:
            # AI 选择移动
            ai = ai_service.create_ai("default")

            # 先获取当前玩家的合法移动
            current_legal = generate_actions_filter(board, player)
            print(f"AI决策前 - 玩家: {player}, 合法移动数: {len(current_legal)}")

            if len(current_legal) == 0:
                # 当前玩家没有合法移动
                print("当前玩家没有合法移动，跳过")
                move_made = None
            else:
                # 在线程池中运行AI决策
                try:
                    future = executor.submit(run_ai_decision, ai, board.copy(), player)
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: future.result(timeout=3)
                    )

                    if result is None:
                        print("AI决策返回None")
                        # 如果AI返回None，使用第一个合法移动
                        if len(current_legal) > 0:
                            result = current_legal[0]
                            print(f"使用默认移动: {result}")

                    if result is not None:
                        move_made = result
                        r, c = move_made
                        update_chessboard(board, (r, c), player)
                        print(f"AI移动: ({r}, {c})")
                    else:
                        move_made = None

                except concurrent.futures.TimeoutError:
                    print("AI决策超时")
                    future.cancel()
                    # 超时后使用第一个合法移动
                    if len(current_legal) > 0:
                        move_made = current_legal[0]
                        r, c = move_made
                        update_chessboard(board, (r, c), player)
                        print(f"超时使用默认移动: ({r}, {c})")
                    else:
                        move_made = None
                except Exception as e:
                    print(f"AI执行出错: {e}")
                    import traceback
                    traceback.print_exc()
                    move_made = None

        # 切换玩家
        next_player = -player
        # 获取下一玩家的合法移动
        legal_moves_next = generate_actions_filter(board, next_player)
        print(f"下一玩家: {next_player}, 合法移动数: {len(legal_moves_next)}")

        game_over = False
        winner = None

        # 检查游戏是否结束
        if len(legal_moves_next) == 0:
            # 检查对方是否也无棋
            if len(generate_actions_filter(board, -next_player)) == 0:
                game_over = True
                black_count = np.sum(board == COLOR_BLACK)
                white_count = np.sum(board == COLOR_WHITE)
                print(f"游戏结束 - 黑:{black_count}, 白:{white_count}")
                # 反向黑白棋：棋子少的一方赢
                if black_count < white_count:
                    winner = COLOR_BLACK
                elif white_count < black_count:
                    winner = COLOR_WHITE
                else:
                    winner = 0

        return MoveResponse(
            board=board.tolist(),
            move=[int(move_made[0]), int(move_made[1])] if move_made is not None else None,
            candidate_moves=[[int(r), int(c)] for r, c in legal_moves_next],
            game_over=game_over,
            winner=winner
        )
    except Exception as e:
        print(f"move端点异常: {e}")
        import traceback
        traceback.print_exc()
        legal_moves_next = generate_actions_filter(board, -player)
        return MoveResponse(
            board=board.tolist(),
            move=None,
            candidate_moves=[[int(r), int(c)] for r, c in legal_moves_next],
            game_over=False,
            winner=None
        )

# 辅助函数：运行AI决策
def run_ai_decision(ai, board, player):
    """在线程中运行AI决策"""
    try:
        ai.chessboard = board
        ai.color = player
        ai.candidate_list = []
        ai.go(board)
        if len(ai.candidate_list) > 1:
            return ai.candidate_list[-1]
        return None
    except Exception as e:
        print(f"AI决策线程错误: {e}")
        return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)