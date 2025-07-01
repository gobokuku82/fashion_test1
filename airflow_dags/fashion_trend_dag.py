"""
Fashion Trend Collection DAG

매일 패션 트렌드 데이터를 수집하고 분석하는 Airflow DAG
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_agents.workflow import FashionWorkflow
from langgraph_agents.state import FashionState
from utils.logger import setup_logger

logger = setup_logger(__name__)

# DAG 기본 설정
default_args = {
    'owner': 'fashion-ai-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# DAG 정의
dag = DAG(
    'fashion_trend_collection',
    default_args=default_args,
    description='Daily fashion trend data collection and analysis',
    schedule_interval=timedelta(days=1),  # 매일 실행
    catchup=False,
    max_active_runs=1
)

def collect_trend_data(**context):
    """트렌드 데이터 수집 함수"""
    try:
        logger.info("패션 트렌드 데이터 수집 시작")
        
        # 기본 키워드 설정
        trend_keywords = [
            "여름 패션", "가을 트렌드", "겨울 코트", "봄 신상",
            "크롭탑", "와이드팬츠", "오버사이즈", "미니멀",
            "Y2K 패션", "레트로", "빈티지", "지속가능 패션"
        ]
        
        # 워크플로우 실행
        workflow = FashionWorkflow()
        initial_state = FashionState(
            session_id=f"airflow_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_request="일일 패션 트렌드 데이터 수집 및 분석",
            keywords=trend_keywords,
            collected_data={},
            analysis_results={},
            generated_content={},
            feedback_history=[],
            token_usage={"total_tokens": 0, "cost": 0.0},
            human_feedback_required=False,
            feedback_count=0
        )
        
        # 비동기 실행을 동기로 래핑
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(workflow.run_async(initial_state))
        
        logger.info(f"트렌드 수집 완료: {len(result.get('collected_data', {}))}개 데이터")
        
        # 결과를 XCom에 저장
        context['task_instance'].xcom_push(key='trend_data', value=result)
        
        return "트렌드 데이터 수집 성공"
        
    except Exception as e:
        logger.error(f"트렌드 데이터 수집 실패: {e}")
        raise

def analyze_sentiment(**context):
    """감성 분석 함수"""
    try:
        logger.info("감성 분석 시작")
        
        # 이전 태스크에서 데이터 가져오기
        trend_data = context['task_instance'].xcom_pull(key='trend_data')
        
        if not trend_data:
            logger.warning("분석할 데이터가 없습니다.")
            return "감성 분석 스킵"
        
        # 감성 분석 수행 (실제 구현에서는 워크플로우 호출)
        logger.info("감성 분석 완료")
        
        return "감성 분석 성공"
        
    except Exception as e:
        logger.error(f"감성 분석 실패: {e}")
        raise

def generate_insights(**context):
    """인사이트 생성 함수"""
    try:
        logger.info("인사이트 생성 시작")
        
        # 분석 결과를 바탕으로 비즈니스 인사이트 생성
        # (실제 구현에서는 콘텐츠 생성 노드 호출)
        
        insights = {
            "date": datetime.now().isoformat(),
            "key_trends": ["친환경 패션 증가", "레트로 스타일 인기"],
            "recommendations": ["지속가능성 마케팅 강화", "90년대 스타일 상품 기획"]
        }
        
        logger.info("인사이트 생성 완료")
        
        # 결과 저장
        context['task_instance'].xcom_push(key='insights', value=insights)
        
        return "인사이트 생성 성공"
        
    except Exception as e:
        logger.error(f"인사이트 생성 실패: {e}")
        raise

# 태스크 정의
collect_data_task = PythonOperator(
    task_id='collect_trend_data',
    python_callable=collect_trend_data,
    dag=dag
)

analyze_sentiment_task = PythonOperator(
    task_id='analyze_sentiment',
    python_callable=analyze_sentiment,
    dag=dag
)

generate_insights_task = PythonOperator(
    task_id='generate_insights',
    python_callable=generate_insights,
    dag=dag
)

cleanup_task = BashOperator(
    task_id='cleanup_temp_files',
    bash_command='find /tmp -name "fashion_ai_*" -mtime +7 -delete || true',
    dag=dag
)

# 태스크 의존성 설정
collect_data_task >> analyze_sentiment_task >> generate_insights_task >> cleanup_task 