"""
AI 模型集成
支持多個模型:
- Ollama (本地模型 - 推薦! 無需 API 密鑰)
- Qwen、GPT-4V 和 Claude 3 Vision (雲端 API)
"""

import logging
import os
import base64
from io import BytesIO
from PIL import Image
import json
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class AIModel:
    """AI 模型管理器"""
    
    def __init__(self):
        """初始化 AI 模型"""
        # Ollama 伺服器位址 (預設改為遠端 PrimeHub URL)
        # 若需改回本地或其他部署，請設定環境變數 OLLAMA_URL
        self.ollama_url = os.getenv('OLLAMA_URL', 'https://primehub.aic.ncku.edu.tw/console/apps/ollama-0-13-0-i1oyy')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llava')  # 推薦使用 llava 視覺模型
        self.ollama_enabled = os.getenv('OLLAMA_ENABLED', 'true').lower() == 'true'
        
        # 雲端 API 配置
        self.qwen_api_key = os.getenv('QWEN_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        
        # 初始化各個模型的客戶端
        self._init_clients()
        
        # 檢查 Ollama 連接
        self._check_ollama_connection()
    
    def _check_ollama_connection(self):
        """檢查 Ollama 是否可用"""
        try:
            if self.ollama_enabled:
                response = requests.get(f'{self.ollama_url}/api/tags', timeout=2)
                if response.status_code == 200:
                    logger.info(f'✅ Ollama 連接成功: {self.ollama_url}')
                    available_models = response.json().get('models', [])
                    logger.info(f'可用模型: {[m["name"] for m in available_models]}')
                else:
                    logger.warning(f'⚠️ Ollama 返回錯誤: {response.status_code}')
                    self.ollama_enabled = False
        except Exception as e:
            logger.warning(f'⚠️ 無法連接到 Ollama ({self.ollama_url}): {str(e)}')
            self.ollama_enabled = False
    
    def _init_clients(self):
        """初始化 API 客戶端"""
        try:
            if self.qwen_api_key:
                from dashscope import MultiModalConversation
                self.qwen_client = MultiModalConversation
                logger.info('✅ Qwen 客戶端已初始化')
            
            if self.openai_api_key:
                import openai
                openai.api_key = self.openai_api_key
                self.openai_client = openai
                logger.info('✅ OpenAI 客戶端已初始化')
            
            if self.claude_api_key:
                import anthropic
                self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
                logger.info('✅ Claude 客戶端已初始化')
        except Exception as e:
            logger.warning(f'初始化 API 客戶端時出現警告: {str(e)}')
    
    def process_query(self, question: str, screenshot: str, model_type: str = 'llava') -> str:
        """
        處理使用者查詢
        
        Args:
            question: 使用者的問題
            screenshot: base64 編碼的截圖
            model_type: 使用的模型名稱 (llava/qwen2.5/qwen/gpt/claude)
        
        Returns:
            AI 的回應文本
        """
        logger.info(f'處理查詢，模型: {model_type}')
        
        try:
            # 解碼截圖
            image_data = base64.b64decode(screenshot.split(',')[1] if ',' in screenshot else screenshot)
            
            # 根據模型類型調用相應的方法
            if model_type in ['llava', 'llava:34b', 'bakllava', 'qwen2.5', 'qwen:7b', 'qwen:7b-vision', 'qwen2.5vl:7b', 'qwen2.5-vl', 'qwen-vl', 'qwen-vl-chat']:
                # 所有本地 Ollama 模型
                return self._query_ollama(question, image_data, model_type)
            elif model_type == 'gpt':
                return self._query_gpt(question, image_data)
            elif model_type == 'claude':
                return self._query_claude(question, image_data)
            else:
                # 默認使用 Ollama 中的 LLaVA
                if self.ollama_enabled:
                    return self._query_ollama(question, image_data, 'llava')
                else:
                    return "無可用的模型，請檢查配置"
                
        except Exception as e:
            logger.error(f'處理查詢失敗: {str(e)}')
            raise
    
    def _query_ollama(self, question: str, image_data: bytes, model_name: str = None) -> str:
        """
        使用 Ollama 本地模型回應 (推薦!)
        
        支持的模型:
        - llava - 視覺語言模型 (推薦用於圖片分析)
        - qwen2.5 - Qwen 開源版本 (多功能)
        - qwen:7b - Qwen 7B 版本
        - bakllava - 輕量視覺模型
        
        無需 API 密鑰，完全本地運行!
        """
        try:
            if not self.ollama_enabled:
                return "Ollama 未配置或無法連接"
            
            # 使用指定的模型或默認模型
            model = model_name or self.ollama_model
            
            # 編碼圖片為 base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 構建系統提示
            system_prompt = """你是一個校務系統智能助手。你的職責是幫助成功大學的師生解決校務系統相關的問題。

你的回應應該：
1. 簡潔明了，直接回答問題
2. 基於提供的截圖和文本內容
3. 包含具體的步驟指引（如果適用）
4. 用繁體中文回應
5. 如果無法從截圖中獲取足夠信息，請說明

校務系統常見功能：
- 選課系統
- 成績查詢
- 課程表查詢
- 教室預約
- 繳費系統
- 學位查詢"""
            
            # 調用 Ollama API
            logger.info(f'調用 Ollama 模型: {model} ({self.ollama_url})')
            
            # 檢查是否是視覺模型（需要圖片）還是文本模型
            is_vision_model = model.lower() in ['llava', 'bakllava', 'qwen:7b-vision', 'qwen2.5vl:7b', 'qwen2.5-vl', 'qwen-vl', 'qwen-vl-chat']
            
            if is_vision_model:
                # 視覺模型：發送圖片和文字
                response = requests.post(
                    f'{self.ollama_url}/api/generate',
                    json={
                        'model': model,
                        'prompt': f"{system_prompt}\n\n用戶問題: {question}",
                        'stream': False,
                        'images': [image_base64]  # 發送 base64 編碼的圖片
                    },
                    timeout=120  # 給 AI 足夠的時間思考
                )
            else:
                # 文本模型（如 Qwen2.5）：只發送文字
                response = requests.post(
                    f'{self.ollama_url}/api/generate',
                    json={
                        'model': model,
                        'prompt': f"{system_prompt}\n\n用戶問題: {question}",
                        'stream': False
                    },
                    timeout=120  # 給 AI 足夠的時間思考
                )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()
                logger.info('✅ Ollama 回應成功')
                return answer if answer else "無法生成回應，請重試"
            else:
                logger.error(f'Ollama API 錯誤: {response.status_code} - {response.text}')
                return f"Ollama 回應失敗 ({response.status_code}): {response.text[:200]}"
                
        except requests.exceptions.Timeout:
            logger.error('Ollama 請求超時')
            return "Ollama 處理超時，請嘗試更簡單的圖片或問題"
        except requests.exceptions.ConnectionError:
            logger.error(f'無法連接到 Ollama: {self.ollama_url}')
            return f"無法連接到 Ollama 服務 ({self.ollama_url})\n\n💡 提示: 確保 Ollama 正在運行:\n  ollama serve"
        except Exception as e:
            logger.error(f'Ollama 查詢失敗: {str(e)}')
            return f"Ollama 查詢出錯: {str(e)}"
    
    def _query_qwen(self, question: str, image_data: bytes) -> str:
        """使用 Qwen 2.5 模型回應"""
        try:
            if not self.qwen_api_key:
                return "Qwen API 密鑰未配置"
            
            from dashscope import MultiModalConversation
            import base64
            
            # 編碼圖片
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 構建系統提示
            system_prompt = """你是一個校務系統智能助手。你的職責是幫助成功大學的師生解決校務系統相關的問題。
            
你的回應應該：
1. 簡潔明了，直接回答問題
2. 基於提供的截圖和文本內容
3. 包含具體的步驟指引（如果適用）
4. 用繁體中文回應
5. 如果無法從截圖中獲取足夠信息，請說明

校務系統常見功能：
- 選課系統
- 成績查詢
- 課程表查詢
- 教室預約
- 繳費系統
- 學位查詢"""
            
            # 準備消息
            message = {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': f"系統截圖的問題：{question}"},
                    {'type': 'image', 'image': f'data:image/jpeg;base64,{image_base64}'}
                ]
            }
            
            # 調用 Qwen API
            response = MultiModalConversation.call(
                model='qwen-vl-max',
                messages=[message],
                system=system_prompt
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content[0].text
            else:
                logger.error(f'Qwen API 錯誤: {response}')
                return f"Qwen 回應失敗: {response.message}"
                
        except ImportError:
            logger.error('dashscope 未安裝')
            return "Qwen SDK 未安裝，請安裝 dashscope"
        except Exception as e:
            logger.error(f'Qwen 查詢失敗: {str(e)}')
            return f"Qwen 查詢出錯: {str(e)}"
    
    def _query_gpt(self, question: str, image_data: bytes) -> str:
        """使用 GPT-4V 模型回應"""
        try:
            if not self.openai_api_key:
                return "OpenAI API 密鑰未配置"
            
            import openai
            import base64
            
            # 編碼圖片
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一個校務系統智能助手。幫助成功大學的師生解決校務系統相關問題。
回應應簡潔、實用，包含具體步驟（如需要）。使用繁體中文回應。"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"根據這個校務系統截圖，請回答：{question}"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1024
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f'GPT 查詢失敗: {str(e)}')
            return f"GPT 查詢出錯: {str(e)}"
    
    def _query_claude(self, question: str, image_data: bytes) -> str:
        """使用 Claude 3 Vision 模型回應"""
        try:
            if not self.claude_api_key:
                return "Claude API 密鑰未配置"
            
            import base64
            
            # 編碼圖片
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                system="""你是一個校務系統智能助手。幫助成功大學的師生解決校務系統相關問題。
回應應簡潔、實用，包含具體步驟（如需要）。使用繁體中文回應。""",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": f"根據這個校務系統截圖，請回答：{question}"
                            }
                        ]
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f'Claude 查詢失敗: {str(e)}')
            return f"Claude 查詢出錯: {str(e)}"
    
    def get_available_models(self) -> dict:
        """獲取可用的模型列表"""
        models = {
            'llava': {
                'name': '🖥️ LLaVA (本地 Ollama)',
                'status': 'available' if self.ollama_enabled else 'unconfigured',
                'description': '視覺模型 - 適合圖片分析',
                'location': 'local',
                'url': self.ollama_url if self.ollama_enabled else '未配置'
            },
            'qwen2.5': {
                'name': '🖥️ Qwen 2.5 (本地 Ollama)',
                'status': 'available' if self.ollama_enabled else 'unconfigured',
                'description': '多功能模型 - 適合文本分析',
                'location': 'local',
                'url': self.ollama_url if self.ollama_enabled else '未配置'
            },
            'bakllava': {
                'name': '🖥️ BakLLaVA (本地 Ollama)',
                'status': 'available' if self.ollama_enabled else 'unconfigured',
                'description': '輕量視覺模型 - 快速推理',
                'location': 'local',
                'url': self.ollama_url if self.ollama_enabled else '未配置'
            },
            'gpt': {
                'name': '☁️ GPT-4V (雲端)',
                'status': 'available' if self.openai_api_key else 'unconfigured',
                'description': 'OpenAI - 需要 API 密鑰',
                'location': 'cloud'
            },
            'claude': {
                'name': '☁️ Claude 3 Vision (雲端)',
                'status': 'available' if self.claude_api_key else 'unconfigured',
                'description': 'Anthropic - 需要 API 密鑰',
                'location': 'cloud'
            }
        }
        return models
    
    @staticmethod
    def validate_image(image_data: bytes) -> bool:
        """驗證圖片數據"""
        try:
            img = Image.open(BytesIO(image_data))
            return True
        except Exception as e:
            logger.error(f'圖片驗證失敗: {str(e)}')
            return False
