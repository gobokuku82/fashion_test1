"""
Fashion AI Automation System - MCP (Model Context Protocol) Client
"""

import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings


class MCPClient:
    """MCP(Model Context Protocol) 기반 LLM 클라이언트"""
    
    def __init__(self):
        try:
            # OpenAI 클라이언트 초기화
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
            
            # MCP 도구 등록
            self.available_tools = self._register_tools()
            
        except Exception as e:
            print(f"MCPClient 초기화 오류: {str(e)}")
            self.llm = None
            self.available_tools = {}
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """사용 가능한 도구들을 MCP 형식으로 등록"""
        
        tools = {
            "trend_analyzer": {
                "name": "trend_analyzer",
                "description": "패션 트렌드 데이터를 분석하고 인사이트를 제공하는 도구",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "분석할 트렌드 데이터"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["trend_summary", "seasonal_analysis", "brand_comparison"],
                            "description": "분석 유형"
                        },
                        "target_audience": {
                            "type": "string",
                            "description": "타겟 고객층"
                        }
                    },
                    "required": ["data", "analysis_type"]
                }
            },
            
            "sentiment_analyzer": {
                "name": "sentiment_analyzer",
                "description": "소비자 리뷰, SNS 댓글 등의 감성을 분석하는 도구",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text_data": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "분석할 텍스트 데이터 리스트"
                        },
                        "context": {
                            "type": "string",
                            "description": "분석 컨텍스트 (제품, 브랜드 등)"
                        }
                    },
                    "required": ["text_data"]
                }
            },
            
            "content_generator": {
                "name": "content_generator",
                "description": "마케팅 콘텐츠, 제품 기획서 등을 생성하는 도구",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content_type": {
                            "type": "string",
                            "enum": ["product_proposal", "marketing_copy", "social_content", "blog_post"],
                            "description": "생성할 콘텐츠 유형"
                        },
                        "input_data": {
                            "type": "object",
                            "description": "콘텐츠 생성에 필요한 입력 데이터"
                        },
                        "style": {
                            "type": "string",
                            "description": "콘텐츠 스타일 (formal, casual, trendy 등)"
                        }
                    },
                    "required": ["content_type", "input_data"]
                }
            },
            
            "data_collector": {
                "name": "data_collector",
                "description": "외부 소스에서 패션 관련 데이터를 수집하는 도구",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_type": {
                            "type": "string",
                            "enum": ["naver_shopping", "web_scraping", "social_media"],
                            "description": "데이터 소스 유형"
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "검색 키워드"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 10,
                            "description": "수집할 데이터 개수"
                        }
                    },
                    "required": ["source_type", "keywords"]
                }
            }
        }
        
        return tools
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 도구 호출"""
        
        try:
            if tool_name not in self.available_tools:
                return {
                    "success": False,
                    "error": f"도구 '{tool_name}'를 찾을 수 없습니다.",
                    "available_tools": list(self.available_tools.keys())
                }
            
            # 도구별 실행 로직
            if tool_name == "trend_analyzer":
                return self._execute_trend_analyzer(parameters)
            elif tool_name == "sentiment_analyzer":
                return self._execute_sentiment_analyzer(parameters)
            elif tool_name == "content_generator":
                return self._execute_content_generator(parameters)
            elif tool_name == "data_collector":
                return self._execute_data_collector(parameters)
            else:
                return {
                    "success": False,
                    "error": f"도구 '{tool_name}'의 실행 로직이 구현되지 않았습니다."
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"도구 실행 중 오류 발생: {str(e)}"
            }
    
    def _execute_trend_analyzer(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """트렌드 분석 도구 실행"""
        
        try:
            data = parameters.get("data", "")
            analysis_type = parameters.get("analysis_type", "trend_summary")
            target_audience = parameters.get("target_audience", "일반 소비자")
            
            # 분석 유형별 프롬프트 설정
            prompts = {
                "trend_summary": f"""다음 패션 데이터를 분석하여 주요 트렌드를 요약해주세요:

데이터: {data}
타겟 고객: {target_audience}

분석 결과를 다음 형식으로 제공해주세요:
1. 주요 트렌드 (3-5개)
2. 타겟 고객별 인사이트
3. 실행 가능한 권장사항""",

                "seasonal_analysis": f"""다음 데이터를 바탕으로 계절별 패션 트렌드를 분석해주세요:

데이터: {data}
타겟 고객: {target_audience}

계절별 특징과 변화 패턴을 분석해주세요.""",

                "brand_comparison": f"""다음 데이터를 바탕으로 브랜드별 포지셔닝을 분석해주세요:

데이터: {data}
타겟 고객: {target_audience}

브랜드별 차별점과 시장 포지션을 분석해주세요."""
            }
            
            prompt = prompts.get(analysis_type, prompts["trend_summary"])
            
            # LLM 호출
            if self.llm:
                messages = [
                    SystemMessage(content="당신은 패션 트렌드 분석 전문가입니다."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                
                return {
                    "success": True,
                    "tool_name": "trend_analyzer",
                    "analysis_type": analysis_type,
                    "result": response.content,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return self._get_sample_trend_analysis(analysis_type)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"트렌드 분석 오류: {str(e)}"
            }
    
    def _execute_sentiment_analyzer(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """감성 분석 도구 실행"""
        
        try:
            text_data = parameters.get("text_data", [])
            context = parameters.get("context", "패션 제품")
            
            if not text_data:
                return {
                    "success": False,
                    "error": "분석할 텍스트 데이터가 없습니다."
                }
            
            # 텍스트 데이터 전처리
            formatted_texts = "\n".join([f"- {text}" for text in text_data[:10]])  # 최대 10개
            
            prompt = f"""다음 텍스트들의 감성을 분석해주세요:

컨텍스트: {context}

텍스트 데이터:
{formatted_texts}

분석 결과를 다음 형식으로 제공해주세요:
1. 전체 감성 점수 (-1.0 ~ 1.0)
2. 긍정/부정/중립 비율
3. 주요 감정 키워드
4. 개선점 제안"""
            
            # LLM 호출
            if self.llm:
                messages = [
                    SystemMessage(content="당신은 소비자 감성 분석 전문가입니다."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                
                return {
                    "success": True,
                    "tool_name": "sentiment_analyzer",
                    "context": context,
                    "analyzed_count": len(text_data),
                    "result": response.content,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return self._get_sample_sentiment_analysis()
                
        except Exception as e:
            return {
                "success": False,
                "error": f"감성 분석 오류: {str(e)}"
            }
    
    def _execute_content_generator(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """콘텐츠 생성 도구 실행"""
        
        try:
            content_type = parameters.get("content_type", "marketing_copy")
            input_data = parameters.get("input_data", {})
            style = parameters.get("style", "professional")
            
            # 콘텐츠 유형별 프롬프트 설정
            prompts = {
                "product_proposal": f"""다음 정보를 바탕으로 제품 기획서를 작성해주세요:

입력 데이터: {json.dumps(input_data, ensure_ascii=False, indent=2)}
스타일: {style}

제품 기획서 형식:
1. 제품명 및 컨셉
2. 타겟 고객 페르소나
3. 주요 특징 및 차별점
4. 가격 전략
5. 마케팅 포인트""",

                "marketing_copy": f"""다음 정보를 바탕으로 마케팅 문구를 작성해주세요:

입력 데이터: {json.dumps(input_data, ensure_ascii=False, indent=2)}
스타일: {style}

다음 형식으로 제공해주세요:
1. 메인 캐치프레이즈 (20자 이내)
2. 서브 카피 (50자 이내)
3. 상세 설명 (100자 이내)
4. 해시태그 (5개)""",

                "social_content": f"""다음 정보를 바탕으로 SNS 콘텐츠를 작성해주세요:

입력 데이터: {json.dumps(input_data, ensure_ascii=False, indent=2)}
스타일: {style}

SNS 포스팅용 텍스트와 해시태그를 작성해주세요.""",

                "blog_post": f"""다음 정보를 바탕으로 블로그 포스트를 작성해주세요:

입력 데이터: {json.dumps(input_data, ensure_ascii=False, indent=2)}
스타일: {style}

블로그 포스트 구조:
1. 제목
2. 서론
3. 본론 (3-4개 섹션)
4. 결론"""
            }
            
            prompt = prompts.get(content_type, prompts["marketing_copy"])
            
            # LLM 호출
            if self.llm:
                messages = [
                    SystemMessage(content="당신은 패션 마케팅 콘텐츠 작성 전문가입니다."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                
                return {
                    "success": True,
                    "tool_name": "content_generator",
                    "content_type": content_type,
                    "style": style,
                    "result": response.content,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return self._get_sample_content_generation(content_type)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"콘텐츠 생성 오류: {str(e)}"
            }
    
    def _execute_data_collector(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 수집 도구 실행"""
        
        try:
            source_type = parameters.get("source_type", "naver_shopping")
            keywords = parameters.get("keywords", [])
            limit = parameters.get("limit", 10)
            
            if not keywords:
                return {
                    "success": False,
                    "error": "검색 키워드가 없습니다."
                }
            
            # 실제 구현에서는 해당 소스에서 데이터를 수집
            # 여기서는 샘플 데이터 반환
            collected_data = self._get_sample_collected_data(source_type, keywords, limit)
            
            return {
                "success": True,
                "tool_name": "data_collector",
                "source_type": source_type,
                "keywords": keywords,
                "collected_count": len(collected_data),
                "result": collected_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"데이터 수집 오류: {str(e)}"
            }
    
    def _get_sample_trend_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """샘플 트렌드 분석 결과"""
        
        analyses = {
            "trend_summary": """
주요 트렌드 분석 결과:

1. 지속가능한 패션
   - 친환경 소재 사용 증가
   - 업사이클링 제품 관심 상승

2. 미니멀 디자인
   - 심플하고 기능적인 디자인 선호
   - 중성적인 컬러 팔레트

3. 편안함 우선
   - 재택근무 증가로 편안한 의류 선호
   - 아웃도어 스타일의 일상화

실행 권장사항:
- 친환경 소재 라인 개발
- 다목적 활용 가능한 아이템 기획
""",
            "seasonal_analysis": "계절별 분석: 여름철 린넨 소재와 밝은 컬러가 주요 트렌드",
            "brand_comparison": "브랜드 비교: 프리미엄 브랜드는 품질과 디자인, 패스트패션은 가격 경쟁력 중심"
        }
        
        return {
            "success": True,
            "tool_name": "trend_analyzer",
            "analysis_type": analysis_type,
            "result": analyses.get(analysis_type, analyses["trend_summary"]),
            "timestamp": datetime.now().isoformat(),
            "note": "샘플 데이터 (LLM 연결 불가)"
        }
    
    def _get_sample_sentiment_analysis(self) -> Dict[str, Any]:
        """샘플 감성 분석 결과"""
        
        return {
            "success": True,
            "tool_name": "sentiment_analyzer",
            "result": """
감성 분석 결과:

1. 전체 감성 점수: 0.6 (긍정적)
2. 감성 분포:
   - 긍정: 65%
   - 중립: 25%  
   - 부정: 10%

3. 주요 감정 키워드:
   - 만족, 예쁘다, 편안하다, 트렌디하다

4. 개선점:
   - 사이즈 가이드 보완 필요
   - 배송 속도 개선 요구
""",
            "timestamp": datetime.now().isoformat(),
            "note": "샘플 데이터 (LLM 연결 불가)"
        }
    
    def _get_sample_content_generation(self, content_type: str) -> Dict[str, Any]:
        """샘플 콘텐츠 생성 결과"""
        
        contents = {
            "product_proposal": """
제품 기획서:

1. 제품명: 에코 린넨 셔츠
2. 컨셉: 지속가능한 여름 기본템
3. 타겟: 20-30대 환경 의식 있는 여성
4. 특징: 100% 오가닉 린넨, 미니멀 디자인
5. 가격: 89,000원
""",
            "marketing_copy": """
마케팅 문구:

1. 메인 카피: "자연이 만든 편안함"
2. 서브 카피: "100% 오가닉 린넨으로 만든 프리미엄 셔츠"
3. 상세 설명: "지구를 생각하는 마음과 편안함을 동시에"
4. 해시태그: #에코패션 #린넨셔츠 #지속가능 #미니멀 #여름룩
""",
            "social_content": "오늘의 #OOTD 🌿 자연스러운 린넨 셔츠로 완성한 에코 스타일링",
            "blog_post": "2024 여름, 지속가능한 패션이 트렌드인 이유"
        }
        
        return {
            "success": True,
            "tool_name": "content_generator",
            "content_type": content_type,
            "result": contents.get(content_type, contents["marketing_copy"]),
            "timestamp": datetime.now().isoformat(),
            "note": "샘플 데이터 (LLM 연결 불가)"
        }
    
    def _get_sample_collected_data(self, source_type: str, keywords: List[str], limit: int) -> List[Dict[str, Any]]:
        """샘플 수집 데이터"""
        
        sample_data = []
        keyword = keywords[0] if keywords else "패션"
        
        for i in range(min(limit, 3)):
            if source_type == "naver_shopping":
                sample_data.append({
                    "title": f"{keyword} 상품 {i+1}",
                    "price": f"{50000 + i*10000}",
                    "brand": f"브랜드{i+1}",
                    "link": f"https://example.com/product{i+1}"
                })
            elif source_type == "web_scraping":
                sample_data.append({
                    "title": f"{keyword} 트렌드 기사 {i+1}",
                    "content": f"{keyword}에 대한 최신 트렌드 분석...",
                    "source": f"패션매거진{i+1}",
                    "url": f"https://example.com/article{i+1}"
                })
            elif source_type == "social_media":
                sample_data.append({
                    "platform": "instagram",
                    "content": f"#{keyword} 오늘의 스타일링 ✨",
                    "likes": 150 + i*50,
                    "comments": 20 + i*5
                })
        
        return sample_data
    
    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """사용 가능한 도구 목록 반환"""
        return self.available_tools
    
    def is_tool_available(self, tool_name: str) -> bool:
        """특정 도구 사용 가능 여부 확인"""
        return tool_name in self.available_tools
    
    def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """여러 도구를 순차적으로 실행하는 워크플로우"""
        
        results = []
        
        for step in workflow_steps:
            tool_name = step.get("tool")
            parameters = step.get("parameters", {})
            
            result = self.call_tool(tool_name, parameters)
            results.append({
                "step": step,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            # 이전 단계의 결과를 다음 단계에 전달 (필요한 경우)
            if result.get("success") and len(workflow_steps) > 1:
                # 결과를 다음 단계의 파라미터에 추가할 수 있음
                pass
        
        return results
    
    def get_sample_trend_analysis(self) -> Dict[str, Any]:
        """테스트용 샘플 트렌드 분석 반환"""
        sample_analysis = self._get_sample_trend_analysis("trend_summary")
        return {
            "main_trends": [
                "지속가능한 패션 확산",
                "미니멀 디자인 선호",
                "편안함 우선 트렌드",
                "Y2K 복고 감성",
                "비비드 컬러 인기"
            ],
            "predictions": [
                "친환경 소재 사용 증가",
                "멀티 기능성 아이템 인기", 
                "개성 표현 아이템 확산"
            ],
            "business_suggestions": [
                "지속가능성 마케팅 강화",
                "편의성 중심 제품 개발",
                "개성 맞춤 서비스 제공"
            ],
            "full_analysis": sample_analysis["result"]
        }
    
    def get_sample_sentiment_analysis(self) -> Dict[str, Any]:
        """테스트용 샘플 감성 분석 반환"""
        return self._get_sample_sentiment_analysis()
    
    def get_sample_content_generation(self, content_type: str = "marketing_copy") -> Dict[str, Any]:
        """테스트용 샘플 콘텐츠 생성 반환"""
        return self._get_sample_content_generation(content_type)
    
    def is_connected(self) -> bool:
        """MCP 클라이언트 연결 상태 확인"""
        return self.llm is not None 