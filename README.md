# Fashion AI Automation System 👗🤖

패션/쇼핑몰 회사용 LangGraph + MCP 기반 AI 자동화 시스템

## 🎯 시스템 목표
- 최신 트렌드, 경쟁사 마케팅, SNS 댓글, 명품 브랜드 동향 자동 수집
- 분석 결과 기반 제품 기획서, 마케팅 문구, 콘텐츠 자동 생성
- LangGraph DAG 구조로 데이터 수집 → 분석 → 콘텐츠 생성 흐름 구성
- Human-in-the-loop을 통한 품질 검증 및 개선

## 🏗️ 프로젝트 구조

```
test_fashion/
├── 📋 requirements.txt              # 패키지 의존성 (50개 패키지)
├── 📖 README.md                     # 프로젝트 문서 
├── 🚀 run_app.py                    # 메인 실행 파일
├── 📝 PROJECT_REPORT.md             # 상세 프로젝트 보고서 (259줄)
├── 📋 PATCH_NOTES_v1.1.md           # 패치노트 v1.1
├── ⚙️ config/                       # 설정 파일들 (3개 파일)
│   ├── __init__.py
│   ├── settings.py                  # 전역 설정 (67줄)
│   └── prompts.yaml                 # LLM 프롬프트 템플릿 (145줄)
├── 🧠 langgraph_agents/             # LangGraph 메인 로직 (4개 파일)
│   ├── __init__.py                  # 패키지 초기화
│   ├── state.py                     # 상태 정의 (143줄)
│   ├── workflow.py                  # 워크플로우 구성 (172줄)
│   └── nodes/                       # 처리 노드들 (6개 파일, 총 1,703줄)
│       ├── __init__.py              # 노드 패키지 초기화
│       ├── data_collection.py       # 데이터 수집 노드 (230줄)
│       ├── trend_analysis.py        # 트렌드 분석 노드 (267줄)
│       ├── sentiment_analysis.py    # 감성 분석 노드 (368줄)
│       ├── content_generation.py    # 콘텐츠 생성 노드 (409줄)
│       └── human_feedback.py        # Human-in-the-loop 노드 (414줄)
├── 🛠️ tools/                        # 외부 도구 연동 (5개 파일, 총 1,877줄)
│   ├── __init__.py                  # 도구 패키지 초기화
│   ├── web_scraper.py              # 웹 크롤링 도구 (345줄)
│   ├── naver_api.py                # 네이버 API 연동 (310줄)
│   ├── opensearch_client.py        # OpenSearch 클라이언트 (408줄)
│   └── mcp_client.py               # MCP 클라이언트 (599줄)
├── 🔄 airflow_dags/                 # Airflow 스케줄링 (3개 파일)
│   ├── __init__.py                  # DAG 패키지 초기화
│   ├── fashion_trend_dag.py        # 트렌드 수집 DAG (161줄)
│   └── data_collection_dag.py      # 데이터 수집 DAG (184줄)
├── 📊 data/                         # 샘플 데이터 (2개 파일)
│   ├── sample_trends.json          # 샘플 트렌드 데이터 (60줄)
│   └── sample_reviews.json         # 샘플 리뷰 데이터 (80줄)
├── 🖥️ streamlit_ui/                 # Streamlit 웹 인터페이스 (2개 파일)
│   ├── app.py                      # 메인 앱 (520줄)
│   └── .streamlit/                 # Streamlit 설정
│       └── secrets.toml           # 시크릿 키 설정 (17줄)
├── 🔧 utils/                       # 유틸리티 (4개 파일)
│   ├── __init__.py                  # 유틸 패키지 초기화
│   ├── logger.py                  # 로깅 설정 (87줄)
│   ├── token_tracker.py           # 토큰 사용량 추적 (76줄)
│   └── helpers.py                 # 헬퍼 함수들 (79줄)
├── 🧪 tests/                       # 테스트 코드 (3개 파일)
│   ├── __init__.py                  # 테스트 패키지 초기화
│   ├── test_nodes.py              # 노드 테스트 (172줄)
│   └── test_tools.py              # 도구 테스트 (194줄)
├── 📁 fashion_ai_env/              # 가상환경 디렉토리
└── 📁 logs/                        # 로그 파일 저장소
```

## 🚀 주요 기능

### 🔄 LangGraph 워크플로우 (v1.1 업데이트)
1. **step_1_collect**: 웹 크롤링, API 호출로 트렌드 데이터 수집
2. **step_2_trends**: MCP 기반 LLM으로 트렌드 패턴 분석  
3. **step_3_sentiment**: SNS 댓글, 리뷰 감성 분석
4. **step_4_content**: 제품 기획서, 마케팅 문구 자동 생성
5. **step_5_feedback**: Human-in-the-loop 품질 검증

### 🌐 Streamlit UI (5개 페이지)
1. **🏠 대시보드**: 실시간 트렌드 모니터링
2. **📈 트렌드 분석**: AI 기반 패션 트렌드 분석
3. **🤖 콘텐츠 생성**: 자동 제품 기획서 및 마케팅 문구
4. **👥 Human-in-the-loop**: 품질 검증 및 피드백 시스템  
5. **💰 토큰 사용량**: AI 비용 실시간 모니터링

### 🔗 주요 연동 기술
- **LangGraph 0.5.0**: 워크플로우 DAG 구성
- **OpenAI API**: GPT-4 기반 LLM 모델 호출
- **Naver API**: 네이버 쇼핑, 블로그 데이터
- **OpenSearch 3.0.0**: 데이터 저장 및 검색
- **Apache Airflow 3.0.1**: 주기적 데이터 수집 스케줄링
- **Streamlit 1.46.1**: 웹 UI 및 대시보드

## 📊 시스템 현황 (v1.1)

| 구성요소 | 파일 수 | 코드 라인 수 | 상태 |
|---------|--------|-------------|------|
| LangGraph 에이전트 | 10개 | 1,875줄 | ✅ 정상 |
| 외부 도구 연동 | 5개 | 1,877줄 | ✅ 정상 |
| 웹 인터페이스 | 2개 | 537줄 | ✅ 정상 |
| 테스트 코드 | 3개 | 371줄 | ✅ 100% 통과 |
| **전체 시스템** | **39개** | **7,500+줄** | **✅ 프로덕션 준비** |

## 🏃‍♂️ 실행 방법

### 📦 **1단계: 가상환경 설정**
```bash
# 가상환경 생성
python -m venv fashion_ai_env

# 가상환경 활성화 (Windows)
fashion_ai_env\Scripts\activate

# 가상환경 활성화 (Linux/Mac)
source fashion_ai_env/bin/activate
```

### 📥 **2단계: 의존성 설치**
```bash
# 패키지 설치 (50개 패키지)
pip install -r requirements.txt
```

### 🚀 **3단계: 시스템 실행 (권장)**
```bash
# 메인 실행 파일 사용 (자동으로 Streamlit 시작)
python run_app.py
```

### 🌐 **4단계: 웹 접속**
- **URL**: http://localhost:8501
- **브라우저에서 자동으로 열림**

### 🔧 **대안 실행 방법**
```bash
# Streamlit 직접 실행
streamlit run streamlit_ui/app.py

# 특정 포트로 실행
streamlit run streamlit_ui/app.py --server.port 8502
```

## 🔑 환경 설정

### **필수 API 키 설정**
Streamlit Cloud 또는 `.env` 파일에 다음 키들을 설정:

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Naver API  
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# OpenSearch (선택사항)
OPENSEARCH_HOST=your_opensearch_host
OPENSEARCH_USERNAME=your_username  
OPENSEARCH_PASSWORD=your_password
```

## 📝 사용 예시

### **트렌드 분석 요청**
```
"올여름 트렌드 요약과 제품 기획서 만들어줘"
```

### **마케팅 문구 생성**
```
"이 제품 리뷰 반응 분석해서 마케팅 문구 제안해줘"
```

### **Human-in-the-loop 품질 개선**
```
생성된 콘텐츠에 대한 피드백을 통해 AI가 지속적으로 학습
```

## 🧪 테스트 실행

```bash
# 전체 테스트 실행
pytest tests/

# 특정 테스트 실행
pytest tests/test_nodes.py
pytest tests/test_tools.py
```

## 🔄 Airflow 스케줄링 (선택사항)

```bash
# Airflow 초기화
airflow db init

# DAG 실행
airflow dags trigger fashion_trend_dag
airflow dags trigger data_collection_dag
```

## 📞 지원 및 문의

- **시스템 상태**: ✅ 프로덕션 준비 완료
- **접속 문제**: http://localhost:8501 확인
- **기술 문의**: 시스템 관련 문제나 추가 기능 요청
- **패치노트**: PATCH_NOTES_v1.1.md 참조

## 🎉 시작하기

**1분 안에 실행하기:**
```bash
python -m venv fashion_ai_env
fashion_ai_env\Scripts\activate  
pip install -r requirements.txt
python run_app.py
```

**✨ 지금 바로 http://localhost:8501 에서 체험하세요!** 