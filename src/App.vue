<template>
  <div id="app">
    <header class="app-header">
      <h1>智能3D设计助手平台</h1>
      <p>上传您的3D模型文件，开始设计之旅</p>
    </header>
    
    <!-- 文件上传区域 -->
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
    
    <div class="main-content">
      <!-- 3D场景容器 -->
      <div ref="threeContainer" class="three-container"></div>
      
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
    </div>
  </div>
</template>

<script>
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js'
import Stats from 'three/examples/jsm/libs/stats.module.js'

export default {
  name: 'App',
  data() {
    return {
      mixer: null,
      clock: null,
      animationId: null,
      selectedFile: null,
      uploadStatus: null,
      loadedModel: null,
      hasAnimation: false,
      animationPlaying: false,
      animationSpeed: 1.0,
      
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
      showAxes: true
    }
  },
  mounted() {
    // 在组件挂载后执行 Three.js 代码
    this.initThree()
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
        
        link.href = url;
        link.download = `beautified-model-${Date.now()}.glb`;
        link.click();
        
        // 清理URL对象
        URL.revokeObjectURL(url);
        
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
    },
    
    updateMaterialEmissive() {
      const emissiveIntensity = this.materialEmissive
      this.loadedModel.traverse((child) => {
        if (child.isMesh) {
          child.material.emissive = new THREE.Color(emissiveIntensity, emissiveIntensity, emissiveIntensity)
        }
      })
    },
    
    updateMaterialMetalness() {
      this.loadedModel.traverse((child) => {
        if (child.isMesh && child.material.metalness !== undefined) {
          child.material.metalness = this.materialMetalness
        }
      })
    },
    
    updateMaterialRoughness() {
      this.loadedModel.traverse((child) => {
        if (child.isMesh && child.material.roughness !== undefined) {
          child.material.roughness = this.materialRoughness
        }
      })
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

.main-content {
    display: flex;
    flex-wrap: wrap;
    gap: 2rem;
    width: 90%;
    max-width: 1400px;
    margin: 2rem auto;
    justify-content: center;
  }
  
  .three-container {
    flex: 1;
    min-width: 300px;
    height: 600px;
    border: 1px solid #ddd;
    border-radius: 10px;
    position: relative;
    overflow: hidden;
    background: white;
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
  }
  
  .control-panel {
    width: 300px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
    padding: 1.5rem;
    height: fit-content;
    max-height: 600px;
    overflow-y: auto;
  }
  
  .control-panel h3 {
    color: #495057;
    margin-bottom: 1.5rem;
    font-size: 1.3rem;
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

/* 响应式设计 */
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
    width: 95%;
  }
}
</style>