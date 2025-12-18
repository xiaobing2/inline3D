<template>
  <div class="home-container">
    <!-- 背景视频 -->
    <div class="bg-video">
      <video src="/backvideo.mp4" autoplay muted loop playsinline preload="auto"></video>
    </div>

    <!-- 页面内容 -->
    <div class="content">
    <div class="hero-section">
      <h1>AI+3D模型创建与编辑平台</h1>
      <p>选择一种方式开始你的3D创作之旅</p>
    </div>
    
    <div class="options-grid">
        <!-- 文字描述生成（弹窗） -->
        <div class="option-card option-blue" @click="openPromptModal">
        <div class="option-icon">
            <span class="icon-badge icon-blue">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
            </span>
        </div>
        <h2>文字描述生成</h2>
        <p>输入文字描述，AI将为您创建3D模型</p>
      </div>
      
        <!-- 图像生成（弹窗） -->
        <div class="option-card option-purple" @click="openImageModal">
        <div class="option-icon">
            <span class="icon-badge icon-purple">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
            </span>
        </div>
        <h2>图像生成</h2>
        <p>上传图像，AI将为您生成3D模型</p>
      </div>
      
        <!-- 加入房间（弹窗） -->
        <div class="option-card option-pink" @click="openJoinModal">
        <div class="option-icon">
            <span class="icon-badge icon-pink">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
            </span>
        </div>
        <h2>在线编辑</h2>
        <p>输入房间号，在线编辑3D模型</p>
        </div>
      </div>
    </div>

    <!-- 文字生成弹窗（带3D效果） -->
    <div v-if="showPromptModal" class="modal-mask" @click.self="closePromptModal">
      <div class="modal-wrapper">
        <div class="modal-card">
          <div class="modal-3d" ref="fx3d"></div>
          <div class="modal-content">
            <h3>用文字创建3D模型</h3>
            <p class="sub">描述你想要的模型（例如：一辆红色跑车，科幻风格）</p>
            <textarea v-model="prompt" :disabled="isGenerating" rows="4" placeholder="请输入模型描述..."></textarea>
            <div class="actions">
              <button class="btn-cancel" @click="closePromptModal" :disabled="isGenerating">取消</button>
              <button class="btn-primary" @click="generateFromText" :disabled="isGenerating || !prompt.trim()">{{ isGenerating ? '生成中...' : '开始生成' }}</button>
            </div>
            <div class="tip" v-if="errorMessage">{{ errorMessage }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图像生成弹窗（带3D效果） -->
    <div v-if="showImageModal" class="modal-mask" @click.self="closeImageModal">
      <div class="modal-wrapper">
        <div class="modal-card">
          <div class="modal-3d" ref="fx3d"></div>
          <div class="modal-content">
            <h3>上传图像生成3D模型</h3>
            <p class="sub">选择一张参考图片，AI 将生成对应的3D模型</p>
            <input type="file" id="imgInput" class="file-input" accept="image/*" @change="handleImageSelect" :disabled="isGeneratingImage">
            <label class="file-label" for="imgInput">
              <span v-if="!imageFile">选择图片文件</span>
              <span v-else>{{ imageFile.name }}</span>
            </label>
            <div v-if="imagePreview" class="image-preview"><img :src="imagePreview" alt="预览" /></div>
            <div class="actions">
              <button class="btn-cancel" @click="closeImageModal" :disabled="isGeneratingImage">取消</button>
              <button class="btn-primary" @click="generateFromImage" :disabled="isGeneratingImage || !imageFile">{{ isGeneratingImage ? '生成中...' : '开始生成' }}</button>
            </div>
            <div class="tip" v-if="imageError">{{ imageError }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加入房间弹窗（带3D效果） -->
    <div v-if="showJoinModal" class="modal-mask" @click.self="closeJoinModal">
      <div class="modal-wrapper">
        <div class="modal-card">
          <div class="modal-3d" ref="fx3d"></div>
          <div class="modal-content">
            <h3>加入3D模型编辑房间</h3>
            <p class="sub">输入房间号（jobId），若模型已完成将直接加载</p>
            <input v-model="jobIdJoin" type="text" class="input" placeholder="请输入jobId" :disabled="joinLoading || joinChecking">
            <div class="actions">
              <button class="btn-cancel" @click="closeJoinModal" :disabled="joinLoading || joinChecking">取消</button>
              <button class="btn-primary" @click="joinRoomFromModal" :disabled="joinLoading || joinChecking || !jobIdJoin.trim()">{{ joinLoading ? '查询中...' : '加入房间' }}</button>
            </div>
            <div class="tip" v-if="joinError">{{ joinError }}</div>

            <div v-if="joinChecking" class="status-mini">
              <div class="bar"><div class="bar-inner" :style="{ width: joinProgress + '%' }"></div></div>
              <div class="status-text">{{ joinStatusMsg }} {{ joinProgress }}%</div>
              <button class="btn-cancel small" @click="stopJoinChecking">停止检查</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as THREE from 'three'
import { API_BASE } from '../config.js'

export default {
  name: 'HomePage',
  mounted() {
    // 预热请求，访问后端根目录，忽略结果
    fetch(API_BASE).catch(err => {
      console.warn('Backend pre-flight request failed:', err);
    });
  },
  data() {
    return {
      // 文字生成
      showPromptModal: false,
      prompt: '',
      isGenerating: false,
      errorMessage: null,
      // 图像生成
      showImageModal: false,
      imageFile: null,
      imagePreview: null,
      isGeneratingImage: false,
      imageError: null,
      // 加入房间
      showJoinModal: false,
      jobIdJoin: '',
      joinLoading: false,
      joinError: null,
      joinChecking: false,
      joinProgress: 0,
      joinStatusMsg: '',
      joinTimer: null,
      // three.js 特效实例
      fx: { scene: null, camera: null, renderer: null, animId: null, mesh: null, particles: null },
      fxResize: null
    }
  },
  methods: {
    // 首页跳转给父组件（用于其它卡片仍需页面切换时）
    navigateTo(section) {
      this.$emit('select-option', section)
    },

    // ========== 文字生成 ==========
    openPromptModal() { this.showPromptModal = true; this.$nextTick(() => { this.initFx3D() }) },
    closePromptModal() { this.disposeFx3D(); this.showPromptModal = false; this.errorMessage = null },
    async generateFromText() {
      if (!this.prompt.trim()) return
      this.isGenerating = true; this.errorMessage = null
      try {
        const resp = await fetch(`${API_BASE}/api/models/generate/text`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: this.prompt, format: 'glb' })
        })
        if (!resp.ok) { const msg = await resp.text().catch(() => ''); throw new Error(msg || `HTTP ${resp.status}`) }
        const data = await resp.json().catch(() => ({}))
        if (data && data.jobId) {
          localStorage.setItem('modelJobId', data.jobId)
          this.$emit('text-job-created', { jobId: data.jobId })
          this.closePromptModal()
        } else { throw new Error('未返回任务ID') }
      } catch (e) { console.error(e); this.errorMessage = '生成任务创建失败，请稍后重试' }
      finally { this.isGenerating = false }
    },

    // ========== 图像生成 ==========
    openImageModal() { this.showImageModal = true; this.$nextTick(() => { this.initFx3D() }) },
    closeImageModal() { this.disposeFx3D(); this.showImageModal = false; this.imageFile = null; this.imagePreview = null; this.imageError = null },
    handleImageSelect(e) {
      const file = e.target.files && e.target.files[0]
      if (!file) return
      if (!file.type.startsWith('image/')) { this.imageError = '请选择有效的图片文件'; return }
      this.imageFile = file
      const reader = new FileReader()
      reader.onload = ev => { this.imagePreview = ev.target.result }
      reader.readAsDataURL(file)
    },
    async generateFromImage() {
      if (!this.imageFile) return
      this.isGeneratingImage = true; this.imageError = null
      try {
        const fd = new FormData()
        fd.append('file', this.imageFile)
        fd.append('format', 'glb')
        const resp = await fetch(`${API_BASE}/api/models/generate/image`, { method: 'POST', body: fd })
        if (!resp.ok) { const msg = await resp.text().catch(() => ''); throw new Error(msg || `HTTP ${resp.status}`) }
        const data = await resp.json().catch(() => ({}))
        if (data && data.jobId) {
          localStorage.setItem('modelJobId', data.jobId)
          // 统一让父组件进入模型状态页
          this.$emit('image-job-created', { jobId: data.jobId })
          this.closeImageModal()
        } else { throw new Error('未返回任务ID') }
      } catch (e) { console.error(e); this.imageError = '生成任务创建失败，请稍后重试' }
      finally { this.isGeneratingImage = false }
    },

    // ========== 加入房间 ==========
    openJoinModal() { this.showJoinModal = true; this.$nextTick(() => { this.initFx3D() }) },
    closeJoinModal() { this.disposeFx3D(); this.stopJoinChecking(); this.showJoinModal = false; this.jobIdJoin = ''; this.joinError = null },
    normalizeUrl(url) {
      if (!url) return url
      if (!url.startsWith('http://') && !url.startsWith('https://')) return `http://${url}`
      return url
    },
    async joinRoomFromModal() {
      if (!this.jobIdJoin.trim()) { this.joinError = '请输入有效的jobId'; return }
      this.joinLoading = true; this.joinError = null
      try {
        const resp = await fetch(`${API_BASE}/api/models/generate/getstatus`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ jobId: this.jobIdJoin })
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const data = await resp.json()
        localStorage.setItem('modelJobId', this.jobIdJoin)
        let status = data.status !== undefined ? data.status : data.Status
        if (typeof status === 'string') {
          if (/^\d+$/.test(status)) {
            status = parseInt(status, 10)
          } else {
            const s = status.toUpperCase()
            if (s === 'DONE' || s === 'SUCCEEDED' || s === 'SUCCESS') status = 3
            else if (s === 'RUN' || s === 'RUNNING') status = 1
            else if (s === 'FAIL' || s === 'FAILED') status = 2
            else status = 1
          }
        }
        status = parseInt(status)
        if (status === 3) {
          // 构建模型URL
          let modelUrl = ''
          if (data.target3durl) {
            const normalized = this.normalizeUrl(data.target3durl)
            const base = normalized.endsWith('/') ? normalized.slice(0, -1) : normalized
            modelUrl = `${base}/${this.jobIdJoin}.glb`
          } else {
            modelUrl = `${API_BASE}/uploads/${this.jobIdJoin}/${this.jobIdJoin}.glb`
          }
          const previewImageUrl = data.targetimgurl ? this.normalizeUrl(data.targetimgurl) : ''
          this.$emit('load-model', { modelUrl, previewImageUrl, jobId: this.jobIdJoin })
          this.closeJoinModal()
        } else {
          this.startJoinChecking()
        }
      } catch (e) {
        console.error('加入房间失败', e)
        this.joinError = '加入房间失败，请核对 jobId 或稍后重试'
      } finally { this.joinLoading = false }
    },
    startJoinChecking() {
      this.joinChecking = true; this.joinProgress = 10; this.joinStatusMsg = '正在检查模型生成状态...'
      this.stopJoinChecking()
      this.joinTimer = setInterval(() => { this.checkJoinStatus() }, 3000)
      this.checkJoinStatus()
    },
    stopJoinChecking() { if (this.joinTimer) { clearInterval(this.joinTimer); this.joinTimer = null } this.joinChecking = false },
    async checkJoinStatus() {
      try {
        const resp = await fetch('http://localhost:8082/api/models/generate/getstatus', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ jobId: this.jobIdJoin })
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const data = await resp.json()
        let status = data.status !== undefined ? data.status : data.Status
        if (typeof status === 'string') {
          if (/^\d+$/.test(status)) {
            status = parseInt(status, 10)
          } else {
            const s = status.toUpperCase()
            if (s === 'DONE' || s === 'SUCCEEDED' || s === 'SUCCESS') status = 3
            else if (s === 'FAIL' || s === 'FAILED') { this.joinStatusMsg = '模型生成失败'; this.stopJoinChecking(); this.joinError = '模型生成失败'; return }
            else if (s === 'RUN' || s === 'RUNNING') status = 1
            else status = 1
          }
        }
        status = parseInt(status)
        if (status === 3) {
          this.joinStatusMsg = '模型生成成功！'; this.joinProgress = 100; this.stopJoinChecking()
          // 构建模型URL
          let modelUrl = ''
          if (data.target3durl) {
            const normalized = this.normalizeUrl(data.target3durl)
            const base = normalized.endsWith('/') ? normalized.slice(0, -1) : normalized
            modelUrl = `${base}/${this.jobIdJoin}.glb`
          } else {
            modelUrl = `${API_BASE}/uploads/${this.jobIdJoin}/${this.jobIdJoin}.glb`
          }
          const previewImageUrl = data.targetimgurl ? this.normalizeUrl(data.targetimgurl) : ''
          this.$emit('load-model', { modelUrl, previewImageUrl, jobId: this.jobIdJoin })
          this.closeJoinModal()
        } else if (status === 0 || status === 1) {
          this.joinStatusMsg = status === 0 ? '模型排队等待中...' : '模型正在生成中...'
          this.joinProgress = Math.min(90, this.joinProgress + Math.floor(Math.random() * 6) + 3)
        } else if (status === 2) {
          this.joinStatusMsg = '模型生成失败'; this.stopJoinChecking(); this.joinError = '模型生成失败'
        } else {
          this.joinStatusMsg = '模型处理中...'; this.joinProgress = Math.min(90, this.joinProgress + Math.floor(Math.random() * 6) + 3)
        }
      } catch (e) {
        console.error('检查模型状态失败', e)
        this.joinStatusMsg = '检查失败'; this.stopJoinChecking(); this.joinError = '检查模型状态失败'
      }
    },

    // ========== 3D 特效（通用） ==========
    initFx3D() {
      const container = this.$refs.fx3d
      const w = container?.clientWidth || 640
      const h = container?.clientHeight || 220

      const scene = new THREE.Scene()
      const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100)
      camera.position.set(0, 0, 6)

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
      renderer.setSize(w, h)
      renderer.setPixelRatio(window.devicePixelRatio || 1)
      container.appendChild(renderer.domElement)

      // 灯光
      scene.add(new THREE.AmbientLight(0xffffff, 0.65))
      const dir = new THREE.DirectionalLight(0xffffff, 0.95)
      dir.position.set(3, 5, 6)
      scene.add(dir)

      // 主体：TorusKnot（简洁且美观）
      const geo = new THREE.TorusKnotGeometry(1.05, 0.33, 320, 40, 2, 3)
      const mat = new THREE.MeshPhysicalMaterial({
        color: new THREE.Color().setHSL(0.62, 0.65, 0.58),
        metalness: 0.65,
        roughness: 0.18,
        clearcoat: 1.0,
        clearcoatRoughness: 0.08,
        transmission: 0.05,
        sheen: 0.25,
        ior: 1.25
      })
      const mesh = new THREE.Mesh(geo, mat)
      mesh.rotation.x = 0.6
      scene.add(mesh)

      // 粒子环（两层），用于“生成中”速度/颜色加速
      const createRing = (radius, count, size) => {
        const g = new THREE.BufferGeometry()
        const pos = new Float32Array(count * 3)
        for (let i = 0; i < count; i++) {
          const ang = (i / count) * Math.PI * 2
          const r = radius + (Math.random() - 0.5) * 0.12
          pos[i * 3] = Math.cos(ang) * r
          pos[i * 3 + 1] = (Math.random() - 0.5) * 0.6
          pos[i * 3 + 2] = Math.sin(ang) * r
        }
        g.setAttribute('position', new THREE.BufferAttribute(pos, 3))
        const m = new THREE.PointsMaterial({ color: 0xffffff, size, opacity: 0.85, transparent: true })
        return new THREE.Points(g, m)
      }
      const ring1 = createRing(2.4, 420, 0.02)
      const ring2 = createRing(3.1, 520, 0.018)
      scene.add(ring1)
      scene.add(ring2)

      // 状态
      this.fx = {
        scene, camera, renderer, animId: null,
        mesh,
        mat,
        pMat1: ring1.material, pMat2: ring2.material,
        hue: 0.6, boost: 0, t0: performance.now()
      }

      const lerp = (a, b, k) => a + (b - a) * k

      const animate = () => {
        // 早退：弹窗关闭或已释放资源
        if (!this.fx || !this.fx.renderer) return
        this.fx.animId = requestAnimationFrame(animate)
        const t = (performance.now() - this.fx.t0) / 1000
        const generating = !!(this.isGenerating || this.isGeneratingImage || this.joinChecking)
        const targetBoost = generating ? 1 : 0
        this.fx.boost = lerp(this.fx.boost, targetBoost, 0.06)
        const speed = 0.6 + 2.0 * this.fx.boost

        // 旋转/摆动（判空保护）
        if (this.fx && this.fx.mesh) {
          const m = this.fx.mesh
          m.rotation.x += 0.15 * 0.01 * speed * 9
          m.rotation.y += 0.24 * 0.01 * speed * 9
          m.position.y = Math.sin(t * (0.6 + this.fx.boost)) * 0.06
        }

        // 粒子旋转
        ring1.rotation.y -= 0.003 * speed
        ring2.rotation.y += 0.002 * speed

        // 颜色渐变（HSL）+ 粒子脉冲大小
        this.fx.hue = (this.fx.hue + 0.002 + 0.012 * this.fx.boost) % 1
        const c1 = new THREE.Color().setHSL(this.fx.hue, 0.65, 0.6)
        const c2 = new THREE.Color().setHSL((this.fx.hue + 0.15) % 1, 0.6, 0.55)
        this.fx.pMat1.color.copy(c1)
        this.fx.pMat2.color.copy(c2)
        this.fx.pMat1.size = 0.02 + 0.012 * (0.5 + 0.5 * Math.sin(t * (6 + 8 * this.fx.boost)))
        this.fx.pMat2.size = 0.018 + 0.01 * (0.5 + 0.5 * Math.cos(t * (5 + 7 * this.fx.boost)))
        if (this.fx && this.fx.mat) { this.fx.mat.color.lerp(c2, 0.15) }

        renderer.render(scene, camera)
      }
      animate()

      this.fxResize = this.onFxResize.bind(this)
      window.addEventListener('resize', this.fxResize)
    },
    disposeFx3D() {
      cancelAnimationFrame(this.fx.animId)
      if (this.fxResize) { window.removeEventListener('resize', this.fxResize) }
      if (this.fx.renderer && this.$refs.fx3d) {
        try { this.$refs.fx3d.removeChild(this.fx.renderer.domElement) } catch(e) { console.warn('移除fx3d画布失败或已移除', e) }
      }
      if (this.fx.scene) {
        this.fx.scene.traverse((obj) => { if (obj.geometry) obj.geometry.dispose(); if (obj.material) { if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose()); else obj.material.dispose() } })
      }
      this.fx = { scene: null, camera: null, renderer: null, animId: null, mesh: null, particles: null }
    },
    onFxResize() {
      if (!this.fx.renderer) return
      const container = this.$refs.fx3d
      if (!container) return
      const w = container.clientWidth; const h = container.clientHeight
      this.fx.renderer.setSize(w, h); this.fx.camera.aspect = w / h; this.fx.camera.updateProjectionMatrix()
    }
  },
  beforeDestroy() { this.disposeFx3D(); this.stopJoinChecking() }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&display=swap');

:root { --card-bg: rgba(255,255,255,1); --card-bg-hover: rgba(255,255,255,1); }

.home-container { position: relative; min-height: 100vh; display: flex; flex-direction: column; align-items: center; }
.home-container::before { content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.35); z-index: 0; }
.bg-video { position: fixed; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: -1; }
.bg-video video { width: 100%; height: 100%; object-fit: cover; }
.content { position: relative; z-index: 1; width: 100%; padding: 2.5rem 2rem; }
.hero-section { text-align: center; margin-bottom: 2.5rem; }
.hero-section h1 { font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Noto Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 2.8rem; font-weight: 800; color: #fff; margin-bottom: .75rem; letter-spacing: .5px; text-shadow: 0 6px 28px rgba(0,0,0,.35); }
.hero-section p { font-size: 1.05rem; color: #eef1f5; text-shadow: 0 2px 12px rgba(0,0,0,.28); }

.options-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 360px)); gap: 2rem; width: 100%; max-width: 1200px; margin: 0 auto; justify-content: center; justify-items: center; }
.option-card { width: 340px; height: 250px; background: var(--card-bg); border: 1px solid rgba(255,255,255,0.55); border-radius: 16px; padding: 1.75rem 1.5rem; box-shadow: 0 20px 60px rgba(0,0,0,0.20); transition: transform .25s ease, box-shadow .25s ease, background-color .25s ease; cursor: pointer; display: flex; flex-direction: column; align-items: center; text-align: center; backdrop-filter: blur(6px); }
.option-card:hover { transform: translateY(-8px); box-shadow: 0 28px 70px rgba(0,0,0,0.28); background: var(--card-bg-hover); }
.option-icon { margin-bottom: 1rem; }
.icon-badge { display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 50%; color: #fff; box-shadow: 0 10px 24px rgba(0,0,0,.18); }
.icon-blue  { background: linear-gradient(135deg,#5D7BFF 0%, #7EA2FF 100%); }
.icon-purple{ background: linear-gradient(135deg,#8C5AFF 0%, #B07CFF 100%); }
.icon-pink  { background: linear-gradient(135deg,#FF66B2 0%, #FF8CCF 100%); }
.option-card h2 { font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Noto Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 1.25rem; font-weight: 800; color: #2b2f36; margin: .25rem 0 .6rem; }
.option-card p { color: #2f3640; line-height: 1.7; font-size: .98rem; font-weight: 500; letter-spacing: .2px; max-width: 260px; text-shadow: none; }

/* 弹窗样式 */
.modal-mask { position: fixed; z-index: 30; top: 0; left: 0; right: 0; bottom: 0; backdrop-filter: blur(4px); background: rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; padding: 1.5rem; }
.modal-wrapper { width: 100%; max-width: 840px; }
.modal-card { position: relative; border-radius: 16px; overflow: hidden; box-shadow: 0 28px 80px rgba(0,0,0,.35); background: rgba(255,255,255,0.96); border: 1px solid rgba(255,255,255,0.6); }
.modal-3d { width: 100%; height: 240px; background: radial-gradient(1200px 280px at 50% 0%, rgba(126,162,255,.35), transparent 60%); }
.modal-content { padding: 1.25rem 1.5rem 1.5rem; }
.modal-content h3 { font-size: 1.35rem; font-weight: 800; color: #2b2f36; margin-bottom: .25rem; }
.modal-content .sub { color: #5b6270; margin-bottom: .75rem; }
.modal-content textarea { width: 100%; resize: vertical; min-height: 120px; border-radius: 10px; border: 1px solid #e6e9f0; padding: .9rem 1rem; outline: none; font-size: .98rem; box-shadow: inset 0 1px 0 rgba(0,0,0,.02); }
.modal-content textarea:focus { border-color: #7ea2ff; box-shadow: 0 0 0 3px rgba(126,162,255,.2); }
.input { width: 100%; border: 1px solid #e6e9f0; border-radius: 10px; padding: .8rem 1rem; font-size: .98rem; }
.input:focus { outline: none; border-color: #7ea2ff; box-shadow: 0 0 0 3px rgba(126,162,255,.2); }
.actions { display: flex; gap: .75rem; justify-content: flex-end; margin-top: .9rem; }
.btn-cancel { background: #e9eef5; color: #2f3640; border: none; padding: .7rem 1.2rem; border-radius: 10px; cursor: pointer; }
.btn-cancel.small { padding: .45rem .9rem; border-radius: 8px; margin-top: .6rem; }
.btn-primary { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color: #fff; border: none; padding: .7rem 1.2rem; border-radius: 10px; cursor: pointer; box-shadow: 0 10px 24px rgba(102,126,234,.28); }
.btn-primary:disabled { opacity: .7; cursor: not-allowed; }
.tip { margin-top: .5rem; color: #b00020; }

/* 文件选择 & 预览 */
.file-input { display: none; }
.file-label { display: inline-block; margin-top: .5rem; padding: .7rem 1.2rem; background: #e9eef5; color: #2f3640; border-radius: 10px; cursor: pointer; }
.image-preview { margin-top: .75rem; border: 1px solid #e6e9f0; border-radius: 10px; overflow: hidden; max-height: 240px; display: flex; align-items: center; justify-content: center; }
.image-preview img { max-width: 100%; max-height: 240px; object-fit: contain; }

/* 小型状态条 */
.status-mini { margin-top: .9rem; }
.status-mini .bar { width: 100%; height: 10px; border-radius: 6px; background: #e9eef5; overflow: hidden; }
.status-mini .bar-inner { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); transition: width .5s ease; }
.status-mini .status-text { margin-top: .4rem; color: #495057; font-size: .9rem; text-align: right; }

@media (max-width: 768px) {
  .hero-section h1 { font-size: 2.1rem; }
  .option-card { width: 92%; height: 230px; }
  .modal-3d { height: 200px; }
}
</style>
