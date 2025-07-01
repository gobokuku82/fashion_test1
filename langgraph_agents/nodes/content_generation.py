"""
Fashion AI Automation System - Content Generation Node
"""

import yaml
from typing import Dict, List, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..state import FashionState, update_state_step, add_error_to_state, update_token_usage
from config.settings import settings


class ContentGenerationNode:
    """콘텐츠 생성을 담당하는 LangGraph 노드"""
    
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
            print(f"ContentGenerationNode 초기화 오류: {str(e)}")
            self.llm = None
            self.prompts = {}
    
    def execute(self, state: FashionState) -> FashionState:
        """콘텐츠 생성 노드 실행"""
        
        try:
            state = update_state_step(state, "콘텐츠 생성 시작")
            
            if not self.llm:
                raise Exception("OpenAI 클라이언트가 초기화되지 않았습니다.")
            
            # 분석 결과 확인
            trend_analysis = state.get("trend_analysis")
            sentiment_analysis = state.get("sentiment_analysis")
            
            if not trend_analysis and not sentiment_analysis:
                state = add_error_to_state(state, "콘텐츠 생성을 위한 분석 결과가 없습니다.")
                return state
            
            # 사용자 요청 분석
            user_request = state["user_request"]
            content_type = self._determine_content_type(user_request)
            
            # 콘텐츠 생성
            if "제품" in user_request or "기획" in user_request:
                product_proposal = self._generate_product_proposal(state)
                state["product_proposal"] = product_proposal
            
            if "마케팅" in user_request or "문구" in user_request:
                marketing_copy = self._generate_marketing_copy(state)
                state["marketing_copy"] = marketing_copy
            
            if "콘텐츠" in user_request or "제안" in user_request:
                content_suggestions = self._generate_content_suggestions(state)
                state["content_suggestions"] = content_suggestions
            
            # 기본적으로 모든 콘텐츠 생성 (사용자 요청이 명확하지 않은 경우)
            if not state.get("product_proposal") and not state.get("marketing_copy") and not state.get("content_suggestions"):
                state["product_proposal"] = self._generate_product_proposal(state)
                state["marketing_copy"] = self._generate_marketing_copy(state)
                state["content_suggestions"] = self._generate_content_suggestions(state)
            
            state = update_state_step(state, "콘텐츠 생성 완료")
            
        except Exception as e:
            state = add_error_to_state(state, f"콘텐츠 생성 오류: {str(e)}")
        
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
            "product_planning": {
                "system_prompt": """당신은 패션 제품 기획 전문가입니다.
트렌드 분석과 시장 데이터를 바탕으로 실제 출시 가능한 제품 기획서를 작성해주세요.""",
                "user_prompt": """다음 정보를 바탕으로 제품 기획서를 작성해주세요:

**트렌드 분석 결과:**
{trend_analysis}

**타겟 시장:**
- 성별: {target_gender}
- 연령대: {target_age}
- 가격대: {price_range}

**카테고리:** {product_category}

제품 기획서 형식:
1. 제품명 및 컨셉
2. 타겟 고객 페르소나
3. 주요 특징 및 차별점
4. 예상 가격 및 채널 전략
5. 출시 일정 및 마케팅 포인트"""
            },
            "marketing_copy": {
                "system_prompt": """당신은 패션 마케팅 카피라이터입니다.
감성 분석 결과와 제품 정보를 바탕으로 매력적이고 효과적인 마케팅 문구를 작성해주세요.""",
                "user_prompt": """다음 정보를 바탕으로 마케팅 문구를 작성해주세요:

**제품 정보:**
{product_info}

**감성 분석 결과:**
{sentiment_analysis}

**타겟 채널:** {marketing_channel}

다음 형식으로 제공해주세요:
1. 메인 캐치프레이즈 (20자 이내)
2. 서브 카피 (50자 이내)
3. 상세 설명 문구 (100자 이내)
4. 해시태그 제안 (5개)
5. 채널별 최적화 버전"""
            },
            "content_suggestion": {
                "system_prompt": """당신은 패션 콘텐츠 전략가입니다.
브랜드의 소셜미디어와 마케팅 콘텐츠 전략을 데이터 기반으로 제안해주세요.""",
                "user_prompt": """다음 정보를 바탕으로 콘텐츠 전략을 제안해주세요:

**브랜드 정보:**
{brand_info}

**최근 트렌드:**
{recent_trends}

**경쟁사 분석:**
{competitor_analysis}

콘텐츠 전략 제안:
1. 주간 콘텐츠 캘린더 (7일간)
2. 플랫폼별 최적화 전략
3. 시즌별 특별 기획안
4. 인플루언서 협업 아이디어
5. 성과 측정 KPI 제안"""
            }
        }
    
    def _determine_content_type(self, user_request: str) -> List[str]:
        """사용자 요청에서 생성할 콘텐츠 타입 결정"""
        content_types = []
        
        if any(word in user_request for word in ["제품", "기획서", "기획"]):
            content_types.append("product_proposal")
        
        if any(word in user_request for word in ["마케팅", "문구", "카피", "광고"]):
            content_types.append("marketing_copy")
        
        if any(word in user_request for word in ["콘텐츠", "제안", "전략", "SNS"]):
            content_types.append("content_suggestions")
        
        # 기본값: 모든 콘텐츠 생성
        if not content_types:
            content_types = ["product_proposal", "marketing_copy", "content_suggestions"]
        
        return content_types
    
    def _generate_product_proposal(self, state: FashionState) -> str:
        """제품 기획서 생성"""
        
        try:
            # 분석 결과 준비
            trend_analysis = state.get("trend_analysis", {})
            trend_summary = trend_analysis.get("raw_analysis", "트렌드 분석 결과 없음")
            
            # 타겟 정보 준비
            demographics = state.get("target_demographics", {})
            target_category = state.get("target_category", "전체")
            
            # 프롬프트 구성
            prompts = self.prompts.get("product_planning", self._get_default_prompts()["product_planning"])
            
            system_prompt = prompts["system_prompt"]
            user_prompt = prompts["user_prompt"].format(
                trend_analysis=trend_summary,
                target_gender=demographics.get("gender", "전체"),
                target_age=demographics.get("age_range", "20-40"),
                price_range=demographics.get("income_level", "중간"),
                product_category=target_category
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
            raise Exception(f"제품 기획서 생성 오류: {str(e)}")
    
    def _generate_marketing_copy(self, state: FashionState) -> str:
        """마케팅 문구 생성"""
        
        try:
            # 분석 결과 준비
            sentiment_analysis = state.get("sentiment_analysis", {})
            sentiment_summary = sentiment_analysis.get("raw_analysis", "감성 분석 결과 없음")
            
            # 제품 정보 준비
            target_category = state.get("target_category", "패션 제품")
            product_info = f"카테고리: {target_category}"
            
            # 프롬프트 구성
            prompts = self.prompts.get("marketing_copy", self._get_default_prompts()["marketing_copy"])
            
            system_prompt = prompts["system_prompt"]
            user_prompt = prompts["user_prompt"].format(
                product_info=product_info,
                sentiment_analysis=sentiment_summary,
                marketing_channel="온라인 쇼핑몰, SNS"
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
            raise Exception(f"마케팅 문구 생성 오류: {str(e)}")
    
    def _generate_content_suggestions(self, state: FashionState) -> List[str]:
        """콘텐츠 제안 생성"""
        
        try:
            # 분석 결과 준비
            trend_analysis = state.get("trend_analysis", {})
            trend_summary = trend_analysis.get("raw_analysis", "트렌드 분석 결과 없음")
            
            # 브랜드 정보 준비
            target_category = state.get("target_category", "패션")
            brand_info = f"패션 브랜드 - 전문 분야: {target_category}"
            
            # 프롬프트 구성
            prompts = self.prompts.get("content_suggestion", self._get_default_prompts()["content_suggestion"])
            
            system_prompt = prompts["system_prompt"]
            user_prompt = prompts["user_prompt"].format(
                brand_info=brand_info,
                recent_trends=trend_summary,
                competitor_analysis="경쟁사 분석 데이터 부족"
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
            
            # 응답을 리스트로 분할
            suggestions = self._parse_content_suggestions(response.content)
            
            return suggestions
            
        except Exception as e:
            raise Exception(f"콘텐츠 제안 생성 오류: {str(e)}")
    
    def _parse_content_suggestions(self, content: str) -> List[str]:
        """콘텐츠 제안 텍스트를 리스트로 파싱"""
        
        suggestions = []
        lines = content.split('\n')
        
        current_suggestion = ""
        for line in lines:
            line = line.strip()
            
            # 번호나 bullet point로 시작하는 새로운 제안
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                if current_suggestion:
                    suggestions.append(current_suggestion.strip())
                current_suggestion = line
            elif line and current_suggestion:
                current_suggestion += " " + line
        
        # 마지막 제안 추가
        if current_suggestion:
            suggestions.append(current_suggestion.strip())
        
        # 최대 10개 제안
        return suggestions[:10]
    
    def _extract_key_insights(self, state: FashionState) -> Dict[str, Any]:
        """분석 결과에서 핵심 인사이트 추출"""
        
        insights = {
            "key_trends": [],
            "sentiment_score": 0.0,
            "recommendations": [],
            "target_keywords": []
        }
        
        # 트렌드 분석에서 인사이트 추출
        trend_analysis = state.get("trend_analysis", {})
        if trend_analysis:
            insights["key_trends"] = trend_analysis.get("key_trends", [])
            insights["recommendations"].extend(trend_analysis.get("business_recommendations", []))
        
        # 감성 분석에서 인사이트 추출
        sentiment_analysis = state.get("sentiment_analysis", {})
        if sentiment_analysis:
            insights["sentiment_score"] = sentiment_analysis.get("overall_sentiment_score", 0.0)
            insights["recommendations"].extend(sentiment_analysis.get("improvement_points", []))
        
        # 수집된 데이터에서 키워드 추출
        collected_data = state.get("collected_data", {})
        keywords_used = collected_data.get("keywords_used", [])
        insights["target_keywords"] = keywords_used
        
        return insights
    
    def _format_insights_for_prompt(self, insights: Dict[str, Any]) -> str:
        """인사이트를 프롬프트용 텍스트로 변환"""
        
        formatted_parts = []
        
        if insights["key_trends"]:
            trends_text = "주요 트렌드: " + ", ".join(insights["key_trends"][:5])
            formatted_parts.append(trends_text)
        
        sentiment_label = "긍정적" if insights["sentiment_score"] > 0.3 else "부정적" if insights["sentiment_score"] < -0.3 else "중립적"
        sentiment_text = f"고객 감성: {sentiment_label} (점수: {insights['sentiment_score']:.2f})"
        formatted_parts.append(sentiment_text)
        
        if insights["recommendations"]:
            rec_text = "주요 권장사항: " + "; ".join(insights["recommendations"][:3])
            formatted_parts.append(rec_text)
        
        if insights["target_keywords"]:
            keyword_text = "타겟 키워드: " + ", ".join(insights["target_keywords"][:5])
            formatted_parts.append(keyword_text)
        
        return "\n".join(formatted_parts) 