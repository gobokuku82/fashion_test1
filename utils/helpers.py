"""
헬퍼 함수 모듈

공통적으로 사용되는 유틸리티 함수들을 제공합니다.
"""

import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
import re

def generate_session_id() -> str:
    """세션 ID 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"session_{timestamp}"

def clean_text(text: str) -> str:
    """텍스트 정리"""
    if not text:
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 특수 문자 정리
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """키워드 추출 (간단한 구현)"""
    if not text:
        return []
    
    # 불용어 제거 및 키워드 추출
    stopwords = {'의', '가', '이', '은', '는', '을', '를', '에', '서', '와', '과', '도', '만', '라', '로'}
    words = text.split()
    keywords = [word for word in words if len(word) > 1 and word not in stopwords]
    
    # 빈도수 기반 정렬
    from collections import Counter
    word_counts = Counter(keywords)
    
    return [word for word, count in word_counts.most_common(max_keywords)]

def format_currency(amount: float, currency: str = "USD") -> str:
    """통화 포맷팅"""
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "KRW":
        return f"₩{amount:,.0f}"
    else:
        return f"{amount:.2f} {currency}"

def safe_json_loads(text: str, default: Any = None) -> Any:
    """안전한 JSON 파싱"""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """텍스트 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def validate_api_key(api_key: str) -> bool:
    """API 키 유효성 검사"""
    if not api_key:
        return False
    
    # OpenAI API 키 패턴 확인
    if api_key.startswith('sk-') and len(api_key) > 20:
        return True
    
    return False 