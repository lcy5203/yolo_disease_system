<script setup>
import { ref, watch } from 'vue'

const props = defineProps(['isLoading', 'detectionResult', 'useAttention', 'previewUrl'])
const emit = defineEmits(['start-detection', 'trigger-upload', 'update:useAttention', 'handle-drop'])

const localUseAttention = ref(props.useAttention)
const isDragging = ref(false)

// 同步父级状态变化
watch(() => props.useAttention, (newVal) => localUseAttention.value = newVal)

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
    <!-- Header Section -->
    <div class="hero-header">
      <h1 class="gradient-text">AI 农作物健康卫士</h1>
      <p class="subtitle">基于 YOLOv11 & CBAM 注意力机制的工业级识别引擎</p>
    </div>

    <div class="detection-grid">
      <!-- 1. 上传控制区 -->
      <div class="glass-card upload-section">
        <div class="upload-area" 
          :class="{ 'is-dragging': isDragging, 'has-preview': props.previewUrl }"
          @click="emit('trigger-upload')"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop">
          
          <div class="upload-placeholder">
            <div v-if="!props.previewUrl">
              <div class="icon">{{ isDragging ? '📥' : '📸' }}</div>
              <p>{{ isDragging ? '松开即刻上传' : '点击或拖拽上传' }}</p>
            </div>
            <div v-else class="preview-container">
              <img :src="props.previewUrl" class="preview-thumb" />
              <div class="preview-overlay">
                 <span>点击更换照片</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="attention-toggle">
           <span>引入 CBAM 注意力机制</span>
           <label class="switch">
              <input type="checkbox" v-model="localUseAttention" @change="emit('update:useAttention', localUseAttention)">
              <span class="slider round"></span>
           </label>
        </div>
        
        <button class="btn-primary-detect" @click="emit('start-detection')" :disabled="isLoading">
          <span v-if="!isLoading">🚀 开始核心检测</span>
          <span v-else>🧪 模型推理中...</span>
        </button>
      </div>

      <!-- 2. 结果展示区 -->
      <transition name="slide-up">
        <div v-if="props.detectionResult" class="glass-card result-card">
          <div class="result-header">
             <h2 class="disease-name">{{ props.detectionResult.disease_name }}</h2>
             <div class="confidence-tag">置信度: {{ (props.detectionResult.confidence * 100).toFixed(1) }}%</div>
          </div>

          <div class="image-comparison">
             <div class="img-wrapper">
                <p class="label">原始图像</p>
                <img :src="props.detectionResult.original_image" alt="Original" />
             </div>
             <div class="img-wrapper">
                <p class="label">检测框展示</p>
                <img :src="props.detectionResult.result_image" alt="Result" />
             </div>
          </div>

          <div class="info-details">
             <div class="info-item">
                <span class="title">病害原因:</span>
                <p>{{ props.detectionResult.causes }}</p>
             </div>
             <div class="info-item">
                <span class="title">防治建议:</span>
                <p>{{ props.detectionResult.prevention }}</p>
             </div>
          </div>
          
          <div class="disclaimer">
             ⚠️ 免责声明：系统识别结果仅供参考，重大灾情请结合人工鉴定。
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<style scoped>
.hero-header { text-align: center; margin-bottom: 4rem; }
.gradient-text { 
  font-size: 3.5rem; margin-bottom: 0.5rem; font-weight: 900;
  background: linear-gradient(to right, var(--text-main), var(--primary));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}
.subtitle { color: var(--text-dim); font-size: 1.1rem; }

.detection-grid { display: grid; grid-template-columns: 1fr 1.5fr; gap: 2.5rem; align-items: start; }

.upload-area { 
  border: 2px dashed var(--glass-border); border-radius: 20px; transition: 0.3s;
  cursor: pointer; position: relative; overflow: hidden;
  background: rgba(255,255,255,0.01);
  min-height: 250px; display: flex; align-items: center; justify-content: center;
}
.upload-area:hover, .upload-area.is-dragging { 
  border-color: var(--primary); 
  background: rgba(74, 222, 128, 0.08); 
  transform: scale(1.02);
}

.upload-placeholder { width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.upload-placeholder .icon { font-size: 3.5rem; margin-bottom: 0.5rem; transition: 0.3s; }
.upload-placeholder p { color: var(--text-main); font-weight: 600; margin: 0; }

/* 预览图容器 */
.preview-container { 
  position: relative; width: 100%; height: 250px; 
  display: flex; align-items: center; justify-content: center;
}
.preview-thumb { 
  max-width: 95%; max-height: 230px; border-radius: 12px; 
  box-shadow: 0 10px 20px rgba(0,0,0,0.3); border: 2px solid var(--primary);
}
.preview-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.4); 
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: 0.3s; color: white; font-weight: 800;
}
.preview-container:hover .preview-overlay { opacity: 1; }

.attention-toggle { 
  margin: 1.5rem 0; display: flex; align-items: center; justify-content: space-between;
  padding: 1rem; background: var(--glass-bg); border-radius: 12px;
  color: var(--text-main); font-weight: 600; font-size: 0.95rem;
}

.btn-primary-detect {
  width: 100%; padding: 1.2rem; border-radius: 15px; border: none; font-size: 1.1rem; font-weight: 800;
  background: linear-gradient(135deg, var(--primary) 0%, #22c55e 100%);
  color: #022c22; cursor: pointer; transition: 0.4s;
  box-shadow: 0 10px 20px -5px rgba(34, 197, 94, 0.5);
}
.btn-primary-detect:hover { transform: translateY(-3px); box-shadow: 0 15px 30px -5px rgba(34, 197, 94, 0.6); }

.result-card { position: sticky; top: 120px; }
.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 1px solid var(--glass-border); padding-bottom: 1rem; }
.disease-name { color: var(--primary); margin: 0; font-size: 1.8rem; }
.confidence-tag { background: rgba(74, 222, 128, 0.1); color: var(--primary); padding: 0.3rem 0.8rem; border-radius: 50px; font-weight: 700; border: 1px solid rgba(74, 222, 128, 0.2); }

.image-comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem; }
.img-wrapper { text-align: center; }
.img-wrapper img { width: 100%; border-radius: 15px; box-shadow: var(--card-shadow); border: 1px solid var(--glass-border); }
.img-wrapper .label { font-size: 0.8rem; color: var(--text-dim); margin-bottom: 0.5rem; }

.info-details { background: var(--glass-bg); padding: 1.5rem; border-radius: 15px; border: 1px solid var(--glass-border); }
.info-item { margin-bottom: 1rem; }
.info-item .title { display: block; color: var(--primary); font-weight: 700; font-size: 0.9rem; margin-bottom: 0.3rem; }
.info-item p { margin: 0; line-height: 1.6; color: var(--text-main); }

.disclaimer { margin-top: 1.5rem; color: #f87171; font-size: 0.8rem; font-style: italic; opacity: 0.8; }

.switch { position: relative; display: inline-block; width: 44px; height: 22px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--glass-border); transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: var(--primary); }
input:checked + .slider:before { transform: translateX(22px); }

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.5s ease-out; }
.slide-up-enter-from { opacity: 0; transform: translateY(30px); }

@media (max-width: 900px) {
  .detection-grid { grid-template-columns: 1fr; }
}
</style>
