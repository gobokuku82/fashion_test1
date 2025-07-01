"""
Global settings configuration for Fashion AI Automation System
"""

import os
from typing import Optional
from pydantic import BaseSettings
import streamlit as st


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""
    
    # OpenAI API 설정
    openai_api_key: str = ""
    openai_model: str = "gpt-4-1106-preview"
    openai_temperature: float = 0.7
    max_tokens: int = 4000
    
    # Naver API 설정
    naver_client_id: str = ""
    naver_client_secret: str = ""
    
    # OpenSearch 설정
    opensearch_host: str = ""
    opensearch_username: str = ""
    opensearch_password: str = ""
    opensearch_index_prefix: str = "fashion_ai"
    
    # 애플리케이션 설정
    app_env: str = "development"
    log_level: str = "INFO"
    
    # 토큰 추적 설정
    token_tracking_enabled: bool = True
    token_cost_per_1k_input: float = 0.01  # GPT-4 가격
    token_cost_per_1k_output: float = 0.03
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @classmethod
    def from_streamlit_secrets(cls) -> "Settings":
        """Streamlit secrets에서 설정을 로드"""
        try:
            return cls(
                openai_api_key=st.secrets.get("OPENAI_API_KEY", ""),
                naver_client_id=st.secrets.get("NAVER_CLIENT_ID", ""),
                naver_client_secret=st.secrets.get("NAVER_CLIENT_SECRET", ""),
                opensearch_host=st.secrets.get("OPENSEARCH_HOST", ""),
                opensearch_username=st.secrets.get("OPENSEARCH_USERNAME", ""),
                opensearch_password=st.secrets.get("OPENSEARCH_PASSWORD", ""),
            )
        except Exception:
            # Streamlit 환경이 아닐 때는 환경변수에서 로드
            return cls()


# 전역 설정 인스턴스
settings = Settings() 