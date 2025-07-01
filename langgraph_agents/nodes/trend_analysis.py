"""
Fashion AI Automation System - Trend Analysis Node
"""

import yaml
from typing import Dict, List, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..state import FashionState, update_state_step, add_error_to_state, update_token_usage
from config.settings import settings


class TrendAnalysisNode:
    """트렌드 분석을 담당하는 LangGraph 노드"""
    
    def __init__(self):
        try:
            # OpenAI 설정에서 API 키 가져오기
            api_key = settings.openai_api_key
            if not api_key:
                # Streamlit secrets에서 가져오기 시도
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
            print(f"TrendAnalysisNode 초기화 오류: {str(e)}")
            self.llm = None
            self.prompts = {}
    
    def execute(self, state: FashionState) -> FashionState:
        """트렌드 분석 노드 실행"""
        
        try:
            state = update_state_step(state, "트렌드 분석 시작")
            
            if not self.llm:
                raise Exception("OpenAI 클라이언트가 초기화되지 않았습니다.")
            
            # 수집된 데이터 준비
            collected_data = state.get("collected_data", {})
            
            if not collected_data:
                state = add_error_to_state(state, "분석할 데이터가 없습니다.")
                return state
            
            # 데이터 전처리
            processed_data = self._preprocess_data(collected_data)
            
            # LLM을 통한 트렌드 분석
            analysis_result = self._analyze_trends(processed_data, state)
            
            # 결과를 상태에 저장
            state["trend_analysis"] = analysis_result
            
            state = update_state_step(state, "트렌드 분석 완료")
            
        except Exception as e:
            state = add_error_to_state(state, f"트렌드 분석 오류: {str(e)}")
        
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
            "trend_analysis": {
                "system_prompt": """당신은 패션 업계의 전문 트렌드 애널리스트입니다. 
수집된 데이터를 바탕으로 정확하고 실용적인 트렌드 분석을 제공해주세요.

분석 시 다음 요소들을 고려해주세요:
- 계절별 트렌드 변화
- 타겟 연령층별 선호도
- 가격대별 시장 동향
- 브랜드별 포지셔닝 전략""",
                
                "user_prompt": """다음 데이터를 분석하여 패션 트렌드 리포트를 작성해주세요:

**수집 데이터:**
{collected_data}

**분석 기간:** {analysis_period}
**타겟 카테고리:** {target_category}

다음 형식으로 답변해주세요:
1. 주요 트렌드 요약 (3-5개)
2. 타겟별 세분화 분석
3. 향후 3개월 예측
4. 실행 가능한 비즈니스 제안"""
            }
        }
    
    def _preprocess_data(self, collected_data: Dict[str, Any]) -> str:
        """수집된 데이터를 LLM 분석용으로 전처리"""
        
        processed_parts = []
        
        # 네이버 쇼핑 데이터 요약
        naver_data = collected_data.get("naver_shopping", [])
        if naver_data:
            naver_summary = f"네이버 쇼핑 데이터 ({len(naver_data)}건):\n"
            for item in naver_data[:10]:  # 최대 10개만 포함
                title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                price = item.get("lprice", "")
                brand = item.get("brand", "")
                naver_summary += f"- {title} | {brand} | {price}원\n"
            processed_parts.append(naver_summary)
        
        # 웹 스크래핑 데이터 요약
        web_data = collected_data.get("web_scraping", [])
        if web_data:
            web_summary = f"웹 스크래핑 데이터 ({len(web_data)}건):\n"
            for item in web_data:
                title = item.get("title", "")
                content = item.get("content", "")[:200]  # 200자까지만
                web_summary += f"- {title}: {content}...\n"
            processed_parts.append(web_summary)
        
        # SNS 데이터 요약
        social_data = collected_data.get("social_media", [])
        if social_data:
            social_summary = f"SNS 데이터 ({len(social_data)}건):\n"
            for item in social_data:
                content = item.get("content", "")
                platform = item.get("platform", "")
                likes = item.get("likes", 0)
                social_summary += f"- {platform}: {content} (좋아요 {likes}개)\n"
            processed_parts.append(social_summary)
        
        return "\n\n".join(processed_parts)
    
    def _analyze_trends(self, processed_data: str, state: FashionState) -> Dict[str, Any]:
        """LLM을 통한 트렌드 분석 수행"""
        
        try:
            # 프롬프트 구성
            prompts = self.prompts.get("trend_analysis", self._get_default_prompts()["trend_analysis"])
            
            system_prompt = prompts["system_prompt"]
            user_prompt = prompts["user_prompt"].format(
                collected_data=processed_data,
                analysis_period=state.get("analysis_period", "최근 1개월"),
                target_category=state.get("target_category", "전체")
            )
            
            # LLM 호출
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # 토큰 사용량 추적 (근사치)
            input_tokens = len(system_prompt + user_prompt) // 4  # 대략적인 토큰 계산
            output_tokens = len(response.content) // 4
            
            state = update_token_usage(
                state, 
                input_tokens, 
                output_tokens,
                settings.token_cost_per_1k_input,
                settings.token_cost_per_1k_output
            )
            
            # 결과 구조화
            analysis_result = {
                "raw_analysis": response.content,
                "summary": self._extract_summary(response.content),
                "key_trends": self._extract_key_trends(response.content),
                "predictions": self._extract_predictions(response.content),
                "business_recommendations": self._extract_recommendations(response.content),
                "analysis_timestamp": datetime.now().isoformat(),
                "data_sources_count": {
                    "naver_shopping": len(state.get("naver_shopping_data", [])),
                    "web_scraping": len(state.get("web_scraping_data", [])),
                    "social_media": len(state.get("social_media_data", []))
                }
            }
            
            return analysis_result
            
        except Exception as e:
            raise Exception(f"LLM 트렌드 분석 오류: {str(e)}")
    
    def _extract_summary(self, analysis_text: str) -> str:
        """분석 텍스트에서 요약 추출"""
        lines = analysis_text.split('\n')
        summary_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in ["요약", "주요", "핵심"]):
                summary_lines.append(line.strip())
        
        return ' '.join(summary_lines) if summary_lines else analysis_text[:200] + "..."
    
    def _extract_key_trends(self, analysis_text: str) -> List[str]:
        """주요 트렌드 키워드 추출"""
        # 간단한 키워드 추출 로직
        keywords = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-')):
                # 번호나 bullet point로 시작하는 라인에서 키워드 추출
                clean_line = line.strip().lstrip('1234567890.- ')
                if len(clean_line) > 0:
                    keywords.append(clean_line[:50])  # 최대 50자
        
        return keywords[:5]  # 최대 5개
    
    def _extract_predictions(self, analysis_text: str) -> List[str]:
        """예측 관련 내용 추출"""
        predictions = []
        lines = analysis_text.split('\n')
        
        in_prediction_section = False
        for line in lines:
            if any(keyword in line for keyword in ["예측", "향후", "미래", "전망"]):
                in_prediction_section = True
            
            if in_prediction_section and line.strip():
                predictions.append(line.strip())
                
            # 다른 섹션이 시작되면 종료
            if in_prediction_section and any(keyword in line for keyword in ["제안", "권장", "결론"]):
                break
        
        return predictions[:3]  # 최대 3개
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """비즈니스 제안 추출"""
        recommendations = []
        lines = analysis_text.split('\n')
        
        in_recommendation_section = False
        for line in lines:
            if any(keyword in line for keyword in ["제안", "권장", "추천", "비즈니스"]):
                in_recommendation_section = True
            
            if in_recommendation_section and line.strip():
                recommendations.append(line.strip())
        
        return recommendations[:5]  # 최대 5개 