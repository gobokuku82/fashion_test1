"""
외부 도구 테스트

각 외부 연동 도구의 기능을 단위 테스트로 검증합니다.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.naver_api import NaverAPIClient
from tools.web_scraper import WebScraper
from tools.opensearch_client import OpenSearchClient
from tools.mcp_client import MCPClient

class TestNaverAPIClient(unittest.TestCase):
    """네이버 API 클라이언트 테스트"""
    
    def setUp(self):
        self.client = NaverAPIClient()
    
    @patch('requests.get')
    def test_search_shopping_success(self, mock_get):
        """쇼핑 검색 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"title": "테스트 상품", "link": "http://test.com"}]
        }
        mock_get.return_value = mock_response
        
        # 테스트 실행
        result = self.client.search_shopping("테스트")
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
    
    @patch('requests.get')
    def test_search_blog_success(self, mock_get):
        """블로그 검색 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"title": "테스트 블로그", "link": "http://blog.test.com"}]
        }
        mock_get.return_value = mock_response
        
        # 테스트 실행
        result = self.client.search_blog("테스트")
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
    
    def test_get_sample_data(self):
        """샘플 데이터 가져오기 테스트"""
        result = self.client.get_sample_shopping_data()
        
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)

class TestWebScraper(unittest.TestCase):
    """웹 스크래퍼 테스트"""
    
    def setUp(self):
        self.scraper = WebScraper()
    
    @patch('requests.get')
    def test_scrape_fashion_articles_success(self, mock_get):
        """패션 기사 스크래핑 성공 테스트"""
        # Mock HTML 응답
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head><title>Fashion Article</title></head>
            <body>
                <article>
                    <h1>테스트 패션 기사</h1>
                    <p>패션 트렌드에 대한 내용</p>
                </article>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # 테스트 실행
        result = self.scraper.scrape_fashion_articles("http://test-fashion.com")
        
        # 검증
        self.assertIsInstance(result, list)
    
    def test_clean_text(self):
        """텍스트 정리 테스트"""
        dirty_text = "<p>테스트 <strong>텍스트</strong></p>"
        clean_text = self.scraper.clean_text(dirty_text)
        
        self.assertNotIn("<", clean_text)
        self.assertNotIn(">", clean_text)
    
    def test_get_sample_data(self):
        """샘플 데이터 가져오기 테스트"""
        result = self.scraper.get_sample_articles()
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

class TestOpenSearchClient(unittest.TestCase):
    """OpenSearch 클라이언트 테스트"""
    
    def setUp(self):
        self.client = OpenSearchClient()
    
    @patch('opensearchpy.OpenSearch')
    def test_index_document_success(self, mock_opensearch):
        """문서 인덱싱 성공 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_client.index.return_value = {"result": "created"}
        mock_opensearch.return_value = mock_client
        
        # OpenSearch 클라이언트 재설정
        self.client.client = mock_client
        
        # 테스트 실행
        result = self.client.index_document("test_index", {"title": "테스트"})
        
        # 검증
        self.assertTrue(result)
    
    @patch('opensearchpy.OpenSearch')
    def test_search_documents_success(self, mock_opensearch):
        """문서 검색 성공 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_client.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_source": {"title": "테스트"}}]
            }
        }
        mock_opensearch.return_value = mock_client
        
        # OpenSearch 클라이언트 재설정
        self.client.client = mock_client
        
        # 테스트 실행
        result = self.client.search_documents("test_index", "테스트")
        
        # 검증
        self.assertIsInstance(result, list)

class TestMCPClient(unittest.TestCase):
    """MCP 클라이언트 테스트"""
    
    def setUp(self):
        self.client = MCPClient()
    
    @patch('openai.ChatCompletion.create')
    def test_analyze_trends_success(self, mock_openai):
        """트렌드 분석 성공 테스트"""
        # Mock 응답 설정
        mock_openai.return_value = {
            "choices": [{
                "message": {
                    "content": '{"main_trends": ["테스트 트렌드"], "predictions": ["예측"]}'
                }
            }],
            "usage": {"total_tokens": 100}
        }
        
        # 테스트 실행
        result = self.client.analyze_trends("테스트 데이터")
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertIn("main_trends", result)
    
    def test_get_sample_analysis(self):
        """샘플 분석 결과 테스트"""
        result = self.client.get_sample_trend_analysis()
        
        self.assertIsInstance(result, dict)
        self.assertIn("main_trends", result)

if __name__ == '__main__':
    unittest.main() 