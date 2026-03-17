<template>
  <div class="login-view">
    <div class="login-container">
      <h1>反向黑白棋 AI 平台</h1>
      
      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label>邮箱</label>
          <input 
            type="email" 
            v-model="email" 
            required
            placeholder="请输入邮箱"
          />
        </div>
        
        <div class="form-group">
          <label>密码</label>
          <input 
            type="password" 
            v-model="password" 
            required
            placeholder="请输入密码"
          />
        </div>
        
        <div class="error-message" v-if="error">{{ error }}</div>
        
        <div class="button-group">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ isLogin ? '登录' : '注册' }}
          </button>
          <button 
            type="button" 
            class="btn btn-secondary"
            @click="toggleMode"
          >
            {{ isLogin ? '没有账号？去注册' : '已有账号？去登录' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/services/api'

const router = useRouter()
const isLogin = ref(true)
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

function toggleMode() {
  isLogin.value = !isLogin.value
  error.value = ''
}

async function handleSubmit() {
  loading.value = true
  error.value = ''
  
  try {
    if (isLogin.value) {
      const response = await authAPI.login(email.value, password.value)
      localStorage.setItem('token', response.data.access_token)
      router.push('/game')
    } else {
      await authAPI.register(email.value, password.value)
      // 注册成功后自动登录
      const response = await authAPI.login(email.value, password.value)
      localStorage.setItem('token', response.data.access_token)
      router.push('/game')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: bold;
  color: #555;
}

.form-group input {
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.error-message {
  color: #ff6b6b;
  text-align: center;
  font-size: 14px;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn {
  padding: 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f0f0f0;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>