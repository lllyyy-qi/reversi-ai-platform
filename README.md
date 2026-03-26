# 反向黑白棋 AI 对战平台

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.0+-brightgreen.svg)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 一个基于遗传算法优化的反向黑白棋AI对战平台，支持人机对战和AI自我对弈观战模式。

## 📋 项目简介

本项目实现了一个完整的反向黑白棋（Reversi）对战平台，核心AI基于Alpha-Beta剪枝算法，并通过遗传算法自动优化评估函数的17个参数。平台提供美观的Web界面，支持用户登录、对局记录、悔棋等功能。

###  核心特性

- **智能AI引擎**：基于Alpha-Beta剪枝的AI，通过遗传算法优化评估参数
- **双人对战模式**：人机对战 + AI自我对弈观战
- **完整游戏功能**：合法移动提示、悔棋、跳过回合、游戏结束判定
- **用户系统**：邮箱注册/登录，对局历史记录（待完善）
- **美观界面**：现代化棋盘设计，流畅的棋子动画

###  游戏规则

反向黑白棋与传统黑白棋相反：
- **胜利条件**：棋盘上棋子数量少的一方获胜
- **落子规则**：必须在至少夹住对方一个棋子的位置落子
- **翻转规则**：被夹住的对方棋子全部翻转

### 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3, Pinia, Vue Router, Axios, Vite |
| **后端** | Python 3.11+, FastAPI, SQLAlchemy, Uvicorn |
| **AI引擎** | NumPy, Numba (JIT加速) |
| **数据库** | SQLite (开发) / PostgreSQL (可扩展) |
| **认证** | JWT (JSON Web Token) |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 安装步骤

#### 1. 克隆项目

git clone https://github.com/yourusername/reversi-ai-platform.git
cd reversi-ai-platform

#### 2.后端配置
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

cd backend
pip install -r requirements.txt

### 3.前端配置

cd frontend
npm install

### 4.启动配置
cd backend 
python run.py
后端服务运行在 http://localhost:8000

##新终端窗口
cd front
npm run dev
前端服务运行在 http://localhost:5173


### 使用说明
访问 http://localhost:5173

注册账号（邮箱 + 密码）

登录后进入游戏界面

选择游戏模式：

人机对战：与AI对战，黑棋先行

AI观战：观看两个AI对弈

### AI 算法详解
评估函数（17个参数）
参数类型	数量	说明
位置权重	10	棋盘各位置的重要性系数
稳定子权重	1	边界稳定子的权重
行动力权重	4	前中期各2个，控制可选落子数
前沿子权重	2	前中期各1个，控制边缘棋子
搜索参数	2	终局阈值和最大搜索深度
搜索算法
Alpha-Beta 剪枝：减少无效搜索分支

迭代深化搜索：逐步增加搜索深度，控制时间

移动排序：优先搜索高价值位置（角落惩罚、边缘奖励）

动态深度调整：根据剩余空格数自动调整搜索深度

### API 接口文档
端点	            方法	    说明
/api/register	    POST	用户注册
/api/login	        POST	用户登录
/api/me	            GET 	获取当前用户
/api/legal_moves	POST	获取合法移动
/api/move	        POST	执行移动（玩家/AI）
/api/games/save	    POST	保存对局
/api/games	        GET	    获取历史对局
/api/health 	    GET    	健康检查

### 配置说明
修改AI参数
在 backend/app/ai_engine.py 中修改 AI.__init__ 方法的默认参数：

python
self.weight_vector = [10.49, 6.07, 23.23, ...]  # 位置权重
self.stability_weight = 112.40                  # 稳定子权重
self.mobility_weight = (20.89, 32.46, ...)      # 行动力权重
self.search_params = (15, 6)                    # 搜索参数
细节部分参考遗传算法工具页面（）

### 修改JWT密钥
在 backend/app/auth.py 中修改：

python
SECRET_KEY = "your-secure-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

### 待开发功能
对局历史记录完整实现

棋谱复盘功能

AI实验室（实时进化演示）

多难度级别

棋盘主题切换

移动端适配

WebSocket实时对战

对局分享功能


### 许可证
本项目采用 MIT 许可证 - 详见 LICENSE 文件

### 联系方式
项目维护者：[]
邮箱：[12312313@mail.edu.cn]

### 致谢
遗传算法参考了 DEAP 框架

棋盘设计灵感来自 OrangeX4/Reversi

### 如果这个项目对你有帮助，欢迎点个 Star！
