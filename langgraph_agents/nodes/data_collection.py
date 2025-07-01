"""
Fashion AI Automation System - Data Collection Node
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime, timedelta

from ..state import FashionState, update_state_step, add_error_to_state
from tools.naver_api import NaverAPIClient
from tools.web_scraper import WebScraper
from tools.opensearch_client import OpenSearchClient


class DataCollectionNode:
    """데이터 수집을 담당하는 LangGraph 노드"""
    
    def __init__(self):
        self.naver_client = NaverAPIClient()
        self.web_scraper = WebScraper()
        self.opensearch_client = OpenSearchClient()
    
    def execute(self, state: FashionState) -> FashionState:
        """데이터 수집 노드 실행"""
        
        try:
            state = update_state_step(state, "데이터 수집 노드 실행 시작")
            
            # 사용자 요청 분석
            user_request = state["user_request"]
            target_category = state["target_category"]
            
            # 키워드 추출
            keywords = self._extract_keywords(user_request, target_category)
            
            # 병렬로 여러 소스에서 데이터 수집
            collected_data = self._collect_data_from_sources(keywords, state)
            
            # 상태 업데이트
            state["collected_data"] = collected_data
            state["naver_shopping_data"] = collected_data.get("naver_shopping", [])
            state["web_scraping_data"] = collected_data.get("web_scraping", [])
            state["social_media_data"] = collected_data.get("social_media", [])
            
            # OpenSearch에 저장
            self._save_to_opensearch(collected_data, state)
            
            state = update_state_step(state, f"데이터 수집 완료: {len(collected_data)} 건")
            
        except Exception as e:
            state = add_error_to_state(state, f"데이터 수집 중 오류: {str(e)}")
        
        return state
    
    def _extract_keywords(self, user_request: str, target_category: str) -> List[str]:
        """사용자 요청과 카테고리에서 키워드 추출"""
        
        # 기본 패션 키워드
        base_keywords = [target_category] if target_category != "전체" else []
        
        # 요청에서 키워드 추출 (간단한 방식)
        common_fashion_terms = [
            "트렌드", "패션", "스타일", "의류", "액세서리", "신발", "가방",
            "여름", "겨울", "봄", "가을", "시즌",
            "20대", "30대", "40대", "여성", "남성",
            "캐주얼", "포멀", "스포츠", "빈티지", "미니멀"
        ]
        
        extracted_keywords = []
        for term in common_fashion_terms:
            if term in user_request:
                extracted_keywords.append(term)
        
        # 키워드가 없으면 기본값 사용
        if not extracted_keywords:
            extracted_keywords = ["패션", "트렌드"]
        
        return base_keywords + extracted_keywords
    
    def _collect_data_from_sources(self, keywords: List[str], state: FashionState) -> Dict[str, Any]:
        """여러 소스에서 데이터 수집"""
        
        collected_data = {
            "naver_shopping": [],
            "web_scraping": [],
            "social_media": [],
            "collection_timestamp": datetime.now().isoformat(),
            "keywords_used": keywords
        }
        
        try:
            # 네이버 쇼핑 API 데이터 수집
            for keyword in keywords[:3]:  # 최대 3개 키워드만 사용
                try:
                    naver_data = self.naver_client.search_shopping(keyword, display=20)
                    if naver_data:
                        collected_data["naver_shopping"].extend(naver_data.get("items", []))
                except Exception as e:
                    state = add_error_to_state(state, f"네이버 API 오류 ({keyword}): {str(e)}")
            
            # 웹 스크래핑 (예: 패션 블로그, 뉴스)
            try:
                fashion_urls = [
                    "https://www.vogue.co.kr",
                    "https://www.elle.co.kr",
                    "https://www.harpersbazaar.co.kr"
                ]
                
                for url in fashion_urls:
                    try:
                        scraped_data = self.web_scraper.scrape_fashion_content(url, keywords[0])
                        if scraped_data:
                            collected_data["web_scraping"].append(scraped_data)
                    except Exception as e:
                        state = add_error_to_state(state, f"웹 스크래핑 오류 ({url}): {str(e)}")
            
            except Exception as e:
                state = add_error_to_state(state, f"웹 스크래핑 전체 오류: {str(e)}")
            
            # SNS 데이터 (모의 데이터 - 실제로는 Instagram, Twitter API 사용)
            try:
                social_data = self._collect_social_media_data(keywords)
                collected_data["social_media"] = social_data
            except Exception as e:
                state = add_error_to_state(state, f"SNS 데이터 수집 오류: {str(e)}")
        
        except Exception as e:
            state = add_error_to_state(state, f"데이터 수집 전체 오류: {str(e)}")
        
        return collected_data
    
    def _collect_social_media_data(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """SNS 데이터 수집 (모의 데이터)"""
        
        # 실제 환경에서는 Instagram Graph API, Twitter API 등을 사용
        sample_social_data = []
        
        for keyword in keywords[:2]:
            sample_social_data.extend([
                {
                    "platform": "instagram",
                    "keyword": keyword,
                    "content": f"#{keyword} 올해 정말 핫한 아이템! 너무 예뻐서 바로 주문했어요 ✨",
                    "likes": 156,
                    "comments": 23,
                    "hashtags": [f"#{keyword}", "#패션", "#스타일", "#OOTD"],
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
                },
                {
                    "platform": "instagram", 
                    "keyword": keyword,
                    "content": f"{keyword} 스타일링 어떻게 생각하세요? 피드백 부탁드려요!",
                    "likes": 89,
                    "comments": 45,
                    "hashtags": [f"#{keyword}", "#코디", "#스타일링"],
                    "timestamp": (datetime.now() - timedelta(hours=5)).isoformat()
                }
            ])
        
        return sample_social_data
    
    def _save_to_opensearch(self, collected_data: Dict[str, Any], state: FashionState):
        """수집된 데이터를 OpenSearch에 저장"""
        
        try:
            session_id = state["session_id"]
            timestamp = datetime.now()
            
            # 인덱스 이름 생성
            index_name = f"fashion_data_{timestamp.strftime('%Y_%m')}"
            
            # 문서 구성
            document = {
                "session_id": session_id,
                "timestamp": timestamp.isoformat(),
                "user_request": state["user_request"],
                "target_category": state["target_category"],
                "collected_data": collected_data,
                "data_summary": {
                    "naver_shopping_count": len(collected_data.get("naver_shopping", [])),
                    "web_scraping_count": len(collected_data.get("web_scraping", [])),
                    "social_media_count": len(collected_data.get("social_media", [])),
                }
            }
            
            # OpenSearch에 저장
            self.opensearch_client.index_document(index_name, document)
            
            state = update_state_step(state, f"데이터 OpenSearch 저장 완료: {index_name}")
            
        except Exception as e:
            state = add_error_to_state(state, f"OpenSearch 저장 오류: {str(e)}")
    
    def get_sample_data(self) -> Dict[str, Any]:
        """샘플 데이터 반환 (개발/테스트용)"""
        
        return {
            "naver_shopping": [
                {
                    "title": "2024 여름 트렌드 린넨 셔츠",
                    "price": "89000",
                    "brand": "ZARA",
                    "category": "여성의류",
                    "link": "https://example.com/product1"
                },
                {
                    "title": "미니멀 크롭 티셔츠",
                    "price": "35000", 
                    "brand": "UNIQLO",
                    "category": "여성의류",
                    "link": "https://example.com/product2"
                }
            ],
            "web_scraping": [
                {
                    "source": "VOGUE Korea",
                    "title": "2024 SS 패션위크 트렌드 리포트",
                    "content": "올 여름 가장 주목받는 트렌드는 지속가능한 패션과 미니멀 디자인...",
                    "url": "https://example.com/article1"
                }
            ],
            "social_media": [
                {
                    "platform": "instagram",
                    "content": "오늘의 #OOTD 여름 린넨 스타일링 ☀️",
                    "likes": 234,
                    "comments": 45
                }
            ]
        } 