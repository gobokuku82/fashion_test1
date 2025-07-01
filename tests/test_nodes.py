"""
LangGraph 노드 테스트

각 노드의 기능을 단위 테스트로 검증합니다.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_agents.state import FashionState
from langgraph_agents.nodes.data_collection import DataCollectionNode
from langgraph_agents.nodes.trend_analysis import TrendAnalysisNode
from langgraph_agents.nodes.sentiment_analysis import SentimentAnalysisNode
from langgraph_agents.nodes.content_generation import ContentGenerationNode

class TestDataCollectionNode(unittest.TestCase):
    """데이터 수집 노드 테스트"""
    
    def setUp(self):
        self.node = DataCollectionNode()
        self.sample_state = FashionState(
            session_id="test_session",
            user_request="테스트 요청",
            keywords=["테스트", "패션"],
            collected_data={},
            analysis_results={},
            generated_content={},
            feedback_history=[],
            token_usage={"total_tokens": 0, "cost": 0.0},
            human_feedback_required=False,
            feedback_count=0
        )
    
    @patch('tools.naver_api.NaverAPIClient')
    def test_collect_data_success(self, mock_naver):
        """데이터 수집 성공 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_client.search_shopping.return_value = {"items": [{"title": "테스트 상품"}]}
        mock_client.search_blog.return_value = {"items": [{"title": "테스트 블로그"}]}
        mock_naver.return_value = mock_client
        
        # 테스트 실행
        result = asyncio.run(self.node.execute(self.sample_state))
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertIn("collected_data", result)
    
    def test_extract_keywords(self):
        """키워드 추출 테스트"""
        keywords = self.node.extract_keywords("패션 트렌드 분석 테스트")
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)

class TestTrendAnalysisNode(unittest.TestCase):
    """트렌드 분석 노드 테스트"""
    
    def setUp(self):
        self.node = TrendAnalysisNode()
        self.sample_state = FashionState(
            session_id="test_session",
            user_request="트렌드 분석 테스트",
            keywords=["여름", "패션"],
            collected_data={"naver_shopping": [{"title": "여름 원피스"}]},
            analysis_results={},
            generated_content={},
            feedback_history=[],
            token_usage={"total_tokens": 0, "cost": 0.0},
            human_feedback_required=False,
            feedback_count=0
        )
    
    @patch('tools.mcp_client.MCPClient')
    def test_analyze_trends(self, mock_mcp):
        """트렌드 분석 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_client.analyze_trends.return_value = {
            "main_trends": ["여름 패션 트렌드"],
            "predictions": ["여름 원피스 인기 예상"]
        }
        mock_mcp.return_value = mock_client
        
        # 테스트 실행
        result = asyncio.run(self.node.execute(self.sample_state))
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertIn("analysis_results", result)

class TestSentimentAnalysisNode(unittest.TestCase):
    """감성 분석 노드 테스트"""
    
    def setUp(self):
        self.node = SentimentAnalysisNode()
        self.sample_state = FashionState(
            session_id="test_session",
            user_request="감성 분석 테스트",
            keywords=["리뷰"],
            collected_data={"reviews": [{"text": "정말 좋은 제품입니다"}]},
            analysis_results={},
            generated_content={},
            feedback_history=[],
            token_usage={"total_tokens": 0, "cost": 0.0},
            human_feedback_required=False,
            feedback_count=0
        )
    
    @patch('tools.mcp_client.MCPClient')
    def test_analyze_sentiment(self, mock_mcp):
        """감성 분석 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_client.analyze_sentiment.return_value = {
            "overall_sentiment": "positive",
            "sentiment_score": 0.8
        }
        mock_mcp.return_value = mock_client
        
        # 테스트 실행
        result = asyncio.run(self.node.execute(self.sample_state))
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertIn("analysis_results", result)

class TestContentGenerationNode(unittest.TestCase):
    """콘텐츠 생성 노드 테스트"""
    
    def setUp(self):
        self.node = ContentGenerationNode()
        self.sample_state = FashionState(
            session_id="test_session",
            user_request="제품 기획서 생성",
            keywords=["여름", "원피스"],
            collected_data={},
            analysis_results={"main_trends": ["여름 패션"]},
            generated_content={},
            feedback_history=[],
            token_usage={"total_tokens": 0, "cost": 0.0},
            human_feedback_required=False,
            feedback_count=0
        )
    
    @patch('tools.mcp_client.MCPClient')
    def test_generate_content(self, mock_mcp):
        """콘텐츠 생성 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_client.generate_content.return_value = {
            "product_plan": "여름 원피스 기획서",
            "marketing_copy": "시원한 여름 원피스"
        }
        mock_mcp.return_value = mock_client
        
        # 테스트 실행
        result = asyncio.run(self.node.execute(self.sample_state))
        
        # 검증
        self.assertIsInstance(result, dict)
        self.assertIn("generated_content", result)

if __name__ == '__main__':
    unittest.main() 