import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: false,
  timeout: 10000 // 10秒超时
})

// 请求拦截器 - 添加token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log(`请求: ${config.method} ${config.url}`, config.data)
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器 - 添加日志
api.interceptors.response.use(
  response => {
    console.log(`响应: ${response.config.url}`, response.status, response.data)
    return response
  },
  error => {
    console.error('请求失败:', error.config?.url, error.message)
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (email, password) => api.post('/register', { email, password }),
  login: (email, password) => api.post('/login', { email, password }),
  getCurrentUser: () => api.get('/me')
}

export const gameAPI = {
  // 获取合法移动
  getLegalMoves: (board, player) => 
    api.post('/legal_moves', { board, player }),
  
  // 玩家移动
  applyMove: (board, player, move) => 
    api.post('/move', { board, player, move }),
  
  // AI 移动
  getAIMove: (board, player, config = {}) => 
    api.post('/move', { board, player }, config)
}

export const systemAPI = {
  healthCheck: () => api.get('/health')
}

// 定期检查后端健康状态
setInterval(async () => {
  try {
    await systemAPI.healthCheck()
  } catch (error) {
    console.error('后端连接丢失', error)
    // 可以显示提示
  }
}, 30000) // 每30秒检查一次

export default api