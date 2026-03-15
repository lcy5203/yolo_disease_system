<template>
  <div class="flex h-screen bg-[#0b0f19] text-white overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-64 glass-card m-4 mr-2 flex flex-col p-6 border-none">
      <div class="text-2xl font-bold text-gradient mb-10 flex items-center gap-2">
        <span class="text-3xl">🌿</span> 农医助手
      </div>
      
      <nav class="flex-1 space-y-2">
        <button 
          v-for="item in menuItems" 
          :key="item.id"
          @click="activeTab = item.id"
          :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all', 
                  activeTab === item.id ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-gray-400 hover:bg-white/5']"
        >
          <span>{{ item.icon }}</span>
          {{ item.name }}
        </button>
      </nav>

      <button @click="logout" class="mt-auto flex items-center gap-3 px-4 py-3 text-red-400 hover:bg-red-500/10 rounded-xl transition">
        <span>🚪</span> 退出系统
      </button>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 m-4 ml-2 overflow-y-auto custom-scrollbar">
      <header class="flex justify-between items-center mb-8 px-4">
        <div>
          <h2 class="text-3xl font-bold">{{ currentMenuName }}</h2>
          <p class="text-gray-500">{{ currentMenuDesc }}</p>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-right">
            <p class="font-medium">{{ user.username }}</p>
            <p class="text-xs text-gray-500 uppercase">{{ user.role }}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-emerald-500 to-blue-500 flex items-center justify-center font-bold">
            {{ user.username?.[0]?.toUpperCase() }}
          </div>
        </div>
      </header>

      <!-- Tab Content: Detection -->
      <section v-if="activeTab === 'detect'" class="animate-fade-in">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Upload Area -->
          <div class="lg:col-span-2 glass-card p-1">
            <div 
              class="relative h-[500px] rounded-[1.4rem] border-2 border-dashed border-white/10 hover:border-emerald-500/50 transition-all flex flex-col items-center justify-center overflow-hidden"
              @click="$refs.fileInput.click()"
              @dragover.prevent
              @drop.prevent="handleDrop"
            >
              <template v-if="!previewUrl">
                <div class="text-center">
                  <div class="text-6xl mb-4 opacity-50">📤</div>
                  <p class="text-xl font-medium">点击或拖拽作物照片</p>
                  <p class="text-gray-500 text-sm mt-2">支持 JPG, PNG 格式</p>
                </div>
              </template>
              <template v-else>
                <img :src="previewUrl" class="w-full h-full object-contain" />
                <div v-if="loading" class="absolute inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center">
                  <div class="loader"></div>
                </div>
              </template>
              <input type="file" ref="fileInput" hidden @change="handleFileSelect">
            </div>
          </div>

          <!-- Result Sidebar -->
          <div class="glass-card p-8 flex flex-col">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-6">诊断报告</h3>
            
            <template v-if="result">
              <div class="mb-8">
                <div class="inline-block px-3 py-1 rounded-full text-xs font-bold mb-2" 
                     :class="result.main_disease === 'Unknown' ? 'bg-gray-600' : 'bg-emerald-500'">
                   {{ result.main_disease === 'Unknown' ? '未识别到病害' : '发现病害' }}
                </div>
                <h4 class="text-4xl font-bold">{{ result.main_disease }}</h4>
              </div>

              <div class="space-y-6 flex-1">
                <div class="p-4 bg-white/5 rounded-2xl">
                  <label class="text-xs text-emerald-400 font-bold uppercase mb-1 block">发病原因</label>
                  <p class="text-gray-200">{{ result.cause }}</p>
                </div>
                <div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl">
                  <label class="text-xs text-emerald-400 font-bold uppercase mb-1 block">防治方案</label>
                  <p class="text-emerald-50">{{ result.treatment }}</p>
                </div>
              </div>

              <div class="mt-8 pt-6 border-t border-white/10 italic text-[10px] text-gray-500 text-center">
                识别结果由 AI 生成，仅供参考
              </div>
            </template>
            <template v-else>
              <div class="flex-1 flex flex-col items-center justify-center text-gray-600 text-center">
                <p>等待上传分析...</p>
              </div>
            </template>
          </div>
        </div>
      </section>

      <!-- Other tabs placeholder -->
      <section v-else class="glass-card p-20 text-center text-gray-500">
        <p>正在开发中... 此页面将由 {{ currentMenuName }} 模块接管</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const activeTab = ref('detect')
const user = reactive(JSON.parse(localStorage.getItem('user') || '{}'))

const menuItems = [
  { id: 'detect', name: '智能识别', icon: '🔍', desc: 'AI 驱动的实时病害诊断' },
  { id: 'history', name: '检测历史', icon: '📅', desc: '追溯过往检测记录' },
  { id: 'ency', name: '病害百科', icon: '📚', desc: '权威的作物病害知识库' },
  { id: 'stats', name: '数据分析', icon: '📊', desc: '全平台统计与趋势分析' }
]

const currentMenuName = computed(() => menuItems.find(i => i.id === activeTab.value)?.name)
const currentMenuDesc = computed(() => menuItems.find(i => i.id === activeTab.value)?.desc)

// Detection logic
const previewUrl = ref(null)
const loading = ref(false)
const result = ref(null)

const handleFileSelect = (e) => handleUpload(e.target.files[0])
const handleDrop = (e) => handleUpload(e.dataTransfer.files[0])

const handleUpload = async (file) => {
  if (!file) return
  previewUrl.value = URL.createObjectURL(file)
  loading.value = true
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const res = await api.post('/detection/detect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = res.data
  } catch (err) {
    alert('识别失败: ' + (err.response?.data?.detail || '服务器忙'))
  } finally {
    loading.value = false
  }
}

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
.loader {
  width: 48px;
  height: 48px;
  border: 5px solid #FFF;
  border-bottom-color: #10b981;
  border-radius: 50%;
  display: inline-block;
  box-sizing: border-box;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
