"""
Fashion AI Automation System - LangGraph State Definition
"""

from typing import List, Dict, Any, Optional, TypedDict
from datetime import datetime
import json


class FashionState(TypedDict):
    """패션 AI 자동화 시스템의 전체 상태를 정의하는 클래스"""
    
    # 기본 정보
    session_id: str
    timestamp: str
    user_request: str
    
    # 데이터 수집 결과
    collected_data: Dict[str, Any]
    naver_shopping_data: List[Dict]
    web_scraping_data: List[Dict]
    social_media_data: List[Dict]
    
    # 분석 결과
    trend_analysis: Optional[Dict[str, Any]]
    sentiment_analysis: Optional[Dict[str, Any]]
    competitor_analysis: Optional[Dict[str, Any]]
    
    # 생성된 콘텐츠
    product_proposal: Optional[str]
    marketing_copy: Optional[str]
    content_suggestions: Optional[List[str]]
    
    # Human-in-the-loop 상태
    human_feedback: Optional[str]
    requires_human_input: bool
    feedback_iteration: int
    
    # 메타데이터
    processing_steps: List[str]
    token_usage: Dict[str, int]
    costs: Dict[str, float]
    errors: List[str]
    
    # 설정
    target_category: str
    target_demographics: Dict[str, Any]
    analysis_period: str


def create_initial_state(
    user_request: str,
    target_category: str = "전체",
    target_demographics: Optional[Dict[str, Any]] = None,
    analysis_period: str = "최근 1개월"
) -> FashionState:
    """초기 상태를 생성하는 헬퍼 함수"""
    
    session_id = f"fashion_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return FashionState(
        # 기본 정보
        session_id=session_id,
        timestamp=datetime.now().isoformat(),
        user_request=user_request,
        
        # 데이터 수집 결과 (초기값)
        collected_data={},
        naver_shopping_data=[],
        web_scraping_data=[],
        social_media_data=[],
        
        # 분석 결과 (초기값)
        trend_analysis=None,
        sentiment_analysis=None,
        competitor_analysis=None,
        
        # 생성된 콘텐츠 (초기값)
        product_proposal=None,
        marketing_copy=None,
        content_suggestions=None,
        
        # Human-in-the-loop 상태
        human_feedback=None,
        requires_human_input=False,
        feedback_iteration=0,
        
        # 메타데이터
        processing_steps=[],
        token_usage={"input_tokens": 0, "output_tokens": 0},
        costs={"total_cost": 0.0},
        errors=[],
        
        # 설정
        target_category=target_category,
        target_demographics=target_demographics or {
            "age_range": "20-40",
            "gender": "전체",
            "income_level": "중간"
        },
        analysis_period=analysis_period
    )


def update_state_step(state: FashionState, step_name: str) -> FashionState:
    """처리 단계를 업데이트하는 헬퍼 함수"""
    state["processing_steps"].append(f"{datetime.now().isoformat()}: {step_name}")
    return state


def add_error_to_state(state: FashionState, error_message: str) -> FashionState:
    """에러를 상태에 추가하는 헬퍼 함수"""
    state["errors"].append(f"{datetime.now().isoformat()}: {error_message}")
    return state


def update_token_usage(
    state: FashionState, 
    input_tokens: int, 
    output_tokens: int,
    cost_per_1k_input: float = 0.01,
    cost_per_1k_output: float = 0.03
) -> FashionState:
    """토큰 사용량과 비용을 업데이트하는 헬퍼 함수"""
    state["token_usage"]["input_tokens"] += input_tokens
    state["token_usage"]["output_tokens"] += output_tokens
    
    # 비용 계산
    input_cost = (input_tokens / 1000) * cost_per_1k_input
    output_cost = (output_tokens / 1000) * cost_per_1k_output
    state["costs"]["total_cost"] += input_cost + output_cost
    
    return state


def serialize_state(state: FashionState) -> str:
    """상태를 JSON 문자열로 직렬화"""
    return json.dumps(state, ensure_ascii=False, indent=2)


def deserialize_state(state_json: str) -> FashionState:
    """JSON 문자열에서 상태를 역직렬화"""
    return json.loads(state_json) 