import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import GameView from '@/views/GameView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/game',
      name: 'game',
      component: GameView,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    // 需要登录但没有token，重定向到登录页
    return '/login'
  }
  
  if (to.path === '/login' && token) {
    // 已登录但访问登录页，重定向到游戏页
    return '/game'
  }
  
  return true
})

export default router