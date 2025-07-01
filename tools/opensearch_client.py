"""
Fashion AI Automation System - OpenSearch Client
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

try:
    from opensearchpy import OpenSearch, RequestsHttpConnection
    OPENSEARCH_AVAILABLE = True
except ImportError:
    print("opensearch-py 패키지가 설치되지 않았습니다. pip install opensearch-py")
    OPENSEARCH_AVAILABLE = False

from config.settings import settings


class OpenSearchClient:
    """OpenSearch 연동 클라이언트"""
    
    def __init__(self):
        try:
            # 설정에서 연결 정보 가져오기
            self.host = settings.opensearch_host
            self.username = settings.opensearch_username
            self.password = settings.opensearch_password
            
            # Streamlit secrets에서 가져오기 시도
            if not self.host:
                try:
                    import streamlit as st
                    self.host = st.secrets.get("OPENSEARCH_HOST", "")
                    self.username = st.secrets.get("OPENSEARCH_USERNAME", "")
                    self.password = st.secrets.get("OPENSEARCH_PASSWORD", "")
                except:
                    pass
            
            self.client = None
            self.index_prefix = settings.opensearch_index_prefix
            
            if OPENSEARCH_AVAILABLE and self.host:
                self._connect()
            else:
                print("OpenSearch 연결 정보가 없거나 라이브러리가 설치되지 않았습니다.")
                
        except Exception as e:
            print(f"OpenSearchClient 초기화 오류: {str(e)}")
            self.client = None
    
    def _connect(self):
        """OpenSearch에 연결"""
        
        try:
            # 연결 설정
            auth = (self.username, self.password) if self.username and self.password else None
            
            self.client = OpenSearch(
                hosts=[self.host],
                http_auth=auth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=30
            )
            
            # 연결 테스트
            if self.client.ping():
                print("OpenSearch 연결 성공")
            else:
                print("OpenSearch 연결 실패")
                self.client = None
                
        except Exception as e:
            print(f"OpenSearch 연결 오류: {str(e)}")
            self.client = None
    
    def create_index(self, index_name: str, mapping: Optional[Dict[str, Any]] = None) -> bool:
        """인덱스 생성"""
        
        try:
            if not self.client:
                print("OpenSearch 클라이언트가 연결되지 않았습니다.")
                return False
            
            # 기본 매핑 설정
            if not mapping:
                mapping = self._get_default_mapping()
            
            # 인덱스가 이미 존재하는지 확인
            if self.client.indices.exists(index=index_name):
                print(f"인덱스 '{index_name}'이 이미 존재합니다.")
                return True
            
            # 인덱스 생성
            response = self.client.indices.create(
                index=index_name,
                body=mapping
            )
            
            print(f"인덱스 '{index_name}' 생성 완료")
            return True
            
        except Exception as e:
            print(f"인덱스 생성 오류: {str(e)}")
            return False
    
    def _get_default_mapping(self) -> Dict[str, Any]:
        """기본 인덱스 매핑 반환"""
        
        return {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "korean": {
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "session_id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "user_request": {
                        "type": "text",
                        "analyzer": "korean"
                    },
                    "target_category": {"type": "keyword"},
                    "collected_data": {
                        "type": "object",
                        "properties": {
                            "naver_shopping": {"type": "object"},
                            "web_scraping": {"type": "object"},
                            "social_media": {"type": "object"},
                            "keywords_used": {"type": "keyword"}
                        }
                    },
                    "trend_analysis": {
                        "type": "object",
                        "properties": {
                            "raw_analysis": {
                                "type": "text",
                                "analyzer": "korean"
                            },
                            "key_trends": {"type": "keyword"},
                            "summary": {
                                "type": "text",
                                "analyzer": "korean"
                            }
                        }
                    },
                    "sentiment_analysis": {
                        "type": "object",
                        "properties": {
                            "overall_sentiment_score": {"type": "float"},
                            "sentiment_distribution": {"type": "object"},
                            "key_emotions": {"type": "keyword"}
                        }
                    },
                    "product_proposal": {
                        "type": "text",
                        "analyzer": "korean"
                    },
                    "marketing_copy": {
                        "type": "text",
                        "analyzer": "korean"
                    },
                    "content_suggestions": {"type": "keyword"},
                    "processing_steps": {"type": "keyword"},
                    "token_usage": {"type": "object"},
                    "costs": {"type": "object"},
                    "errors": {"type": "keyword"}
                }
            }
        }
    
    def index_document(self, index_name: str, document: Dict[str, Any], doc_id: Optional[str] = None) -> bool:
        """문서 인덱싱"""
        
        try:
            if not self.client:
                print("OpenSearch 클라이언트가 연결되지 않았습니다.")
                return False
            
            # 인덱스가 존재하지 않으면 생성
            if not self.client.indices.exists(index=index_name):
                self.create_index(index_name)
            
            # 문서 인덱싱
            response = self.client.index(
                index=index_name,
                body=document,
                id=doc_id,
                refresh=True
            )
            
            print(f"문서 인덱싱 완료: {response['_id']}")
            return True
            
        except Exception as e:
            print(f"문서 인덱싱 오류: {str(e)}")
            return False
    
    def search_documents(self, index_name: str, query: Dict[str, Any], size: int = 10) -> Optional[Dict[str, Any]]:
        """문서 검색"""
        
        try:
            if not self.client:
                print("OpenSearch 클라이언트가 연결되지 않았습니다.")
                return self._get_sample_search_results()
            
            response = self.client.search(
                index=index_name,
                body=query,
                size=size
            )
            
            return response
            
        except Exception as e:
            print(f"문서 검색 오류: {str(e)}")
            return self._get_sample_search_results()
    
    def search_by_keyword(self, index_name: str, keyword: str, fields: List[str] = None) -> Optional[List[Dict[str, Any]]]:
        """키워드로 문서 검색"""
        
        try:
            if not fields:
                fields = ["user_request", "trend_analysis.raw_analysis", "product_proposal", "marketing_copy"]
            
            query = {
                "query": {
                    "multi_match": {
                        "query": keyword,
                        "fields": fields,
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                "sort": [
                    {"timestamp": {"order": "desc"}}
                ]
            }
            
            response = self.search_documents(index_name, query)
            
            if response and "hits" in response:
                return [hit["_source"] for hit in response["hits"]["hits"]]
            
            return []
            
        except Exception as e:
            print(f"키워드 검색 오류: {str(e)}")
            return []
    
    def get_recent_analyses(self, index_name: str, days: int = 7, size: int = 10) -> List[Dict[str, Any]]:
        """최근 분석 결과 조회"""
        
        try:
            query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": f"now-{days}d/d",
                            "lte": "now/d"
                        }
                    }
                },
                "sort": [
                    {"timestamp": {"order": "desc"}}
                ]
            }
            
            response = self.search_documents(index_name, query, size)
            
            if response and "hits" in response:
                return [hit["_source"] for hit in response["hits"]["hits"]]
            
            return []
            
        except Exception as e:
            print(f"최근 분석 조회 오류: {str(e)}")
            return []
    
    def get_trend_summary(self, index_name: str, category: str = None) -> Dict[str, Any]:
        """트렌드 요약 통계"""
        
        try:
            # 기본 집계 쿼리
            query = {
                "size": 0,
                "aggs": {
                    "category_stats": {
                        "terms": {
                            "field": "target_category",
                            "size": 10
                        }
                    },
                    "sentiment_avg": {
                        "avg": {
                            "field": "sentiment_analysis.overall_sentiment_score"
                        }
                    },
                    "daily_count": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "day",
                            "format": "yyyy-MM-dd"
                        }
                    }
                }
            }
            
            # 카테고리 필터 추가
            if category:
                query["query"] = {
                    "term": {
                        "target_category": category
                    }
                }
            
            response = self.search_documents(index_name, query)
            
            if response and "aggregations" in response:
                return response["aggregations"]
            
            return {}
            
        except Exception as e:
            print(f"트렌드 요약 조회 오류: {str(e)}")
            return {}
    
    def delete_old_data(self, index_name: str, days: int = 30) -> bool:
        """오래된 데이터 삭제"""
        
        try:
            if not self.client:
                return False
            
            query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "lt": f"now-{days}d/d"
                        }
                    }
                }
            }
            
            response = self.client.delete_by_query(
                index=index_name,
                body=query
            )
            
            deleted_count = response.get("deleted", 0)
            print(f"{deleted_count}개의 오래된 문서를 삭제했습니다.")
            
            return True
            
        except Exception as e:
            print(f"오래된 데이터 삭제 오류: {str(e)}")
            return False
    
    def _get_sample_search_results(self) -> Dict[str, Any]:
        """샘플 검색 결과 반환 (OpenSearch 연결 불가 시)"""
        
        return {
            "took": 5,
            "timed_out": False,
            "hits": {
                "total": {"value": 2, "relation": "eq"},
                "max_score": 1.0,
                "hits": [
                    {
                        "_id": "sample1",
                        "_score": 1.0,
                        "_source": {
                            "session_id": "fashion_ai_sample_001",
                            "timestamp": datetime.now().isoformat(),
                            "user_request": "올여름 트렌드 분석해줘",
                            "target_category": "여름패션",
                            "trend_analysis": {
                                "summary": "2024 여름 주요 트렌드는 린넨 소재와 밝은 컬러가 특징입니다."
                            }
                        }
                    },
                    {
                        "_id": "sample2",
                        "_score": 0.8,
                        "_source": {
                            "session_id": "fashion_ai_sample_002",
                            "timestamp": datetime.now().isoformat(),
                            "user_request": "마케팅 문구 만들어줘",
                            "target_category": "액세서리",
                            "marketing_copy": "트렌디한 여름 액세서리로 스타일을 완성하세요!"
                        }
                    }
                ]
            }
        }
    
    def is_connected(self) -> bool:
        """OpenSearch 연결 상태 확인"""
        return self.client is not None and OPENSEARCH_AVAILABLE 