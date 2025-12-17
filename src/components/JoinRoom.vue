<template>
  <div class="join-room-container">
    <div class="header">
      <h1>加入3D模型编辑房间</h1>
      <button @click="$emit('back')" class="back-button">返回</button>
    </div>
    
    <div class="join-room-form">
      <div class="form-group">
        <label for="jobId">请输入房间号（jobid）</label>
        <input 
          id="jobId" 
          v-model="jobId" 
          type="text" 
          placeholder="请输入jobid，例如：63731e3d-4f3e-4b5c-8d1a-2b3c4d5e6f7g"
          :disabled="isLoading || isCheckingStatus"
        />
      </div>
      
      <div class="action-section">
        <button 
          @click="joinRoom" 
          class="join-button"
          :disabled="isLoading || isCheckingStatus || !jobId.trim()"
        >
          {{ isLoading ? '查询中...' : '加入房间' }}
        </button>
      </div>
      
      <div v-if="errorMessage" class="error-message">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f44336" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="15" y1="9" x2="9" y2="15"></line>
          <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
        {{ errorMessage }}
      </div>
      
      <!-- 模型生成进度显示 -->
      <div v-if="isCheckingStatus" class="status-container">
        <h3>模型生成状态</h3>
        <div class="progress-bar">
          <div class="progress" :style="{ width: modelProgress + '%' }"></div>
        </div>
        <p>{{ statusMessage }}</p>
        <button @click="stopCheckingStatus" class="stop-button">停止检查</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'JoinRoom',
  data() {
    return {
      jobId: '',
      isLoading: false,
      errorMessage: null,
      isCheckingStatus: false,
      modelProgress: 0,
      statusMessage: '',
      statusCheckTimer: null
    }
  },
  methods: {
    async joinRoom() {
      if (!this.jobId.trim()) {
        this.errorMessage = '请输入有效的jobid'
        return
      }
      
      this.isLoading = true
      this.errorMessage = null
      
      try {
        // 先检查模型状态
        const response = await fetch('http://localhost:8082/api/models/generate/getstatus', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ jobId: this.jobId })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        console.log('模型状态检查结果:', data)
        
        // 将jobId保存到localStorage
        localStorage.setItem('modelJobId', this.jobId)
        
        // 处理后端返回的状态字段
        let status = data.status !== undefined ? data.status : data.Status
        
        // 如果status是字符串，转换为数字
        if (typeof status === 'string') {
          const statusUpper = status.toUpperCase()
          if (statusUpper === 'DONE' || statusUpper === 'SUCCEEDED' || statusUpper === 'SUCCESS') {
            status = 3
          } else {
            // 其他字符串状态视为未完成
            status = 1
          }
        }
        
        status = parseInt(status)
        
        // 如果模型已经生成完成（status为3），直接跳转到模型编辑器
        if (status === 3) {
          // 构建模型URL：target3durl是文件夹路径，需要加上jobId.glb
          let modelUrl = ''
          if (data.target3durl) {
            // 确保URL格式正确，避免双斜杠
            const baseUrl = data.target3durl.endsWith('/') ? data.target3durl.slice(0, -1) : data.target3durl
            modelUrl = `${baseUrl}/${this.jobId}.glb`
          } else {
            // 如果后端没有返回target3durl，使用默认路径
            modelUrl = `http://localhost:8082/uploads/${this.jobId}/${this.jobId}.glb`
          }
          const previewImageUrl = data.targetimgurl || ''
          
          console.log('模型URL:', modelUrl)
          console.log('预览图URL:', previewImageUrl)
          
          // 触发页面切换事件，跳转到模型编辑器并加载模型
          this.$emit('load-model', {
            modelUrl: modelUrl,
            previewImageUrl: previewImageUrl,
            jobId: this.jobId
          })
        } else {
          // 如果模型还在生成中，开始定期检查状态并显示进度条
          this.startCheckingStatus()
        }
      } catch (error) {
        console.error('加入房间失败:', error)
        this.errorMessage = '加入房间失败，请检查jobid是否正确'
      } finally {
        this.isLoading = false
      }
    },
    
    // 开始定期检查模型状态
    startCheckingStatus() {
      this.isCheckingStatus = true
      // 初始化进度条，从10%开始，避免一开始就是0%
      this.modelProgress = 10
      this.statusMessage = '正在检查模型生成状态...'
      
      // 清除可能存在的旧定时器
      if (this.statusCheckTimer) {
        clearInterval(this.statusCheckTimer)
      }
      
      // 每3秒检查一次模型状态（更快响应）
      this.statusCheckTimer = setInterval(() => {
        this.checkModelStatus()
      }, 3000)
      
      // 立即检查一次
      this.checkModelStatus()
    },
    
    // 检查模型生成状态
    async checkModelStatus() {
      try {
        const response = await fetch('http://localhost:8082/api/models/generate/getstatus', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ jobId: this.jobId })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        console.log('模型状态检查结果:', data)
        
        // 处理后端返回的状态字段
        // 后端可能返回status（数字）或Status（字符串，来自腾讯云API）
        let status = data.status !== undefined ? data.status : data.Status
        
        // 如果status是字符串，转换为数字或特殊处理
        if (typeof status === 'string') {
          const statusUpper = status.toUpperCase()
          if (statusUpper === 'DONE' || statusUpper === 'SUCCEEDED' || statusUpper === 'SUCCESS') {
            // 如果后端已经处理完成并更新数据库，status应该已经是3
            // 但如果是腾讯云API直接返回的DONE，后端会继续处理
            status = 3
          } else if (statusUpper === 'RUN' || statusUpper === 'RUNNING') {
            // 运行中，显示进度条（伪装进度）
            this.statusMessage = '模型正在生成中...'
            // 伪装进度：每次检查增加3-8%，最高到90%
            this.modelProgress += Math.floor(Math.random() * 6) + 3
            if (this.modelProgress > 90) {
              this.modelProgress = 90
            }
            return
          } else if (statusUpper === 'FAIL' || statusUpper === 'FAILED') {
            // 生成失败
            this.statusMessage = '模型生成失败，请稍后重试'
            this.isCheckingStatus = false
            this.errorMessage = '模型生成失败，请稍后重试'
            clearInterval(this.statusCheckTimer)
            return
          }
        }
        
        // 转换为数字进行比较
        status = parseInt(status)
        
        // 处理数字状态
        if (status === 3) {
          // 生成成功，跳转到模型编辑器
          this.statusMessage = '模型生成成功！'
          this.modelProgress = 100
          this.isCheckingStatus = false
          
          // 清除定时器
          clearInterval(this.statusCheckTimer)
          
          // 构建模型URL：target3durl是文件夹路径，需要加上jobId.glb
          let modelUrl = ''
          if (data.target3durl) {
            // 确保URL格式正确，避免双斜杠
            const baseUrl = data.target3durl.endsWith('/') ? data.target3durl.slice(0, -1) : data.target3durl
            modelUrl = `${baseUrl}/${this.jobId}.glb`
          } else {
            // 如果后端没有返回target3durl，使用默认路径
            modelUrl = `http://localhost:8082/uploads/${this.jobId}/${this.jobId}.glb`
          }
          const previewImageUrl = data.targetimgurl || ''
          
          console.log('模型URL:', modelUrl)
          console.log('预览图URL:', previewImageUrl)
          
          // 触发页面切换事件，跳转到模型编辑器并加载模型
          this.$emit('load-model', {
            modelUrl: modelUrl,
            previewImageUrl: previewImageUrl,
            jobId: this.jobId
          })
        } else if (status === 0 || status === 1 || status === 2) {
          // 等待中或生成中
          if (status === 0) {
            this.statusMessage = '模型排队等待中...'
          } else if (status === 1) {
            this.statusMessage = '模型正在生成中...'
          } else if (status === 2) {
            // 生成失败
            this.statusMessage = '模型生成失败，请稍后重试'
            this.isCheckingStatus = false
            this.errorMessage = '模型生成失败，请稍后重试'
            clearInterval(this.statusCheckTimer)
            return
          }
          
          // 伪装进度：每次检查增加3-8%，最高到90%
          this.modelProgress += Math.floor(Math.random() * 6) + 3
          if (this.modelProgress > 90) {
            this.modelProgress = 90
          }
        } else {
          // 未知状态，可能还在生成中
          this.statusMessage = '模型正在处理中...'
          // 伪装进度
          this.modelProgress += Math.floor(Math.random() * 6) + 3
          if (this.modelProgress > 90) {
            this.modelProgress = 90
          }
        }
      } catch (error) {
        console.error('检查模型状态失败:', error)
        this.statusMessage = '检查模型状态失败，请稍后重试'
        this.isCheckingStatus = false
        this.errorMessage = '检查模型状态失败，请稍后重试'
        // 清除定时器
        clearInterval(this.statusCheckTimer)
      }
    },
    
    // 停止检查状态
    stopCheckingStatus() {
      this.isCheckingStatus = false
      if (this.statusCheckTimer) {
        clearInterval(this.statusCheckTimer)
      }
    }
  },
  
  // 组件销毁前清理定时器
  beforeDestroy() {
    if (this.statusCheckTimer) {
      clearInterval(this.statusCheckTimer)
    }
  }
}
</script>

<style scoped>
.join-room-container {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header {
  width: 100%;
  max-width: 600px;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  font-size: 2rem;
  color: #495057;
}

.back-button {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.back-button:hover {
  background-color: #5a6268;
}

.join-room-form {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
}

.form-group {
  margin-bottom: 2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
  color: #495057;
}

.form-group input {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.action-section {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.join-button {
  background-color: #667eea;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: background-color 0.3s ease;
}

.join-button:hover {
  background-color: #5a67d8;
}

.join-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.error-message {
  display: flex;
  align-items: center;
  color: #f44336;
  margin-top: 1rem;
  font-size: 1rem;
}

.error-message svg {
  margin-right: 0.5rem;
}

/* 模型状态显示样式 */
.status-container {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.status-container h3 {
  margin-bottom: 1rem;
  color: #495057;
  text-align: center;
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

.status-container p {
  text-align: center;
  color: #495057;
  margin-bottom: 1rem;
}

.stop-button {
  display: block;
  margin: 0 auto;
  padding: 0.5rem 1rem;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.stop-button:hover {
  background-color: #5a6268;
}
</style>