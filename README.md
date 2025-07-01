# Fashion AI Automation System 👗🤖

패션/쇼핑몰 회사용 LangGraph + MCP 기반 AI 자동화 시스템

## 🎯 시스템 목표
- 최신 트렌드, 경쟁사 마케팅, SNS 댓글, 명품 브랜드 동향 자동 수집
- 분석 결과 기반 제품 기획서, 마케팅 문구, 콘텐츠 자동 생성
- LangGraph DAG 구조로 데이터 수집 → 분석 → 콘텐츠 생성 흐름 구성

## 🏗️ 프로젝트 구조

```
test_fashion/
├── 📋 requirements.txt              # 패키지 의존성
├── 📖 README.md                     # 프로젝트 문서
├── 🔐 .env.example                  # 환경변수 예시
├── ⚙️ config/                       # 설정 파일들
│   ├── __init__.py
│   ├── settings.py                  # 전역 설정
│   └── prompts.yaml                 # LLM 프롬프트 템플릿
├── 🧠 langgraph_agents/             # LangGraph 메인 로직
│   ├── __init__.py
│   ├── state.py                     # 상태 정의
│   ├── workflow.py                  # 워크플로우 구성
│   └── nodes/                       # 각 처리 노드들
│       ├── __init__.py
│       ├── data_collection.py       # 데이터 수집 노드
│       ├── trend_analysis.py        # 트렌드 분석 노드
│       ├── sentiment_analysis.py    # 감성 분석 노드
│       ├── content_generation.py    # 콘텐츠 생성 노드
│       └── human_feedback.py        # Human-in-the-loop 노드
├── 🛠️ tools/                        # 외부 도구 연동
│   ├── __init__.py
│   ├── web_scraper.py              # 웹 크롤링 도구
│   ├── naver_api.py                # 네이버 API 연동
│   ├── opensearch_client.py        # OpenSearch 클라이언트
│   └── mcp_client.py               # MCP 클라이언트
├── 🔄 airflow_dags/                 # Airflow 스케줄링
│   ├── __init__.py
│   ├── fashion_trend_dag.py        # 트렌드 수집 DAG
│   └── data_collection_dag.py      # 데이터 수집 DAG
├── 📊 data/                         # 데이터 저장소
│   ├── sample_trends.json          # 샘플 트렌드 데이터
│   ├── sample_reviews.json         # 샘플 리뷰 데이터
│   └── processed/                  # 처리된 데이터
├── 🖥️ streamlit_ui/                 # Streamlit 웹 인터페이스
│   ├── app.py                      # 메인 앱
│   ├── pages/                      # 페이지별 UI
│   │   ├── dashboard.py            # 대시보드
│   │   ├── trend_analysis.py       # 트렌드 분석 페이지
│   │   ├── content_generator.py    # 콘텐츠 생성 페이지
│   │   └── token_usage.py          # 토큰 사용량 추적
│   ├── components/                 # UI 컴포넌트
│   │   ├── __init__.py
│   │   ├── charts.py              # 차트 컴포넌트
│   │   └── forms.py               # 폼 컴포넌트
│   └── .streamlit/                # Streamlit 설정
│       └── secrets.toml           # 시크릿 키 설정
├── 🔧 utils/                       # 유틸리티
│   ├── __init__.py
│   ├── logger.py                  # 로깅 설정
│   ├── token_tracker.py           # 토큰 사용량 추적
│   └── helpers.py                 # 헬퍼 함수들
└── 🧪 tests/                       # 테스트 코드
    ├── __init__.py
    ├── test_nodes.py              # 노드 테스트
    └── test_tools.py              # 도구 테스트
```

## 🚀 주요 기능

### LangGraph 워크플로우
1. **데이터 수집**: 웹 크롤링, API 호출로 트렌드 데이터 수집
2. **트렌드 분석**: MCP 기반 LLM으로 트렌드 패턴 분석
3. **감성 분석**: SNS 댓글, 리뷰 감성 분석
4. **콘텐츠 생성**: 제품 기획서, 마케팅 문구 자동 생성
5. **Human-in-the-loop**: 사람의 피드백 반영

### 주요 연동 기술
- **LangGraph**: 워크플로우 DAG 구성
- **OpenAI API**: LLM 모델 호출
- **Naver API**: 네이버 쇼핑, 블로그 데이터
- **OpenSearch**: 데이터 저장 및 검색
- **Airflow**: 주기적 데이터 수집 스케줄링
- **Streamlit**: 웹 UI 및 대시보드

## 📝 사용 예시

```python
# 트렌드 분석 요청
"올여름 트렌드 요약과 제품 기획서 만들어줘"

# 마케팅 문구 생성
"이 제품 리뷰 반응 분석해서 마케팅 문구 제안해줘"
```

## 🔑 환경 설정

Streamlit Cloud에서 다음 시크릿 키들을 설정해주세요:
- `OPENAI_API_KEY`: OpenAI API 키
- `NAVER_CLIENT_ID`: 네이버 API 클라이언트 ID  
- `NAVER_CLIENT_SECRET`: 네이버 API 클라이언트 시크릿
- `OPENSEARCH_HOST`: OpenSearch 호스트 URL
- `OPENSEARCH_USERNAME`: OpenSearch 사용자명
- `OPENSEARCH_PASSWORD`: OpenSearch 비밀번호

## 🏃‍♂️ 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run streamlit_ui/app.py

# Airflow DAG 실행 (로컬 환경)
airflow dags trigger fashion_trend_dag
``` 