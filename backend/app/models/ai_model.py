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
import time

logger = logging.getLogger(__name__)

class AIModel:
    """AI 模型管理器"""
    
    def __init__(self):
        """初始化 AI 模型"""
        # Ollama 伺服器位址（強制使用遠端 server；預設為 PrimeHub URL）
        # 若要改成其他遠端 Ollama，請設定環境變數 OLLAMA_URL
        self.ollama_url = os.getenv('OLLAMA_URL', 'https://primehub.aic.ncku.edu.tw/console/apps/ollama-0-13-0-i1oyy')
        # 運行時預設模型（server-side default）
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        # 強制啟用遠端 Ollama 路徑（不保留本地 serve 分支）
        self.ollama_enabled = True

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
            model_type: 使用的模型名稱 (llava/qwen2.5vl/qwen/gpt/claude)
        
        Returns:
            AI 的回應文本
        """
        logger.info(f'處理查詢，模型: {model_type}')
        
        try:
            # 解碼截圖
            image_data = base64.b64decode(screenshot.split(',')[1] if ',' in screenshot else screenshot)
            
            # 根據模型類型調用相應的方法
            # 僅允許使用遠端提供的五個模型（由 server 端管理）
            if model_type in ['llava', 'llama3.2', 'qwen2.5vl', 'qwen3-vl', 'gemma3', 'llama4']:
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
        使用遠端 Ollama 服務回應。

        注意：本系統僅會向遠端 Ollama 伺服器發出請求（不再支援本地 ollama serve），
        並且後端僅公開配置的模型選項給前端使用。
        """
        try:
            if not self.ollama_enabled:
                return "Ollama 未配置或無法連接"
            
            # 使用指定的模型或運行時伺服器預設模型
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
            
            # 檢查是否是視覺模型（需要圖片）
            # 我們將以下模型視為視覺+語言（Vision+Language）模型
            is_vision_model = model.lower() in ['llava', 'qwen2.5vl', 'qwen3-vl', 'gemma3', 'llama3.2', 'llama4']
            
            if is_vision_model:
                # 視覺模型：發送圖片和文字
                start = time.time()
                # log debug: whether image is present and its approximate size
                try:
                    logger.info(f'Ollama request -> model={model} is_vision={is_vision_model} images_len={len(image_base64) if image_base64 else 0}')
                except Exception:
                    pass

                # 當為視覺模型時，強化 prompt，明確指示模型使用 images 欄位並描述圖片內容
                vision_instruction = (
                    "注意：此請求包含一張截圖（已放在 images 欄位）。\n"
                    "請優先使用圖片資訊回答，逐項描述圖片中可見的內容（例如文字、按鈕、標題、圖示、位置關係等），"
                    "並只在無法從圖片判斷時才使用文字上下文。\n"
                )

                payload = {
                    'model': model,
                    'prompt': f"{vision_instruction}{system_prompt}\n\n用戶問題: {question}",
                    'stream': False,
                    'images': [image_base64]
                }
                logger.debug(f'Ollama payload keys: {list(payload.keys())}')

                response = requests.post(
                    f'{self.ollama_url}/api/generate',
                    json=payload,
                    timeout=120  # 給 AI 足夠的時間思考
                )
                elapsed = time.time() - start
            else:
                # 文本模型（如 Qwen2.5）：只發送文字
                start = time.time()
                response = requests.post(
                    f'{self.ollama_url}/api/generate',
                    json={
                        'model': model,
                        'prompt': f"{system_prompt}\n\n用戶問題: {question}",
                        'stream': False
                    },
                    timeout=120  # 給 AI 足夠的時間思考
                )
                elapsed = time.time() - start

            # 處理回應；若 model not found (404)，嘗試用不含 tag 的 model 名稱重試（例如 qwen2.5vl:7b -> qwen2.5vl）
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()
                logger.info('✅ Ollama 回應成功')
                # 記錄 LLM 回應耗時
                try:
                    logger.info(f'LLM 回應時間: {elapsed:.2f}s')
                except Exception:
                    pass
                return answer if answer else "無法生成回應，請重試"

            # 若為 404 且錯誤訊息指出 model not found，嘗試 fallback
            try:
                body = response.json()
            except Exception:
                body = None

            if response.status_code == 404 and body and isinstance(body, dict) and 'error' in body and 'model' in str(body.get('error')).lower() and ':' in model:
                fallback_model = model.split(':')[0]
                logger.warning(f"Ollama 回傳 model not found，嘗試 fallback model={fallback_model}")

                # 再次發送請求，但使用 fallback_model
                if is_vision_model:
                    start2 = time.time()
                    response2 = requests.post(
                        f'{self.ollama_url}/api/generate',
                        json={
                            'model': fallback_model,
                            'prompt': f"{system_prompt}\n\n用戶問題: {question}",
                            'stream': False,
                            'images': [image_base64]
                        },
                        timeout=120
                    )
                    elapsed2 = time.time() - start2
                else:
                    start2 = time.time()
                    response2 = requests.post(
                        f'{self.ollama_url}/api/generate',
                        json={
                            'model': fallback_model,
                            'prompt': f"{system_prompt}\n\n用戶問題: {question}",
                            'stream': False
                        },
                        timeout=120
                    )
                    elapsed2 = time.time() - start2

                if response2.status_code == 200:
                    result = response2.json()
                    answer = result.get('response', '').strip()
                    logger.info(f'✅ Ollama 回應成功 (fallback model={fallback_model})')
                    # 記錄 fallback LLM 回應耗時
                    try:
                        logger.info(f'LLM 回應時間 (fallback): {elapsed2:.2f}s')
                    except Exception:
                        pass
                    return answer if answer else "無法生成回應，請重試"
                else:
                    logger.error(f'Ollama API (fallback) 錯誤: {response2.status_code} - {response2.text}')
                    return f"Ollama 回應失敗 ({response2.status_code}): {response2.text[:200]}"

            # 其他非 200 錯誤
            logger.error(f'Ollama API 錯誤: {response.status_code} - {response.text}')
            return f"Ollama 回應失敗 ({response.status_code}): {response.text[:200]}"
                
        except requests.exceptions.Timeout:
            logger.error('Ollama 請求超時')
            return "Ollama 處理超時，請嘗試更簡單的圖片或問題"
        except requests.exceptions.ConnectionError:
                logger.error(f'無法連接到 Ollama: {self.ollama_url}')
                return f"無法連接到遠端 Ollama 服務 ({self.ollama_url})。請確認該遠端服務可用並且 URL 正確。"
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
        # 只回傳遠端伺服器上允許的五個模型（與擴展一致）
        models = {
            'qwen2.5vl': {
                'name': 'Qwen 2.5VL (遠端)',
                'status': 'available',
                'description': 'Qwen 2.5VL 視覺/文本模型（遠端 Ollama）',
                'location': 'remote',
                'url': self.ollama_url
            },
            'llava': {
                'name': 'LLaVA (遠端)',
                'status': 'available',
                'description': '視覺語言模型（遠端 Ollama）',
                'location': 'remote',
                'url': self.ollama_url
            },
            'llama3.2': {
                'name': 'LLaMA 3.2 (遠端)',
                'status': 'available',
                'description': '文本生成模型（遠端 Ollama）',
                'location': 'remote',
                'url': self.ollama_url
            },
            'qwen3-vl': {
                'name': 'Qwen 3 VL (遠端)',
                'status': 'available',
                'description': 'Qwen 第三代視覺語言模型（遠端 Ollama）',
                'location': 'remote',
                'url': self.ollama_url
            },
            'gemma3': {
                'name': 'Gemma 3 (遠端)',
                'status': 'available',
                'description': 'Gemma 系列模型（遠端 Ollama）',
                'location': 'remote',
                'url': self.ollama_url
            },
            'llama4': {
                'name': 'LLaMA 4 (遠端)',
                'status': 'available',
                'description': 'LLaMA 4 - 視覺+語言模型（遠端 Ollama）',
                'location': 'remote',
                'url': self.ollama_url
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
