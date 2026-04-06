<script setup>
const props = defineProps(['data'])
const emit = defineEmits(['fetch-ency'])
</script>

<template>
  <div class="view-container animate-fade-in">
     <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
        <h1>农作物病害百科库</h1>
        <input type="text" @input="emit('fetch-ency', $event.target.value)" placeholder="搜索病害名称..." class="search-input" />
     </div>
     <div class="ency-grid">
        <div v-for="item in props.data" :key="item.id" class="glass-card ency-card">
            <img :src="item.image_url" style="width: 100%; border-radius: 10px; height: 150px; object-fit: cover; margin-bottom: 1rem;" />
            <h2 style="color: #4ade80;">{{ item.name }} ({{ item.crop_type }})</h2>
            <p><strong>原因:</strong> {{ item.causes.substring(0, 50) }}...</p>
        </div>
     </div>
  </div>
</template>
