<script setup>
import { ref, reactive } from 'vue'

const props = defineProps(['data', 'isAdmin', 'token'])
const emit = defineEmits(['fetch-ency'])

const API_BASE = 'http://127.0.0.1:8000/api'

// --- 弹窗与状态控制 ---
const showModal = ref(false)
const isEditing = ref(false)
const currentId = ref(null)
const form = reactive({
  name: '',
  crop_type: 'Apple',
  causes: '',
  prevention: '',
  image_url: ''
})

// --- 打开表单 ---
const openAdd = () => {
  isEditing.value = false
  Object.assign(form, { name: '', crop_type: 'Apple', causes: '', prevention: '', image_url: '' })
  showModal.value = true
}

const openEdit = (item) => {
  isEditing.value = true
  currentId.value = item.id
  Object.assign(form, { ...item })
  showModal.value = true
}

// --- 图片上传逻辑 ---
const handleUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const res = await fetch(`${API_BASE}/admin/encyclopedia/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${props.token}` },
      body: formData
    })
    const data = await res.json()
    form.image_url = data.url
  } catch (e) {
    alert('图片上传失败')
  }
}

// --- 保存提交 ---
const saveEntry = async () => {
  const url = isEditing.value 
    ? `${API_BASE}/admin/encyclopedia/${currentId.value}`
    : `${API_BASE}/admin/encyclopedia`
  
  const method = isEditing.value ? 'PUT' : 'POST'
  
  try {
    const res = await fetch(url, {
      method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${props.token}`
      },
      body: JSON.stringify(form)
    })
    if (res.ok) {
      alert('保存成功！')
      showModal.value = false
      emit('fetch-ency', '') // 刷新列表
    } else {
      const err = await res.json()
      alert(err.detail || '保存失败')
    }
  } catch (e) {
    alert('由于网络原因，保存操作未完成')
  }
}

// --- 删除词条 ---
const deleteEntry = async (id) => {
  if (!confirm('确定要永久删除这个词条吗？')) return
  try {
    const res = await fetch(`${API_BASE}/admin/encyclopedia/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${props.token}` }
    })
    if (res.ok) {
      alert('已妥善删除')
      emit('fetch-ency', '')
    }
  } catch (e) {
    alert('删除过程中发生异常')
  }
}
</script>

<template>
  <div class="view-container animate-fade-in">
    <!-- 百科头部 -->
    <div class="ency-header">
       <div class="title-group">
          <h1 class="gradient-text">全科病害百科库</h1>
          <p class="subtitle-dim">集成多模态病害知识，支持管理员动态演进</p>
       </div>
       <div class="actions">
          <input type="text" @input="emit('fetch-ency', $event.target.value)" placeholder="全库搜索..." class="glass-input" />
          <button v-if="props.isAdmin" @click="openAdd" class="btn-add-ency">＋ 新增病害</button>
       </div>
    </div>

    <!-- 百科网格 -->
    <div class="ency-grid">
       <div v-for="item in props.data" :key="item.id" class="glass-card ency-card">
          <!-- 管理员操作悬浮层 -->
          <div v-if="props.isAdmin" class="admin-actions">
             <button @click="openEdit(item)" title="编辑" class="mini-btn">✏️</button>
             <button @click="deleteEntry(item.id)" title="删除" class="mini-btn del">🗑️</button>
          </div>

          <div class="card-img-wrapper">
             <img :src="item.image_url" class="card-img" />
             <div class="crop-tag" :class="item.crop_type.toLowerCase()">{{ item.crop_type }}</div>
          </div>
          <div class="card-body">
             <h2 class="disease-name">{{ item.name }}</h2>
             <div class="info-section">
                <label>🔬 病理成因</label>
                <p>{{ item.causes }}</p>
             </div>
             <div class="info-section">
                <label>🛡️ 防治策略</label>
                <p>{{ item.prevention }}</p>
             </div>
          </div>
       </div>
    </div>

    <!-- 沉浸式编辑弹窗 -->
    <transition name="fade">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="glass-card modal-content animate-pop">
           <h3>{{ isEditing ? '🖊️ 编辑病害资料' : '✨ 新增病害种类' }}</h3>
           
           <div class="form-grid">
              <div class="input-group">
                 <label>病害名称</label>
                 <input v-model="form.name" type="text" placeholder="如：苹果黑星病" />
              </div>
              <div class="input-group">
                 <label>所属作物</label>
                 <select v-model="form.crop_type">
                    <option value="Apple">苹果 (Apple)</option>
                    <option value="Grape">葡萄 (Grape)</option>
                    <option value="Other">其他</option>
                 </select>
              </div>
              <div class="input-group full">
                 <label>展示图片</label>
                 <div class="upload-wrapper">
                    <input type="text" v-model="form.image_url" placeholder="图片路径或 URL" readonly />
                    <label class="btn-upload">
                       📤 上传
                       <input type="file" @change="handleUpload" hidden accept="image/*" />
                    </label>
                 </div>
              </div>
              <div class="input-group full">
                 <label>病理成因</label>
                 <textarea v-model="form.causes" rows="3" placeholder="描述该病害的根源与爆发条件..."></textarea>
              </div>
              <div class="input-group full">
                 <label>防治建议</label>
                 <textarea v-model="form.prevention" rows="3" placeholder="提供专业的植保解决方案..."></textarea>
              </div>
           </div>

           <div class="modal-footer">
              <button @click="showModal = false" class="btn-cancel">取消</button>
              <button @click="saveEntry" class="btn-confirm">立即同步</button>
           </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.ency-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 3rem; }
.actions { display: flex; gap: 15px; }

.gradient-text { font-size: 2.8rem; font-weight: 800; background: linear-gradient(to right, #fff, var(--primary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.glass-input { background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); border-radius: 50px; padding: 12px 25px; color: #fff; outline: none; transition: 0.3s; }

.btn-add-ency { background: var(--primary); color: #022c22; border: none; border-radius: 50px; padding: 0 25px; font-weight: 800; cursor: pointer; transition: 0.3s; }
.btn-add-ency:hover { transform: scale(1.05); filter: brightness(1.1); box-shadow: 0 0 20px rgba(74, 222, 128, 0.4); }

/* 网格卡片 */
.ency-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 2rem; }
.ency-card { padding: 0; overflow: hidden; position: relative; }

.admin-actions { position: absolute; top: 10px; left: 10px; z-index: 20; display: flex; gap: 5px; opacity: 0; transition: 0.3s; }
.ency-card:hover .admin-actions { opacity: 1; }
.mini-btn { width: 32px; height: 32px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.6); backdrop-filter: blur(5px); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; }
.mini-btn:hover { background: var(--primary); }
.mini-btn.del:hover { background: #ef4444; }

.card-img-wrapper { height: 220px; background: #000; display: flex; justify-content: center; align-items: center; }
.card-img { max-width: 100%; max-height: 100%; object-fit: contain; }
.crop-tag { position: absolute; top: 15px; right: 15px; padding: 3px 12px; border-radius: 4px; color: #000; font-weight: 900; font-size: 0.7rem; }
.crop-tag.apple { background: #fb7185; }
.crop-tag.grape { background: #c084fc; }

.card-body { padding: 1.5rem; }
.disease-name { color: var(--primary); margin: 0 0 1rem 0; font-size: 1.4rem; }
.info-section { margin-bottom: 1rem; }
.info-section label { display: block; color: var(--primary); font-size: 0.8rem; font-weight: bold; margin-bottom: 4px; opacity: 0.8; }
.info-section p { font-size: 0.92rem; line-height: 1.6; color: #cbd5e1; margin: 0; }

/* 弹窗样式 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.8); backdrop-filter: blur(10px); z-index: 1000; display: flex; align-items: center; justify-content: center; }
.modal-content { width: 90%; max-width: 600px; padding: 2.5rem; border: 1px solid rgba(255,255,255,0.1); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin: 1.5rem 0; }
.input-group.full { grid-column: span 2; }
.input-group label { display: block; margin-bottom: 8px; font-size: 0.85rem; color: #94a3b8; }
.input-group input, .input-group select, .input-group textarea { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px; color: #fff; outline: none; }
.input-group input:focus, .input-group textarea:focus { border-color: var(--primary); }

.upload-wrapper { display: flex; gap: 10px; }
.btn-upload { background: rgba(255,255,255,0.1); padding: 0 15px; border-radius: 8px; display: flex; align-items: center; cursor: pointer; font-size: 0.85rem; }

.modal-footer { display: flex; justify-content: flex-end; gap: 15px; margin-top: 2rem; }
.btn-cancel { background: transparent; border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 10px 25px; border-radius: 8px; cursor: pointer; }
.btn-confirm { background: var(--primary); border: none; color: #022c22; font-weight: 800; padding: 10px 30px; border-radius: 8px; cursor: pointer; }

@keyframes pop { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
.animate-pop { animation: pop 0.3s ease-out; }
</style>
