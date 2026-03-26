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
    ai_candidates: Optional[List[List[int]]] = None  # AI 候选移动列表

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
    import time
    request_time = time.time()
    print(f"\n{'='*50}")
    print(f"[API] /move 被调用 at {time.strftime('%H:%M:%S')}")
    print(f"[API] 请求参数: player={request.player}, user_move={request.move}")
    
    board = np.array(request.board)
    player = request.player
    user_move = request.move
    
    # 打印棋盘状态
    black_count = np.sum(board == COLOR_BLACK)
    white_count = np.sum(board == COLOR_WHITE)
    empty_count = np.sum(board == COLOR_NONE)
    print(f"[API] 当前棋盘: 黑={black_count}, 白={white_count}, 空={empty_count}")
    
    try:
        # 如果提供了 user_move，则应用玩家移动
        if user_move is not None:
            print(f"[API] 处理玩家移动: {user_move}")
            r, c = user_move
            # 验证合法性
            legal_moves = generate_actions_filter(board, player)
            print(f"[API] 当前合法移动: {legal_moves}")
            
            if (r, c) not in legal_moves:
                print(f"[API] 错误: 非法移动 {user_move}")
                raise HTTPException(status_code=400, detail="Illegal move")
            
            # 应用移动
            update_chessboard(board, (r, c), player)
            move_made = user_move
            print(f"[API] 玩家移动应用成功")
            
        else:
            # AI 选择移动
            print(f"[API] AI决策开始 - 玩家: {player} ({'黑棋' if player == -1 else '白棋'})")
            ai = ai_service.get_ai("default")
            print(f"[API] 获取AI实例成功")
            
            # 获取当前玩家的合法移动
            current_legal = generate_actions_filter(board, player)
            print(f"[API] 当前合法移动数: {len(current_legal)}")
            if len(current_legal) > 0:
                print(f"[API] 合法移动示例: {current_legal[:5]}")
            
            if len(current_legal) == 0:
                print(f"[API] 当前玩家没有合法移动")
                move_made = None
            else:
                try:
                    print(f"[API] 调用AI.get_move()...")
                    start_ai = time.time()
                    best_move, all_moves = ai.get_move(board.copy(), player)
                    ai_time = time.time() - start_ai
                    print(f"[API] AI.get_move() 完成，耗时: {ai_time:.3f}秒")
                    print(f"[API] AI返回: best_move={best_move}, 候选数={len(all_moves)}")
                    
                    if best_move is not None:
                        move_made = best_move
                        r, c = move_made
                        update_chessboard(board, (r, c), player)
                        print(f"[API] AI移动: ({r}, {c})")
                    else:
                        print(f"[API] AI返回None，使用第一个合法移动")
                        move_made = current_legal[0]
                        r, c = move_made
                        update_chessboard(board, (r, c), player)
                        
                except Exception as e:
                    print(f"[API] AI执行出错: {e}")
                    import traceback
                    traceback.print_exc()
                    if len(current_legal) > 0:
                        move_made = current_legal[0]
                        r, c = move_made
                        update_chessboard(board, (r, c), player)
                    else:
                        move_made = None

        # 切换玩家
        next_player = -player
        # 获取下一玩家的合法移动
        legal_moves_next = generate_actions_filter(board, next_player)
        print(f"[API] 下一玩家: {next_player} ({'黑棋' if next_player == -1 else '白棋'}), 合法移动数: {len(legal_moves_next)}")
        
        game_over = False
        winner = None

        # 检查游戏是否结束
        if len(legal_moves_next) == 0:
            # 检查对方是否也无棋
            opponent_moves = generate_actions_filter(board, -next_player)
            if len(opponent_moves) == 0:
                game_over = True
                black_count = np.sum(board == COLOR_BLACK)
                white_count = np.sum(board == COLOR_WHITE)
                print(f"[API] 游戏结束 - 黑:{black_count}, 白:{white_count}")
                # 反向黑白棋：棋子少的一方赢
                if black_count < white_count:
                    winner = COLOR_BLACK
                elif white_count < black_count:
                    winner = COLOR_WHITE
                else:
                    winner = 0
                print(f"[API] 胜者: {winner} ({'黑棋' if winner == -1 else '白棋' if winner == 1 else '平局'})")

        total_time = time.time() - request_time
        print(f"[API] 请求处理完成，总耗时: {total_time:.3f}秒")
        print(f"{'='*50}\n")
        
        return MoveResponse(
            board=board.tolist(),
            move=[int(move_made[0]), int(move_made[1])] if move_made is not None else None,
            candidate_moves=[[int(r), int(c)] for r, c in legal_moves_next],
            game_over=game_over,
            winner=winner
        )
        
    except Exception as e:
        print(f"[API] 异常: {e}")
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