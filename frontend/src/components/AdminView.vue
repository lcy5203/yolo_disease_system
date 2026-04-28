<script setup>
import { reactive } from 'vue'

const props = defineProps(['encyclopediaData'])
const emit = defineEmits(['update-model'])

const modelConfig = reactive({
  modelPath: 'models/yolo11s_ema_mpdiou.pt'
})
</script>

<template>
  <div class="view-container animate-fade-in">
    <div class="hero-header">
       <h1 class="gradient-text">系统底层参数枢纽</h1>
       <p class="subtitle-dim">管理员专属：调控核心推理引擎与性能配置</p>
    </div>

    <div class="admin-grid-simple">
       <!-- 核心权重配置 -->
       <div class="glass-card config-section">
          <div class="section-title">
             <span class="icon">🧠</span>
             <h2>核心推理权重 (Weights)</h2>
          </div>
          <p class="desc">指定系统启动时加载的 YOLO 权重文件路径。更新后将在下一次检测请求时生效。</p>
          
          <div class="input-group-admin">
             <label>权重文件路径</label>
             <input v-model="modelConfig.modelPath" type="text" placeholder="e.g. models/best.pt" />
          </div>
          
          <button class="btn-apply" @click="emit('update-model', { ...modelConfig })">
             应用新权重并重启引擎
          </button>
       </div>

       <!-- 系统状态监控 (示例) -->
       <div class="glass-card status-section">
          <div class="section-title">
             <span class="icon">📊</span>
             <h2>系统服务状态</h2>
          </div>
          <div class="status-list">
             <div class="status-item">
                <span class="dot online"></span>
                <span class="label">FastAPI 后端服务:</span>
                <span class="val">运行中 (Active)</span>
             </div>
             <div class="status-item">
                <span class="dot online"></span>
                <span class="label">YOLO 推理集群:</span>
                <span class="val">已就绪 (Ready)</span>
             </div>
             <div class="status-item">
                <span class="dot warning"></span>
                <span class="label">百科热更新模块:</span>
                <span class="val">已迁移至百科页面</span>
             </div>
          </div>
       </div>
    </div>
  </div>
</template>

<style scoped>
.admin-grid-simple { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; margin-top: 2rem; }
.section-title { display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem; }
.section-title h2 { margin: 0; font-size: 1.4rem; color: var(--primary); }
.desc { color: #94a3b8; font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.5rem; }

.input-group-admin { margin-bottom: 1.5rem; }
.input-group-admin label { display: block; color: #fff; font-size: 0.85rem; margin-bottom: 8px; font-weight: bold; }
.input-group-admin input { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); border-radius: 8px; padding: 12px; color: #fff; outline: none; }

.btn-apply { width: 100%; padding: 12px; background: var(--primary); color: #022c22; border: none; border-radius: 8px; font-weight: 800; cursor: pointer; transition: 0.3s; }
.btn-apply:hover { filter: brightness(1.1); transform: translateY(-2px); }

.status-list { display: flex; flex-direction: column; gap: 15px; }
.status-item { display: flex; align-items: center; gap: 10px; font-size: 0.95rem; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.online { background: #4ade80; box-shadow: 0 0 10px #4ade80; }
.dot.warning { background: #fbbf24; }
.label { color: #94a3b8; }
.val { color: #fff; font-weight: bold; }
</style>
