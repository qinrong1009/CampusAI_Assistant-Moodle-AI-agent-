"""
數據模型定義
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Query:
    """查詢模型"""
    question: str
    screenshot: str
    model: str
    timestamp: datetime
    user_id: Optional[str] = None
    
    def to_dict(self):
        return {
            'question': self.question,
            'screenshot': self.screenshot[:50] + '...',  # 只保留前 50 個字符用於日誌
            'model': self.model,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class Response:
    """回應模型"""
    status: str
    response: str
    model: str
    timestamp: datetime
    processing_time: Optional[float] = None
    
    def to_dict(self):
        return {
            'status': self.status,
            'response': self.response,
            'model': self.model,
            'timestamp': self.timestamp.isoformat(),
            'processing_time': self.processing_time
        }
