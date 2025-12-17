<template>
  <div id="app">
    <!-- 主页 -->
    <HomePage v-if="currentPage === 'home'" @select-option="handleSelectOption" />
    
    <!-- 文字生成3D模型页面 -->
    <TextTo3D v-if="currentPage === 'text-to-3d'" @back="handleBack" @view-model-status="handleViewModelStatus" />
    
    <!-- 房间编辑器页面 -->
    <JoinRoom v-if="currentPage === 'room-editor'" @back="handleBack" @view-model-status="handleViewModelStatus" @load-model="handleLoadModel" />
    
    <!-- 模型生成状态页面 -->
    <div v-if="currentPage === 'model-status'">
      <button @click="handleBack" class="back-button">返回</button>
      <div class="model-status-container">
        <h2>模型生成状态</h2>
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
    
    <!-- 原有的3D模型上传和编辑页面 -->
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
        </div>
        
        <!-- 右侧：功能面板 -->
        <div class="right-panel">
          <!-- 标签页导航 -->
          <div class="tabs-nav">
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
            <!-- 上传模型标签页 -->
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
              
              <!-- 美化控制面板 -->
              <div class="control-panel" v-if="loadedModel">
                <h3>模型美化控制</h3>
                
                <!-- 材质控制 -->
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
                
                <!-- 光照控制 -->
                <div class="control-group">
                  <h4>光照设置</h4>
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
                </div>
                
                <!-- 场景控制 -->
                <div class="control-group">
                  <h4>场景设置</h4>
                  <div class="control-item">
                    <label>背景颜色</label>
                    <input type="color" v-model="backgroundColor" @change="updateBackgroundColor" />
                  </div>
                  <div class="control-item">
                    <label>网格显示</label>
                    <input type="checkbox" v-model="showGrid" @change="toggleGrid" />
                  </div>
                  <div class="control-item">
                    <label>坐标系显示</label>
                    <input type="checkbox" v-model="showAxes" @change="toggleAxes" />
                  </div>
                </div>
                
                <!-- 视角控制 -->
                <div class="control-group">
                  <h4>视角预设</h4>
                  <div class="preset-buttons">
                    <button @click="setPerspective('front')" class="preset-btn">正面视角</button>
                    <button @click="setPerspective('side')" class="preset-btn">侧面视角</button>
                    <button @click="setPerspective('top')" class="preset-btn">俯视视角</button>
                    <button @click="setPerspective('isometric')" class="preset-btn">等轴视角</button>
                  </div>
                </div>
                
                <!-- 动画控制 -->
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
            
            <!-- 生成纹理标签页 -->
            <div v-show="activeTab === 'texture'" class="tab-panel">
              <h3>生成模型纹理</h3>
              <div class="texture-generation-section">
                <div class="texture-tabs">
                  <button 
                    :class="['texture-tab-btn', { active: textureMode === 'prompt' }]"
                    @click="textureMode = 'prompt'"
                  >
                    提示词生成
                  </button>
                  <button 
                    :class="['texture-tab-btn', { active: textureMode === 'image' }]"
                    @click="textureMode = 'image'"
                  >
                    图片生成
                  </button>
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
                    ></textarea>
                  </div>
                  <button 
                    @click="generateTextureFromPrompt" 
                    :disabled="!texturePrompt.trim() || !loadedModel || isGeneratingTexture"
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
                    <div v-if="textureImagePreview" class="image-preview">
                      <img :src="textureImagePreview" alt="预览" />
                    </div>
                  </div>
                  <button 
                    @click="generateTextureFromImage" 
                    :disabled="!selectedTextureImage || !loadedModel || isGeneratingTexture"
                    class="generate-texture-btn"
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
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js'
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js'
import Stats from 'three/examples/jsm/libs/stats.module.js'
import HomePage from './components/HomePage.vue'
import TextTo3D from './components/TextTo3D.vue'
import JoinRoom from './components/JoinRoom.vue'

export default {
  name: 'App',
  components: {
    HomePage,
    TextTo3D,
    JoinRoom
  },
  data() {
    return {
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
      
      // 标签页控制
      activeTab: 'upload', // upload, texture, history
      
      // 纹理生成相关
      textureMode: 'prompt', // prompt 或 image
      texturePrompt: '',
      selectedTextureImage: null,
      textureImagePreview: null,
      isGeneratingTexture: false,
      textureStatus: null,
      
      // 操作历史记录
      operationHistory: [],
      currentUserName: '当前用户' // 可以从登录系统获取
    }
  },
  mounted() {
    // 初始页面为首页，不自动初始化3D场景
  },
  beforeDestroy() {
    // 组件销毁前清理资源
    this.cleanup()
  },
  methods: {
    // 保存模型方法
    saveModel() {
       if (!this.loadedModel) return;
       
       const exporter = new GLTFExporter();
       
       // 配置导出选项
       const options = {
         trs: false,
         onlyVisible: true,
         binary: true, // 导出为GLB格式
         maxTextureSize: 4096
       };
       
       // 导出场景中的模型
       exporter.parse(this.modelGroup, (result) => {
        // 创建下载链接
        const blob = new Blob([result], { type: 'application/octet-stream' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        const filename = `beautified-model-${Date.now()}.glb`;
        link.href = url;
        link.download = filename;
        link.click();
        
        // 清理URL对象
        URL.revokeObjectURL(url);
        
        // 记录操作历史
        this.recordOperation('保存模型', `文件名：${filename}`);
        
        alert('模型保存成功！');
      }, (error) => {
        console.error('导出模型时发生错误:', error);
        alert('模型保存失败，请检查控制台错误信息。');
      }, options);
    },
    
    initThree() {
      // 创建一个三维场景
      this.scene = new THREE.Scene()

      // 创建一个模型组
      this.modelGroup = new THREE.Group()
      this.scene.add(this.modelGroup)

      // 辅助观察的坐标系
      this.axesHelper = new THREE.AxesHelper(100)
      this.scene.add(this.axesHelper)
      
      // 添加一个辅助网格地面
      this.gridHelper = new THREE.GridHelper(10, 10, 0x004444, 0x004444)
      this.scene.add(this.gridHelper)

      // 模型缩放调整
      // this.model.scale.set(20, 20, 20)

      // 光源设置
      this.directionalLight = new THREE.DirectionalLight(0xffffff, 1)
      this.directionalLight.position.set(15, 15, 15)
      this.scene.add(this.directionalLight)
      
      this.ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
      this.scene.add(this.ambientLight)

      // 定义相机输出画布尺寸（单位：像素px）
      const width = this.$refs.threeContainer.clientWidth
      const height = this.$refs.threeContainer.clientHeight

      // 创建一个透视投影相机对象
      this.camera = new THREE.PerspectiveCamera(60, width / height, 1, 1000)
      // 设置相机位置
      this.camera.position.set(5, 5, -10)
      // 相机的视线 观察目标点的坐标
      this.camera.lookAt(0, 0, 0)

      // 创建一个WebGL渲染器
      this.renderer = new THREE.WebGLRenderer({
        antialias: true // 开启优化锯齿
      })
      this.renderer.setSize(width, height) // canvas的宽高度
      this.renderer.setPixelRatio(window.devicePixelRatio) // 防止输出模糊
      
      // 解决加载gltf格式模型颜色偏差问题
      this.renderer.outputEncoding = THREE.sRGBEncoding
      this.renderer.setClearColor(0xf0f0f0) // 设置背景色

      // 把渲染结果canvas画布添加到Vue组件的容器中
      this.$refs.threeContainer.appendChild(this.renderer.domElement)

      // 创建性能监视器
      this.stats = new Stats()
      this.$refs.threeContainer.appendChild(this.stats.dom)

      // 创建一个相机控件对象
      this.controls = new OrbitControls(this.camera, this.renderer.domElement)
      this.controls.update()

      // 动画循环
      this.animate()

      // 窗口大小调整处理
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
      
      // 重置动画混合器
      if (this.mixer) {
        this.mixer.stopAllAction()
        this.mixer = null
      }
      
      const loader = new GLTFLoader()
      const fileURL = URL.createObjectURL(this.selectedFile)
      
      loader.load(
        fileURL,
        (gltf) => {
          console.log('模型加载成功:', gltf)
          this.loadedModel = gltf.scene
          this.modelGroup.add(this.loadedModel)
          
          // 自动缩放和定位模型
          this.autoScaleAndPositionModel(this.loadedModel)
          
          // 如果有动画，初始化动画混合器
          if (gltf.animations && gltf.animations.length > 0) {
            this.hasAnimation = true
            this.animationPlaying = true
            this.mixer = new THREE.AnimationMixer(gltf.scene)
            this.clock = new THREE.Clock()
            
            // 播放第一个动画
            this.clipAction = this.mixer.clipAction(gltf.animations[0])
            this.clipAction.play()
          } else {
            this.hasAnimation = false
            this.animationPlaying = false
          }
          
          // 记录操作历史
          this.recordOperation('上传模型', `文件名：${this.selectedFile.name}`)
          
          this.uploadStatus = '模型加载成功！'
          
          // 5秒后清除状态消息
          setTimeout(() => {
            this.uploadStatus = null
          }, 5000)
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
      
      // 计算模型的最大尺寸
      const maxDim = Math.max(size.x, size.y, size.z)
      // 计算缩放比例，使模型适合在场景中显示
      const scale = 5 / maxDim
      
      // 缩放模型
      model.scale.setScalar(scale)
      
      // 重新计算边界框
      box.setFromObject(model)
      
      // 将模型移动到原点
      const newCenter = box.getCenter(new THREE.Vector3())
      model.position.sub(newCenter)
    },
    
    // 动画循环
    animate() {
      this.animationId = requestAnimationFrame(this.animate)
      
      // 更新动画混合器
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

    // 材质控制方法
    updateMaterialColor() {
      const color = new THREE.Color(this.materialColor)
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          child.material.color = color
        }
      })
      this.recordOperation('修改材质颜色', `颜色值：${this.materialColor}`)
    },
    
    updateMaterialEmissive() {
      const emissiveIntensity = this.materialEmissive
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          child.material.emissive = new THREE.Color(emissiveIntensity, emissiveIntensity, emissiveIntensity)
        }
      })
      this.recordOperation('修改材质亮度', `亮度值：${this.materialEmissive}`)
    },
    
    updateMaterialMetalness() {
      this.loadedModel.traverse((child) => {
        if (child.isMesh && child.material.metalness !== undefined) {
          child.material.metalness = this.materialMetalness
        }
      })
      this.recordOperation('修改材质金属度', `金属度：${this.materialMetalness}`)
    },
    
    updateMaterialRoughness() {
      this.loadedModel.traverse((child) => {
        if (child.isMesh && child.material.roughness !== undefined) {
          child.material.roughness = this.materialRoughness
        }
      })
      this.recordOperation('修改材质粗糙度', `粗糙度：${this.materialRoughness}`)
    },
    
    // 光照控制方法
    updateLightColor() {
      this.directionalLight.color = new THREE.Color(this.lightColor)
    },
    
    updateLightIntensity() {
      this.directionalLight.intensity = this.lightIntensity
    },
    
    updateAmbientIntensity() {
      this.ambientLight.intensity = this.ambientIntensity
    },
    
    // 场景控制方法
    updateBackgroundColor() {
      this.renderer.setClearColor(this.backgroundColor)
    },
    
    toggleGrid() {
      if (this.showGrid) {
        this.scene.add(this.gridHelper)
      } else {
        this.scene.remove(this.gridHelper)
      }
    },
    
    toggleAxes() {
      if (this.showAxes) {
        this.scene.add(this.axesHelper)
      } else {
        this.scene.remove(this.axesHelper)
      }
    },
    
    // 视角控制方法
    setPerspective(type) {
      const perspectiveNames = {
        'front': '正面视角',
        'side': '侧面视角',
        'top': '俯视视角',
        'isometric': '等轴视角'
      }
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
      this.recordOperation('切换视角', perspectiveNames[type] || type)
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
      // 移除事件监听器
      window.removeEventListener('resize', this.handleResize)
      
      // 取消动画帧
      if (this.animationId) {
        cancelAnimationFrame(this.animationId)
      }
      
      // 清理动画混合器
      if (this.mixer) {
        this.mixer.stopAllAction()
        this.mixer.uncacheRoot(this.modelGroup)
      }
      
      // 清理Three.js资源
      if (this.renderer) {
        this.renderer.dispose()
        this.renderer.forceContextLoss()
      }
      
      // 清理控制器
      if (this.controls) {
        this.controls.dispose()
      }
      
      // 从DOM中移除canvas
      if (this.$refs.threeContainer && this.renderer) {
        try {
          this.$refs.threeContainer.removeChild(this.renderer.domElement)
        } catch (e) {
          console.log('Canvas元素已移除')
        }
      }
      
      // 移除性能监视器
      if (this.stats && this.stats.dom) {
        try {
          this.$refs.threeContainer.removeChild(this.stats.dom)
        } catch (e) {
          console.log('Stats元素已移除')
        }
      }
      
      // 清理场景
      if (this.scene) {
        this.scene.traverse((object) => {
          if (object.geometry) {
            object.geometry.dispose()
          }
          if (object.material) {
            if (Array.isArray(object.material)) {
              object.material.forEach(material => material.dispose())
            } else {
              object.material.dispose()
            }
          }
          if (object.texture) {
            object.texture.dispose()
          }
        })
      }
    },
    
    // 页面切换方法
    handleSelectOption(option) {
      switch(option) {
        case 'text-to-3d':
          this.currentPage = 'text-to-3d';
          break;
        case 'image-to-3d':
          this.currentPage = 'image-to-3d';
          break;
        case 'room-editor':
          this.currentPage = 'room-editor';
          break;
        case 'model-editor':
          this.currentPage = 'model-editor';
          this.initThree(); // 初始化3D场景
          break;
        default:
          this.currentPage = 'home';
      }
    },
    
    // 处理加载模型事件（来自JoinRoom组件）
    handleLoadModel(modelData) {
      // 保存模型数据到状态
      this.modelStatus = {
        loading: false,
        success: true,
        progress: 100,
        message: '模型加载成功！',
        error: null,
        previewImageUrl: modelData.previewImageUrl,
        modelUrl: modelData.modelUrl
      };
      
      // 跳转到模型编辑器页面
      this.currentPage = 'model-editor';
      
      // 使用$nextTick确保DOM更新后再初始化3D场景和加载模型
      this.$nextTick(() => {
        // 初始化3D场景
        this.initThree();
        
        // 延迟一点时间确保场景完全初始化后再加载模型
        setTimeout(() => {
          // 加载模型
          this.loadModelFromUrl(modelData.modelUrl);
        }, 100);
      });
    },
    
    // 从URL加载模型
    async loadModelFromUrl(modelUrl) {
      try {
        console.log('开始加载模型:', modelUrl);
        
        // 加载生成的模型
        this.uploadStatus = '正在加载模型...';
        
        // 清理之前加载的模型
        if (this.loadedModel) {
          this.modelGroup.remove(this.loadedModel);
          this.loadedModel = null;
        }
        
        // 重置动画混合器
        if (this.mixer) {
          this.mixer.stopAllAction();
          this.mixer = null;
        }
        
        // 使用GLTFLoader加载模型
        const loader = new GLTFLoader();
        
        loader.load(
          modelUrl,
          (gltf) => {
            console.log('模型加载成功:', gltf);
            this.loadedModel = gltf.scene;
            this.modelGroup.add(this.loadedModel);
            
            // 自动缩放和定位模型
            this.autoScaleAndPositionModel(this.loadedModel);
            
            // 如果有动画，初始化动画混合器
            if (gltf.animations && gltf.animations.length > 0) {
              this.hasAnimation = true;
              this.animationPlaying = true;
              this.mixer = new THREE.AnimationMixer(gltf.scene);
              this.clock = new THREE.Clock();
              
              // 播放第一个动画
              this.clipAction = this.mixer.clipAction(gltf.animations[0]);
              this.clipAction.play();
            } else {
              this.hasAnimation = false;
              this.animationPlaying = false;
            }
            
            this.uploadStatus = '模型加载成功！';
            
            // 5秒后清除状态消息
            setTimeout(() => {
              this.uploadStatus = null;
            }, 5000);
          },
          (progress) => {
            const percent = Math.round((progress.loaded / progress.total) * 100);
            this.uploadStatus = `模型加载中... ${percent}%`;
          },
          (error) => {
            console.error('模型加载失败:', error);
            this.uploadStatus = '模型加载失败，请稍后重试';
          }
        );
      } catch (error) {
        console.error('加载模型失败:', error);
        this.uploadStatus = '模型加载失败，请稍后重试';
      }
    },
    
    // 处理查看模型状态事件
    handleViewModelStatus() {
      this.currentPage = 'model-status';
      // 初始化模型状态
      this.modelStatus = {
        loading: true,
        progress: 0,
        message: '模型生成中，请稍候...',
        success: false,
        error: null,
        previewImageUrl: '',
        modelUrl: ''
      };
      // 开始定期检查模型状态
      this.startCheckingModelStatus();
    },
    
    // 开始定期检查模型状态
    startCheckingModelStatus() {
      // 清除可能存在的旧定时器
      if (this.statusCheckTimer) {
        clearInterval(this.statusCheckTimer);
      }
      // 每5秒检查一次模型状态
      this.statusCheckTimer = setInterval(() => {
        this.checkModelStatus();
      }, 5000);
      // 立即检查一次
      this.checkModelStatus();
    },
    
    // 检查模型生成状态
    async checkModelStatus() {
      const jobId = localStorage.getItem('modelJobId');
      if (!jobId) {
        this.modelStatus.error = '未找到任务ID';
        this.modelStatus.loading = false;
        return;
      }
      
      try {
        const response = await fetch('http://localhost:8082/api/models/status', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ jobId })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('模型状态检查结果(完整数据):', JSON.stringify(data));
        console.log('模型状态值:', data.status);
        
        // 处理腾讯云API返回的字符串状态或后端返回的数字状态
        let status = data.status;
        
        // 如果是字符串状态（来自腾讯云API）
        if (typeof status === 'string') {
          status = status.toUpperCase();
          
          if (status === 'RUN') {
            // 运行中
            this.modelStatus.loading = true;
            // 假进度：每次增加5-10%，最高到90%
            this.modelStatus.progress += Math.floor(Math.random() * 6) + 5; // 5-10%的随机增量
            if (this.modelStatus.progress > 90) {
              this.modelStatus.progress = 90;
            }
            this.modelStatus.message = '模型正在生成中...';
            return;
          } else if (status === 'FAIL' || status === 'FAILED') {
            // 生成失败
            this.modelStatus.loading = false;
            this.modelStatus.error = '模型生成失败，请稍后重试';
            // 清除定时器
            clearInterval(this.statusCheckTimer);
            return;
          } else if (status === 'DONE' || status === 'SUCCEEDED' || status === 'SUCCESS') {
            // 生成成功
            status = 3;
          }
        } else {
          // 如果是数字状态（来自后端转换）
          status = parseInt(status);
        }
        
        // 处理数字状态
        if (status === 0) {
          // 等待中
          this.modelStatus.loading = true;
          this.modelStatus.progress += 5;
          if (this.modelStatus.progress > 90) {
            this.modelStatus.progress = 90;
          }
          this.modelStatus.message = '模型排队等待中...';
        } else if (status === 1) {
          // 生成中
          this.modelStatus.loading = true;
          this.modelStatus.progress += 10;
          if (this.modelStatus.progress > 90) {
            this.modelStatus.progress = 90;
          }
          this.modelStatus.message = '模型正在生成中...';
        } else if (status === 2) {
          // 生成失败
          this.modelStatus.loading = false;
          this.modelStatus.error = '模型生成失败，请稍后重试';
          // 清除定时器
          clearInterval(this.statusCheckTimer);
        } else if (status === 3) {
          // 生成成功
          this.modelStatus.loading = false;
          this.modelStatus.success = true;
          this.modelStatus.progress = 100;
          this.modelStatus.message = '模型生成成功！';
          
          // 保存模型URL信息
          this.modelStatus.previewImageUrl = data.targetimgurl || '';
          this.modelStatus.modelUrl = data.target3durl || '';
          
          console.log('更新后的模型状态:', JSON.stringify(this.modelStatus));
          
          // 清除定时器
          clearInterval(this.statusCheckTimer);
        } else {
          // 未知状态
          console.log('未知的模型状态:', status);
          this.modelStatus.loading = false;
          this.modelStatus.error = '未知的模型状态';
          // 清除定时器
          clearInterval(this.statusCheckTimer);
        }
      } catch (error) {
        console.error('检查模型状态失败:', error);
        this.modelStatus.loading = false;
        this.modelStatus.error = '检查模型状态失败，请稍后重试';
        // 清除定时器
        clearInterval(this.statusCheckTimer);
      }
    },
    
    // 加载生成成功的模型（从模型状态页面）
    async handleLoadModelFromStatus() {
      const jobId = localStorage.getItem('modelJobId');
      if (!jobId) {
        alert('未找到任务ID');
        return;
      }
      
      try {
        console.log('开始加载模型...');
        console.log('当前模型状态:', JSON.stringify(this.modelStatus));
        
        // 跳转到模型编辑器页面
        this.currentPage = 'model-editor';
        
        // 使用$nextTick确保DOM更新后再初始化3D场景和加载模型
        this.$nextTick(() => {
          // 初始化3D场景
          this.initThree();
          
          // 延迟一点时间确保场景完全初始化后再加载模型
          setTimeout(() => {
            // 加载生成的模型
            this.uploadStatus = '正在加载模型...';
            
            // 清理之前加载的模型
            if (this.loadedModel) {
              this.modelGroup.remove(this.loadedModel);
              this.loadedModel = null;
            }
            
            // 重置动画混合器
            if (this.mixer) {
              this.mixer.stopAllAction();
              this.mixer = null;
            }
            
            // 使用从后端获取的模型URL
            const modelUrl = this.modelStatus.modelUrl;
            
            console.log('模型URL:', modelUrl);
            
            if (!modelUrl) {
              console.error('模型URL为空，无法加载模型');
              this.uploadStatus = '模型URL获取失败';
              return;
            }
            
            // 检查模型格式，如果是.obj格式，需要加载材质
            if (modelUrl.endsWith('.obj')) {
              // 加载材质
              const mtlLoader = new MTLLoader();
              const mtlUrl = modelUrl.replace('.obj', '.mtl');
              
              mtlLoader.load(
            mtlUrl,
            (materials) => {
              materials.preload();
              
              // 加载模型
              const objLoader = new OBJLoader();
              objLoader.setMaterials(materials);
              
              objLoader.load(
                modelUrl,
                (object) => {
                  console.log('模型加载成功:', object);
                  this.loadedModel = object;
                  this.modelGroup.add(this.loadedModel);
                  
                  // 自动缩放和定位模型
                  this.autoScaleAndPositionModel(this.loadedModel);
                  
                  // OBJ模型通常没有动画
                  this.hasAnimation = false;
                  this.animationPlaying = false;
                  
                  this.uploadStatus = '模型加载成功！';
                  
                  // 5秒后清除状态消息
                  setTimeout(() => {
                    this.uploadStatus = null;
                  }, 5000);
                },
                (progress) => {
                  const percent = Math.round((progress.loaded / progress.total) * 100);
                  this.uploadStatus = `模型加载中... ${percent}%`;
                },
                (error) => {
                  console.error('模型加载失败:', error);
                  this.uploadStatus = '模型加载失败，请稍后重试';
                }
              );
            },
            (progress) => {
              const percent = Math.round((progress.loaded / progress.total) * 100);
              this.uploadStatus = `材质加载中... ${percent}%`;
            },
              (error) => {
                console.error('材质加载失败:', error);
                this.uploadStatus = '材质加载失败，请稍后重试';
              }
            );
          } else {
              // 使用GLTFLoader加载其他格式的模型
              const loader = new GLTFLoader();
              
              loader.load(
                modelUrl,
                (gltf) => {
                  console.log('模型加载成功:', gltf);
                  this.loadedModel = gltf.scene;
                  this.modelGroup.add(this.loadedModel);
                  
                  // 自动缩放和定位模型
                  this.autoScaleAndPositionModel(this.loadedModel);
                  
                  // 如果有动画，初始化动画混合器
                  if (gltf.animations && gltf.animations.length > 0) {
                    this.hasAnimation = true;
                    this.animationPlaying = true;
                    this.mixer = new THREE.AnimationMixer(gltf.scene);
                    this.clock = new THREE.Clock();
                    
                    // 播放第一个动画
                    this.clipAction = this.mixer.clipAction(gltf.animations[0]);
                    this.clipAction.play();
                  } else {
                    this.hasAnimation = false;
                    this.animationPlaying = false;
                  }
                  
                  this.uploadStatus = '模型加载成功！';
                  
                  // 5秒后清除状态消息
                  setTimeout(() => {
                    this.uploadStatus = null;
                  }, 5000);
                },
                (progress) => {
                  const percent = Math.round((progress.loaded / progress.total) * 100);
                  this.uploadStatus = `模型加载中... ${percent}%`;
                },
                (error) => {
                  console.error('模型加载失败:', error);
                  this.uploadStatus = '模型加载失败，请稍后重试';
                }
              );
            }
          }, 100);
        });
      } catch (error) {
        console.error('加载模型失败:', error);
        alert('加载模型失败，请稍后重试');
      }
    },
    
    // 重试生成模型
    handleRetry() {
      // 跳回文字生成页面
      this.currentPage = 'text-to-3d';
      // 清除jobId
      localStorage.removeItem('modelJobId');
      // 清除定时器
      if (this.statusCheckTimer) {
        clearInterval(this.statusCheckTimer);
      }
    },
    
    // 返回主页
    handleBack() {
      this.currentPage = 'home';
      this.cleanup(); // 清理3D场景资源
      // 清除jobId和定时器
      localStorage.removeItem('modelJobId');
      if (this.statusCheckTimer) {
        clearInterval(this.statusCheckTimer);
      }
    },
    
    // 记录操作历史
    recordOperation(action, details = '') {
      const record = {
        user: this.currentUserName,
        action: action,
        details: details,
        timestamp: new Date()
      };
      this.operationHistory.unshift(record); // 添加到开头
      // 限制历史记录数量，最多保存100条
      if (this.operationHistory.length > 100) {
        this.operationHistory = this.operationHistory.slice(0, 100);
      }
    },
    
    // 处理纹理图片选择
    handleTextureImageSelect(event) {
      const file = event.target.files[0];
      if (file) {
        if (file.type.startsWith('image/')) {
          this.selectedTextureImage = file;
          // 创建预览
          const reader = new FileReader();
          reader.onload = (e) => {
            this.textureImagePreview = e.target.result;
          };
          reader.readAsDataURL(file);
        } else {
          this.textureStatus = '请选择有效的图片文件';
          this.selectedTextureImage = null;
          this.textureImagePreview = null;
        }
      }
    },
    
    // 从提示词生成纹理
    async generateTextureFromPrompt() {
      if (!this.texturePrompt.trim() || !this.loadedModel) {
        return;
      }
      
      this.isGeneratingTexture = true;
      this.textureStatus = '正在生成纹理...';
      
      try {
        // TODO: 调用后端API生成纹理
        // 这里需要根据实际的后端API接口来实现
        console.log('生成纹理提示词:', this.texturePrompt);
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 记录操作历史
        this.recordOperation('生成纹理', `使用提示词：${this.texturePrompt}`);
        
        this.textureStatus = '纹理生成成功！';
        setTimeout(() => {
          this.textureStatus = null;
        }, 3000);
      } catch (error) {
        console.error('生成纹理失败:', error);
        this.textureStatus = '纹理生成失败，请稍后重试';
      } finally {
        this.isGeneratingTexture = false;
      }
    },
    
    // 从图片生成纹理
    async generateTextureFromImage() {
      if (!this.selectedTextureImage || !this.loadedModel) {
        return;
      }
      
      this.isGeneratingTexture = true;
      this.textureStatus = '正在生成纹理...';
      
      try {
        // TODO: 调用后端API生成纹理
        // 这里需要根据实际的后端API接口来实现
        console.log('生成纹理图片:', this.selectedTextureImage.name);
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 记录操作历史
        this.recordOperation('生成纹理', `使用图片：${this.selectedTextureImage.name}`);
        
        this.textureStatus = '纹理生成成功！';
        setTimeout(() => {
          this.textureStatus = null;
        }, 3000);
      } catch (error) {
        console.error('生成纹理失败:', error);
        this.textureStatus = '纹理生成失败，请稍后重试';
      } finally {
        this.isGeneratingTexture = false;
      }
    },
    
    // 格式化时间
    formatTime(timestamp) {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now - date;
      
      // 如果小于1分钟，显示"刚刚"
      if (diff < 60000) {
        return '刚刚';
      }
      // 如果小于1小时，显示分钟
      if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`;
      }
      // 如果小于1天，显示小时
      if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`;
      }
      // 否则显示完整时间
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    // 清空历史记录
    clearHistory() {
      if (confirm('确定要清空所有操作历史记录吗？')) {
        this.operationHistory = [];
        this.recordOperation('清空历史记录');
      }
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f7fa;
  color: #333;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem 2rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.app-header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.upload-section {
  padding: 2rem;
  background: white;
  margin: 2rem auto;
  border-radius: 10px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
  width: 90%;
  max-width: 800px;
  text-align: center;
}

.upload-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  align-items: center;
  margin-bottom: 1rem;
}

.file-input {
  display: none;
}

.file-label {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  background: #e9ecef;
  color: #495057;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  min-width: 200px;
}

/* 模型状态页面样式 */
.model-status-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.model-status-container h2 {
  color: #495057;
  margin-bottom: 2rem;
}

.loading-container {
  margin: 2rem 0;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  transition: width 0.5s ease;
}

.error-container {
  color: #f44336;
  margin: 2rem 0;
}

.success-container {
  color: #4CAF50;
  margin: 2rem 0;
}

.retry-button, .load-button {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.retry-button:hover, .load-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.file-label:hover {
  background: #dee2e6;
}

.upload-btn {
  padding: 0.8rem 2rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.upload-btn:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-2px);
}

.save-btn {
  padding: 0.8rem 2rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.save-btn:hover {
  background: #43A047;
  transform: translateY(-2px);
}

.back-button {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 0.8rem 2rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  z-index: 10;
}

.back-button:hover {
  background: #43A047;
  transform: translateY(-2px);
}

.upload-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
}

.upload-status {
  padding: 0.8rem;
  border-radius: 5px;
  font-weight: 500;
  margin-top: 1rem;
}

.upload-status:contains('成功') {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.upload-status:contains('失败') {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.upload-status:contains('加载中') {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* 模型编辑器页面布局 */
.model-editor-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content-wrapper {
  display: flex;
  gap: 2rem;
  width: 95%;
  max-width: 1600px;
  margin: 2rem auto;
  flex: 1;
}

.scene-container-wrapper {
  flex: 1;
  min-width: 600px;
}

.three-container {
  width: 100%;
  height: 70vh;
  min-height: 600px;
  border: 1px solid #ddd;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
}

.right-panel {
  width: 400px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  max-height: 70vh;
  min-height: 600px;
}

/* 标签页导航 */
.tabs-nav {
  display: flex;
  border-bottom: 2px solid #e9ecef;
  background: #f8f9fa;
  border-radius: 10px 10px 0 0;
}

.tab-btn {
  flex: 1;
  padding: 1rem;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.tab-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
  background: white;
}

.tab-btn svg {
  width: 16px;
  height: 16px;
}

/* 标签页内容 */
.tabs-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.tab-panel {
  height: 100%;
}

.tab-panel h3 {
  color: #495057;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.main-content {
    display: flex;
    flex-wrap: wrap;
    gap: 2rem;
    width: 90%;
    max-width: 1400px;
    margin: 2rem auto;
    justify-content: center;
  }
  
  .control-panel {
    width: 100%;
    background: transparent;
    border-radius: 0;
    box-shadow: none;
    padding: 0;
    height: fit-content;
    max-height: none;
    overflow-y: visible;
  }
  
  .control-panel h3 {
    color: #495057;
    margin-bottom: 1.5rem;
    font-size: 1.2rem;
    border-bottom: 2px solid #e9ecef;
    padding-bottom: 0.5rem;
  }
  
  .control-group {
    margin-bottom: 1.5rem;
  }
  
  .control-group h4 {
    color: #6c757d;
    margin-bottom: 1rem;
    font-size: 1rem;
    font-weight: 600;
  }
  
  .control-item {
    margin-bottom: 1rem;
  }
  
  .control-item label {
    display: block;
    color: #495057;
    margin-bottom: 0.5rem;
    font-weight: 500;
    font-size: 0.9rem;
  }
  
  .control-item input[type="color"] {
    width: 100%;
    height: 40px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .control-item input[type="range"] {
    width: 100%;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
    outline: none;
    -webkit-appearance: none;
    appearance: none;
  }
  
  .control-item input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    background: #007bff;
    border-radius: 50%;
    cursor: pointer;
  }
  
  .control-item input[type="range"]::-moz-range-thumb {
    width: 18px;
    height: 18px;
    background: #007bff;
    border-radius: 50%;
    cursor: pointer;
    border: none;
  }
  
  .control-item input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
  
  .preset-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .preset-btn {
    padding: 0.7rem;
    background: #6c757d;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
    font-size: 0.9rem;
  }
  
  .preset-btn:hover {
    background: #5a6268;
    transform: translateY(-2px);
  }

/* 调整性能监视器位置 */
.three-container .stats {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
}

/* 纹理生成样式 */
.texture-generation-section {
  margin-top: 1rem;
}

.texture-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.texture-tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  color: #6c757d;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.texture-tab-btn:hover {
  color: #495057;
  background: #f8f9fa;
}

.texture-tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.texture-content {
  margin-top: 1rem;
}

.texture-content .form-group {
  margin-bottom: 1.5rem;
}

.texture-content label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-weight: 500;
  font-size: 0.9rem;
}

.texture-content textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.texture-content textarea:focus {
  outline: none;
  border-color: #667eea;
}

.image-preview {
  margin-top: 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  max-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}

.generate-texture-btn {
  width: 100%;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.generate-texture-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.generate-texture-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.texture-status {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
  font-size: 0.9rem;
}

/* 操作历史样式 */
.history-section {
  margin-top: 1rem;
}

.empty-history {
  text-align: center;
  padding: 3rem 1rem;
  color: #6c757d;
}

.history-list {
  max-height: 500px;
  overflow-y: auto;
}

.history-item {
  padding: 1rem;
  margin-bottom: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.history-user {
  font-weight: 600;
  color: #495057;
  font-size: 0.95rem;
}

.history-time {
  font-size: 0.85rem;
  color: #6c757d;
}

.history-action {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.action-type {
  font-weight: 500;
  color: #667eea;
  font-size: 0.9rem;
}

.action-details {
  font-size: 0.85rem;
  color: #6c757d;
  font-style: italic;
}

.clear-history-btn {
  width: 100%;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-history-btn:hover {
  background: #c82333;
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content-wrapper {
    flex-direction: column;
  }
  
  .scene-container-wrapper {
    min-width: 100%;
  }
  
  .right-panel {
    width: 100%;
    max-height: none;
  }
}

@media (max-width: 768px) {
  .app-header h1 {
    font-size: 2rem;
  }
  
  .upload-section {
    width: 95%;
    padding: 1.5rem;
  }
  
  .upload-container {
    flex-direction: column;
  }
  
  .file-label,
  .upload-btn {
    width: 100%;
    max-width: 300px;
  }
  
  .three-container {
    height: 400px;
    min-height: 400px;
  }
  
  .tabs-nav {
    flex-direction: column;
  }
  
  .tab-btn {
    border-bottom: 1px solid #e9ecef;
    border-right: none;
  }
  
  .tab-btn.active {
    border-bottom-color: #e9ecef;
    border-left: 3px solid #667eea;
  }
}
</style>