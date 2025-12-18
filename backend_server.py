from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import time
import uuid
import threading

app = Flask(__name__)
CORS(app)

# 设置跨域响应头
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# 配置静态文件目录
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 模拟数据库存储
model_tasks = {}

def simulate_model_generation(job_id, prompt):
    """模拟模型生成过程"""
    time.sleep(5)  # 模拟5秒的生成时间
    
    # 创建模型文件夹
    model_dir = os.path.join(UPLOAD_FOLDER, job_id)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    # 创建模拟文件
    model_file = os.path.join(model_dir, f"{job_id}.glb")
    preview_file = os.path.join(model_dir, "preview.jpg")
    
    with open(model_file, 'w') as f:
        f.write("dummy glb file content")
    with open(preview_file, 'w') as f:
        f.write("dummy jpg file content")
    
    # 更新任务状态
    model_tasks[job_id].update({
        "status": 3,  # 3: 生成完成
        "target3durl": f"http://localhost:8082/uploads/{job_id}/{job_id}.glb",
        "targetimgurl": f"http://localhost:8082/uploads/{job_id}/preview.jpg",
        "completed_at": time.time()
    })

@app.route('/')
def hello_world():
    return 'Backend server is running!'

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/models/generate/text', methods=['POST'])
def text_to_generation3d():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' parameter"}), 400
        
        prompt = data['text'].strip()
        if not prompt:
            return jsonify({"error": "Text parameter cannot be empty"}), 400
        
        # 生成jobId
        job_id = str(uuid.uuid4())
        
        # 初始化任务
        model_tasks[job_id] = {
            "jobId": job_id,
            "prompt": prompt,
            "status": 1,  # 1: 生成中
            "created_at": time.time()
        }
        
        # 在后台线程中模拟生成过程
        thread = threading.Thread(target=simulate_model_generation, args=(job_id, prompt))
        thread.daemon = True
        thread.start()
        
        return jsonify({"jobId": job_id})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/models/generate/getstatus', methods=['POST'])
def getstatus():
    try:
        data = request.get_json()
        if not data or 'jobId' not in data:
            return jsonify({"error": "Missing 'jobId' parameter"}), 400
        
        job_id = data['jobId']
        
        if job_id not in model_tasks:
            return jsonify({"error": "Job not found"}), 404
        
        task = model_tasks[job_id]
        
        response = {
            "jobId": task["jobId"],
            "prompt": task["prompt"],
            "status": task["status"]
        }
        
        # 如果任务完成，添加文件URL
        if task["status"] == 3:
            response["target3durl"] = task["target3durl"]
            response["targetimgurl"] = task["targetimgurl"]
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("启动后端服务...")
    print("API端点:")
    print("- POST /api/models/generate/text - 文本生成3D模型")
    print("- POST /api/models/generate/getstatus - 获取模型状态")
    print("- GET /uploads/<filename> - 静态文件服务")
    app.run(host='0.0.0.0', port=8082, debug=True)