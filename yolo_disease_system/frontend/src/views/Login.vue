<template>
  <div class="min-h-screen flex items-center justify-center bg-[#0f172a] p-4">
    <div class="glass-card p-10 w-full max-w-md animate-fade-in">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gradient mb-2">🌿 农医助手</h1>
        <p class="text-gray-400">智能农作物病害分类系统</p>
      </div>
      
      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-1">用户名</label>
          <input 
            v-model="username" 
            type="text" 
            class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition"
            placeholder="请输入管理员账号"
          >
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-1">密码</label>
          <input 
            v-model="password" 
            type="password" 
            class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition"
            placeholder="请输入密码"
          >
        </div>

        <button 
          @click="handleLogin" 
          :disabled="loading"
          class="w-full bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-400 hover:to-blue-400 text-white font-bold py-3 rounded-xl shadow-lg shadow-emerald-500/20 transition-all active:scale-95 disabled:opacity-50"
        >
          {{ loading ? '进入中...' : '立即登录' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const username = ref('admin')
const password = ref('password')
const loading = ref(false)

const handleLogin = async () => {
  loading.ref = true
  try {
    const res = await api.post('/auth/login', { username: username.value, password: password.value })
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data))
    router.push('/')
  } catch (err) {
    alert('登录失败: ' + (err.response?.data?.detail || '网络异常'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
