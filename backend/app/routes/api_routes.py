"""
API 路由定義
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime
import base64
import logging
import traceback
from ..models.retriever import get_retriever
from ..models import memory_manager
import uuid

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
        # session_id: optional. If provided, server will keep short-term memory
        # for this session. If not provided, server will generate one and return
        # it in the response so the client can reuse it for subsequent calls.
        session_id = data.get('session_id')

        if not question:
            return jsonify({'error': '問題不能為空'}), 400

        if not screenshot:
            return jsonify({'error': '截圖不能為空'}), 400
        
        # 記錄請求
        logger.info(f'接收問題: {question[:50]}... 使用模型: {model}')
        # 記錄是否收到截圖與簡短預覽（避免在日誌中打出完整 base64）
        try:
            if screenshot:
                preview = (screenshot[:80] + '...') if len(screenshot) > 80 else screenshot
                logger.info(f'[api] 收到 screenshot 長度={len(screenshot)} preview={preview}')
            else:
                logger.info('[api] 未收到 screenshot')
        except Exception as e:
            logger.warning(f'[api] 無法記錄 screenshot 資訊: {e}')
        
        # 🎯 使用輕量級檢索器取得相關知識片段
        retriever = get_retriever()
        relevant_chunks = retriever.retrieve(question, max_chunks=2)
        context = "\n\n".join(relevant_chunks) if relevant_chunks else ""

        # 使用 LangChain ConversationBufferMemory 管理短期會話記憶
        # 若 client 未傳 session_id，建立一個並回傳給 client
        if not session_id:
            session_id = str(uuid.uuid4())

        memory = memory_manager.manager.get_memory(session_id)
        # load memory history (string)
        try:
            logger.info(f"[memory] loading memory for session={session_id}")
            mem_vars = memory.load_memory_variables({})
            history = mem_vars.get('history', '') if mem_vars else ''
            logger.info(f"[memory] loaded history length={len(history) if history else 0} for session={session_id}")
        except Exception as me:
            logger.warning(f"[memory] failed to load memory for session={session_id}: {me}")
            mem_vars = {}
            history = ''

        parts = []
        if history:
            parts.append(f"Conversation history:\n{history}")
        if context:
            parts.append(f"Reference materials:\n{context}")
        parts.append(f"User question:\n{question}")

        enhanced_question = "\n\n".join(parts)

        # 調用 AI 模型（使用增強後的問題）
        response_text = g.ai_model.process_query(
            question=enhanced_question,
            screenshot=screenshot,
            model_type=model
        )

        # 將本輪對話存入 memory（user input + assistant output）
        try:
            logger.info(f"[memory] saving conversation for session={session_id} (question_len={len(question)})")
            memory.save_context({"input": question}, {"output": response_text})
            logger.info(f"[memory] saved conversation for session={session_id}")
        except Exception as save_err:
            logger.warning(f'無法將對話保存至記憶: {save_err}')
        
        return jsonify({
            'status': 'success',
            'response': response_text,
            'model': model,
            'session_id': session_id,
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


@bp.route('/set_model', methods=['POST'])
def set_model():
    """在運行時設置全局預設模型（會更新 server-side 的 default model）。"""
    try:
        data = request.get_json() or {}
        model = data.get('model')
        if not model:
            return jsonify({'error': 'model required'}), 400

        # 驗證模型是否在可用清單中
        available = g.ai_model.get_available_models()
        if model not in available:
            return jsonify({'error': 'model not recognized', 'available': list(available.keys())}), 400

        # 設置全局預設模型
        g.ai_model.ollama_model = model
        logger.info(f'全局預設模型已更新為: {model}')
        return jsonify({'status': 'success', 'model': model}), 200
    except Exception as e:
        logger.error(f'設置模型失敗: {e}')
        return jsonify({'error': '設置模型失敗'}), 500

@bp.route('/test', methods=['GET'])
def test_endpoint():
    """測試端點"""
    return jsonify({
        'status': 'success',
        'message': '校務系統 AI 助手後端正在運行',
        'timestamp': datetime.now().isoformat()
    }), 200


@bp.route('/clear_memory', methods=['POST'])
def clear_memory():
    """清除指定 session 的短期記憶（若提供）。"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id required'}), 400

        logger.info(f"[memory] clear_memory request for session={session_id}")
        removed = memory_manager.manager.clear_memory(session_id)
        logger.info(f"[memory] clear_memory result for session={session_id} removed={removed}")
        return jsonify({'status': 'success', 'removed': removed}), 200
    except Exception as e:
        logger.error(f'清除記憶失敗: {e}')
        return jsonify({'error': '清除記憶失敗'}), 500
