<template>
  <div class="text-to-3d-container">
    <div class="header">
      <h1>文字描述生成3D模型</h1>
      <button @click="$emit('back')" class="back-button">返回</button>
    </div>
    
    <div class="main-content">
      <div class="input-section">
        <div class="form-group">
          <label for="prompt">模型描述</label>
          <textarea 
            id="prompt" 
            v-model="prompt" 
            placeholder="请输入3D模型的文字描述，例如：一个红色的汽车模型..."
            rows="4"
            :disabled="isGenerating"
          ></textarea>
        </div>
        
        <div class="action-section">
          <button 
            @click="generateModel" 
            class="generate-button"
            :disabled="isGenerating || !prompt.trim()"
          >
            {{ isGenerating ? '生成中...' : '生成3D模型' }}
          </button>
        </div>
      </div>
      
      <div v-if="isGenerating" class="status-section">
        <div class="loading-spinner"></div>
        <p>正在生成3D模型，请稍候...</p>
      </div>
      
      <div v-else-if="modelResult" class="result-section">
        <div class="success-message">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="16 12 12 8 8 12"></polyline>
            <line x1="12" y1="16" x2="12" y2="12"></line>
          </svg>
          <h2>模型生成成功！</h2>
        </div>
        
        <div class="model-info">
          <div class="info-item">
            <strong>模型名称:</strong> {{ modelResult.name }}
          </div>
          <div class="info-item">
            <strong>模型格式:</strong> {{ modelResult.format }}
          </div>
          <div class="info-item">
            <strong>模型大小:</strong> {{ formatFileSize(modelResult.size) }}
          </div>
          <div class="info-item">
            <strong>创建时间:</strong> {{ formatDateTime(modelResult.createdAt) }}
          </div>
        </div>
        
        <div class="room-info">
          <h3>房间信息</h3>
          <div class="room-number">
            <span class="label">房间号:</span>
            <span class="value">{{ modelResult.roomNumber }}</span>
          </div>
          <p class="room-description">使用此房间号可以在"在线编辑"功能中继续编辑该模型</p>
          
          <div class="action-buttons">
            <button @click="copyRoomNumber" class="copy-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              复制房间号
            </button>
            <button @click="viewModel" class="view-button">查看模型</button>
          </div>
        </div>
      </div>
      
      <div v-else-if="errorMessage" class="error-section">
        <div class="error-message">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f44336" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <h2>生成失败</h2>
          <p>{{ errorMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TextTo3D',
  data() {
    return {
      prompt: '',
      isGenerating: false,
      modelResult: null,
      errorMessage: null
    }
  },
  methods: {
    async generateModel() {
      console.log('点击了生成模型按钮')
      if (!this.prompt.trim()) {
        this.errorMessage = '请输入模型描述'
        console.log('未输入模型描述')
        return
      }
      
      this.isGenerating = true
      this.errorMessage = null
      this.modelResult = null
      
      try {
        console.log('开始调用后端API')
        // 调用后端API生成模型
        const response = await fetch('http://localhost:8082/api/models/generate/text', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text: this.prompt, format: 'glb' })
        })
        
        console.log('API调用返回状态:', response.status)
        if (!response.ok) {
          const errorText = await response.text()
          console.log('API返回错误信息:', errorText)
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
        }
        
        const data = await response.json()
        console.log('API调用成功，返回数据:', data)
        
        // 检查是否包含jobId
        if (data.jobId) {
          // 将jobId保存到localStorage
          localStorage.setItem('modelJobId', data.jobId)
          
          // 触发页面切换事件，跳转到模型状态页面
          this.$emit('view-model-status')
        } else {
          throw new Error('API返回数据中缺少jobId')
        }
        
      } catch (error) {
        console.error('生成模型失败:', error)
        this.errorMessage = '生成3D模型失败，请稍后重试'
      } finally {
        this.isGenerating = false
      }
    },
    
    copyRoomNumber() {
      if (this.modelResult) {
        navigator.clipboard.writeText(this.modelResult.roomNumber.toString())
          .then(() => {
            alert('房间号已复制到剪贴板')
          })
          .catch(err => {
            console.error('复制失败:', err)
            alert('复制失败，请手动复制')
          })
      }
    },
    
    viewModel() {
      // 这里可以跳转到模型查看页面或在当前页面加载模型
      alert('模型查看功能开发中...')
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    
    formatDateTime(dateTime) {
      if (!dateTime) return ''
      const date = new Date(dateTime)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.text-to-3d-container {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  color: #495057;
}

.back-button {
  padding: 0.5rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s ease;
}

.back-button:hover {
  background: #5a6268;
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.input-section {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.form-group textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  font-family: inherit;
}

.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.action-section {
  display: flex;
  justify-content: center;
}

.generate-button {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.generate-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.generate-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-section {
  text-align: center;
  padding: 2rem;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border-left-color: #667eea;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result-section {
  text-align: center;
}

.success-message {
  margin-bottom: 2rem;
}

.success-message h2 {
  color: #4CAF50;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.model-info {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  text-align: left;
}

.info-item {
  margin-bottom: 0.8rem;
  color: #495057;
}

.info-item:last-child {
  margin-bottom: 0;
}

.room-info {
  background: #e3f2fd;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #2196F3;
}

.room-info h3 {
  color: #1565C0;
  margin-bottom: 1rem;
}

.room-number {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.room-number .label {
  margin-right: 1rem;
  font-weight: 600;
  color: #1565C0;
}

.room-number .value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2196F3;
}

.room-description {
  color: #455A64;
  margin-bottom: 1.5rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.copy-button, .view-button {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.copy-button {
  background: #4CAF50;
  color: white;
}

.copy-button:hover {
  background: #43A047;
  transform: translateY(-2px);
}

.view-button {
  background: #2196F3;
  color: white;
}

.view-button:hover {
  background: #1976D2;
  transform: translateY(-2px);
}

.error-section {
  text-align: center;
  padding: 2rem;
}

.error-message h2 {
  color: #f44336;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.error-message p {
  color: #6D4C41;
}
</style>