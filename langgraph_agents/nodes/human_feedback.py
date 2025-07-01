"""
Fashion AI Automation System - Human Feedback Node
"""

import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..state import FashionState, update_state_step, add_error_to_state, update_token_usage
from config.settings import settings


class HumanFeedbackNode:
    """Human-in-the-loop 피드백을 처리하는 LangGraph 노드"""
    
    def __init__(self):
        try:
            # OpenAI 설정
            api_key = settings.openai_api_key
            if not api_key:
                try:
                    import streamlit as st
                    api_key = st.secrets.get("OPENAI_API_KEY", "")
                except:
                    pass
            
            self.llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=settings.openai_temperature,
                max_tokens=settings.max_tokens,
                api_key=api_key
            )
            
            # 프롬프트 템플릿 로드
            self.prompts = self._load_prompts()
            
        except Exception as e:
            print(f"HumanFeedbackNode 초기화 오류: {str(e)}")
            self.llm = None
            self.prompts = {}
    
    def execute(self, state: FashionState) -> FashionState:
        """Human-in-the-loop 피드백 노드 실행"""
        
        try:
            state = update_state_step(state, "휴먼 피드백 처리 시작")
            
            # 피드백 반복 횟수 증가
            current_iteration = state.get("feedback_iteration", 0) + 1
            state["feedback_iteration"] = current_iteration
            
            # 최대 반복 횟수 체크
            if current_iteration > 3:
                state = update_state_step(state, "최대 피드백 반복 횟수 도달")
                state["requires_human_input"] = False
                return state
            
            # 사용자 피드백 가져오기
            user_feedback = state.get("human_feedback")
            
            if not user_feedback:
                # 피드백이 없는 경우 기본 검증 수행
                state = self._perform_automatic_validation(state)
            else:
                # 사용자 피드백이 있는 경우 반영
                state = self._process_user_feedback(state, user_feedback)
            
            state = update_state_step(state, f"휴먼 피드백 처리 완료 (반복: {current_iteration})")
            
        except Exception as e:
            state = add_error_to_state(state, f"휴먼 피드백 처리 오류: {str(e)}")
        
        return state
    
    def _load_prompts(self) -> Dict[str, Any]:
        """프롬프트 템플릿을 로드합니다"""
        try:
            with open("config/prompts.yaml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"프롬프트 로드 오류: {str(e)}")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Any]:
        """기본 프롬프트 반환"""
        return {
            "human_feedback": {
                "system_prompt": """사용자의 피드백을 받아 이전 결과를 개선하는 역할을 합니다.
피드백을 정확히 이해하고 요구사항에 맞게 수정해주세요.""",
                "user_prompt": """이전 결과에 대한 피드백입니다:

**이전 결과:**
{previous_result}

**사용자 피드백:**
{user_feedback}

피드백을 반영하여 개선된 결과를 제공해주세요.
변경사항과 개선된 이유를 명확히 설명해주세요."""
            }
        }
    
    def _perform_automatic_validation(self, state: FashionState) -> FashionState:
        """자동 검증 수행 (사용자 피드백이 없는 경우)"""
        
        try:
            # 생성된 콘텐츠 품질 검증
            validation_results = self._validate_generated_content(state)
            
            # 검증 결과에 따라 개선 필요 여부 결정
            if validation_results["needs_improvement"]:
                state["requires_human_input"] = True
                
                # 개선 제안 생성
                improvement_suggestions = self._generate_improvement_suggestions(validation_results)
                state["human_feedback"] = f"자동 검증 결과 개선이 필요합니다: {improvement_suggestions}"
                
                state = update_state_step(state, "자동 검증 결과: 개선 필요")
            else:
                state["requires_human_input"] = False
                state = update_state_step(state, "자동 검증 결과: 품질 기준 만족")
            
        except Exception as e:
            state = add_error_to_state(state, f"자동 검증 오류: {str(e)}")
            state["requires_human_input"] = True
        
        return state
    
    def _validate_generated_content(self, state: FashionState) -> Dict[str, Any]:
        """생성된 콘텐츠 품질 검증"""
        
        validation_results = {
            "needs_improvement": False,
            "issues": [],
            "scores": {},
            "suggestions": []
        }
        
        # 제품 기획서 검증
        product_proposal = state.get("product_proposal")
        if product_proposal:
            product_score = self._validate_product_proposal(product_proposal)
            validation_results["scores"]["product_proposal"] = product_score
            
            if product_score < 0.7:
                validation_results["needs_improvement"] = True
                validation_results["issues"].append("제품 기획서 품질 개선 필요")
        
        # 마케팅 문구 검증
        marketing_copy = state.get("marketing_copy")
        if marketing_copy:
            marketing_score = self._validate_marketing_copy(marketing_copy)
            validation_results["scores"]["marketing_copy"] = marketing_score
            
            if marketing_score < 0.7:
                validation_results["needs_improvement"] = True
                validation_results["issues"].append("마케팅 문구 개선 필요")
        
        # 콘텐츠 제안 검증
        content_suggestions = state.get("content_suggestions")
        if content_suggestions:
            content_score = self._validate_content_suggestions(content_suggestions)
            validation_results["scores"]["content_suggestions"] = content_score
            
            if content_score < 0.7:
                validation_results["needs_improvement"] = True
                validation_results["issues"].append("콘텐츠 제안 개선 필요")
        
        # 전반적 품질 점수
        if validation_results["scores"]:
            overall_score = sum(validation_results["scores"].values()) / len(validation_results["scores"])
            validation_results["overall_score"] = overall_score
            
            if overall_score < 0.7:
                validation_results["needs_improvement"] = True
        
        return validation_results
    
    def _validate_product_proposal(self, proposal: str) -> float:
        """제품 기획서 품질 점수 계산"""
        
        score = 0.0
        max_score = 5.0
        
        # 필수 요소 체크
        essential_elements = [
            "제품명", "컨셉", "타겟", "고객", "특징", "차별점", "가격", "마케팅"
        ]
        
        for element in essential_elements:
            if element in proposal:
                score += 1.0
        
        # 길이 체크 (너무 짧거나 긴 경우 감점)
        word_count = len(proposal.split())
        if 50 <= word_count <= 500:
            score += 1.0
        elif 30 <= word_count < 50 or 500 < word_count <= 800:
            score += 0.5
        
        # 구조화 체크 (번호나 bullet point 사용)
        if any(marker in proposal for marker in ["1.", "2.", "3.", "-", "•"]):
            score += 1.0
        
        return min(score / max_score, 1.0)
    
    def _validate_marketing_copy(self, copy: str) -> float:
        """마케팅 문구 품질 점수 계산"""
        
        score = 0.0
        max_score = 5.0
        
        # 필수 요소 체크
        essential_elements = [
            "캐치프레이즈", "카피", "설명", "해시태그", "#"
        ]
        
        for element in essential_elements:
            if element in copy:
                score += 1.0
        
        # 감정적 어조 체크
        emotional_words = [
            "새로운", "특별한", "독특한", "매력적인", "스타일리시한", 
            "편안한", "세련된", "트렌디한", "완벽한", "최고의"
        ]
        
        emotional_count = sum(1 for word in emotional_words if word in copy)
        if emotional_count >= 2:
            score += 1.0
        elif emotional_count >= 1:
            score += 0.5
        
        # 행동 유도 문구 체크
        cta_words = ["지금", "바로", "즉시", "놓치지", "기회", "한정", "특가", "할인"]
        if any(word in copy for word in cta_words):
            score += 1.0
        
        return min(score / max_score, 1.0)
    
    def _validate_content_suggestions(self, suggestions: List[str]) -> float:
        """콘텐츠 제안 품질 점수 계산"""
        
        if not suggestions:
            return 0.0
        
        score = 0.0
        max_score = 5.0
        
        # 제안 개수 체크
        if len(suggestions) >= 5:
            score += 2.0
        elif len(suggestions) >= 3:
            score += 1.5
        elif len(suggestions) >= 1:
            score += 1.0
        
        # 다양성 체크
        unique_types = set()
        for suggestion in suggestions:
            if "캘린더" in suggestion or "일정" in suggestion:
                unique_types.add("calendar")
            if "플랫폼" in suggestion or "SNS" in suggestion:
                unique_types.add("platform")
            if "인플루언서" in suggestion or "협업" in suggestion:
                unique_types.add("collaboration")
            if "KPI" in suggestion or "측정" in suggestion:
                unique_types.add("metrics")
        
        score += min(len(unique_types), 2.0)
        
        # 구체성 체크
        specific_count = 0
        for suggestion in suggestions:
            if any(keyword in suggestion for keyword in ["일", "주", "월", "시간", "개", "회"]):
                specific_count += 1
        
        if specific_count >= len(suggestions) * 0.5:
            score += 1.0
        
        return min(score / max_score, 1.0)
    
    def _generate_improvement_suggestions(self, validation_results: Dict[str, Any]) -> str:
        """개선 제안 생성"""
        
        suggestions = []
        
        for issue in validation_results["issues"]:
            if "제품 기획서" in issue:
                suggestions.append("제품 기획서에 타겟 고객, 차별점, 가격 전략을 더 구체적으로 포함해주세요.")
            elif "마케팅 문구" in issue:
                suggestions.append("마케팅 문구에 감정적 어조와 행동 유도 문구를 강화해주세요.")
            elif "콘텐츠 제안" in issue:
                suggestions.append("콘텐츠 제안을 더 구체적이고 다양하게 작성해주세요.")
        
        if not suggestions:
            suggestions.append("전반적인 품질 향상을 위해 더 구체적이고 실행 가능한 내용으로 개선해주세요.")
        
        return " ".join(suggestions)
    
    def _process_user_feedback(self, state: FashionState, user_feedback: str) -> FashionState:
        """사용자 피드백 처리 및 콘텐츠 개선"""
        
        try:
            if not self.llm:
                state = add_error_to_state(state, "OpenAI 클라이언트가 초기화되지 않았습니다.")
                return state
            
            # 개선이 필요한 콘텐츠 식별
            content_to_improve = self._identify_content_to_improve(user_feedback, state)
            
            # 각 콘텐츠별로 개선 수행
            for content_type in content_to_improve:
                improved_content = self._improve_content(content_type, user_feedback, state)
                if improved_content:
                    state[content_type] = improved_content
                    state = update_state_step(state, f"{content_type} 개선 완료")
            
            # 피드백 반영 완료 플래그 설정
            state["requires_human_input"] = False
            
        except Exception as e:
            state = add_error_to_state(state, f"사용자 피드백 처리 오류: {str(e)}")
        
        return state
    
    def _identify_content_to_improve(self, feedback: str, state: FashionState) -> List[str]:
        """피드백에서 개선이 필요한 콘텐츠 식별"""
        
        content_to_improve = []
        
        if any(word in feedback for word in ["제품", "기획서", "기획"]):
            if state.get("product_proposal"):
                content_to_improve.append("product_proposal")
        
        if any(word in feedback for word in ["마케팅", "문구", "카피", "광고"]):
            if state.get("marketing_copy"):
                content_to_improve.append("marketing_copy")
        
        if any(word in feedback for word in ["콘텐츠", "제안", "전략"]):
            if state.get("content_suggestions"):
                content_to_improve.append("content_suggestions")
        
        # 특정 콘텐츠가 명시되지 않은 경우 모든 콘텐츠 개선
        if not content_to_improve:
            if state.get("product_proposal"):
                content_to_improve.append("product_proposal")
            if state.get("marketing_copy"):
                content_to_improve.append("marketing_copy")
            if state.get("content_suggestions"):
                content_to_improve.append("content_suggestions")
        
        return content_to_improve
    
    def _improve_content(self, content_type: str, user_feedback: str, state: FashionState) -> Optional[str]:
        """특정 콘텐츠 개선"""
        
        try:
            # 기존 콘텐츠 가져오기
            previous_content = state.get(content_type, "")
            if not previous_content:
                return None
            
            # 프롬프트 구성
            prompts = self.prompts.get("human_feedback", self._get_default_prompts()["human_feedback"])
            
            system_prompt = prompts["system_prompt"]
            user_prompt = prompts["user_prompt"].format(
                previous_result=previous_content,
                user_feedback=user_feedback
            )
            
            # LLM 호출
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # 토큰 사용량 추적
            input_tokens = len(system_prompt + user_prompt) // 4
            output_tokens = len(response.content) // 4
            
            state = update_token_usage(
                state, 
                input_tokens, 
                output_tokens,
                settings.token_cost_per_1k_input,
                settings.token_cost_per_1k_output
            )
            
            return response.content
            
        except Exception as e:
            state = add_error_to_state(state, f"{content_type} 개선 오류: {str(e)}")
            return None
    
    def get_feedback_summary(self, state: FashionState) -> Dict[str, Any]:
        """피드백 처리 요약 생성"""
        
        return {
            "feedback_iteration": state.get("feedback_iteration", 0),
            "requires_human_input": state.get("requires_human_input", False),
            "last_feedback": state.get("human_feedback", ""),
            "processing_steps": [
                step for step in state.get("processing_steps", [])
                if "휴먼 피드백" in step or "검증" in step
            ],
            "validation_status": "개선 필요" if state.get("requires_human_input", False) else "검증 완료"
        } 