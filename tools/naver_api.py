"""
Fashion AI Automation System - Naver API Client
"""

import requests
import urllib.parse
from typing import Dict, List, Any, Optional
from datetime import datetime

from config.settings import settings


class NaverAPIClient:
    """네이버 API 연동 클라이언트"""
    
    def __init__(self):
        try:
            # 설정에서 API 키 가져오기
            self.client_id = settings.naver_client_id
            self.client_secret = settings.naver_client_secret
            
            # Streamlit secrets에서 가져오기 시도
            if not self.client_id or not self.client_secret:
                try:
                    import streamlit as st
                    self.client_id = st.secrets.get("NAVER_CLIENT_ID", "")
                    self.client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")
                except:
                    pass
            
            # API 엔드포인트
            self.base_url = "https://openapi.naver.com/v1"
            self.headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret,
                "Content-Type": "application/json"
            }
            
        except Exception as e:
            print(f"NaverAPIClient 초기화 오류: {str(e)}")
            self.client_id = ""
            self.client_secret = ""
            self.headers = {}
    
    def search_shopping(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> Optional[Dict[str, Any]]:
        """네이버 쇼핑 검색 API 호출"""
        
        try:
            if not self.client_id or not self.client_secret:
                print("네이버 API 키가 설정되지 않았습니다.")
                return self._get_sample_shopping_data(query)
            
            # URL 인코딩
            encoded_query = urllib.parse.quote(query)
            
            # API 호출
            url = f"{self.base_url}/search/shop.json"
            params = {
                "query": encoded_query,
                "display": display,
                "start": start,
                "sort": sort
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"네이버 쇼핑 API 오류: {str(e)}")
            return self._get_sample_shopping_data(query)
        except Exception as e:
            print(f"네이버 쇼핑 검색 오류: {str(e)}")
            return self._get_sample_shopping_data(query)
    
    def search_blog(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> Optional[Dict[str, Any]]:
        """네이버 블로그 검색 API 호출"""
        
        try:
            if not self.client_id or not self.client_secret:
                print("네이버 API 키가 설정되지 않았습니다.")
                return self._get_sample_blog_data(query)
            
            # URL 인코딩
            encoded_query = urllib.parse.quote(query)
            
            # API 호출
            url = f"{self.base_url}/search/blog.json"
            params = {
                "query": encoded_query,
                "display": display,
                "start": start,
                "sort": sort
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"네이버 블로그 API 오류: {str(e)}")
            return self._get_sample_blog_data(query)
        except Exception as e:
            print(f"네이버 블로그 검색 오류: {str(e)}")
            return self._get_sample_blog_data(query)
    
    def search_news(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> Optional[Dict[str, Any]]:
        """네이버 뉴스 검색 API 호출"""
        
        try:
            if not self.client_id or not self.client_secret:
                print("네이버 API 키가 설정되지 않았습니다.")
                return self._get_sample_news_data(query)
            
            # URL 인코딩
            encoded_query = urllib.parse.quote(query)
            
            # API 호출
            url = f"{self.base_url}/search/news.json"
            params = {
                "query": encoded_query,
                "display": display,
                "start": start,
                "sort": sort
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"네이버 뉴스 API 오류: {str(e)}")
            return self._get_sample_news_data(query)
        except Exception as e:
            print(f"네이버 뉴스 검색 오류: {str(e)}")
            return self._get_sample_news_data(query)
    
    def _get_sample_shopping_data(self, query: str) -> Dict[str, Any]:
        """샘플 쇼핑 데이터 반환 (API 키가 없을 때)"""
        
        sample_items = [
            {
                "title": f"<b>{query}</b> 2024 여름 신상품",
                "link": "https://shopping.naver.com/example1",
                "image": "https://example.com/image1.jpg",
                "lprice": "89000",
                "hprice": "120000",
                "mallName": "ZARA",
                "productId": "123456789",
                "productType": "1",
                "brand": "ZARA",
                "maker": "ZARA",
                "category1": "패션의류",
                "category2": "여성의류",
                "category3": "원피스",
                "category4": "미니원피스"
            },
            {
                "title": f"트렌디한 <b>{query}</b> 스타일",
                "link": "https://shopping.naver.com/example2",
                "image": "https://example.com/image2.jpg",
                "lprice": "45000",
                "hprice": "65000",
                "mallName": "UNIQLO",
                "productId": "987654321",
                "productType": "1",
                "brand": "UNIQLO",
                "maker": "UNIQLO",
                "category1": "패션의류",
                "category2": "여성의류",
                "category3": "상의",
                "category4": "티셔츠"
            },
            {
                "title": f"<b>{query}</b> 미니멀 디자인",
                "link": "https://shopping.naver.com/example3",
                "image": "https://example.com/image3.jpg",
                "lprice": "129000",
                "hprice": "180000",
                "mallName": "COS",
                "productId": "456789123",
                "productType": "1",
                "brand": "COS",
                "maker": "COS",
                "category1": "패션의류",
                "category2": "여성의류",
                "category3": "아우터",
                "category4": "재킷"
            }
        ]
        
        return {
            "lastBuildDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"),
            "total": len(sample_items),
            "start": 1,
            "display": len(sample_items),
            "items": sample_items
        }
    
    def _get_sample_blog_data(self, query: str) -> Dict[str, Any]:
        """샘플 블로그 데이터 반환"""
        
        sample_items = [
            {
                "title": f"2024 {query} 트렌드 완벽 가이드",
                "link": "https://blog.naver.com/example1",
                "description": f"{query} 관련 최신 트렌드를 소개합니다. 이번 시즌 주목받는 스타일과 코디법을 자세히 알아보세요.",
                "bloggername": "패션인플루언서",
                "bloggerlink": "https://blog.naver.com/fashionista",
                "postdate": datetime.now().strftime("%Y%m%d")
            },
            {
                "title": f"{query} 스타일링 팁과 추천 아이템",
                "link": "https://blog.naver.com/example2",
                "description": f"실용적인 {query} 스타일링 방법과 코디에 필요한 필수 아이템들을 추천해드립니다.",
                "bloggername": "스타일블로거",
                "bloggerlink": "https://blog.naver.com/styleblogger",
                "postdate": datetime.now().strftime("%Y%m%d")
            }
        ]
        
        return {
            "lastBuildDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"),
            "total": len(sample_items),
            "start": 1,
            "display": len(sample_items),
            "items": sample_items
        }
    
    def _get_sample_news_data(self, query: str) -> Dict[str, Any]:
        """샘플 뉴스 데이터 반환"""
        
        sample_items = [
            {
                "title": f"2024 {query} 패션 트렌드 전망",
                "originallink": "https://news.example.com/fashion1",
                "link": "https://news.naver.com/example1",
                "description": f"올해 {query} 트렌드가 패션 업계에 미치는 영향과 소비자 반응을 분석한 보고서가 발표되었습니다.",
                "pubDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            },
            {
                "title": f"{query} 브랜드 신규 컬렉션 출시",
                "originallink": "https://news.example.com/fashion2",
                "link": "https://news.naver.com/example2",
                "description": f"주요 {query} 브랜드들이 신규 컬렉션을 공개하며 새로운 트렌드를 제시하고 있습니다.",
                "pubDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            }
        ]
        
        return {
            "lastBuildDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"),
            "total": len(sample_items),
            "start": 1,
            "display": len(sample_items),
            "items": sample_items
        }
    
    def get_fashion_trends(self, category: str = "패션") -> Dict[str, Any]:
        """패션 트렌드 종합 검색"""
        
        trend_queries = [
            f"{category} 트렌드",
            f"{category} 신상품",
            f"{category} 스타일링",
            f"2024 {category}"
        ]
        
        all_results = {
            "shopping": [],
            "blog": [],
            "news": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for query in trend_queries:
            # 쇼핑 데이터
            shopping_result = self.search_shopping(query, display=5)
            if shopping_result and "items" in shopping_result:
                all_results["shopping"].extend(shopping_result["items"])
            
            # 블로그 데이터
            blog_result = self.search_blog(query, display=3)
            if blog_result and "items" in blog_result:
                all_results["blog"].extend(blog_result["items"])
            
            # 뉴스 데이터
            news_result = self.search_news(query, display=2)
            if news_result and "items" in news_result:
                all_results["news"].extend(news_result["items"])
        
        return all_results
    
    def get_sample_shopping_data(self) -> Dict[str, Any]:
        """테스트용 샘플 쇼핑 데이터 반환"""
        return self._get_sample_shopping_data("패션")
    
    def get_sample_blog_data(self) -> Dict[str, Any]:
        """테스트용 샘플 블로그 데이터 반환"""
        return self._get_sample_blog_data("패션")
    
    def get_sample_news_data(self) -> Dict[str, Any]:
        """테스트용 샘플 뉴스 데이터 반환"""
        return self._get_sample_news_data("패션")
    
    def is_api_available(self) -> bool:
        """API 사용 가능 여부 확인"""
        return bool(self.client_id and self.client_secret) 