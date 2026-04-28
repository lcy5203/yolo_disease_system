<script setup>
import { computed } from 'vue'

// 这里的 props 增加了 historyRecords
const props = defineProps(['statsData', 'historyRecords'])

// 格式化日期辅助函数
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: '2-digit', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  })
}

// 统计逻辑 (适配后端新结构 + 智能兜底)
const totalCount = computed(() => {
  // 1. 优先使用统计接口数据
  let count = props.statsData?.total_count
  
  // 2. 兜底：如果统计接口为 0 或空，但流水记录有数据，直接取流水长度
  if (!count && props.historyRecords?.length > 0) {
    count = props.historyRecords.length
  }
  
  return typeof count === 'number' ? count : 0
})

const avgConf = computed(() => {
  let val = props.statsData?.avg_confidence
  if (!val && props.historyRecords?.length > 0) {
    const sum = props.historyRecords.reduce((acc, cur) => acc + (cur.confidence || 0), 0)
    val = sum / props.historyRecords.length
  }
  return ((val || 0) * 100).toFixed(1) + '%'
})

// 3. 核心：病害分布自愈逻辑
const diseaseCounts = computed(() => {
  // 优先使用统计接口数据
  if (props.statsData?.disease_counts && Object.keys(props.statsData.disease_counts).length > 0) {
    return props.statsData.disease_counts
  }
  
  // 兜底：现场解析流水记录中的病害分布
  const counts = {}
  if (props.historyRecords?.length > 0) {
    props.historyRecords.forEach(r => {
      const name = r.disease_name || '未知'
      counts[name] = (counts[name] || 0) + 1
    })
  }
  return counts
})
</script>

<template>
  <div class="view-container animate-fade-in stats-integrated">
    <!-- 头部：核心指标概览 (KPIs) -->
    <div class="stats-hero-grid">
       <div class="glass-card kpi-card">
          <div class="kpi-label">累计检测次数</div>
          <div class="kpi-value">{{ totalCount }} <span class="unit">次</span></div>
       </div>
       <div class="glass-card kpi-card prim">
          <div class="kpi-label">平均识别置信度</div>
          <div class="kpi-value">{{ avgConf }}</div>
       </div>
       <div class="glass-card kpi-card">
          <div class="kpi-label">系统运行状态</div>
          <div class="kpi-value online">稳定运行</div>
       </div>
    </div>

    <!-- 中间：病害分布热力条 (示例逻辑) -->
    <div class="glass-card distribution-section">
       <h3>病害分布密度</h3>
       <div class="dist-bar">
          <div v-for="(count, name) in diseaseCounts" 
               :key="name" 
               class="dist-segment"
               :style="{ width: (totalCount > 0 ? (count / totalCount * 100) : 0) + '%' }"
               :title="name + ': ' + count">
          </div>
       </div>
       <div class="dist-legend">
          <span v-for="(count, name) in diseaseCounts" :key="name">
             ● {{ name }} ({{ count }})
          </span>
       </div>
    </div>

    <!-- 底部：集成的检测流水模块 -->
    <div class="glass-card history-integrated">
       <div class="header-with-action">
          <h3>详细检测流水记录</h3>
          <span class="count-tag">共 {{ props.historyRecords?.length || 0 }} 条记录</span>
       </div>
       
       <div class="table-wrapper">
          <table class="history-table">
             <thead>
                <tr>
                   <th>时间轴</th>
                   <th>检测目标</th>
                   <th>置信度</th>
                   <th>作物类型</th>
                   <th>耗时</th>
                   <th>原始样本</th>
                   <th>推理结果</th>
                </tr>
             </thead>
             <tbody>
                <tr v-for="record in props.historyRecords" :key="record.id">
                   <td class="time">{{ formatDate(record.created_at) }}</td>
                   <td class="disease">{{ record.disease_name }}</td>
                   <td>
                      <div class="conf-pill">{{ (record.confidence * 100).toFixed(1) }}%</div>
                   </td>
                   <td>{{ record.crop_type || '未分类' }}</td>
                   <td class="time">{{ record.inference_time ? record.inference_time.toFixed(1) + 'ms' : '-' }}</td>
                   <td>
                      <img :src="record.original_image" class="thumb" @click="window.open(record.original_image)" />
                   </td>
                   <td>
                      <img :src="record.result_image" class="thumb res" @click="window.open(record.result_image)" />
                   </td>
                </tr>
             </tbody>
          </table>
          <div v-if="!props.historyRecords || props.historyRecords.length === 0" class="empty-hint">
             暂无检测流水数据
          </div>
       </div>
    </div>
  </div>
</template>

<style scoped>
.stats-hero-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; margin-bottom: 2rem; }
.kpi-card { padding: 2rem; text-align: center; }
.kpi-card.prim { border-color: var(--primary); background: rgba(74, 222, 128, 0.05); }
.kpi-label { font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.8rem; }
.kpi-value { font-size: 2.2rem; font-weight: 900; color: #fff; }
.kpi-value.online { color: var(--primary); font-size: 1.5rem; }
.unit { font-size: 1rem; opacity: 0.5; }

.distribution-section { margin-bottom: 2rem; padding: 2rem; }
.dist-bar { height: 12px; background: rgba(255,255,255,0.05); border-radius: 6px; display: flex; overflow: hidden; margin: 1.5rem 0; }
.dist-segment { height: 100%; border-right: 2px solid #000; transition: 0.3s; }
.dist-segment:nth-child(odd) { background: var(--primary); opacity: 0.8; }
.dist-segment:nth-child(even) { background: #3b82f6; opacity: 0.8; }
.dist-legend { display: flex; flex-wrap: wrap; gap: 15px; font-size: 0.85rem; color: #94a3b8; }

.history-integrated { padding: 2rem; }
.header-with-action { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.count-tag { font-size: 0.8rem; background: rgba(255,255,255,0.1); padding: 4px 12px; border-radius: 50px; }

.table-wrapper { overflow-x: auto; }
.history-table { width: 100%; border-collapse: collapse; min-width: 800px; }
.history-table th { text-align: left; padding: 12px; font-size: 0.85rem; color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.1); }
.history-table td { padding: 15px 12px; font-size: 0.95rem; border-bottom: 1px solid rgba(255,255,255,0.05); }

.disease { color: var(--primary); font-weight: bold; }
.time { font-family: monospace; opacity: 0.7; }
.conf-pill { display: inline-block; padding: 2px 8px; border-radius: 4px; background: rgba(74, 222, 128, 0.1); color: var(--primary); font-weight: 800; font-size: 0.8rem; }
.thumb { width: 45px; height: 45px; object-fit: cover; border-radius: 6px; cursor: zoom-in; transition: 0.2s; border: 1px solid rgba(255,255,255,0.1); }
.thumb.res { border-color: var(--primary); }
.thumb:hover { transform: scale(1.2); }

.empty-hint { padding: 4rem; text-align: center; color: #64748b; font-style: italic; }
</style>
