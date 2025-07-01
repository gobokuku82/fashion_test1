"""
Fashion AI Automation System - Sentiment Analysis Node
"""

import yaml
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..state import FashionState, update_state_step, add_error_to_state, update_token_usage
from config.settings import settings


class SentimentAnalysisNode:
    """감성 분석을 담당하는 LangGraph 노드"""
    
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
                temperature=0.3,  # 감성 분석은 일관성을 위해 낮은 temperature
                max_tokens=settings.max_tokens,
                api_key=api_key
            )
            
            # 프롬프트 템플릿 로드
            self.prompts = self._load_prompts()
            
        except Exception as e:
            print(f"SentimentAnalysisNode 초기화 오류: {str(e)}")
            self.llm = None
            self.prompts = {}
    
    def execute(self, state: FashionState) -> FashionState:
        """감성 분석 노드 실행"""
        
        try:
            state = update_state_step(state, "감성 분석 시작")
            
            if not self.llm:
                raise Exception("OpenAI 클라이언트가 초기화되지 않았습니다.")
            
            # 분석할 텍스트 데이터 준비
            text_data = self._prepare_text_data(state)
            
            if not text_data:
                state = add_error_to_state(state, "감성 분석할 텍스트 데이터가 없습니다.")
                return state
            
            # 감성 분석 수행
            sentiment_result = self._analyze_sentiment(text_data, state)
            
            # 결과를 상태에 저장
            state["sentiment_analysis"] = sentiment_result
            
            state = update_state_step(state, "감성 분석 완료")
            
        except Exception as e:
            state = add_error_to_state(state, f"감성 분석 오류: {str(e)}")
        
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
            "sentiment_analysis": {
                "system_prompt": """당신은 소비자 감성 분석 전문가입니다.
SNS 댓글, 리뷰, 블로그 포스트 등의 텍스트 데이터를 분석하여
소비자들의 감정과 의견을 정확히 파악해주세요.""",
                
                "user_prompt": """다음 텍스트 데이터들의 감성을 분석해주세요:

**분석 대상 텍스트:**
{text_data}

**제품/브랜드:** {product_brand}

분석 결과를 다음 형식으로 제공해주세요:
1. 전체 감성 점수 (-1.0 ~ 1.0)
2. 긍정/부정/중립 비율
3. 주요 키워드 감성 분석
4. 개선 포인트 제안"""
            }
        }
    
    def _prepare_text_data(self, state: FashionState) -> List[Dict[str, Any]]:
        """분석할 텍스트 데이터 준비"""
        
        text_data = []
        
        # SNS 데이터에서 텍스트 추출
        social_media_data = state.get("social_media_data", [])
        for item in social_media_data:
            if item.get("content"):
                text_data.append({
                    "text": item["content"],
                    "source": f"SNS_{item.get('platform', 'unknown')}",
                    "metadata": {
                        "likes": item.get("likes", 0),
                        "comments": item.get("comments", 0),
                        "hashtags": item.get("hashtags", [])
                    }
                })
        
        # 네이버 쇼핑 리뷰 데이터 (제목에서 감성 추출)
        naver_data = state.get("naver_shopping_data", [])
        for item in naver_data[:20]:  # 최대 20개
            title = item.get("title", "")
            if title:
                # HTML 태그 제거
                clean_title = re.sub(r'<[^>]+>', '', title)
                text_data.append({
                    "text": clean_title,
                    "source": "naver_shopping",
                    "metadata": {
                        "price": item.get("lprice", ""),
                        "brand": item.get("brand", ""),
                        "category": item.get("category1", "")
                    }
                })
        
        # 웹 스크래핑 데이터에서 텍스트 추출
        web_data = state.get("web_scraping_data", [])
        for item in web_data:
            content = item.get("content", "")
            if content:
                text_data.append({
                    "text": content[:500],  # 최대 500자
                    "source": "web_content",
                    "metadata": {
                        "title": item.get("title", ""),
                        "url": item.get("url", "")
                    }
                })
        
        return text_data
    
    def _analyze_sentiment(self, text_data: List[Dict[str, Any]], state: FashionState) -> Dict[str, Any]:
        """LLM을 통한 감성 분석 수행"""
        
        try:
            # 텍스트 데이터를 문자열로 변환
            formatted_text = self._format_text_for_analysis(text_data)
            
            # 프롬프트 구성
            prompts = self.prompts.get("sentiment_analysis", self._get_default_prompts()["sentiment_analysis"])
            
            system_prompt = prompts["system_prompt"]
            user_prompt = prompts["user_prompt"].format(
                text_data=formatted_text,
                product_brand=state.get("target_category", "패션 제품")
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
            
            # 감성 점수 추출
            sentiment_score = self._extract_sentiment_score(response.content)
            sentiment_distribution = self._calculate_sentiment_distribution(text_data, sentiment_score)
            key_emotions = self._extract_key_emotions(response.content)
            improvement_points = self._extract_improvement_points(response.content)
            
            # 결과 구조화
            analysis_result = {
                "overall_sentiment_score": sentiment_score,
                "sentiment_distribution": sentiment_distribution,
                "key_emotions": key_emotions,
                "improvement_points": improvement_points,
                "raw_analysis": response.content,
                "data_summary": {
                    "total_texts_analyzed": len(text_data),
                    "sources": list(set([item["source"] for item in text_data])),
                    "analysis_timestamp": datetime.now().isoformat()
                },
                "detailed_insights": self._generate_detailed_insights(text_data, sentiment_score)
            }
            
            return analysis_result
            
        except Exception as e:
            raise Exception(f"LLM 감성 분석 오류: {str(e)}")
    
    def _format_text_for_analysis(self, text_data: List[Dict[str, Any]]) -> str:
        """텍스트 데이터를 분석용 형식으로 변환"""
        
        formatted_texts = []
        
        for i, item in enumerate(text_data[:30], 1):  # 최대 30개
            text = item["text"]
            source = item["source"]
            metadata = item.get("metadata", {})
            
            if source.startswith("SNS"):
                likes = metadata.get("likes", 0)
                formatted_texts.append(f"{i}. [SNS] {text} (좋아요: {likes})")
            elif source == "naver_shopping":
                price = metadata.get("price", "")
                formatted_texts.append(f"{i}. [쇼핑] {text} (가격: {price}원)")
            else:
                formatted_texts.append(f"{i}. [웹] {text}")
        
        return "\n".join(formatted_texts)
    
    def _extract_sentiment_score(self, analysis_text: str) -> float:
        """분석 텍스트에서 감성 점수 추출"""
        
        # 숫자 패턴 찾기 (-1.0 ~ 1.0 범위)
        import re
        score_patterns = [
            r'감성\s*점수[:\s]*([+-]?\d*\.?\d+)',
            r'점수[:\s]*([+-]?\d*\.?\d+)',
            r'(-?\d*\.?\d+)\s*점',
            r'(-1\.0|[-+]?0\.\d+|1\.0)'
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, analysis_text)
            if matches:
                try:
                    score = float(matches[0])
                    # -1.0 ~ 1.0 범위로 제한
                    return max(-1.0, min(1.0, score))
                except ValueError:
                    continue
        
        # 패턴을 찾지 못한 경우 텍스트 분석으로 추정
        if any(word in analysis_text for word in ["매우 긍정", "매우 좋", "훌륭"]):
            return 0.8
        elif any(word in analysis_text for word in ["긍정", "좋", "만족"]):
            return 0.4
        elif any(word in analysis_text for word in ["부정", "나쁨", "불만"]):
            return -0.4
        elif any(word in analysis_text for word in ["매우 부정", "매우 나쁨", "최악"]):
            return -0.8
        else:
            return 0.0  # 중립
    
    def _calculate_sentiment_distribution(self, text_data: List[Dict[str, Any]], overall_score: float) -> Dict[str, float]:
        """감성 분포 계산"""
        
        # 간단한 분포 계산 (실제로는 각 텍스트별로 개별 분석해야 함)
        if overall_score > 0.3:
            return {"positive": 0.7, "neutral": 0.2, "negative": 0.1}
        elif overall_score < -0.3:
            return {"positive": 0.1, "neutral": 0.2, "negative": 0.7}
        else:
            return {"positive": 0.3, "neutral": 0.5, "negative": 0.2}
    
    def _extract_key_emotions(self, analysis_text: str) -> List[str]:
        """주요 감정 키워드 추출"""
        
        emotion_keywords = [
            "만족", "불만", "기대", "실망", "흥미", "지루함",
            "신뢰", "불신", "호감", "비호감", "선호", "거부감",
            "즐거움", "불쾌", "편안함", "불편함", "안전", "불안"
        ]
        
        found_emotions = []
        for emotion in emotion_keywords:
            if emotion in analysis_text:
                found_emotions.append(emotion)
        
        return found_emotions[:5]  # 최대 5개
    
    def _extract_improvement_points(self, analysis_text: str) -> List[str]:
        """개선 포인트 추출"""
        
        improvement_lines = []
        lines = analysis_text.split('\n')
        
        in_improvement_section = False
        for line in lines:
            if any(keyword in line for keyword in ["개선", "향상", "보완", "권장", "제안"]):
                in_improvement_section = True
            
            if in_improvement_section and line.strip():
                improvement_lines.append(line.strip())
        
        return improvement_lines[:5]  # 최대 5개
    
    def _generate_detailed_insights(self, text_data: List[Dict[str, Any]], sentiment_score: float) -> Dict[str, Any]:
        """상세 인사이트 생성"""
        
        # 소스별 감성 분석
        source_sentiment = {}
        for item in text_data:
            source = item["source"]
            if source not in source_sentiment:
                source_sentiment[source] = []
            source_sentiment[source].append(item["text"])
        
        return {
            "sentiment_by_source": {
                source: len(texts) for source, texts in source_sentiment.items()
            },
            "overall_sentiment_label": self._get_sentiment_label(sentiment_score),
            "confidence_level": self._calculate_confidence(len(text_data)),
            "recommendation": self._generate_recommendation(sentiment_score)
        }
    
    def _get_sentiment_label(self, score: float) -> str:
        """감성 점수를 라벨로 변환"""
        if score > 0.5:
            return "매우 긍정적"
        elif score > 0.1:
            return "긍정적"
        elif score > -0.1:
            return "중립적"
        elif score > -0.5:
            return "부정적"
        else:
            return "매우 부정적"
    
    def _calculate_confidence(self, data_count: int) -> str:
        """신뢰도 계산"""
        if data_count >= 50:
            return "높음"
        elif data_count >= 20:
            return "보통"
        else:
            return "낮음"
    
    def _generate_recommendation(self, sentiment_score: float) -> str:
        """감성 점수 기반 추천사항 생성"""
        if sentiment_score > 0.3:
            return "현재 긍정적인 반응을 보이고 있습니다. 이 트렌드를 유지하며 마케팅을 강화하세요."
        elif sentiment_score < -0.3:
            return "부정적인 반응이 감지됩니다. 고객 피드백을 수집하고 제품/서비스 개선이 필요합니다."
        else:
            return "중립적인 반응입니다. 더 명확한 포지셔닝과 차별화 전략이 필요할 수 있습니다." 