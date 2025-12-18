<template>
  <div id="app">
    <!-- 主页 -->
    <HomePage v-if="currentPage === 'home'"
              @select-option="handleSelectOption"
              @text-job-created="handleTextJobCreated"
              @image-job-created="handleTextJobCreated"
              @load-model="handleLoadModel"
    />
    
    <!-- 文字生成3D模型页面 -->
    <TextTo3D v-if="currentPage === 'text-to-3d'" @back="handleBack" @view-model-status="handleViewModelStatus" />
    
    <!-- 房间编辑器页面 -->
    <JoinRoom v-if="currentPage === 'room-editor'" @back="handleBack" @view-model-status="handleViewModelStatus" @load-model="handleLoadModel" />
    
    <!-- 模型生成状态页面 -->
    <div v-if="currentPage === 'model-status'">
      <button @click="handleBack" class="back-button">返回</button>
      <div class="model-status-container">
        <h2>模型生成状态</h2>
      <div v-if="currentJobId" class="job-id-container">
        <span class="job-id-text">任务ID: {{ currentJobId }}</span>
        <button @click="copyJobId" class="copy-btn">复制</button>
      </div>
      <p v-if="currentJobId" class="job-id-hint">你可以使用此ID在“在线编辑”中随时返回查看或编辑模型。</p>
        <div v-if="modelStatus.loading" class="loading-container">
          <div class="progress-bar">
            <div class="progress" :style="{ width: modelStatus.progress + '%' }"></div>
          </div>
          <p>{{ modelStatus.message }}</p>
        </div>
        <div v-else-if="modelStatus.error" class="error-container">
          <h3>生成失败</h3>
          <p>{{ modelStatus.error }}</p>
          <button @click="handleRetry" class="retry-button">重试</button>
        </div>
        <div v-else-if="modelStatus.success" class="success-container">
          <h3>生成成功</h3>
          <button @click="handleLoadModelFromStatus" class="load-button">加载模型</button>
        </div>
      </div>
    </div>
    
    <!-- 模型上传与编辑页面 -->
    <div v-if="currentPage === 'model-editor'" class="model-editor-page">
      <button @click="handleBack" class="back-button">返回主页</button>
      <header class="app-header">
        <h1>智能3D设计助手平台</h1>
        <p>上传您的3D模型文件，开始设计之旅</p>
      </header>
      
      <div class="main-content-wrapper">
        <!-- 左侧：3D场景容器 -->
        <div class="scene-container-wrapper">
                    <div ref="threeContainer" class="three-container"></div>
          <!-- 模型加载遮罩 -->
          <div v-if="isModelLoading" class="loading-overlay">
            <div class="loading-content">
              <div class="spinner"></div>
              <p>正在加载模型...</p>
              <div class="loading-progress-bar">
                <div class="loading-progress" :style="{ width: modelLoadProgress + '%' }"></div>
              </div>
              <p>{{ modelLoadProgress }}%</p>
            </div>
          </div>
        </div>
        
        <!-- 右侧：功能面板 -->
        <div class="right-panel">
          <!-- 标签页导航 -->
          <div class="tabs-nav">
            <button 
              :class="['tab-btn', { active: activeTab === 'adjust' }]"
              @click="activeTab = 'adjust'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"></path>
              </svg>
              模型调整
            </button>
            <button 
              :class="['tab-btn', { active: activeTab === 'upload' }]"
              @click="activeTab = 'upload'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              上传模型
            </button>
            <button 
              :class="['tab-btn', { active: activeTab === 'texture' }]"
              @click="activeTab = 'texture'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              生成纹理
            </button>
            <button 
              :class="['tab-btn', { active: activeTab === 'history' }]"
              @click="activeTab = 'history'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
              操作历史
            </button>
          </div>
          
          <!-- 标签页内容 -->
          <div class="tabs-content">
            <!-- 模型调整标签页（新增通用处理 + 纹理应用） -->
            <div v-show="activeTab === 'adjust'" class="tab-panel">
              <h3>模型调整</h3>
              <div v-if="!loadedModel" class="no-model-tip">
                <p>请先在“上传模型”标签上传模型后再进行调整</p>
              </div>
              <div v-else class="control-panel">
                <!-- 变换控制 -->
                <div class="control-group">
                  <h4>变换控制</h4>
                  <div class="control-item">
                    <label>位置 (X/Y/Z)</label>
                    <div class="triple-input">
                      <input type="number" step="0.1" v-model.number="posX" />
                      <input type="number" step="0.1" v-model.number="posY" />
                      <input type="number" step="0.1" v-model.number="posZ" />
                    </div>
                  </div>
                  <div class="control-item">
                    <label>旋转 (度) (X/Y/Z)</label>
                    <div class="triple-input">
                      <input type="number" step="1" v-model.number="rotX" />
                      <input type="number" step="1" v-model.number="rotY" />
                      <input type="number" step="1" v-model.number="rotZ" />
                    </div>
                  </div>
                  <div class="control-item">
                    <label>缩放 (统一)</label>
                    <input type="range" min="0.1" max="5" step="0.1" v-model.number="scaleU" />
                  </div>
                  <div class="preset-buttons" style="flex-direction: row; gap: .5rem; margin-top: .5rem;">
                    <button class="preset-btn" @click="applyTransform">应用变换</button>
                    <button class="preset-btn" @click="resetTransform">重置变换</button>
                    <button class="preset-btn" @click="centerModel">居中到原点</button>
                    <button class="preset-btn" @click="fitModelToView">适配视图</button>
                  </div>
                </div>

                <!-- 材质设置（原有） -->
                <div class="control-group">
                  <h4>材质设置</h4>
                  <div class="control-item">
                    <label>模型颜色</label>
                    <input type="color" v-model="materialColor" @change="updateMaterialColor" />
                  </div>
                  <div class="control-item">
                    <label>材质亮度</label>
                    <input type="range" min="0" max="2" step="0.1" v-model.number="materialEmissive" @input="updateMaterialEmissive" />
                  </div>
                  <div class="control-item">
                    <label>材质金属度</label>
                    <input type="range" min="0" max="1" step="0.1" v-model.number="materialMetalness" @input="updateMaterialMetalness" />
                  </div>
                  <div class="control-item">
                    <label>材质粗糙度</label>
                    <input type="range" min="0" max="1" step="0.1" v-model.number="materialRoughness" @input="updateMaterialRoughness" />
                  </div>
                </div>

                <!-- 纹理应用（常用 + 自定义） -->
                <div class="control-group">
                  <h4>纹理应用</h4>
                  <div class="control-item">
                    <label>常用纹理</label>
                    <select v-model="presetTextureKey" class="texture-mode-select">
                      <option value="">不使用</option>
                      <option v-for="tex in presetTextures" :key="tex.key" :value="tex.key">{{ tex.name }}</option>
                    </select>
                  </div>
                  <div class="preset-buttons" style="flex-direction: row; gap: .5rem; margin-bottom: .5rem;">
                    <button class="preset-btn" @click="applyPresetTexture">应用常用纹理</button>
                    <button class="preset-btn" @click="clearTexture">移除纹理</button>
                  </div>
                  <div class="control-item">
                    <label>自定义纹理图片</label>
                    <input 
                      type="file" 
                      id="userTexInput"
                      accept="image/*"
                      @change="handleUserTextureSelect"
                      class="file-input"
                    />
                    <label for="userTexInput" class="file-label">
                      <span v-if="!userTextureFile">选择图片文件</span>
                      <span v-else>{{ userTextureFile.name }}</span>
                    </label>
                  </div>
                  <div v-if="userTexturePreview" class="image-preview" style="margin-bottom:.5rem;">
                    <img :src="userTexturePreview" alt="预览" />
                  </div>
                  <div class="control-item">
                    <label>UV 平铺 (X/Y)</label>
                    <div class="triple-input">
                      <input type="number" step="0.1" v-model.number="textureRepeatX" />
                      <input type="number" step="0.1" v-model.number="textureRepeatY" />
                    </div>
                  </div>
                  <div class="control-item">
                    <label>纹理旋转 (度)</label>
                    <input type="number" step="1" v-model.number="textureRotation" />
                  </div>
                  <div class="preset-buttons" style="flex-direction: row; gap: .5rem;">
                    <button class="preset-btn" @click="applyUserTexture" :disabled="!userTextureFile">应用自定义纹理</button>
                  </div>
                </div>

                <!-- 光照与显示 -->
                <div class="control-group">
                  <h4>显示与光照</h4>
                  <div class="control-item">
                    <label>主光源颜色</label>
                    <input type="color" v-model="lightColor" @change="updateLightColor" />
                  </div>
                  <div class="control-item">
                    <label>主光源强度</label>
                    <input type="range" min="0" max="2" step="0.1" v-model.number="lightIntensity" @input="updateLightIntensity" />
                  </div>
                  <div class="control-item">
                    <label>环境光强度</label>
                    <input type="range" min="0" max="1" step="0.1" v-model.number="ambientIntensity" @input="updateAmbientIntensity" />
                  </div>
                  <div class="control-item">
                    <label><input type="checkbox" v-model="wireframe" @change="applyWireframe" /> 线框显示</label>
                  </div>
                  <div class="control-item">
                    <label><input type="checkbox" v-model="castShadow" @change="applyShadows" /> 投射阴影</label>
                  </div>
                  <div class="control-item">
                    <label><input type="checkbox" v-model="receiveShadow" @change="applyShadows" /> 接收阴影</label>
                  </div>
                  <div class="control-item">
                    <label>背景颜色</label>
                    <input type="color" v-model="backgroundColor" @change="updateBackgroundColor" />
                  </div>
                  <div class="control-item">
                    <label>网格显示 <input type="checkbox" v-model="showGrid" @change="toggleGrid" /></label>
                  </div>
                  <div class="control-item">
                    <label>坐标系显示 <input type="checkbox" v-model="showAxes" @change="toggleAxes" /></label>
                  </div>
                </div>

                <!-- 几何处理 -->
                <div class="control-group">
                  <h4>几何处理</h4>
                  <div class="preset-buttons" style="flex-direction: row; gap: .5rem; margin-bottom:.5rem;">
                    <button class="preset-btn" @click="recalcNormals">重新计算法线</button>
                    <button class="preset-btn" @click="mergeAllMeshes">合并网格</button>
                  </div>
                  <div class="control-item">
                    <label>简化模型（保留比例）</label>
                    <input type="range" min="0.1" max="1" step="0.05" v-model.number="simplifyRatio" />
                    <div style="margin-top:.5rem;">
                      <button class="preset-btn" @click="applySimplify">应用简化</button>
                    </div>
                  </div>
                </div>

                <!-- 视角预设 -->
                <div class="control-group">
                  <h4>视角预设</h4>
                  <div class="preset-buttons">
                    <button @click="setPerspective('front')" class="preset-btn">正面视角</button>
                    <button @click="setPerspective('side')" class="preset-btn">侧面视角</button>
                    <button @click="setPerspective('top')" class="preset-btn">俯视视角</button>
                    <button @click="setPerspective('isometric')" class="preset-btn">等轴视角</button>
                  </div>
                </div>

                <!-- 动画控制（如有） -->
                <div class="control-group" v-if="hasAnimation">
                  <h4>动画控制</h4>
                  <div class="control-item">
                    <button @click="toggleAnimation" class="preset-btn">
                      {{ animationPlaying ? '暂停动画' : '播放动画' }}
                    </button>
                  </div>
                  <div class="control-item">
                    <label>动画速度</label>
                    <input type="range" min="0.1" max="3" step="0.1" v-model.number="animationSpeed" @input="updateAnimationSpeed" />
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 上传模型标签页（仅保留上传相关内容） -->
            <div v-show="activeTab === 'upload'" class="tab-panel">
              <h3>上传模型</h3>
              <div class="upload-section">
                <div class="upload-container">
                  <input 
                    type="file" 
                    id="fileInput"
                    ref="fileInput" 
                    accept=".glb,.gltf" 
                    @change="handleFileSelect"
                    class="file-input"
                  />
                  <label for="fileInput" class="file-label">
                    <span v-if="!selectedFile">选择GLB/GLTF文件</span>
                    <span v-else>{{ selectedFile.name }}</span>
                  </label>
                  <button 
                    @click="uploadModel" 
                    :disabled="!selectedFile" 
                    class="upload-btn"
                  >
                    上传模型
                  </button>
                  <button 
                    v-if="loadedModel" 
                    @click="saveModel" 
                    class="save-btn"
                  >
                    保存当前模型
                  </button>
                </div>
                <div v-if="uploadStatus" class="upload-status">
                  {{ uploadStatus }}
                </div>
              </div>
            </div>
            
            <!-- 生成纹理标签页（AI 纹理生成，保持不变） -->
            <div v-show="activeTab === 'texture'" class="tab-panel">
              <h3>生成模型纹理</h3>
              <div v-if="!loadedModel" class="no-model-tip">
                <p>请先上传模型后再生成纹理</p>
              </div>
              <div v-else class="texture-generation-section">
                <!-- 纹理调用选择器 -->
                <div class="form-group">
                  <label>纹理生成方式</label>
                  <select v-model="textureMode" class="texture-mode-select">
                    <option value="prompt">提示词生成</option>
                    <option value="image">图片生成</option>
                  </select>
                </div>
                
                <!-- 提示词生成模式 -->
                <div v-if="textureMode === 'prompt'" class="texture-content">
                  <div class="form-group">
                    <label>纹理描述提示词</label>
                    <textarea 
                      v-model="texturePrompt" 
                      placeholder="请输入纹理描述，例如：木纹材质、金属质感、粗糙的石头表面..."
                      rows="4"
                      :disabled="isGeneratingTexture"
                      class="texture-textarea"
                    ></textarea>
                  </div>
                  <button 
                    @click="generateTextureFromPrompt" 
                    :disabled="!texturePrompt.trim() || isGeneratingTexture"
                    class="generate-texture-btn"
                  >
                    {{ isGeneratingTexture ? '生成中...' : '生成纹理' }}
                  </button>
                </div>
                
                <!-- 图片生成模式 -->
                <div v-if="textureMode === 'image'" class="texture-content">
                  <div class="form-group">
                    <label>上传参考图片</label>
                    <input 
                      type="file" 
                      id="textureImageInput"
                      ref="textureImageInput" 
                      accept="image/*" 
                      @change="handleTextureImageSelect"
                      class="file-input"
                    />
                    <label for="textureImageInput" class="file-label">
                      <span v-if="!selectedTextureImage">选择图片文件</span>
                      <span v-else>{{ selectedTextureImage.name }}</span>
                    </label>
                  </div>
                  <div v-if="textureImagePreview" class="image-preview">
                    <img :src="textureImagePreview" alt="预览" />
                  </div>
                  <button 
                    @click="generateTextureFromImage" 
                    :disabled="!selectedTextureImage || isGeneratingTexture"
                    class="generate-texture-btn"
                    style="margin-top: 1rem;"
                  >
                    {{ isGeneratingTexture ? '生成中...' : '生成纹理' }}
                  </button>
                </div>
                
                <div v-if="textureStatus" class="texture-status">
                  {{ textureStatus }}
                </div>
              </div>
            </div>
            
            <!-- 操作历史标签页 -->
            <div v-show="activeTab === 'history'" class="tab-panel">
              <h3>操作历史记录</h3>
              <div class="history-section">
                <div v-if="operationHistory.length === 0" class="empty-history">
                  <p>暂无操作记录</p>
                </div>
                <div v-else class="history-list">
                  <div 
                    v-for="(record, index) in operationHistory" 
                    :key="index"
                    class="history-item"
                  >
                    <div class="history-header">
                      <span class="history-user">{{ record.user || '未知用户' }}</span>
                      <span class="history-time">{{ formatTime(record.timestamp) }}</span>
                    </div>
                    <div class="history-action">
                      <span class="action-type">{{ record.action }}</span>
                      <span v-if="record.details" class="action-details">{{ record.details }}</span>
                    </div>
                  </div>
                </div>
                <button 
                  v-if="operationHistory.length > 0"
                  @click="clearHistory" 
                  class="clear-history-btn"
                >
                  清空历史记录
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js'
import Stats from 'three/examples/jsm/libs/stats.module.js'
import { BufferGeometryUtils } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import { SimplifyModifier } from 'three/examples/jsm/modifiers/SimplifyModifier.js'
import HomePage from './components/HomePage.vue'
import TextTo3D from './components/TextTo3D.vue'
import JoinRoom from './components/JoinRoom.vue'
import { API_BASE } from './config.js'

export default {
  name: 'App',
  components: {
    HomePage,
    TextTo3D,
    JoinRoom
  },
  data() {
    return {
      currentJobId: null, // 当前任务ID
      isModelLoading: false, // 模型是否正在加载
      modelLoadProgress: 0, // 模型加载进度
      currentPage: 'home', // 页面状态：home, text-to-3d, image-to-3d, room-editor, model-editor, model-status
      mixer: null,
      clock: null,
      animationId: null,
      selectedFile: null,
      uploadStatus: null,
      loadedModel: null,
      hasAnimation: false,
      animationPlaying: false,
      animationSpeed: 1.0,
      
      // 模型生成状态
      modelStatus: {
        loading: true,
        progress: 0,
        message: '模型生成中，请稍候...',
        success: false,
        error: null,
        previewImageUrl: '',
        modelUrl: ''
      },
      
      // 材质控制参数
      materialColor: '#ffffff',
      materialEmissive: 0,
      materialMetalness: 0.5,
      materialRoughness: 0.5,
      
      // 光照控制参数
      lightColor: '#ffffff',
      lightIntensity: 1,
      ambientIntensity: 0.4,
      
      // 场景控制参数
      backgroundColor: '#f0f0f0',
      showGrid: true,
      showAxes: true,
      
      // 标签页控制（默认切到“模型调整”作为第一个菜单）
      activeTab: 'adjust', // adjust, upload, texture, history
      
      // 纹理生成相关（AI）
      textureMode: 'prompt', // prompt 或 image
      texturePrompt: '',
      selectedTextureImage: null,
      textureImagePreview: null,
      isGeneratingTexture: false,
      textureStatus: null,

      // 模型调整 - 变换
      posX: 0,
      posY: 0,
      posZ: 0,
      rotX: 0,
      rotY: 0,
      rotZ: 0,
      scaleU: 1,

      // 模型调整 - 显示/阴影/线框
      wireframe: false,
      castShadow: true,
      receiveShadow: true,

      // 模型调整 - 纹理应用（常用+自定义）
      presetTextureKey: '',
      presetTextures: [
        { key: 'wood', name: '木纹', url: 'https://threejs.org/examples/textures/hardwood2_diffuse.jpg' },
        { key: 'metal', name: '金属拉丝', url: 'https://threejs.org/examples/textures/metal.jpg' },
        { key: 'marble', name: '大理石', url: 'https://threejs.org/examples/textures/marble.jpg' },
        { key: 'brick', name: '砖块', url: 'https://threejs.org/examples/textures/brick_diffuse.jpg' },
        { key: 'fabric', name: '织物', url: 'https://threejs.org/examples/textures/uv_grid_opengl.jpg' }
      ],
      userTextureFile: null,
      userTexturePreview: null,
      textureRepeatX: 1,
      textureRepeatY: 1,
      textureRotation: 0,

      // 几何处理 - 简化
      simplifyRatio: 0.6,

      // 历史记录
      operationHistory: [],
      currentUserName: '当前用户' // 可以从登录系统获取
    }
  },
  mounted() {
    // 支持通过 GET 查询参数控制页面与数据，刷新后不丢失状态
    this.syncPageFromQuery()
    window.addEventListener('popstate', this.syncPageFromQuery)
  },
  beforeDestroy() {
    // 组件销毁前清理资源
    this.cleanup()
    window.removeEventListener('popstate', this.syncPageFromQuery)
  },
  methods: {
    // 使用 URL 查询参数同步页面与数据（GET 方式）
    syncPageFromQuery() {
      const params = new URLSearchParams(window.location.search)
      const page = params.get('page') || 'home'
      const modelUrl = params.get('modelUrl')
      const jobId = params.get('jobId')

      // 如果切换离开编辑页，先做清理
      if (this.currentPage === 'model-editor' && page !== 'model-editor') {
        this.cleanup()
      }

      this.currentPage = page

      if (page === 'model-editor') {
        this.$nextTick(() => {
          if (!this.renderer) {
            this.initThree()
          }
          if (modelUrl) {
            this.loadModelFromUrl(modelUrl)
          }
        })
      } else if (page === 'model-status') {
        if (jobId) {
          localStorage.setItem('modelJobId', jobId);
          this.currentJobId = jobId;
        }
        // 初始化模型状态并开始轮询
        this.modelStatus = {
          loading: true,
          progress: 0,
          message: '模型生成中，请稍候...',
          success: false,
          error: null,
          previewImageUrl: '',
          modelUrl: ''
        }
        this.startCheckingModelStatus()
      }
    },

    // 更新 URL 查询参数（不刷新页面）
    updateQuery(next = {}) {
      const params = new URLSearchParams(window.location.search)
      Object.keys(next).forEach(key => {
        const val = next[key]
        if (val === undefined || val === null || val === '') {
          params.delete(key)
        } else {
          params.set(key, val)
        }
      })
      const search = params.toString()
      const path = window.location.pathname + (search ? `?${search}` : '')
      window.history.pushState({}, '', path)
    },

    // 保存模型方法
    saveModel() {
       if (!this.loadedModel) return
       const exporter = new GLTFExporter()
       const options = { trs: false, onlyVisible: true, binary: true, maxTextureSize: 4096 }
       exporter.parse(this.modelGroup, (result) => {
        const blob = new Blob([result], { type: 'application/octet-stream' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        const filename = `beautified-model-${Date.now()}.glb`
        link.href = url
        link.download = filename
        link.click()
        URL.revokeObjectURL(url)
        this.recordOperation('保存模型', `文件名：${filename}`)
        alert('模型保存成功！')
      }, (error) => {
        console.error('导出模型时发生错误:', error)
        alert('模型保存失败，请检查控制台错误信息。')
      }, options)
    },
    
    initThree() {
      // 创建一个三维场景
      this.scene = new THREE.Scene()

      // 创建一个模型组
      this.modelGroup = new THREE.Group()
      this.scene.add(this.modelGroup)

      // 坐标系与网格
      this.axesHelper = new THREE.AxesHelper(100)
      this.scene.add(this.axesHelper)
      this.gridHelper = new THREE.GridHelper(10, 10, 0x004444, 0x004444)
      this.scene.add(this.gridHelper)

      // 光源设置（开启阴影）
      this.directionalLight = new THREE.DirectionalLight(0xffffff, 1)
      this.directionalLight.position.set(15, 15, 15)
      this.directionalLight.castShadow = true
      this.directionalLight.shadow.mapSize.width = 2048
      this.directionalLight.shadow.mapSize.height = 2048
      this.scene.add(this.directionalLight)
      
      this.ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
      this.scene.add(this.ambientLight)

      // 画布尺寸
      const width = this.$refs.threeContainer.clientWidth
      const height = this.$refs.threeContainer.clientHeight

      // 相机
      this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 2000)
      this.camera.position.set(5, 5, -10)
      this.camera.lookAt(0, 0, 0)

      // 渲染器
      this.renderer = new THREE.WebGLRenderer({ antialias: true })
      this.renderer.setSize(width, height)
      this.renderer.setPixelRatio(window.devicePixelRatio)
      this.renderer.outputEncoding = THREE.sRGBEncoding
      this.renderer.setClearColor(0xf0f0f0)
      this.renderer.shadowMap.enabled = true
      this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
      this.$refs.threeContainer.appendChild(this.renderer.domElement)

      // 性能监视器
      this.stats = new Stats()
      this.$refs.threeContainer.appendChild(this.stats.dom)

      // 轨道控制器
      this.controls = new OrbitControls(this.camera, this.renderer.domElement)
      this.controls.update()

      // 动画循环
      this.animate = this.animate.bind(this)
      this.animate()

      // 窗口尺寸变化
      window.addEventListener('resize', this.handleResize)
    },
    
    // 文件选择处理
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        if (file.type === 'model/gltf-binary' || file.name.endsWith('.glb') || file.name.endsWith('.gltf')) {
          this.selectedFile = file
          this.uploadStatus = null
        } else {
          this.selectedFile = null
          this.uploadStatus = '请选择有效的GLB或GLTF文件'
        }
      }
    },
    
    // 上传并加载模型
    uploadModel() {
      if (!this.selectedFile) return
      this.uploadStatus = '正在加载模型...'

      // 清理之前加载的模型
      if (this.loadedModel) {
        this.modelGroup.remove(this.loadedModel)
        this.loadedModel = null
      }

      if (this.mixer) {
        this.mixer.stopAllAction()
        this.mixer = null
      }
      
      const loader = new GLTFLoader()
      const fileURL = URL.createObjectURL(this.selectedFile)
      loader.load(
        fileURL,
        (gltf) => {
          this.loadedModel = gltf.scene
          this.modelGroup.add(this.loadedModel)
          // 默认让所有网格支持阴影设置受控
          this.applyShadows()

          // 自动缩放和定位模型
          this.autoScaleAndPositionModel(this.loadedModel)
          
          // 动画
          if (gltf.animations && gltf.animations.length > 0) {
            this.hasAnimation = true
            this.animationPlaying = true
            this.mixer = new THREE.AnimationMixer(gltf.scene)
            this.clock = new THREE.Clock()
            this.clipAction = this.mixer.clipAction(gltf.animations[0])
            this.clipAction.play()
          } else {
            this.hasAnimation = false
            this.animationPlaying = false
          }

          this.recordOperation('上传模型', `文件名：${this.selectedFile.name}`)
          this.uploadStatus = '模型加载成功！'
          setTimeout(() => { this.uploadStatus = null }, 5000)
        },
        (progress) => {
          const percent = Math.round((progress.loaded / progress.total) * 100)
          this.uploadStatus = `模型加载中... ${percent}%`
        },
        (error) => {
          console.error('模型加载失败:', error)
          this.uploadStatus = '模型加载失败，请检查文件格式'
        }
      )
    },
    
    // 自动缩放和定位模型
    autoScaleAndPositionModel(model) {
      const box = new THREE.Box3().setFromObject(model)
      const size = box.getSize(new THREE.Vector3())
      const maxDim = Math.max(size.x, size.y, size.z)
      const scale = 5 / (maxDim || 1)
      model.scale.setScalar(scale)
      box.setFromObject(model)
      const newCenter = box.getCenter(new THREE.Vector3())
      model.position.sub(newCenter)
      // 同步 UI 变换值
      this.posX = model.position.x
      this.posY = model.position.y
      this.posZ = model.position.z
      this.rotX = THREE.MathUtils.radToDeg(model.rotation.x)
      this.rotY = THREE.MathUtils.radToDeg(model.rotation.y)
      this.rotZ = THREE.MathUtils.radToDeg(model.rotation.z)
      this.scaleU = model.scale.x
    },

    // 通用变换
    applyTransform() {
      if (!this.loadedModel) return
      this.loadedModel.position.set(this.posX, this.posY, this.posZ)
      this.loadedModel.rotation.set(
        THREE.MathUtils.degToRad(this.rotX),
        THREE.MathUtils.degToRad(this.rotY),
        THREE.MathUtils.degToRad(this.rotZ)
      )
      this.loadedModel.scale.setScalar(this.scaleU)
      this.recordOperation('应用变换', `pos(${this.posX},${this.posY},${this.posZ}) rot(${this.rotX},${this.rotY},${this.rotZ}) scale(${this.scaleU})`)
    },
    resetTransform() {
      if (!this.loadedModel) return
      this.loadedModel.position.set(0,0,0)
      this.loadedModel.rotation.set(0,0,0)
      this.loadedModel.scale.setScalar(1)
      this.posX = this.posY = this.posZ = 0
      this.rotX = this.rotY = this.rotZ = 0
      this.scaleU = 1
      this.recordOperation('重置变换')
    },
    centerModel() {
      if (!this.loadedModel) return
      const box = new THREE.Box3().setFromObject(this.loadedModel)
      const center = box.getCenter(new THREE.Vector3())
      this.loadedModel.position.sub(center)
      this.posX = this.loadedModel.position.x
      this.posY = this.loadedModel.position.y
      this.posZ = this.loadedModel.position.z
      this.recordOperation('居中到原点')
    },
    fitModelToView() {
      if (!this.loadedModel || !this.camera || !this.controls) return
      const box = new THREE.Box3().setFromObject(this.loadedModel)
      const sphere = box.getBoundingSphere(new THREE.Sphere())
      const distance = sphere.radius / Math.sin(THREE.MathUtils.degToRad(this.camera.fov) / 2)
      const dir = new THREE.Vector3(1, 1, 1).normalize()
      this.camera.position.copy(sphere.center.clone().add(dir.multiplyScalar(distance)))
      this.controls.target.copy(sphere.center)
      this.controls.update()
      this.recordOperation('适配视图')
    },

    // 动画循环
    animate() {
      this.animationId = requestAnimationFrame(this.animate)
      if (this.mixer && this.clock) {
        const frameT = this.clock.getDelta()
        this.mixer.update(frameT)
      }
      if (this.controls) this.controls.update()
      if (this.stats) this.stats.update()
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera)
      }
    },

    handleResize() {
      if (this.renderer && this.camera) {
        const width = this.$refs.threeContainer.clientWidth
        const height = this.$refs.threeContainer.clientHeight
        this.renderer.setSize(width, height)
        this.camera.aspect = width / height
        this.camera.updateProjectionMatrix()
      }
    },

    // 材质控制方法（基础）
    updateMaterialColor() {
      if (!this.loadedModel) return
      const color = new THREE.Color(this.materialColor)
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          if (Array.isArray(child.material)) {
            child.material.forEach(m => { m.color = color; m.needsUpdate = true })
          } else {
            child.material.color = color
            child.material.needsUpdate = true
          }
        }
      })
      this.recordOperation('修改材质颜色', `颜色值：${this.materialColor}`)
    },
    updateMaterialEmissive() {
      if (!this.loadedModel) return
      const emissiveIntensity = this.materialEmissive
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          if (Array.isArray(child.material)) {
            child.material.forEach(m => { m.emissive = new THREE.Color(emissiveIntensity, emissiveIntensity, emissiveIntensity); m.needsUpdate = true })
          } else {
            child.material.emissive = new THREE.Color(emissiveIntensity, emissiveIntensity, emissiveIntensity)
            child.material.needsUpdate = true
          }
        }
      })
      this.recordOperation('修改材质亮度', `亮度值：${this.materialEmissive}`)
    },
    updateMaterialMetalness() {
      if (!this.loadedModel) return
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          if (Array.isArray(child.material)) {
            child.material.forEach(m => { if (m.metalness !== undefined) { m.metalness = this.materialMetalness; m.needsUpdate = true } })
          } else if (child.material.metalness !== undefined) {
            child.material.metalness = this.materialMetalness
            child.material.needsUpdate = true
          }
        }
      })
      this.recordOperation('修改材质金属度', `金属度：${this.materialMetalness}`)
    },
    updateMaterialRoughness() {
      if (!this.loadedModel) return
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          if (Array.isArray(child.material)) {
            child.material.forEach(m => { if (m.roughness !== undefined) { m.roughness = this.materialRoughness; m.needsUpdate = true } })
          } else if (child.material.roughness !== undefined) {
            child.material.roughness = this.materialRoughness
            child.material.needsUpdate = true
          }
        }
      })
      this.recordOperation('修改材质粗糙度', `粗糙度：${this.materialRoughness}`)
    },

    // 纹理应用（常用 + 自定义）
    applyTextureToModel(texture) {
      if (!this.loadedModel || !texture) return
      texture.wrapS = texture.wrapT = THREE.RepeatWrapping
      texture.repeat.set(this.textureRepeatX || 1, this.textureRepeatY || 1)
      texture.center.set(0.5, 0.5)
      texture.rotation = THREE.MathUtils.degToRad(this.textureRotation || 0)
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          const applyToMat = (mat) => {
            mat.map = texture
            mat.needsUpdate = true
          }
          if (Array.isArray(child.material)) {
            child.material.forEach(m => applyToMat(m))
          } else if (child.material) {
            applyToMat(child.material)
          }
        }
      })
      this.recordOperation('应用纹理')
    },
    applyPresetTexture() {
      if (!this.presetTextureKey) return
      const item = this.presetTextures.find(t => t.key === this.presetTextureKey)
      if (!item) return
      const loader = new THREE.TextureLoader()
      loader.load(item.url, (tex) => {
        this.applyTextureToModel(tex)
      })
    },
    clearTexture() {
      if (!this.loadedModel) return
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          const clearMat = (mat) => {
            if (mat.map) { mat.map.dispose(); mat.map = null }
            mat.needsUpdate = true
          }
          if (Array.isArray(child.material)) child.material.forEach(clearMat)
          else if (child.material) clearMat(child.material)
        }
      })
      this.recordOperation('移除纹理')
    },
    handleUserTextureSelect(e) {
      const file = e.target.files && e.target.files[0]
      if (!file) return
      if (!file.type.startsWith('image/')) return
      this.userTextureFile = file
      const reader = new FileReader()
      reader.onload = ev => { this.userTexturePreview = ev.target.result }
      reader.readAsDataURL(file)
    },
    applyUserTexture() {
      if (!this.userTextureFile) return
      const url = URL.createObjectURL(this.userTextureFile)
      const loader = new THREE.TextureLoader()
      loader.load(url, (tex) => {
        this.applyTextureToModel(tex)
        URL.revokeObjectURL(url)
      })
    },

    // 线框与阴影
    applyWireframe() {
      if (!this.loadedModel) return
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          const setWF = (m) => { m.wireframe = this.wireframe; m.needsUpdate = true }
          if (Array.isArray(child.material)) child.material.forEach(setWF)
          else if (child.material) setWF(child.material)
        }
      })
      this.recordOperation('切换线框', this.wireframe ? '开启' : '关闭')
    },
    applyShadows() {
      if (!this.loadedModel) return
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = this.castShadow
          child.receiveShadow = this.receiveShadow
        }
      })
    },

    // 几何处理
    recalcNormals() {
      if (!this.loadedModel) return
      this.loadedModel.traverse((child) => {
        if (child.isMesh && child.geometry) {
          child.geometry.computeVertexNormals()
          child.geometry.normalsNeedUpdate = true
        }
      })
      this.recordOperation('重新计算法线')
    },
    mergeAllMeshes() {
      if (!this.loadedModel) return
      const geometries = []
      let baseMaterial = null
      this.loadedModel.traverse((child) => {
        if (child.isMesh && child.geometry) {
          const geom = child.geometry.clone()
          geom.applyMatrix4(child.matrixWorld)
          geometries.push(geom)
          if (!baseMaterial) baseMaterial = Array.isArray(child.material) ? child.material[0] : child.material
        }
      })
      if (geometries.length === 0) return
      const merged = BufferGeometryUtils.mergeGeometries(geometries, true)
      const material = baseMaterial ? baseMaterial.clone() : new THREE.MeshStandardMaterial({ color: this.materialColor })
      // 清空原有
      for (let i = this.modelGroup.children.length - 1; i >= 0; i--) {
        const obj = this.modelGroup.children[i]
        this.modelGroup.remove(obj)
      }
      const mesh = new THREE.Mesh(merged, material)
      mesh.castShadow = this.castShadow
      mesh.receiveShadow = this.receiveShadow
      this.modelGroup.add(mesh)
      this.loadedModel = mesh
      this.recordOperation('合并网格')
    },
    applySimplify() {
      if (!this.loadedModel) return
      const modifier = new SimplifyModifier()
      this.loadedModel.traverse((child) => {
        if (child.isMesh && child.geometry && child.geometry.index) {
          const count = Math.floor(child.geometry.attributes.position.count * this.simplifyRatio)
          if (count >= 4) {
            child.geometry = modifier.modify(child.geometry, count)
            child.geometry.computeVertexNormals()
            child.geometry.needsUpdate = true
          }
        }
      })
      this.recordOperation('简化模型', `保留比例：${this.simplifyRatio}`)
    },

    // 光照控制方法（基础）
    updateLightColor() {
      if (this.directionalLight) this.directionalLight.color = new THREE.Color(this.lightColor)
    },
    updateLightIntensity() {
      if (this.directionalLight) this.directionalLight.intensity = this.lightIntensity
    },
    updateAmbientIntensity() {
      if (this.ambientLight) this.ambientLight.intensity = this.ambientIntensity
    },

    // 场景控制方法
    updateBackgroundColor() {
      if (this.renderer) this.renderer.setClearColor(this.backgroundColor)
    },
    toggleGrid() {
      if (this.showGrid) {
        if (this.gridHelper && !this.scene.children.includes(this.gridHelper)) this.scene.add(this.gridHelper)
      } else {
        if (this.gridHelper && this.scene.children.includes(this.gridHelper)) this.scene.remove(this.gridHelper)
      }
    },
    toggleAxes() {
      if (this.showAxes) {
        if (this.axesHelper && !this.scene.children.includes(this.axesHelper)) this.scene.add(this.axesHelper)
      } else {
        if (this.axesHelper && this.scene.children.includes(this.axesHelper)) this.scene.remove(this.axesHelper)
      }
    },

    // 视角控制方法
    setPerspective(type) {
      switch (type) {
        case 'front':
          this.camera.position.set(0, 0, 10)
          break
        case 'side':
          this.camera.position.set(10, 0, 0)
          break
        case 'top':
          this.camera.position.set(0, 10, 0)
          break
        case 'isometric':
          this.camera.position.set(7, 7, 7)
          break
      }
      this.camera.lookAt(0, 0, 0)
      this.controls.update()
      this.recordOperation('切换视角', type)
    },

    // 动画控制方法
    toggleAnimation() {
      if (this.animationPlaying) {
        this.clipAction.pause()
        this.animationPlaying = false
      } else {
        this.clipAction.play()
        this.animationPlaying = true
      }
    },
    updateAnimationSpeed() {
      if (this.mixer) {
        this.mixer.timeScale = this.animationSpeed
      }
    },

    cleanup() {
      window.removeEventListener('resize', this.handleResize)
      if (this.animationId) cancelAnimationFrame(this.animationId)
      if (this.mixer) {
        this.mixer.stopAllAction()
        this.mixer.uncacheRoot(this.modelGroup)
      }
      if (this.renderer) {
        this.renderer.dispose()
        this.renderer.forceContextLoss()
      }
      if (this.controls) this.controls.dispose()
      if (this.$refs.threeContainer && this.renderer) {
        try { this.$refs.threeContainer.removeChild(this.renderer.domElement) } catch(e) { console.warn('移除renderer画布失败或已移除', e) }
      }
      if (this.stats && this.stats.dom) {
        try { this.$refs.threeContainer.removeChild(this.stats.dom) } catch(e) { console.warn('移除stats元素失败或已移除', e) }
      }
      if (this.scene) {
        this.scene.traverse((object) => {
          if (object.geometry) object.geometry.dispose()
          if (object.material) {
            if (Array.isArray(object.material)) object.material.forEach(m => m.dispose())
            else object.material.dispose()
          }
          if (object.texture) object.texture.dispose()
        })
      }
    },

    // 页面切换方法
    handleSelectOption(option) {
      switch(option) {
        case 'text-to-3d':
          this.currentPage = 'text-to-3d'
          this.updateQuery({ page: 'text-to-3d', modelUrl: '', jobId: '' })
          break
        case 'image-to-3d':
          this.currentPage = 'image-to-3d'
          this.updateQuery({ page: 'image-to-3d', modelUrl: '', jobId: '' })
          break
        case 'room-editor':
          this.currentPage = 'room-editor'
          this.updateQuery({ page: 'room-editor', modelUrl: '', jobId: '' })
          break
        case 'model-editor':
          this.currentPage = 'model-editor'
          this.updateQuery({ page: 'model-editor' })
          this.initThree()
          break
        default:
          this.currentPage = 'home'
          this.updateQuery({ page: 'home', modelUrl: '', jobId: '' })
      }
    },

    // 处理加载模型事件（来自JoinRoom组件）
    handleLoadModel(modelData) {
      this.modelStatus = {
        loading: false,
        success: true,
        progress: 100,
        message: '模型加载成功！',
        error: null,
        previewImageUrl: modelData.previewImageUrl,
        modelUrl: modelData.modelUrl
      }
      this.currentPage = 'model-editor'
      this.updateQuery({ page: 'model-editor', modelUrl: modelData.modelUrl })
      this.$nextTick(() => {
        this.initThree()
        setTimeout(() => { this.loadModelFromUrl(modelData.modelUrl) }, 100)
      })
    },

    // 从URL加载模型
    async loadModelFromUrl(modelUrl) {
      try {
        this.isModelLoading = true; // 显示加载遮罩
        this.modelLoadProgress = 0;
        this.uploadStatus = '正在加载模型...';

        if (this.loadedModel) {
          this.modelGroup.remove(this.loadedModel);
          this.loadedModel = null;
        }
        if (this.mixer) { this.mixer.stopAllAction(); this.mixer = null; }

        const loader = new GLTFLoader();
        loader.load(
          modelUrl,
          (gltf) => { // OnLoad
            this.loadedModel = gltf.scene;
            this.modelGroup.add(this.loadedModel);
            this.applyShadows();
            this.autoScaleAndPositionModel(this.loadedModel);
            if (gltf.animations && gltf.animations.length > 0) {
              this.hasAnimation = true;
              this.animationPlaying = true;
              this.mixer = new THREE.AnimationMixer(gltf.scene);
              this.clock = new THREE.Clock();
              this.clipAction = this.mixer.clipAction(gltf.animations[0]);
              this.clipAction.play();
            } else { this.hasAnimation = false; this.animationPlaying = false; }
            this.uploadStatus = '模型加载成功！';
            setTimeout(() => { this.uploadStatus = null; }, 5000);
            this.isModelLoading = false; // 加载成功，隐藏遮罩
          },
          (progress) => { // OnProgress
            if (progress.total > 0) {
              const percent = Math.round((progress.loaded / progress.total) * 100);
              this.modelLoadProgress = percent;
              this.uploadStatus = `模型加载中... ${percent}%`;
            }
          },
          (error) => { // OnError
            console.error('模型加载失败:', error);
            this.uploadStatus = '模型加载失败，请稍后重试';
            this.isModelLoading = false; // 加载失败，隐藏遮罩
          }
        );
      } catch (error) {
        console.error('加载模型失败:', error);
        this.uploadStatus = '模型加载失败，请稍后重试';
        this.isModelLoading = false; // 异常，隐藏遮罩
      }
    },

        normalizeUrl(url) {
      if (!url) return url
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        return `https://${url}`
      }
      return url
    },

    // 模型状态相关（保持原有逻辑）
    handleTextJobCreated(payload) {
      const jobId = (payload && payload.jobId) ? payload.jobId : (localStorage.getItem('modelJobId') || '')
      if (jobId) {
        localStorage.setItem('modelJobId', jobId)
      }
      this.currentPage = 'model-status'
      this.modelStatus = { loading: true, progress: 0, message: '模型生成中，请稍候...', success: false, error: null, previewImageUrl: '', modelUrl: '' }
      this.currentJobId = jobId;
      this.updateQuery({ page: 'model-status', jobId })
      this.startCheckingModelStatus()
    },
    handleViewModelStatus() {
      this.currentPage = 'model-status'
      this.modelStatus = { loading: true, progress: 0, message: '模型生成中，请稍候...', success: false, error: null, previewImageUrl: '', modelUrl: '' }
      const jobId = localStorage.getItem('modelJobId') || ''
      this.currentJobId = jobId;
      this.updateQuery({ page: 'model-status', jobId })
      this.startCheckingModelStatus()
    },
    startCheckingModelStatus() {
      if (this.statusCheckTimer) { clearInterval(this.statusCheckTimer) }
      this.statusCheckTimer = setInterval(() => { this.checkModelStatus() }, 5000)
      this.checkModelStatus()
    },
    async checkModelStatus() {
      const jobId = localStorage.getItem('modelJobId')
      if (!jobId) { this.modelStatus.error = '未找到任务ID'; this.modelStatus.loading = false; return }
      try {
        const response = await fetch(`${API_BASE}/api/models/generate/getstatus`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ jobId }) })
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        const data = await response.json()
        let status = data.status
        if (typeof status === 'string') {
          // 兼容字符串数字与字符串状态
          if (/^\d+$/.test(status)) {
            status = parseInt(status, 10)
          } else {
            const up = status.toUpperCase()
            if (up === 'RUN' || up === 'RUNNING') {
              this.modelStatus.loading = true
              this.modelStatus.progress += Math.floor(Math.random() * 6) + 5
              if (this.modelStatus.progress > 90) this.modelStatus.progress = 90
              this.modelStatus.message = '模型正在生成中...'
              return
            } else if (up === 'FAIL' || up === 'FAILED') {
              this.modelStatus.loading = false
              this.modelStatus.error = '模型生成失败，请稍后重试'
              clearInterval(this.statusCheckTimer)
              return
            } else if (up === 'DONE' || up === 'SUCCEEDED' || up === 'SUCCESS') {
              status = 3
            } else {
              // 未知字符串，按生成中处理为1
              status = 1
            }
          }
        } else { status = parseInt(status) }
        if (status === 0) {
          this.modelStatus.loading = true; this.modelStatus.progress = Math.min(90, this.modelStatus.progress + 5); this.modelStatus.message = '模型排队等待中...'
        } else if (status === 1) {
          this.modelStatus.loading = true; this.modelStatus.progress = Math.min(90, this.modelStatus.progress + 10); this.modelStatus.message = '模型正在生成中...'
        } else if (status === 2) {
          this.modelStatus.loading = false; this.modelStatus.error = '模型生成失败，请稍后重试'; clearInterval(this.statusCheckTimer)
        } else if (status === 3) {
          this.modelStatus.loading = false; this.modelStatus.success = true; this.modelStatus.progress = 100; this.modelStatus.message = '模型生成成功！'
          this.modelStatus.previewImageUrl = this.normalizeUrl(data.targetimgurl || '')
          let modelUrl = ''
          if (data.target3durl) {
            const normalized = this.normalizeUrl(data.target3durl)
            const base = normalized.endsWith('/') ? normalized.slice(0, -1) : normalized
            modelUrl = `${base}/${jobId}.glb`
          } else {
            modelUrl = `${API_BASE}/uploads/${jobId}/${jobId}.glb`
          }
          this.modelStatus.modelUrl = modelUrl
          clearInterval(this.statusCheckTimer)
        } else {
          this.modelStatus.loading = false; this.modelStatus.error = '未知的模型状态'; clearInterval(this.statusCheckTimer)
        }
      } catch (error) {
        console.error('检查模型状态失败:', error)
        this.modelStatus.loading = false
        this.modelStatus.error = '检查模型状态失败，请稍后重试'
        clearInterval(this.statusCheckTimer)
      }
    },
    async handleLoadModelFromStatus() {
      const jobId = localStorage.getItem('modelJobId')
      if (!jobId) { alert('未找到任务ID'); return }
      try {
        this.currentPage = 'model-editor'
        this.updateQuery({ page: 'model-editor', modelUrl: this.modelStatus.modelUrl })
        this.$nextTick(() => {
          this.initThree()
          setTimeout(() => {
            this.uploadStatus = '正在加载模型...'
            if (this.loadedModel) { this.modelGroup.remove(this.loadedModel); this.loadedModel = null }
            if (this.mixer) { this.mixer.stopAllAction(); this.mixer = null }
            const modelUrl = this.modelStatus.modelUrl
            if (!modelUrl) { this.uploadStatus = '模型URL获取失败'; return }
            const loader = new GLTFLoader()
            loader.load(
              modelUrl,
              (gltf) => {
                this.loadedModel = gltf.scene
                this.modelGroup.add(this.loadedModel)
                this.applyShadows()
                this.autoScaleAndPositionModel(this.loadedModel)
                if (gltf.animations && gltf.animations.length > 0) {
                  this.hasAnimation = true; this.animationPlaying = true; this.mixer = new THREE.AnimationMixer(gltf.scene); this.clock = new THREE.Clock(); this.clipAction = this.mixer.clipAction(gltf.animations[0]); this.clipAction.play()
                } else { this.hasAnimation = false; this.animationPlaying = false }
                this.uploadStatus = '模型加载成功！'
                setTimeout(() => { this.uploadStatus = null }, 5000)
              },
              (progress) => { const percent = Math.round((progress.loaded / progress.total) * 100); this.uploadStatus = `模型加载中... ${percent}%` },
              (error) => { console.error('模型加载失败:', error); this.uploadStatus = '模型加载失败，请稍后重试' }
            )
          }, 100)
        })
      } catch (error) {
        console.error('加载模型失败:', error)
        alert('加载模型失败，请稍后重试')
      }
    },

    copyJobId() {
      if (this.currentJobId) {
        navigator.clipboard.writeText(this.currentJobId)
          .then(() => {
            alert('任务ID已复制到剪贴板');
          })
          .catch(err => {
            console.error('复制失败:', err);
            alert('复制失败，请手动复制');
          });
      }
    },

    // 重试 & 返回
    handleRetry() {
      this.currentPage = 'text-to-3d'
      this.updateQuery({ page: 'text-to-3d', jobId: '' })
      localStorage.removeItem('modelJobId')
      if (this.statusCheckTimer) clearInterval(this.statusCheckTimer)
    },
    handleBack() {
      this.currentPage = 'home'
      this.updateQuery({ page: 'home', modelUrl: '', jobId: '' })
      this.cleanup()
      localStorage.removeItem('modelJobId')
      if (this.statusCheckTimer) clearInterval(this.statusCheckTimer)
    },

    // 历史记录
    recordOperation(action, details = '') {
      const record = { user: this.currentUserName, action, details, timestamp: new Date() }
      this.operationHistory.unshift(record)
      if (this.operationHistory.length > 100) {
        this.operationHistory = this.operationHistory.slice(0, 100)
      }
    },
    formatTime(timestamp) {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
      return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
    },
    clearHistory() {
      if (confirm('确定要清空所有操作历史记录吗？')) {
        this.operationHistory = []
        this.recordOperation('清空历史记录')
      }
    },

    // AI 纹理页面用到的图片选择（保持原有）
    handleTextureImageSelect(event) {
      const file = event.target.files[0]
      if (file) {
        if (file.type.startsWith('image/')) {
          this.selectedTextureImage = file
          const reader = new FileReader()
          reader.onload = (e) => { this.textureImagePreview = e.target.result }
          reader.readAsDataURL(file)
        } else {
          this.textureStatus = '请选择有效的图片文件'
          this.selectedTextureImage = null
          this.textureImagePreview = null
        }
      }
    },
    async generateTextureFromPrompt() {
      if (!this.texturePrompt.trim() || !this.loadedModel) return
      this.isGeneratingTexture = true
      this.textureStatus = '正在生成纹理...'
      try {
        await new Promise(r => setTimeout(r, 2000))
        this.recordOperation('生成纹理', `使用提示词：${this.texturePrompt}`)
        this.textureStatus = '纹理生成成功！'
        setTimeout(() => { this.textureStatus = null }, 3000)
      } catch (e) {
        console.error('生成纹理失败:', e)
        this.textureStatus = '纹理生成失败，请稍后重试'
      } finally { this.isGeneratingTexture = false }
    },
    async generateTextureFromImage() {
      if (!this.selectedTextureImage || !this.loadedModel) return
      this.isGeneratingTexture = true
      this.textureStatus = '正在生成纹理...'
      try {
        await new Promise(r => setTimeout(r, 2000))
        this.recordOperation('生成纹理', `使用图片：${this.selectedTextureImage.name}`)
        this.textureStatus = '纹理生成成功！'
        setTimeout(() => { this.textureStatus = null }, 3000)
      } catch (e) {
        console.error('生成纹理失败:', e)
        this.textureStatus = '纹理生成失败，请稍后重试'
      } finally { this.isGeneratingTexture = false }
    }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f7fa; color: #333; line-height: 1.6; }
#app { min-height: 100vh; display: flex; flex-direction: column; }

.app-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 3rem 2rem; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.app-header h1 { font-size: 2.5rem; margin-bottom: .5rem; font-weight: 700; }
.app-header p { font-size: 1.1rem; opacity: .9; }

.upload-section { padding: 2rem; background: white; margin: 2rem auto; border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.05); width: 90%; max-width: 800px; text-align: center; }
.upload-container { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; align-items: center; margin-bottom: 1rem; }
.file-input { display: none; }
.file-label { display: inline-block; padding: .8rem 1.5rem; background: #e9ecef; color: #495057; border-radius: 5px; cursor: pointer; transition: all .3s ease; font-weight: 500; min-width: 200px; }
.file-label:hover { background: #dee2e6; }

.model-status-container { max-width: 800px; margin: 2rem auto; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); text-align: center; }
.model-status-container h2 { color: #495057; margin-bottom: 2rem; }
.loading-container { margin: 2rem 0; }
.progress-bar { width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; margin-bottom: 1rem; }
.progress { height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; transition: width .5s ease; }
.error-container { color: #f44336; margin: 2rem 0; }
.success-container { color: #4CAF50; margin: 2rem 0; }
.retry-button, .load-button { padding: 1rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all .3s ease; margin-top: 1rem; }
.retry-button:hover, .load-button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102,126,234,.3); }

.back-button { position: absolute; top: 20px; right: 20px; padding: .8rem 2rem; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600; transition: all .3s ease; z-index: 10; }
.back-button:hover { background: #43A047; transform: translateY(-2px); }

.upload-btn { padding: .8rem 2rem; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600; transition: all .3s ease; }
.upload-btn:hover:not(:disabled) { background: #0056b3; transform: translateY(-2px); }
.upload-btn:disabled { background: #6c757d; cursor: not-allowed; opacity: .7; }
.save-btn { padding: .8rem 2rem; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600; transition: all .3s ease; }
.save-btn:hover { background: #43A047; transform: translateY(-2px); }

.model-editor-page { min-height: 100vh; display: flex; flex-direction: column; }
.main-content-wrapper { display: flex; gap: 2rem; width: 95%; max-width: 1600px; margin: 2rem auto; flex: 1; }
.scene-container-wrapper { flex: 1; min-width: 600px; }
.three-container { width: 100%; height: 70vh; min-height: 600px; border: 1px solid #ddd; border-radius: 10px; position: relative; overflow: hidden; background: white; box-shadow: 0 2px 20px rgba(0,0,0,0.05); }
.right-panel { width: 420px; background: white; border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.05); display: flex; flex-direction: column; max-height: 70vh; min-height: 600px; }

.tabs-nav { display: flex; border-bottom: 2px solid #e9ecef; background: #f8f9fa; border-radius: 10px 10px 0 0; }
.tab-btn { flex: 1; padding: 1rem; border: none; background: transparent; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: .5rem; font-size: .9rem; font-weight: 500; color: #6c757d; transition: all .3s ease; border-bottom: 3px solid transparent; }
.tab-btn:hover { background: #e9ecef; color: #495057; }
.tab-btn.active { color: #667eea; border-bottom-color: #667eea; background: white; }
.tab-btn svg { width: 16px; height: 16px; }

.tabs-content { flex: 1; overflow-y: auto; padding: 1.5rem; }
.tab-panel { height: 100%; }
.tab-panel h3 { color: #495057; margin-bottom: 1.5rem; font-size: 1.3rem; border-bottom: 2px solid #e9ecef; padding-bottom: .5rem; }

.control-panel { width: 100%; background: transparent; border-radius: 0; box-shadow: none; padding: 0; height: fit-content; max-height: none; overflow-y: visible; }
.control-group { margin-bottom: 1.5rem; }
.control-group h4 { color: #6c757d; margin-bottom: 1rem; font-size: 1rem; font-weight: 600; }
.control-item { margin-bottom: 1rem; }
.control-item label { display: block; color: #495057; margin-bottom: .5rem; font-weight: 500; font-size: .9rem; }
.control-item input[type="color"] { width: 100%; height: 40px; border: none; border-radius: 5px; cursor: pointer; }
.control-item input[type="range"] { width: 100%; height: 6px; background: #e9ecef; border-radius: 3px; outline: none; -webkit-appearance: none; appearance: none; }
.control-item input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; background: #007bff; border-radius: 50%; cursor: pointer; }
.control-item input[type="range"]::-moz-range-thumb { width: 18px; height: 18px; background: #007bff; border-radius: 50%; cursor: pointer; border: none; }
.control-item input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; }

.triple-input { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: .5rem; }
.triple-input input { width: 100%; padding: .4rem .5rem; border: 1px solid #e9ecef; border-radius: 6px; }

.preset-buttons { display: flex; flex-direction: column; gap: .5rem; }
.preset-btn { padding: .7rem; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 500; transition: all .3s ease; font-size: .9rem; }
.preset-btn:hover { background: #5a6268; transform: translateY(-2px); }

.three-container .stats { position: absolute; top: 10px; left: 10px; z-index: 10; }

/* 纹理生成样式（AI） */
.texture-generation-section { margin-top: 1rem; }
.texture-mode-select { width: 100%; padding: .75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: .95rem; background: white; color: #495057; cursor: pointer; transition: border-color .3s ease; box-sizing: border-box; }
.texture-mode-select:focus { outline: none; border-color: #667eea; }
.texture-content { margin-top: 1.5rem; }
.texture-content .form-group { margin-bottom: 1.5rem; }
.texture-content label { display: block; margin-bottom: .5rem; color: #495057; font-weight: 500; font-size: .9rem; }
.texture-textarea { width: 100%; padding: .75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: .95rem; resize: vertical; transition: border-color .3s ease; box-sizing: border-box; }
.texture-textarea:focus { outline: none; border-color: #667eea; }
.image-preview { margin-top: 1rem; border: 2px solid #e9ecef; border-radius: 8px; overflow: hidden; max-height: 300px; display: flex; align-items: center; justify-content: center; }
.image-preview img { max-width: 100%; max-height: 300px; object-fit: contain; }
.generate-texture-btn { width: 100%; padding: .75rem 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all .3s ease; }
.generate-texture-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102,126,234,.3); }
.generate-texture-btn:disabled { opacity: .6; cursor: not-allowed; }
.texture-status { margin-top: 1rem; padding: .75rem; border-radius: 8px; background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; font-size: .9rem; }

.no-model-tip { text-align: center; padding: 3rem 1rem; color: #6c757d; }
.no-model-tip p { font-size: 1rem; margin: 0; }

.history-section { margin-top: 1rem; }
.empty-history { text-align: center; padding: 3rem 1rem; color: #6c757d; }
.history-list { max-height: 500px; overflow-y: auto; }
.history-item { padding: 1rem; margin-bottom: .75rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea; transition: all .3s ease; }
.history-item:hover { background: #e9ecef; transform: translateX(5px); }
.history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: .5rem; }
.history-user { font-weight: 600; color: #495057; font-size: .95rem; }
.history-time { font-size: .85rem; color: #6c757d; }
.history-action { display: flex; flex-direction: column; gap: .25rem; }
.action-type { font-weight: 500; color: #667eea; font-size: .9rem; }
.action-details { font-size: .85rem; color: #6c757d; font-style: italic; }
.clear-history-btn { width: 100%; margin-top: 1rem; padding: .75rem; background: #dc3545; color: white; border: none; border-radius: 8px; font-size: .9rem; font-weight: 500; cursor: pointer; transition: all .3s ease; }
.clear-history-btn:hover { background: #c82333; transform: translateY(-2px); }

@media (max-width: 1200px) { .main-content-wrapper { flex-direction: column; } .scene-container-wrapper { min-width: 100%; } .right-panel { width: 100%; max-height: none; } }

.job-id-container {
  margin-bottom: 2rem;
  font-size: 1rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.job-id-text {
  background-color: #f8f9fa;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  word-break: break-all;
}

.copy-btn {
  padding: 0.5rem 1rem;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.copy-btn:hover {
  background-color: #5a67d8;
}

.job-id-hint {
  font-size: 0.9rem;
  color: #868e96;
  margin-top: -1.5rem; /* Adjust to pull it closer */
  margin-bottom: 2rem;
  text-align: center;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* 模型加载遮罩样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  color: white;
  border-radius: 10px; /* 与容器保持一致 */
}

.loading-content {
  text-align: center;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 4px solid #fff;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-progress-bar {
  width: 200px;
  height: 10px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  overflow: hidden;
  margin: 1rem auto;
}

.loading-progress {
  height: 100%;
  background-color: #fff;
  transition: width 0.3s ease;
}

@media (max-width: 768px) {
  .app-header h1 { font-size: 2rem; }
  .upload-section { width: 95%; padding: 1.5rem; }
  .upload-container { flex-direction: column; }
  .file-label, .upload-btn { width: 100%; max-width: 300px; }
  .three-container { height: 400px; min-height: 400px; }
  .tabs-nav { flex-direction: column; }
  .tab-btn { border-bottom: 1px solid #e9ecef; border-right: none; }
  .tab-btn.active { border-bottom-color: #e9ecef; border-left: 3px solid #667eea; }
}
</style>
