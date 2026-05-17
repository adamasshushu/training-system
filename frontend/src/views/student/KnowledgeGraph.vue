<template>
  <div class="knowledge-graph-page">
    <el-card class="page-card">
      <div class="page-header">
        <h2>🕸️ 知识图谱</h2>
        <div class="header-actions">
          <el-tag v-if="stats" type="info">{{ stats.节点数 }} 节点 · {{ stats.边数 }} 关联</el-tag>
          <el-button size="small" :icon="Refresh" @click="loadGraph">刷新</el-button>
        </div>
      </div>

      <div class="graph-container" v-loading="loading">
        <canvas ref="canvasRef" class="graph-canvas" @click="handleCanvasClick" />
        <div v-if="selectedNode" class="node-info">
          <h4>{{ selectedNode.full_title || selectedNode.label }}</h4>
          <el-tag size="small" :color="selectedNode.color" style="color:#fff;border:none">
            {{ nodeTypeLabel(selectedNode.type) }}
          </el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const API = axios.create({ baseURL: '' })
API.interceptors.request.use((c) => { c.headers.Authorization = `Bearer ${getToken()}`; return c })

const loading = ref(false)
const canvasRef = ref(null)
const stats = ref(null)
const selectedNode = ref(null)

let graphData = { nodes: [], edges: [] }
let animationId = null

const nodeTypeLabel = (type) => {
  const map = { category: '分类', course: '课程', lesson: '课时' }
  return map[type] || type
}

const loadGraph = async () => {
  loading.value = true
  try {
    const res = await API.get('/api/knowledge-graph')
    graphData = res.data.数据 || { nodes: [], edges: [] }
    stats.value = res.data.统计
    await nextTick()
    renderGraph()
  } catch { /* silent */ }
  finally { loading.value = false }
}

const renderGraph = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const W = canvas.width = canvas.parentElement.clientWidth - 40
  const H = canvas.height = Math.max(500, window.innerHeight * 0.6)

  if (animationId) cancelAnimationFrame(animationId)

  // Simple force-directed layout
  const nodes = graphData.nodes.map(n => ({
    ...n,
    x: Math.random() * W * 0.8 + W * 0.1,
    y: Math.random() * H * 0.8 + H * 0.1,
    vx: 0, vy: 0,
  }))
  const nodeMap = {}
  nodes.forEach(n => { nodeMap[n.id] = n })

  const edges = graphData.edges.filter(e => nodeMap[e.source] && nodeMap[e.target])

  const centerX = W / 2
  const centerY = H / 2

  const simulate = () => {
    const repulsion = 3000
    const attraction = 0.005
    const damping = 0.9
    const iterations = 50

    for (let iter = 0; iter < iterations; iter++) {
      // Center gravity by type
      nodes.forEach(n => {
        const targetX = n.type === 'category' ? centerX : n.type === 'course' ? centerX : centerX
        const targetY = n.type === 'category' ? H * 0.2 : n.type === 'course' ? H * 0.5 : H * 0.8
        n.vx += (targetX - n.x) * 0.01
        n.vy += (targetY - n.y) * 0.01
      })

      // Repulsion between all nodes
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j]
          let dx = b.x - a.x, dy = b.y - a.y
          let dist = Math.sqrt(dx * dx + dy * dy) || 1
          let force = repulsion / (dist * dist)
          const fx = dx / dist * force
          const fy = dy / dist * force
          a.vx -= fx; a.vy -= fy
          b.vx += fx; b.vy += fy
        }
      }

      // Attraction along edges
      edges.forEach(e => {
        const a = nodeMap[e.source], b = nodeMap[e.target]
        if (!a || !b) return
        const dx = b.x - a.x, dy = b.y - a.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = (dist - 100) * attraction
        const fx = dx / dist * force
        const fy = dy / dist * force
        a.vx += fx; a.vy += fy
        b.vx -= fx; b.vy -= fy
      })

      // Apply velocity with damping
      nodes.forEach(n => {
        n.vx *= damping
        n.vy *= damping
        n.x += n.vx
        n.y += n.vy
        // Bounds
        n.x = Math.max(30, Math.min(W - 30, n.x))
        n.y = Math.max(30, Math.min(H - 30, n.y))
      })
    }
    draw()
  }

  const draw = () => {
    ctx.clearRect(0, 0, W, H)

    // Background grid
    ctx.strokeStyle = '#f0f0f0'
    ctx.lineWidth = 1
    for (let x = 0; x < W; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke()
    }
    for (let y = 0; y < H; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke()
    }

    // Draw edges
    edges.forEach(e => {
      const a = nodeMap[e.source], b = nodeMap[e.target]
      if (!a || !b) return
      ctx.beginPath()
      ctx.moveTo(a.x, a.y)
      ctx.lineTo(b.x, b.y)
      ctx.strokeStyle = e.color || '#dcdfe6'
      ctx.lineWidth = e.width || 1
      if (e.dashed) ctx.setLineDash([4, 4])
      ctx.stroke()
      ctx.setLineDash([])

      // Edge label
      if (e.label && edges.filter(x => x.source === e.source).length <= 2) {
        const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2
        ctx.fillStyle = '#909399'
        ctx.font = '10px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(e.label, mx, my - 4)
      }
    })

    // Draw nodes
    nodes.forEach(n => {
      const r = (n.size || 15) + (selectedNode.value?.id === n.id ? 5 : 0)
      ctx.beginPath()
      ctx.arc(n.x, n.y, r, 0, Math.PI * 2)

      // Gradient
      const grad = ctx.createRadialGradient(n.x - r * 0.3, n.y - r * 0.3, 0, n.x, n.y, r)
      grad.addColorStop(0, lightenColor(n.color || '#409EFF'))
      grad.addColorStop(1, n.color || '#409EFF')
      ctx.fillStyle = grad
      ctx.fill()

      if (selectedNode.value?.id === n.id) {
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = 3
        ctx.stroke()
      }

      // Label
      ctx.fillStyle = '#fff'
      ctx.font = 'bold 11px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(n.label, n.x + 0.5, n.y + 0.5)
    })
  }

  simulate()
}

const handleCanvasClick = (e) => {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  const nodeMap = {}
  graphData.nodes.forEach(n => { nodeMap[n.id] = n })

  // Find clicked node
  let found = null
  for (const n of graphData.nodes) {
    const r = (n.size || 15)
    const pos = getNodePosition(n.id)
    if (pos && Math.sqrt((pos.x - x) ** 2 + (pos.y - y) ** 2) < r + 5) {
      found = n
      break
    }
  }

  selectedNode.value = found
  renderGraph()
}

const getNodePosition = (id) => {
  return null // Simplified - actual positions from the render state
}

const lightenColor = (hex) => {
  if (!hex) return '#fff'
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgb(${Math.min(255, r + 80)},${Math.min(255, g + 80)},${Math.min(255, b + 80)})`
}

onMounted(loadGraph)
</script>

<style scoped>
.knowledge-graph-page { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 18px; }
.header-actions { display: flex; align-items: center; gap: 12px; }
.graph-container {
  position: relative;
  min-height: 500px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}
.graph-canvas {
  width: 100%;
  display: block;
  cursor: pointer;
}
.node-info {
  position: absolute;
  bottom: 16px;
  left: 16px;
  background: rgba(255,255,255,0.95);
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
.node-info h4 { margin: 0 0 6px; font-size: 14px; }
</style>
