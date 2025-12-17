<template>
  <div class="home-container">
    <div class="hero-section">
      <h1>3D模型创建与编辑平台</h1>
      <p>选择一种方式开始你的3D创作之旅</p>
    </div>
    
    <div class="options-grid">
      <!-- 选项1：输入文字描述创建3D模型 -->
      <div class="option-card" @click="navigateTo('text-to-3d')">
        <div class="option-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#667eea" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        </div>
        <h2>文字描述生成</h2>
        <p>输入文字描述，AI将为您创建3D模型</p>
      </div>
      
      <!-- 选项2：上传图像生成3D模型 -->
      <div class="option-card" @click="navigateTo('image-to-3d')">
        <div class="option-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#764ba2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
        </div>
        <h2>图像生成</h2>
        <p>上传图像，AI将为您生成3D模型</p>
      </div>
      
      <!-- 选项3：输入房间号在线修改模型 -->
      <div class="option-card" @click="navigateTo('room-editor')">
        <div class="option-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f093fb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
        </div>
        <h2>在线编辑</h2>
        <p>输入房间号，在线编辑3D模型</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  methods: {
    navigateTo(section) {
      // 触发父组件的导航事件
      this.$emit('select-option', section);
    }
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-section {
  text-align: center;
  margin-bottom: 3rem;
}

.hero-section h1 {
  font-size: 2.5rem;
  color: #495057;
  margin-bottom: 1rem;
}

.hero-section p {
  font-size: 1.2rem;
  color: #6c757d;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
}

.option-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.option-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.option-icon {
  margin-bottom: 1.5rem;
}

.option-card h2 {
  font-size: 1.5rem;
  color: #495057;
  margin-bottom: 1rem;
}

.option-card p {
  color: #6c757d;
  line-height: 1.6;
}
</style>