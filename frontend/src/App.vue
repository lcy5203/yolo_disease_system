<script setup>
import { ref, onMounted } from 'vue'
import DetectView from './components/DetectView.vue'
import HistoryView from './components/HistoryView.vue'
import EncyclopediaView from './components/EncyclopediaView.vue'
import StatsView from './components/StatsView.vue'
import AdminView from './components/AdminView.vue'
import AIChat from './components/AIChat.vue'

// --- 响应式状态 ---
const isDarkMode = ref(localStorage.getItem('theme') !== 'light')
const currentView = ref('detect') 
const files = ref([])
const previewUrl = ref(null)
const detectionResult = ref(null)
const isLoading = ref(false)
const historyRecords = ref([])
const encyclopediaData = ref([])
const statsData = ref(null)
const searchKey = ref('')

// --- 用户认证与权限 ---
const isLoggedIn = ref(false)
const userRole = ref(localStorage.getItem('role') || 'user')
const token = ref(localStorage.getItem('token') || '')
const currentUser = ref(null)
const showLoginDialog = ref(false)
const loginForm = ref({ username: '', password: '', email: '' })
const isRegisterMode = ref(false)

const API_BASE = '/api'

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

// --- 路由切换逻辑 ---
const switchView = (view) => {
  currentView.value = view
  if (view === 'stats') {
    fetchStats();
    fetchHistory(); 
  }
  if (view === 'admin') fetchEncyclopedia()
}

// --- 核心业务逻辑 (API 调用) ---
const handleAuth = async () => {
    const endpoint = isRegisterMode.value ? '/auth/register' : '/auth/login'
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(loginForm.value)
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.detail || '操作失败')
        
        if (isRegisterMode.value) {
            alert('注册成功，请登录！')
            isRegisterMode.value = false
        } else {
            localStorage.setItem('token', data.access_token)
            localStorage.setItem('role', data.role)
            localStorage.setItem('username', loginForm.value.username)
            token.value = data.access_token
            isLoggedIn.value = true
            userRole.value = data.role
            currentUser.value = loginForm.value.username
            showLoginDialog.value = false
        }
    } catch (e) { alert(e.message) }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  isLoggedIn.value = false
  userRole.value = 'user'
  currentUser.value = null
  token.value = ''
}

const startDetection = async () => {
  if (!isLoggedIn.value) { showLoginDialog.value = true; return }
  isLoading.value = true
  const formData = new FormData()
  formData.append('image', files.value[0])
  // 注意：此处不再发送 use_attention 参数，后端将默认启用

  try {
    const res = await fetch(`${API_BASE}/detect/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token.value}` },
      body: formData
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      const detail = errData.detail || '未知服务器错误';
      throw new Error(`检测失败 [状态码: ${res.status}]: ${JSON.stringify(detail)}`)
    }
    detectionResult.value = await res.json()
  } catch (e) { 
    console.error('Detection Trace:', e);
    alert(e.message); 
  }
  finally { isLoading.value = false }
}

const fetchHistory = async () => {
  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/history/my`, { headers: { 'Authorization': `Bearer ${token}` } })
  const data = await res.json()
  historyRecords.value = data.records
}

const fetchEncyclopedia = async (query = '') => {
  const search = typeof query === 'string' ? query : '';
  const res = await fetch(`${API_BASE}/encyclopedia/?search=${search}`)
  encyclopediaData.value = await res.json()
}

const fetchStats = async () => {
  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/stats/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  if (!res.ok) {
    console.error('获取统计数据失败')
    return
  }
  statsData.value = await res.json()
}

// --- 管理端逻辑 ---
const updateModel = async (config) => {
  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/admin/model/switch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ model_path: config.modelPath })
  })
  const data = await res.json()
  alert(data.msg || data.detail)
}

const updateEncyData = async (ency) => {
  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/admin/encyclopedia/${ency.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ prevention: ency.prevention })
  })
  const data = await res.json()
  alert(data.msg || data.detail)
}

// 文件上传的辅助触发
const fileInput = ref(null)
const triggerUpload = () => fileInput.value.click()
const handleFileUpload = (e) => { 
    const file = e.target.files[0]
    if(file) {
        files.value = [file]
        previewUrl.value = URL.createObjectURL(file)
    }
}

const handleDropUpload = (file) => {
    files.value = [file]
    previewUrl.value = URL.createObjectURL(file)
}

onMounted(() => {
  if (localStorage.getItem('token')) {
      isLoggedIn.value = true
      // 简单恢复角色显示，实际应用应从后端校验 token
      userRole.value = localStorage.getItem('role') || 'user'
      currentUser.value = localStorage.getItem('username') || '管理员'
      token.value = localStorage.getItem('token') || ''
  }
})
</script>

<template>
  <div class="app-container" :class="{ 'light-mode': !isDarkMode }">
    <!-- 全局导航栏 -->
    <nav class="navbar glass-card">
      <div class="logo">基于YOLO模型的病害分类系统</div>
      <div class="nav-links">
        <a href="#" @click.prevent="switchView('detect')" :class="{ active: currentView === 'detect' }">病害检测</a>
        <a href="#" @click.prevent="switchView('encyclopedia')" :class="{ active: currentView === 'encyclopedia' }">全科百科</a>
        <a href="#" @click.prevent="switchView('stats')" :class="{ active: currentView === 'stats' }">数据看板</a>
        <a v-if="userRole === 'admin'" href="#" @click.prevent="switchView('admin')" class="admin-link">⚙️ 管理中心</a>
        
        <div class="user-area">
          <button v-if="!isLoggedIn" @click="showLoginDialog = true" class="btn-auth">登录</button>
          <div v-else class="user-chip">
            <span>👤 {{ currentUser || '管理员' }}</span>
            <button @click="logout" class="btn-logout">退出</button>
          </div>
        </div>
      </div>
    </nav>

    <!-- 🌟 右下角主题切换 FAB 按钮 -->
    <button @click="toggleTheme" class="fab-theme-toggle" :title="isDarkMode ? '切换到白昼模式' : '切换到暗黑模式'">
        <span v-if="isDarkMode">☀️</span><span v-else>🌙</span>
    </button>

    <!-- 👨‍🌾 AI 农业专家 RAG 悬浮对话窗 (仅登录后可见) -->
    <AIChat v-if="isLoggedIn" :lastResult="detectionResult" />


    <!-- 视图渲染区 (解耦组件) -->
    <main class="main-content">
        <DetectView v-if="currentView === 'detect'" 
            :isLoading="isLoading" 
            :detectionResult="detectionResult" 
            :previewUrl="previewUrl"
            @start-detection="startDetection" 
            @trigger-upload="triggerUpload"
            @handle-drop="handleDropUpload" />
        
        <input type="file" ref="fileInput" @change="handleFileUpload" hidden accept="image/*" />

        <HistoryView v-if="currentView === 'history'" :records="historyRecords" />

        <EncyclopediaView v-if="currentView === 'encyclopedia'" 
            :data="encyclopediaData" 
            :isAdmin="userRole === 'admin'"
            :token="token"
            @fetch-ency="fetchEncyclopedia" />

        <StatsView v-if="currentView === 'stats'" 
            :statsData="statsData" 
            :historyRecords="historyRecords" />

        <AdminView v-if="currentView === 'admin'" 
            :encyclopediaData="encyclopediaData" 
            @update-model="updateModel" 
            @update-ency="updateEncyData" />
    </main>

    <!-- 登录弹窗 (恢复极简风格) -->
    <div v-if="showLoginDialog" class="overlay" @click.self="showLoginDialog = false">
      <div class="login-card">
        <button class="close-btn" @click="showLoginDialog = false">×</button>
        <h3 class="login-title-simple">{{ isRegisterMode ? '创建账户' : '安全登录' }}</h3>
        
        <div class="form-group-simple">
            <input v-model="loginForm.username" type="text" placeholder="用户名">
            <input v-if="isRegisterMode" v-model="loginForm.email" type="email" placeholder="邮箱">
            <input v-model="loginForm.password" type="password" placeholder="密码">
            <button class="btn-primary-auth" @click="handleAuth">
                {{ isRegisterMode ? '立即注册' : '点击进入系统' }}
            </button>
        </div>
        <p class="toggle-text-simple" @click="isRegisterMode = !isRegisterMode">
          {{ isRegisterMode ? '返回登录' : '没有账号？去注册' }}
        </p>
      </div>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap');

:root {
  --primary: #4ade80;
  --primary-glow: rgba(74, 222, 128, 0.4);
  --bg: #030712;
  --nav-bg: rgba(3, 7, 18, 0.85);
  --glass-bg: rgba(255, 255, 255, 0.04);
  --glass-border: rgba(255, 255, 255, 0.1);
  --text-main: #f1f5f9;
  --text-dim: #94a3b8;
  --card-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

/* 🌿 护眼苔藓/青瓷绿 (Celadon Sage Theme) */
.light-mode {
  --bg: #dae8d1;
  --nav-bg: rgba(218, 232, 209, 0.98);
  --glass-bg: #ccd9c7;
  --glass-border: rgba(0, 0, 0, 0.05);
  --text-main: #2d3b2d;
  --text-dim: #4a5d4a;
  --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

body { 
  margin: 0; background: var(--bg); color: var(--text-main); 
  font-family: 'Outfit', sans-serif;
  overflow-x: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.app-container { min-height: 100vh; position: relative; background: var(--bg); }

/* 宇宙底噪纹理 (深色独有) */
.app-container:not(.light-mode)::before {
  content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: radial-gradient(circle at 50% 50%, #1e293b 0%, #030712 100%);
  z-index: -1;
}

.fab-theme-toggle {
  position: fixed; right: 2rem; bottom: 2rem; width: 3.5rem; height: 3.5rem;
  background: var(--primary); color: #000; border-radius: 50%;
  border: none; cursor: pointer; font-size: 1.5rem;
  box-shadow: 0 10px 25px var(--primary-glow);
  z-index: 2000; transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex; align-items: center; justify-content: center;
}
.fab-theme-toggle:hover { transform: scale(1.1) rotate(15deg); filter: brightness(1.1); }
.light-mode .fab-theme-toggle { background: #0f172a; color: #fff; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }

/* 导航栏：极光磨砂 */
.navbar { 
  display: flex; justify-content: space-between; align-items: center; 
  padding: 1.2rem 8%; background: var(--nav-bg); 
  backdrop-filter: blur(20px); border-bottom: 1px solid var(--glass-border); 
  position: sticky; top: 0; z-index: 1000;
}

.logo { 
  font-size: 1.8rem; font-weight: 900; letter-spacing: -1px;
  background: linear-gradient(135deg, var(--text-main) 0%, var(--primary) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.btn-theme {
  background: none; border: none; font-size: 1.25rem; cursor: pointer;
  padding: 0.5rem; border-radius: 12px; transition: 0.3s;
}
.btn-theme:hover { background: rgba(128,128,128,0.1); transform: rotate(15deg); }

.nav-links { display: flex; gap: 2.5rem; align-items: center; }
.nav-links a { 
  color: var(--text-dim); text-decoration: none; font-weight: 600; 
  font-size: 0.95rem; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}
.nav-links a:hover, .nav-links a.active { color: var(--primary); transform: scale(1.05); }
.nav-links a.active::after {
  content: ""; position: absolute; bottom: -8px; left: 0; width: 100%; height: 2px;
  background: var(--primary); box-shadow: 0 0 10px var(--primary);
}

.admin-link { color: #fbbf24 !important; filter: drop-shadow(0 0 5px rgba(251, 191, 36, 0.4)); }

/* 登录/用户信息区域 */
.user-chip {
  display: flex; align-items: center; gap: 1rem;
  background: var(--glass-bg); padding: 0.4rem 1rem; border-radius: 50px;
  border: 1px solid var(--glass-border);
  color: var(--text-main); font-weight: 600; font-size: 0.9rem;
}
.btn-auth {
  background: var(--primary); color: #022c22; border: none; padding: 0.45rem 1.5rem;
  border-radius: 50px; font-weight: 800; cursor: pointer; transition: 0.4s;
}
.btn-logout { background: none; border: none; color: #f87171; cursor: pointer; font-size: 0.8rem; }

/* 主内容布局 */
.main-content { padding: 4rem 8%; max-width: 1400px; margin: 0 auto; }

/* 后台通用卡片 */
.glass-card { 
  background: var(--glass-bg); border: 1px solid var(--glass-border); 
  border-radius: 24px; padding: 2rem; backdrop-filter: blur(12px);
  transition: transform 0.3s, border-color 0.3s;
}
.glass-card:hover { border-color: rgba(74, 222, 128, 0.3); }

/* 登录弹窗 (极致美化) */
.overlay { 
  position: fixed; inset: 0; background: rgba(0,0,0,0.8); 
  display: flex; align-items: center; justify-content: center; z-index: 2000;
  backdrop-filter: blur(12px); animation: fadeIn 0.4s ease-out;
}
.login-card { 
  width: 340px; padding: 2.5rem; border-radius: 24px; text-align: center;
  background: var(--nav-bg);
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4);
  border: 1px solid var(--glass-border);
  position: relative;
}

.close-btn {
  position: absolute; top: 1rem; right: 1.2rem; background: none; border: none;
  font-size: 1.5rem; color: var(--text-dim); cursor: pointer; transition: 0.3s;
}
.close-btn:hover { color: #f87171; transform: rotate(90deg); }

.login-title-simple { margin: 0 0 2rem 0; font-size: 1.5rem; font-weight: 700; color: var(--text-main); }

.form-group-simple { display: flex; flex-direction: column; gap: 1rem; }
.form-group-simple input { 
  width: 100%; padding: 1rem; background: rgba(128,128,128,0.05); 
  border: 1px solid var(--glass-border); border-radius: 12px; 
  color: var(--text-main); box-sizing: border-box; transition: 0.3s;
  font-family: inherit;
}
.form-group-simple input:focus { outline: none; border-color: var(--primary); background: rgba(74, 222, 128, 0.05); }

.btn-primary-auth {
  width: 100%; padding: 1rem; border-radius: 12px; border: none;
  background: var(--primary); color: #022c22; font-weight: 800; font-size: 1rem; cursor: pointer;
  transition: 0.3s; margin-top: 0.5rem;
}
.btn-primary-auth:hover { filter: brightness(1.1); transform: translateY(-2px); }

.toggle-text-simple { margin-top: 1.5rem; color: var(--primary); cursor: pointer; font-size: 0.85rem; font-weight: 600; opacity: 0.8; }
.toggle-text-simple:hover { opacity: 1; text-decoration: underline; }

/* 响应式适配 */
@media (max-width: 768px) {
    .nav-links { display: none; }
    .main-content { padding: 2rem 5%; }
}
</style>
