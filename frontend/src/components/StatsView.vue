<script setup>
const props = defineProps(['statsData'])
</script>

<template>
  <div class="view-container animate-fade-in">
     <h1>全平台数据大屏</h1>
     <div v-if="props.statsData" class="stats-overview">
        <div class="glass-card stat-box">
           <p>累计检测次数</p>
           <div style="font-size: 3rem; font-weight: 800; color: #4ade80;">{{ props.statsData.total_detections }}</div>
        </div>
        <div class="glass-card stat-box" style="flex: 2;">
           <p>高频病害榜 TOP 5</p>
           <div class="rank-list">
              <div v-for="(item, idx) in props.statsData.top_diseases" :key="idx" class="rank-item">
                 <span>{{ idx + 1 }}. {{ item.name }}</span>
                 <span>{{ item.value }} 次</span>
              </div>
           </div>
        </div>
     </div>
  </div>
</template>
