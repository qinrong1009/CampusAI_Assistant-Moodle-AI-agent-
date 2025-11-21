"""
後端主應用文件
校務系統AI助手 - Flask REST API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

from app.routes import api_routes
from app.models.ai_model import AIModel

# 載入環境變數
load_dotenv()

# 初始化 Flask 應用
app = Flask(__name__)
CORS(app)

# 配置
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

# 日誌設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 AI 模型
ai_model = AIModel()

# 註冊藍圖
app.register_blueprint(api_routes.bp)

# 將 AI 模型添加到應用上下文
@app.before_request
def setup_context():
    from flask import g
    g.ai_model = ai_model

# 健康檢查端點
@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

# 錯誤處理
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': '不良請求',
        'message': str(error),
        'timestamp': datetime.now().isoformat()
    }), 400

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal server error: {error}')
    return jsonify({
        'error': '內部伺服器錯誤',
        'message': '發生未預期的錯誤',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logger.info(f'啟動 Flask 應用，監聽 localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=debug)
