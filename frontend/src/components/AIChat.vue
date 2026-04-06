<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps(['lastResult'])
const isOpen = ref(false)
const isLoading = ref(false)
const userInput = ref('')
const messages = ref([
  { role: 'ai', text: '你好！我是农医 AI 农业专家。基于 YOLO 识别出的实时画面，我可以为您提供深度的防治指导。有什么我可以为您解答的？' }
])

const chatContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const userMsg = userInput.value
  messages.value.push({ role: 'user', text: userMsg })
  userInput.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ 
        query: userMsg,
        // 关键：如果还没识别图片，就传空字典，防止后端 422 报错
        last_result: props.lastResult || {} 
      })
    })

    const data = await res.json()
    if (!res.ok) {
        // 如果后端报错是列表形式（比如 Pydantic 验证错误），将其转为字符串
        const errorMsg = typeof data.detail === 'object' ? JSON.stringify(data.detail) : (data.detail || '服务器异常')
        throw new Error(errorMsg)
    }
    
    messages.value.push({ role: 'ai', text: data.answer })
  } catch (e) {
    console.error('AIChat Error:', e)
    messages.value.push({ role: 'ai', text: '专家连线中断：' + (e.message || '未知错误') })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
</script>

<template>
  <div class="ai-chat-wrapper" :class="{ 'is-open': isOpen }">
    <!-- 专家悬浮球 -->
    <button class="chat-toggle-btn" @click="isOpen = !isOpen">
      <span v-if="!isOpen">👨‍🌾 专家问诊</span>
      <span v-else>✖ 关闭对话</span>
    </button>

    <!-- 对话面板 -->
    <div v-show="isOpen" class="chat-panel glass-card">
      <div class="chat-header">
        <span class="status-dot"></span>
        <h4>农业 AI 专家 (RAG 版)</h4>
      </div>

      <div class="message-list" ref="chatContainer">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['msg-bubble', msg.role]">
          <div class="avatar">{{ msg.role === 'ai' ? '📑' : '👤' }}</div>
          <div class="content">{{ msg.text }}</div>
        </div>
        <div v-if="isLoading" class="msg-bubble ai">
          <div class="avatar">⏳</div>
          <div class="content thinking">正在连接全球农业数据库检索中...</div>
        </div>
      </div>

      <div class="chat-input-area">
        <input 
          v-model="userInput" 
          @keyup.enter="sendMessage" 
          placeholder="描述你的病害疑惑..." 
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading">🚀</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-chat-wrapper { position: fixed; right: 2rem; bottom: 6.5rem; z-index: 2500; }

.chat-toggle-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 50px;
  font-weight: 800; cursor: pointer; box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
  transition: 0.4s; display: flex; align-items: center; gap: 0.5rem;
}
.chat-toggle-btn:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(16, 185, 129, 0.5); }

.chat-panel {
  position: absolute; bottom: 4.5rem; right: 0; width: 380px; height: 500px;
  display: flex; flex-direction: column; overflow: hidden;
  border: 1px solid var(--glass-border); background: var(--nav-bg);
  box-shadow: 0 30px 60px rgba(0,0,0,0.4);
}

.chat-header {
  padding: 1rem; background: var(--glass-bg); border-bottom: 1px solid var(--glass-border);
  display: flex; align-items: center; gap: 0.8rem;
}
.chat-header h4 { margin: 0; font-size: 0.95rem; }
.status-dot { width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981; }

.message-list { flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }

.msg-bubble { display: flex; gap: 0.8rem; max-width: 85%; }
.msg-bubble.user { align-self: flex-end; flex-direction: row-reverse; }
.msg-bubble.ai { align-self: flex-start; }

.avatar { font-size: 1.2rem; }
.content { 
  padding: 0.8rem 1rem; border-radius: 12px; font-size: 0.9rem; line-height: 1.5;
  background: var(--glass-bg); color: var(--text-main);
}
.user .content { background: var(--primary); color: #022c22; font-weight: 600; }

.thinking { font-style: italic; opacity: 0.7; }

.chat-input-area {
  padding: 1rem; background: var(--glass-bg); display: flex; gap: 0.5rem;
}
.chat-input-area input {
  flex: 1; padding: 0.7rem; border-radius: 10px; border: 1px solid var(--glass-border);
  background: var(--bg); color: var(--text-main); outline: none;
}
.chat-input-area button {
  background: var(--primary); border: none; border-radius: 10px; padding: 0 1rem; cursor: pointer;
}

/* 随主题变色适配 */
.light-mode .chat-panel { background: #eef7ed; }
</style>
