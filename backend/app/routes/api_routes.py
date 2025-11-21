"""
API 路由定義
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime
import base64
import logging
import traceback
from ..models.retriever import get_retriever

bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@bp.route('/ask', methods=['POST'])
def ask_ai():
    """
    主要端點：接收螢幕截圖和問題，返回 AI 回應
    
    請求數據:
    {
        "question": "使用者的問題",
        "screenshot": "base64 編碼的圖片",
        "model": "ai 模型名稱 (qwen/gpt/claude)",
        "timestamp": "ISO 格式時間戳"
    }
    """
    try:
        data = request.get_json()
        
        # 驗證必需的欄位
        if not data:
            return jsonify({'error': '無效的請求體'}), 400
        
        question = data.get('question', '').strip()
        screenshot = data.get('screenshot')
        model = data.get('model', 'llava')
        
        if not question:
            return jsonify({'error': '問題不能為空'}), 400
        
        if not screenshot:
            return jsonify({'error': '截圖不能為空'}), 400
        
        # 記錄請求
        logger.info(f'接收問題: {question[:50]}... 使用模型: {model}')
        
        # 🎯 使用輕量級檢索器增強 prompt
        retriever = get_retriever()
        enhanced_question = retriever.get_context_prompt(question)
        
        # 調用 AI 模型（使用增強後的問題）
        response_text = g.ai_model.process_query(
            question=enhanced_question,
            screenshot=screenshot,
            model_type=model
        )
        
        return jsonify({
            'status': 'success',
            'response': response_text,
            'model': model,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f'處理請求時發生錯誤: {str(e)}')
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '處理請求失敗',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Chrome 擴展使用的端點（別名）
    與 /ask 相同的功能
    """
    return ask_ai()

@bp.route('/models', methods=['GET'])
def get_available_models():
    """獲取可用的 AI 模型列表"""
    try:
        models = g.ai_model.get_available_models()
        return jsonify({
            'status': 'success',
            'models': models,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f'獲取模型列表失敗: {str(e)}')
        return jsonify({
            'error': '獲取模型列表失敗',
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/test', methods=['GET'])
def test_endpoint():
    """測試端點"""
    return jsonify({
        'status': 'success',
        'message': '校務系統 AI 助手後端正在運行',
        'timestamp': datetime.now().isoformat()
    }), 200
