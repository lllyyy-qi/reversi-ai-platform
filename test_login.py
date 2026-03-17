from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 简化登录（不检查数据库）
@app.post("/api/login")
async def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    # 临时接受任何登录
    return {
        "access_token": "fake-token-12345",
        "token_type": "bearer"
    }


@app.post("/api/register")
async def register(data: dict):
    return {
        "id": 1,
        "email": data.get("email"),
        "created_at": "2024-01-01T00:00:00"
    }


@app.get("/api/me")
async def get_me():
    return {
        "id": 1,
        "email": "test@test.com",
        "created_at": "2024-01-01T00:00:00"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)