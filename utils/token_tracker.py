"""
토큰 사용량 추적 모듈
"""

import json
from datetime import datetime, date
from typing import Dict, Any, Optional
from pathlib import Path
import os

class TokenTracker:
    """토큰 사용량 추적 클래스"""
    
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
    }
    
    def __init__(self):
        self.usage_data = {
            "daily_usage": {},
            "function_usage": {
                "data_collection": {"tokens": 0, "cost": 0.0},
                "trend_analysis": {"tokens": 0, "cost": 0.0},
                "sentiment_analysis": {"tokens": 0, "cost": 0.0},
                "content_generation": {"tokens": 0, "cost": 0.0},
                "human_feedback": {"tokens": 0, "cost": 0.0}
            },
            "total_usage": {"tokens": 0, "cost": 0.0}
        }
    
    def track_usage(self, model: str, input_tokens: int, output_tokens: int, function: str = "other") -> Dict[str, Any]:
        """토큰 사용량 추적"""
        total_tokens = input_tokens + output_tokens
        pricing = self.PRICING.get(model, {"input": 0.001, "output": 0.002})
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000
        
        today = date.today().isoformat()
        
        # 일별 사용량 업데이트
        if today not in self.usage_data["daily_usage"]:
            self.usage_data["daily_usage"][today] = {"tokens": 0, "cost": 0.0}
        
        self.usage_data["daily_usage"][today]["tokens"] += total_tokens
        self.usage_data["daily_usage"][today]["cost"] += cost
        
        # 기능별 사용량 업데이트
        if function in self.usage_data["function_usage"]:
            self.usage_data["function_usage"][function]["tokens"] += total_tokens
            self.usage_data["function_usage"][function]["cost"] += cost
        
        # 총 사용량 업데이트
        self.usage_data["total_usage"]["tokens"] += total_tokens
        self.usage_data["total_usage"]["cost"] += cost
        
        return {
            "model": model,
            "total_tokens": total_tokens,
            "cost": cost,
            "function": function
        }
    
    def get_daily_usage(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """일별 사용량 조회"""
        if target_date is None:
            target_date = date.today().isoformat()
        return self.usage_data["daily_usage"].get(target_date, {"tokens": 0, "cost": 0.0})
    
    def get_function_usage(self) -> Dict[str, Dict[str, Any]]:
        """기능별 사용량 조회"""
        return self.usage_data["function_usage"]
    
    def get_total_usage(self) -> Dict[str, Any]:
        """총 사용량 조회"""
        return self.usage_data["total_usage"] 