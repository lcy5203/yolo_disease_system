<script setup>
import { ref } from 'vue'

const props = defineProps(['encyclopediaData'])
const emit = defineEmits(['update-model', 'update-ency'])

const adminConfig = ref({ modelPath: 'models/best.pt', isAttention: false })
const selectedEncy = ref(null)

const handleModelUpdate = () => { emit('update-model', adminConfig.value) }
const handleEncyUpdate = () => { if (selectedEncy.value) emit('update-ency', selectedEncy.value) }
</script>

<template>
  <div class="view-container animate-fade-in">
    <div class="admin-hero">
      <h1 class="admin-title">⚙️ 平台系统管理中心</h1>
      <div class="status-badge"><span class="dot"></span> 系统状态: 运行良好 (12400f + 4060 Ti)</div>
    </div>
    
    <div class="admin-grid">
      <!-- 1. 模型控制核心 -->
      <div class="glass-card control-card">
        <div class="card-header">
           <div class="icon">💾</div>
           <h3>模型动态权重切换</h3>
        </div>
        <p class="desc">更改后台推理引擎加载的 .pt 权重文件路径</p>
        
        <div class="field-group">
           <label>本地权重路径 (Relative Path):</label>
           <input type="text" v-model="adminConfig.modelPath" class="premium-input" placeholder="models/yolov11_attention.pt">
        </div>

        <div class="toggle-group">
           <label class="check-container">
             <input type="checkbox" v-model="adminConfig.isAttention">
             <span class="checkmark"></span>
             标记为全注意力增强版 (CBAM)
           </label>
        </div>

        <button class="btn-primary-admin" @click="handleModelUpdate">
            更新全局推理配置
        </button>
      </div>
      
      <!-- 2. 百科防治专家系统 -->
      <div class="glass-card control-card">
        <div class="card-header">
           <div class="icon">📚</div>
           <h3>病害专家库动态维护</h3>
        </div>
        <p class="desc">实时修改百科词条及防治专家建议（立即生效于全端）</p>

        <div class="field-group">
           <label>选择待更新病害：</label>
           <select v-model="selectedEncy" class="premium-select">
             <option v-for="item in props.encyclopediaData" :key="item.id" :value="item">{{ item.name }}</option>
           </select>
        </div>

        <div v-if="selectedEncy" class="editor-area animate-fade-in">
           <label>修改防治建议 (HTML 支持):</label>
           <textarea v-model="selectedEncy.prevention" rows="6" class="premium-textarea"></textarea>
           <button class="btn-primary-admin secondary" @click="handleEncyUpdate">
               同步专家建议到云端
           </button>
        </div>
        <div v-else class="empty-state">
           👈 请先选择一个病害词条开始编辑
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-hero { margin-bottom: 3rem; }
.admin-title { font-size: 2.5rem; margin-bottom: 0.8rem; font-weight: 800; color: #fbbf24; text-shadow: 0 0 15px rgba(251, 191, 36, 0.3); }
.status-badge { display: inline-flex; align-items: center; gap: 0.6rem; padding: 0.4rem 1rem; background: rgba(255,255,255,0.05); border-radius: 50px; font-size: 0.85rem; color: var(--text-dim); }
.dot { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 8px #22c55e; animation: pulse 2s infinite; }

.admin-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2.5rem; }

.card-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
.card-header .icon { font-size: 1.5rem; }
.card-header h3 { margin: 0; font-size: 1.3rem; color: var(--text-main); }

.desc { font-size: 0.85rem; color: var(--text-dim); margin-bottom: 2rem; border-bottom: 1px solid var(--glass-border); padding-bottom: 1rem; }

.field-group { margin-bottom: 1.5rem; }
.field-group label { display: block; margin-bottom: 0.8rem; font-size: 0.85rem; color: var(--text-dim); font-weight: 600; }

.premium-input, .premium-select, .premium-textarea {
  width: 100%; box-sizing: border-box; padding: 0.9rem; background: var(--bg); 
  border: 1px solid var(--glass-border); border-radius: 12px; color: var(--text-main);
  transition: 0.3s; font-family: inherit; font-size: 0.95rem;
}

.premium-input:focus, .premium-select:focus, .premium-textarea:focus { border-color: #fbbf24; outline: none; background: rgba(251, 191, 36, 0.05); }

.premium-select { background: #1e293b; cursor: pointer; }

.btn-primary-admin {
  width: 100%; padding: 1rem; border-radius: 12px; border: none; font-size: 1rem; font-weight: 700;
  background: linear-gradient(135deg, #fbbf24 0%, #d97706 100%);
  color: #000; cursor: pointer; transition: 0.3s; margin-top: 1rem;
}
.btn-primary-admin:hover { transform: translateY(-3px); box-shadow: 0 10px 20px -5px rgba(251, 191, 36, 0.4); }
.btn-primary-admin.secondary { background: linear-gradient(135deg, #4ade80 0%, #16a34a 100%); margin-top: 1.5rem; }

.empty-state { text-align: center; padding: 3rem; color: var(--text-dim); font-style: italic; border: 2px dashed rgba(255,255,255,0.05); border-radius: 15px; }

/* 自定义 Checkbox */
.check-container { display: flex; align-items: center; cursor: pointer; font-size: 0.9rem; color: var(--text-dim); }
.check-container input { display: none; }
.checkmark { width: 18px; height: 18px; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); border-radius: 4px; margin-right: 10px; position: relative; }
.check-container input:checked ~ .checkmark { background: #fbbf24; border-color: #fbbf24; }
.checkmark:after { content: "✓"; position: absolute; display: none; left: 4px; top: 0px; color: #000; font-weight: 900; font-size: 12px; }
.check-container input:checked ~ .checkmark:after { display: block; }

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

@media (max-width: 1000px) { .admin-grid { grid-template-columns: 1fr; } }
</style>
