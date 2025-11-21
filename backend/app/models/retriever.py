"""
輕量級知識庫檢索模組
使用關鍵字匹配找出相關文檔片段
"""
import json
import os
from pathlib import Path

class LightweightRetriever:
    def __init__(self, knowledge_base_path=None):
        """初始化檢索器"""
        if knowledge_base_path is None:
            # 預設路徑：app/knowledge/knowledge_base.json
            current_dir = Path(__file__).parent.parent  # 從 models/ 回到 app/
            knowledge_base_path = current_dir / "knowledge" / "knowledge_base.json"
        
        self.knowledge_base_path = knowledge_base_path
        self.chunks = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """載入知識庫"""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.chunks = data.get('chunks', [])
            print(f"[Retriever] 已載入 {len(self.chunks)} 個知識片段")
        except FileNotFoundError:
            print(f"[Retriever] 警告: 找不到知識庫檔案 {self.knowledge_base_path}")
            self.chunks = []
        except Exception as e:
            print(f"[Retriever] 錯誤: 載入知識庫失敗 - {e}")
            self.chunks = []
    
    def retrieve(self, question, max_chunks=2):
        """
        根據問題檢索相關片段
        
        Args:
            question: 用戶問題
            max_chunks: 最多返回幾個片段（預設2個，避免 token 過多）
        
        Returns:
            相關文檔片段的列表
        """
        if not self.chunks:
            return []
        
        # 將問題轉為小寫以便匹配
        question_lower = question.lower()
        
        # 計算每個片段的相關分數
        scored_chunks = []
        for chunk in self.chunks:
            score = 0
            keywords = chunk.get('keywords', [])
            
            # 計算有多少關鍵字出現在問題中
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    score += 1
            
            if score > 0:
                scored_chunks.append({
                    'chunk': chunk,
                    'score': score
                })
        
        # 按分數排序（分數高的在前）
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # 返回前 max_chunks 個片段
        top_chunks = scored_chunks[:max_chunks]
        
        # 記錄檢索結果
        if top_chunks:
            chunk_ids = [c['chunk']['id'] for c in top_chunks]
            print(f"[Retriever] 問題: '{question[:30]}...' 匹配到: {chunk_ids}")
        else:
            print(f"[Retriever] 問題: '{question[:30]}...' 沒有匹配到相關知識")
        
        return [c['chunk']['content'] for c in top_chunks]
    
    def get_context_prompt(self, question):
        """
        生成帶有參考資料的完整 prompt
        
        Args:
            question: 用戶問題
        
        Returns:
            完整的 prompt 字串
        """
        # 檢索相關片段
        relevant_chunks = self.retrieve(question, max_chunks=2)
        
        if not relevant_chunks:
            # 沒有相關資料，返回基礎 prompt
            base_prompt = f"""請根據截圖回答以下問題：

{question}

回答指引：
- 若問題是關於使用介面（可從畫面直接看出），請直接說明
- 若缺乏實際資料來源，請直接說「我不知道」或「無法從截圖中確定」
- 請用繁體中文回答"""
            return base_prompt
        
        # 有相關資料，組合完整 prompt
        context = "\n\n".join(relevant_chunks)
        
        full_prompt = f"""請根據以下參考資料和截圖回答問題：

【參考資料】
{context}

【用戶問題】
{question}

回答指引：
- 若問題在參考資料中有明確說明，請使用參考資料的答案回答
- 若問題是關於使用介面（可從截圖直接看出），請直接說明介面內容
- 若參考資料和截圖都無法回答問題，請直接說「我不知道」或「參考資料中沒有相關說明」
- 請用繁體中文回答，語氣親切專業"""
        
        return full_prompt


# 單例模式：全域共享一個檢索器
_retriever_instance = None

def get_retriever():
    """獲取全域檢索器實例"""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = LightweightRetriever()
    return _retriever_instance
