"""
Data Collection DAG

주기적으로 다양한 소스에서 데이터를 수집하는 Airflow DAG
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.naver_api import NaverAPIClient
from tools.web_scraper import WebScraper
from tools.opensearch_client import OpenSearchClient
from utils.logger import setup_logger

logger = setup_logger(__name__)

# DAG 기본 설정
default_args = {
    'owner': 'fashion-ai-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10)
}

# DAG 정의
dag = DAG(
    'data_collection_pipeline',
    default_args=default_args,
    description='Periodic data collection from various sources',
    schedule_interval=timedelta(hours=6),  # 6시간마다 실행
    catchup=False,
    max_active_runs=1
)

def collect_naver_data(**context):
    """네이버 API 데이터 수집"""
    try:
        logger.info("네이버 API 데이터 수집 시작")
        
        naver_client = NaverAPIClient()
        
        # 패션 관련 키워드들
        keywords = ["패션", "트렌드", "스타일", "옷", "신상품"]
        
        collected_data = []
        for keyword in keywords:
            # 쇼핑 데이터
            shopping_data = naver_client.search_shopping(keyword, display=20)
            collected_data.extend(shopping_data.get('items', []))
            
            # 블로그 데이터
            blog_data = naver_client.search_blog(keyword, display=20)
            collected_data.extend(blog_data.get('items', []))
        
        logger.info(f"네이버 API에서 {len(collected_data)}개 데이터 수집")
        
        # OpenSearch에 저장
        opensearch_client = OpenSearchClient()
        for item in collected_data:
            opensearch_client.index_document("naver_data", item)
        
        return f"네이버 데이터 {len(collected_data)}개 수집 완료"
        
    except Exception as e:
        logger.error(f"네이버 데이터 수집 실패: {e}")
        raise

def collect_web_data(**context):
    """웹 스크래핑 데이터 수집"""
    try:
        logger.info("웹 스크래핑 데이터 수집 시작")
        
        scraper = WebScraper()
        
        # 패션 사이트들에서 데이터 수집
        fashion_sites = [
            "https://www.vogue.com/fashion",
            "https://www.elle.com/fashion",
            "https://www.harpersbazaar.com/fashion"
        ]
        
        collected_articles = []
        for site in fashion_sites:
            try:
                articles = scraper.scrape_fashion_articles(site)
                collected_articles.extend(articles)
            except Exception as e:
                logger.warning(f"사이트 {site} 스크래핑 실패: {e}")
                continue
        
        logger.info(f"웹에서 {len(collected_articles)}개 기사 수집")
        
        # OpenSearch에 저장
        opensearch_client = OpenSearchClient()
        for article in collected_articles:
            opensearch_client.index_document("web_articles", article)
        
        return f"웹 데이터 {len(collected_articles)}개 수집 완료"
        
    except Exception as e:
        logger.error(f"웹 데이터 수집 실패: {e}")
        raise

def update_search_index(**context):
    """검색 인덱스 업데이트"""
    try:
        logger.info("검색 인덱스 업데이트 시작")
        
        opensearch_client = OpenSearchClient()
        
        # 인덱스 최적화
        opensearch_client.refresh_index("naver_data")
        opensearch_client.refresh_index("web_articles")
        
        # 통계 정보 수집
        naver_count = opensearch_client.get_document_count("naver_data")
        web_count = opensearch_client.get_document_count("web_articles")
        
        logger.info(f"인덱스 업데이트 완료 - 네이버: {naver_count}, 웹: {web_count}")
        
        return f"인덱스 업데이트 완료 (네이버: {naver_count}, 웹: {web_count})"
        
    except Exception as e:
        logger.error(f"인덱스 업데이트 실패: {e}")
        raise

def cleanup_old_data(**context):
    """오래된 데이터 정리"""
    try:
        logger.info("오래된 데이터 정리 시작")
        
        opensearch_client = OpenSearchClient()
        
        # 30일 이전 데이터 삭제
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # 실제로는 날짜 필드를 기준으로 삭제 쿼리 실행
        # 여기서는 샘플 구현
        deleted_count = 0  # opensearch_client.delete_old_documents(cutoff_date)
        
        logger.info(f"오래된 데이터 {deleted_count}개 삭제")
        
        return f"데이터 정리 완료 ({deleted_count}개 삭제)"
        
    except Exception as e:
        logger.error(f"데이터 정리 실패: {e}")
        raise

# 태스크 정의
collect_naver_task = PythonOperator(
    task_id='collect_naver_data',
    python_callable=collect_naver_data,
    dag=dag
)

collect_web_task = PythonOperator(
    task_id='collect_web_data',
    python_callable=collect_web_data,
    dag=dag
)

update_index_task = PythonOperator(
    task_id='update_search_index',
    python_callable=update_search_index,
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_data',
    python_callable=cleanup_old_data,
    dag=dag
)

# 태스크 의존성 설정 (병렬 수집 후 인덱스 업데이트)
[collect_naver_task, collect_web_task] >> update_index_task >> cleanup_task 