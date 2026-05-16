<script setup>
const props = defineProps(['records'])
const API_URL = 'http://localhost:8000' // 如果后端在 8000
</script>

<template>
  <div class="view-container animate-fade-in">
     <h1 style="margin-bottom: 2rem;">最近检测流水</h1>
     <div class="history-grid">
        <div v-for="rec in props.records" :key="rec.id" class="glass-card history-item">
           <img :src="rec.result_image" class="history-thumb" />
           <div class="history-meta">
              <h3>{{ rec.disease_name }}</h3>
              <p>{{ (rec.confidence*100).toFixed(1) }}%</p>
           </div>
        </div>
     </div>
  </div>
</template>
