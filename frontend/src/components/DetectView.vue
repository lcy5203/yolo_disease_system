<script setup>
import { ref } from 'vue'

const props = defineProps(['isLoading', 'detectionResult', 'previewUrl'])
const emit = defineEmits(['start-detection', 'trigger-upload', 'handle-drop'])

const isDragging = ref(false)

const onDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    emit('handle-drop', file)
  } else {
    alert('请上传有效的图片文件！')
  }
}
</script>

<template>
  <div class="view-container animate-fade-in">
    <!-- 顶部标题 -->
    <div class="hero-header">
      <h1 class="gradient-text">农作物病害快速识别</h1>
    </div>

    <div class="detection-grid">
      <!-- 1. 操作区 -->
      <div class="glass-card upload-section">
        <div class="upload-area" 
          :class="{ 'is-dragging': isDragging, 'has-preview': props.previewUrl }"
          @click="emit('trigger-upload')"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop">
          
          <div class="upload-placeholder">
            <div v-if="!props.previewUrl">
              <p>{{ isDragging ? '松开即刻上传' : '点击或拖拽上传' }}</p>
            </div>
            <div v-else class="preview-container">
              <img :src="props.previewUrl" class="preview-thumb" />
              <div class="preview-overlay"><span>更换照片</span></div>
            </div>
          </div>
        </div>
        
        <button class="btn-primary-detect" @click="emit('start-detection')" :disabled="isLoading">
          <span v-if="!isLoading">开启智能识别</span>
          <span v-else>🧪 模型推理中...</span>
        </button>
      </div>

      <!-- 2. 详细推理解析报告 -->
      <transition name="slide-up">
        <div v-if="props.detectionResult" class="glass-card result-panel">
          <!-- 性能勋章区 -->
          <div class="performance-header">
             <div class="model-badge"> {{ props.detectionResult.model_name }}</div>
             <div class="time-badge">⚡ 推理耗时: {{ props.detectionResult.inference_time }}ms</div>
          </div>

          <div class="main-result">
             <h2 class="disease-title">{{ props.detectionResult.disease_name }}</h2>
             <div class="conf-pill">置信度: {{ (props.detectionResult.confidence * 100).toFixed(1) }}%</div>
          </div>

          <div class="image-showcase">
             <div class="image-box">
                <span class="img-label">原始样本</span>
                <img :src="props.detectionResult.original_image" />
             </div>
             <div class="image-box featured">
                <span class="img-label">推理标注图</span>
                <img :src="props.detectionResult.result_image" />
             </div>
          </div>

          <div class="analysis-box">
             <div class="analysis-item">
                <label>病因分析</label>
                <p>{{ props.detectionResult.causes }}</p>
             </div>
             <div class="analysis-item">
                <label>防治建议</label>
                <p>{{ props.detectionResult.prevention }}</p>
             </div>
          </div>

          <div class="disclaimer">⚠️ 本系统仅作科研参考，重大生产决策请咨询植物保护专家。</div>
        </div>
      </transition>
    </div>
  </div>
</template>

<style scoped>
.hero-header { text-align: center; margin-bottom: 3rem; }
.gradient-text { font-size: 3rem; font-weight: 900; background: linear-gradient(to right, #f1f5f9, var(--primary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.subtitle { color: var(--text-dim); }

.detection-grid { display: grid; grid-template-columns: 1fr 1.8fr; gap: 2rem; align-items: start; }

/* 上传部分 */
.upload-area { border: 2px dashed var(--glass-border); border-radius: 16px; min-height: 280px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s; }
.upload-area:hover { border-color: var(--primary); background: rgba(74, 222, 128, 0.05); }
.preview-thumb { width: 100%; height: 100%; object-fit: cover; border-radius: 12px; }
.preview-container { position: relative; width: 100%; height: 280px; overflow: hidden; }
.preview-overlay { 
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
  background: rgba(0,0,0,0.4); 
  display: flex; align-items: center; justify-content: center; 
  opacity: 0; transition: 0.3s;
}
.preview-container:hover .preview-overlay { opacity: 1; }
.preview-overlay span { 
  background: var(--primary); 
  color: #022c22; 
  padding: 8px 20px; 
  border-radius: 50px; 
  font-weight: 800; 
  font-size: 0.9rem;
  box-shadow: 0 4px 15px rgba(74, 222, 128, 0.4);
  transform: translateY(10px);
  transition: 0.3s;
}
.preview-container:hover span { transform: translateY(0); }

/* 性能勋章 */
.performance-header { display: flex; gap: 10px; margin-bottom: 20px; }
.model-badge, .time-badge { padding: 4px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); }
.time-badge { color: #facc15; border-color: rgba(250, 204, 21, 0.2); }

.main-result { display: flex; align-items: center; gap: 15px; margin-bottom: 1.5rem; }
.disease-title { font-size: 2rem; margin: 0; color: var(--primary); }
.conf-pill { background: var(--primary); color: #022c22; padding: 4px 15px; border-radius: 50px; font-weight: 800; font-size: 0.9rem; }

/* 图像双开对比 */
.image-showcase { display: grid; grid-template-columns: 1fr 1.2fr; gap: 20px; margin-bottom: 20px; }
.image-box { 
  position: relative; 
  border-radius: 12px; 
  overflow: hidden; 
  border: 1px solid var(--glass-border); 
  height: 320px; /* 固定高度，防止黑边 */
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-box img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover; /* 充满容器，消除黑边 */
  display: block; 
}
.img-label { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; color: #fff; z-index: 10; }
.featured { border-color: var(--primary); }

.analysis-box { background: rgba(255,255,255,0.02); padding: 20px; border-radius: 12px; border: 1px solid var(--glass-border); }
.analysis-item { margin-bottom: 15px; }
.analysis-item label { display: block; color: var(--primary); font-weight: bold; margin-bottom: 5px; font-size: 0.9rem; }
.analysis-item p { margin: 0; line-height: 1.5; font-size: 0.95rem; color: #cbd5e1; }

.disclaimer { font-size: 0.75rem; color: #94a3b8; font-style: italic; margin-top: 15px; }

.btn-primary-detect { width: 100%; padding: 1.2rem; border-radius: 12px; border: none; font-weight: 800; background: var(--primary); color: #022c22; cursor: pointer; margin-top: 20px; }

.slide-up-enter-active { transition: all 0.4s ease-out; }
.slide-up-enter-from { opacity: 0; transform: translateY(20px); }

@media (max-width: 1000px) { .detection-grid { grid-template-columns: 1fr; } }
</style>
