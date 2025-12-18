const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 8082;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// 确保uploads目录存在
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// 存储模型状态的内存数据库
const modelStatus = new Map();

// 生成随机jobId
function generateJobId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// 文本生成3D模型API
app.post('/api/models/generate/text', (req, res) => {
  const { text, format } = req.body;
  
  if (!text) {
    return res.status(400).json({ error: '文本描述不能为空' });
  }
  
  // 生成jobId
  const jobId = generateJobId();
  
  // 初始化模型状态
  modelStatus.set(jobId, {
    jobId,
    status: 1, // 1: 生成中
    text,
    format: format || 'glb',
    createdAt: new Date().toISOString()
  });
  
  // 模拟异步生成过程
  setTimeout(() => {
    // 创建模型文件夹
    const modelDir = path.join(uploadsDir, jobId);
    if (!fs.existsSync(modelDir)) {
      fs.mkdirSync(modelDir, { recursive: true });
    }
    
    // 模拟生成完成
    modelStatus.set(jobId, {
      ...modelStatus.get(jobId),
      status: 3, // 3: 生成完成
      target3durl: `http://localhost:8082/uploads/${jobId}`,
      targetimgurl: `http://localhost:8082/uploads/${jobId}/preview.jpg`,
      completedAt: new Date().toISOString()
    });
    
    // 创建一个空的模型文件（实际应用中这里应该是真实的3D模型文件）
    const modelPath = path.join(modelDir, `${jobId}.glb`);
    fs.writeFileSync(modelPath, Buffer.from('dummy glb file'));
    
    // 创建一个预览图
    const previewPath = path.join(modelDir, 'preview.jpg');
    fs.writeFileSync(previewPath, Buffer.from('dummy jpg file'));
  }, 5000); // 模拟5秒的生成时间
  
  res.json({ jobId });
});

// 获取模型状态API
app.post('/api/models/generate/getstatus', (req, res) => {
  const { jobId } = req.body;
  
  if (!jobId) {
    return res.status(400).json({ error: 'jobId不能为空' });
  }
  
  const status = modelStatus.get(jobId);
  
  if (!status) {
    return res.status(404).json({ error: '未找到该jobId对应的模型' });
  }
  
  res.json(status);
});

// 提供静态文件访问
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// 启动服务器
app.listen(PORT, () => {
  console.log(`后端服务已启动，运行在 http://localhost:${PORT}`);
  console.log('API端点:');
  console.log('- POST /api/models/generate/text - 文本生成3D模型');
  console.log('- POST /api/models/generate/getstatus - 获取模型状态');
});