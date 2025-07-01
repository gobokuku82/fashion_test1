import streamlit as st
import asyncio
import json
from typing import Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 프로젝트 모듈 import
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_agents.workflow import FashionWorkflow
from langgraph_agents.state import FashionState
from tools.opensearch_client import OpenSearchClient
from utils.token_tracker import TokenTracker
from utils.logger import setup_logger

# 페이지 설정
st.set_page_config(
    page_title="Fashion AI Automation System",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 로거 설정
logger = setup_logger(__name__)

class FashionAIApp:
    def __init__(self):
        self.workflow = FashionWorkflow()
        self.opensearch_client = OpenSearchClient()
        self.token_tracker = TokenTracker()
        
    def main(self):
        """메인 애플리케이션"""
        st.title("👗 Fashion AI Automation System")
        st.markdown("""
        ### 패션/쇼핑몰 회사용 AI 자동화 시스템
        최신 트렌드 분석부터 콘텐츠 생성까지 한 번에!
        """)
        
        # 사이드바 메뉴
        page = st.sidebar.selectbox(
            "페이지 선택",
            ["🏠 대시보드", "📈 트렌드 분석", "🎯 콘텐츠 생성", "💬 Human-in-the-loop", "📊 토큰 사용량"]
        )
        
        if page == "🏠 대시보드":
            self.dashboard_page()
        elif page == "📈 트렌드 분석":
            self.trend_analysis_page()
        elif page == "🎯 콘텐츠 생성":
            self.content_generation_page()
        elif page == "💬 Human-in-the-loop":
            self.human_feedback_page()
        elif page == "📊 토큰 사용량":
            self.token_usage_page()
    
    def dashboard_page(self):
        """대시보드 페이지"""
        st.header("📊 대시보드")
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("오늘 수집된 데이터", "1,234", "12%")
        with col2:
            st.metric("분석 완료된 트렌드", "56", "8%")
        with col3:
            st.metric("생성된 콘텐츠", "23", "15%")
        with col4:
            st.metric("토큰 사용량", "45,678", "-5%")
        
        # 최근 활동 차트
        st.subheader("📈 최근 7일 활동")
        
        # 샘플 데이터 생성
        dates = [datetime.now() - timedelta(days=i) for i in range(7)]
        data = {
            'Date': dates,
            'Data Collection': [120, 135, 98, 156, 142, 167, 134],
            'Trend Analysis': [45, 52, 38, 61, 49, 58, 56],
            'Content Generation': [12, 18, 15, 23, 19, 25, 23]
        }
        df = pd.DataFrame(data)
        
        fig = px.line(df, x='Date', y=['Data Collection', 'Trend Analysis', 'Content Generation'],
                     title='일별 활동 현황')
        st.plotly_chart(fig, use_container_width=True)
        
        # 최근 생성된 콘텐츠
        st.subheader("🆕 최근 생성된 콘텐츠")
        recent_content = [
            {"시간": "2시간 전", "타입": "제품 기획서", "주제": "2024 봄 트렌치코트 컬렉션"},
            {"시간": "4시간 전", "타입": "마케팅 문구", "주제": "여름 원피스 프로모션"},
            {"시간": "6시간 전", "타입": "SNS 콘텐츠", "주제": "명품 백 트렌드 분석"},
            {"시간": "8시간 전", "타입": "제품 기획서", "주제": "지속가능한 패션 라인"},
        ]
        
        for content in recent_content:
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    st.write(f"**{content['타입']}**")
                with col2:
                    st.write(content['주제'])
                with col3:
                    st.write(content['시간'])
                st.divider()
    
    def trend_analysis_page(self):
        """트렌드 분석 페이지"""
        st.header("📈 트렌드 분석")
        
        # 분석 키워드 입력
        col1, col2 = st.columns([3, 1])
        with col1:
            keywords = st.text_input("분석할 키워드를 입력하세요", placeholder="예: 여름 원피스, 트렌치코트")
        with col2:
            analyze_btn = st.button("🔍 분석 시작", type="primary")
        
        if analyze_btn and keywords:
            with st.spinner("트렌드 분석 중..."):
                self.run_trend_analysis(keywords)
        
        # 기존 분석 결과 표시
        st.subheader("📋 최근 분석 결과")
        
        # 샘플 트렌드 데이터 표시
        self.display_sample_trends()
    
    def content_generation_page(self):
        """콘텐츠 생성 페이지"""
        st.header("🎯 콘텐츠 생성")
        
        # 콘텐츠 타입 선택
        content_type = st.selectbox(
            "생성할 콘텐츠 타입을 선택하세요",
            ["제품 기획서", "마케팅 문구", "SNS 콘텐츠", "블로그 포스트"]
        )
        
        # 콘텐츠 주제 입력
        topic = st.text_area(
            "콘텐츠 주제나 설명을 입력하세요",
            placeholder="예: 2024년 여름 시즌 원피스 컬렉션 기획서 작성"
        )
        
        # 추가 옵션
        with st.expander("⚙️ 추가 옵션"):
            target_audience = st.selectbox("타겟 고객층", ["20대 여성", "30대 여성", "40대 여성", "전 연령층"])
            tone = st.selectbox("톤앤매너", ["친근한", "전문적인", "트렌디한", "고급스러운"])
            length = st.selectbox("콘텐츠 길이", ["짧게", "보통", "길게"])
        
        if st.button("✨ 콘텐츠 생성", type="primary"):
            if topic:
                with st.spinner("콘텐츠 생성 중..."):
                    self.generate_content(content_type, topic, target_audience, tone, length)
            else:
                st.error("콘텐츠 주제를 입력해주세요.")
    
    def human_feedback_page(self):
        """Human-in-the-loop 페이지"""
        st.header("💬 Human-in-the-loop")
        
        st.markdown("""
        생성된 콘텐츠를 검토하고 피드백을 제공해주세요.
        AI가 피드백을 학습하여 더 나은 콘텐츠를 생성합니다.
        """)
        
        # 검토 대기 중인 콘텐츠
        st.subheader("⏳ 검토 대기 중인 콘텐츠")
        
        if 'pending_content' not in st.session_state:
            st.session_state.pending_content = [
                {
                    "id": 1,
                    "type": "제품 기획서",
                    "title": "2024 여름 원피스 컬렉션",
                    "content": "여름철 트렌드를 반영한 원피스 컬렉션 기획안입니다...",
                    "status": "pending"
                }
            ]
        
        for content in st.session_state.pending_content:
            if content['status'] == 'pending':
                with st.container():
                    st.write(f"**{content['type']}**: {content['title']}")
                    st.text_area("생성된 콘텐츠", content['content'], height=150, key=f"content_{content['id']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ 승인", key=f"approve_{content['id']}"):
                            content['status'] = 'approved'
                            st.success("콘텐츠가 승인되었습니다!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ 거절", key=f"reject_{content['id']}"):
                            content['status'] = 'rejected'
                            st.error("콘텐츠가 거절되었습니다.")
                            st.rerun()
                    
                    with col3:
                        if st.button("✏️ 수정 요청", key=f"revise_{content['id']}"):
                            self.show_revision_form(content['id'])
                    
                    st.divider()
        
        # 처리 완료된 콘텐츠
        approved_content = [c for c in st.session_state.pending_content if c['status'] == 'approved']
        if approved_content:
            st.subheader("✅ 승인된 콘텐츠")
            for content in approved_content:
                st.write(f"**{content['type']}**: {content['title']}")
    
    def token_usage_page(self):
        """토큰 사용량 페이지"""
        st.header("📊 토큰 사용량 추적")
        
        # 오늘의 토큰 사용량
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("오늘 사용량", "12,345 토큰", "1,234")
        with col2:
            st.metric("이번 달 사용량", "345,678 토큰", "23,456")
        with col3:
            st.metric("예상 비용", "$8.67", "$2.34")
        
        # 토큰 사용량 차트
        st.subheader("📈 일별 토큰 사용량")
        
        # 샘플 데이터
        dates = [datetime.now() - timedelta(days=i) for i in range(30)]
        usage_data = {
            'Date': dates,
            'Tokens': [12000 + i*100 + (i%3)*500 for i in range(30)]
        }
        df = pd.DataFrame(usage_data)
        
        fig = px.bar(df, x='Date', y='Tokens', title='최근 30일 토큰 사용량')
        st.plotly_chart(fig, use_container_width=True)
        
        # 기능별 사용량
        st.subheader("🔍 기능별 토큰 사용량")
        
        function_data = {
            '기능': ['트렌드 분석', '감성 분석', '콘텐츠 생성', 'Human-in-the-loop'],
            '토큰 수': [15420, 8760, 21340, 3280],
            '비율': [32.1, 18.3, 44.5, 6.8]
        }
        
        fig = px.pie(function_data, values='토큰 수', names='기능', title='기능별 토큰 사용 분포')
        st.plotly_chart(fig, use_container_width=True)
    
    def run_trend_analysis(self, keywords: str):
        """트렌드 분석 실행"""
        try:
            # 초기 상태 생성
            initial_state = FashionState(
                session_id=f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_request=f"다음 키워드에 대한 트렌드 분석을 수행해주세요: {keywords}",
                keywords=[k.strip() for k in keywords.split(',')],
                collected_data={},
                analysis_results={},
                generated_content={},
                feedback_history=[],
                token_usage={"total_tokens": 0, "cost": 0.0},
                human_feedback_required=False,
                feedback_count=0
            )
            
            # 워크플로우 실행 (비동기 실행을 동기로 래핑)
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(self.workflow.run_async(initial_state))
                
                # 결과 표시
                if result.get('analysis_results'):
                    st.success("트렌드 분석이 완료되었습니다!")
                    
                    analysis = result['analysis_results']
                    
                    st.subheader("📊 분석 결과")
                    
                    # 주요 트렌드
                    if 'main_trends' in analysis:
                        st.write("**주요 트렌드:**")
                        for trend in analysis['main_trends']:
                            st.write(f"• {trend}")
                    
                    # 예측
                    if 'predictions' in analysis:
                        st.write("**향후 전망:**")
                        for pred in analysis['predictions']:
                            st.write(f"• {pred}")
                    
                    # 비즈니스 제안
                    if 'business_suggestions' in analysis:
                        st.write("**비즈니스 제안:**")
                        for suggestion in analysis['business_suggestions']:
                            st.write(f"• {suggestion}")
                    
                    # 토큰 사용량
                    if 'token_usage' in result:
                        st.info(f"사용된 토큰: {result['token_usage']['total_tokens']}")
                
                else:
                    st.warning("분석 결과를 가져올 수 없습니다. 샘플 데이터를 표시합니다.")
                    self.display_sample_trends()
                    
            except Exception as e:
                logger.error(f"워크플로우 실행 오류: {e}")
                st.error("분석 중 오류가 발생했습니다. 샘플 데이터를 표시합니다.")
                self.display_sample_trends()
                
        except Exception as e:
            logger.error(f"트렌드 분석 오류: {e}")
            st.error("트렌드 분석 중 오류가 발생했습니다.")
    
    def generate_content(self, content_type: str, topic: str, audience: str, tone: str, length: str):
        """콘텐츠 생성"""
        try:
            # 초기 상태 생성
            initial_state = FashionState(
                session_id=f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_request=f"{content_type} 생성: {topic}",
                keywords=[topic],
                collected_data={},
                analysis_results={
                    "target_audience": audience,
                    "tone": tone,
                    "length": length
                },
                generated_content={},
                feedback_history=[],
                token_usage={"total_tokens": 0, "cost": 0.0},
                human_feedback_required=False,
                feedback_count=0
            )
            
            # 워크플로우 실행
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(self.workflow.run_async(initial_state))
                
                if result.get('generated_content'):
                    st.success(f"{content_type}이(가) 생성되었습니다!")
                    
                    content = result['generated_content']
                    
                    # 생성된 콘텐츠 표시
                    st.subheader("✨ 생성된 콘텐츠")
                    
                    if 'product_plan' in content:
                        st.text_area("제품 기획서", content['product_plan'], height=300)
                    
                    if 'marketing_copy' in content:
                        st.text_area("마케팅 문구", content['marketing_copy'], height=200)
                    
                    if 'content_suggestions' in content:
                        st.write("**콘텐츠 제안:**")
                        for suggestion in content['content_suggestions']:
                            st.write(f"• {suggestion}")
                    
                    # Human-in-the-loop 추가
                    if st.button("💬 검토 요청"):
                        if 'pending_content' not in st.session_state:
                            st.session_state.pending_content = []
                        
                        new_content = {
                            "id": len(st.session_state.pending_content) + 1,
                            "type": content_type,
                            "title": topic,
                            "content": str(content),
                            "status": "pending"
                        }
                        st.session_state.pending_content.append(new_content)
                        st.success("검토 요청이 추가되었습니다!")
                else:
                    st.warning("콘텐츠 생성에 실패했습니다. 샘플 콘텐츠를 표시합니다.")
                    self.display_sample_content(content_type, topic)
                    
            except Exception as e:
                logger.error(f"워크플로우 실행 오류: {e}")
                st.error("콘텐츠 생성 중 오류가 발생했습니다. 샘플 콘텐츠를 표시합니다.")
                self.display_sample_content(content_type, topic)
                
        except Exception as e:
            logger.error(f"콘텐츠 생성 오류: {e}")
            st.error("콘텐츠 생성 중 오류가 발생했습니다.")
    
    def display_sample_trends(self):
        """샘플 트렌드 데이터 표시"""
        sample_trends = {
            "main_trends": [
                "Y2K 패션 복고 트렌드 지속",
                "지속가능한 패션에 대한 관심 증가",
                "오버사이즈 실루엣 인기",
                "비비드 컬러 아이템 선호도 상승"
            ],
            "predictions": [
                "여름철 크롭탑과 하이웨스트 조합 인기 예상",
                "친환경 소재 사용 제품 수요 증가",
                "레트로 스포츠웨어 트렌드 확산"
            ],
            "business_suggestions": [
                "지속가능성을 강조한 마케팅 전략 수립",
                "Y2K 감성의 한정판 컬렉션 출시",
                "인플루언서 협업을 통한 트렌드 확산"
            ]
        }
        
        st.subheader("📊 트렌드 분석 결과 (샘플)")
        
        st.write("**주요 트렌드:**")
        for trend in sample_trends["main_trends"]:
            st.write(f"• {trend}")
        
        st.write("**향후 전망:**")
        for pred in sample_trends["predictions"]:
            st.write(f"• {pred}")
        
        st.write("**비즈니스 제안:**")
        for suggestion in sample_trends["business_suggestions"]:
            st.write(f"• {suggestion}")
    
    def display_sample_content(self, content_type: str, topic: str):
        """샘플 콘텐츠 표시"""
        if content_type == "제품 기획서":
            sample_content = f"""
# {topic} 제품 기획서

## 1. 개요
- **제품명**: {topic}
- **타겟 고객**: 20-30대 여성
- **예상 가격대**: 50,000-80,000원

## 2. 시장 분석
- 현재 시장에서 해당 카테고리의 성장률: 15%
- 주요 경쟁사: A브랜드, B브랜드
- 차별화 포인트: 지속가능한 소재 사용

## 3. 제품 특징
- 친환경 소재 100% 사용
- 다양한 사이즈 옵션 제공
- 세탁 후에도 형태 유지

## 4. 마케팅 전략
- SNS 인플루언서 협업
- 온라인 커뮤니티 타겟 마케팅
- 첫 구매 고객 할인 혜택

## 5. 출시 일정
- 기획: 1주차
- 제작: 2-4주차
- 마케팅: 4-5주차
- 출시: 6주차
            """
        elif content_type == "마케팅 문구":
            sample_content = f"""
🌟 {topic} 마케팅 문구 🌟

📢 메인 카피:
"당신의 스타일을 완성하는 특별한 선택"

💫 서브 카피:
- "트렌드를 앞서가는 디자인"
- "편안함과 스타일을 동시에"
- "지속가능한 패션의 새로운 기준"

🎯 타겟별 메시지:
- 20대: "나만의 개성을 표현하세요"
- 30대: "세련된 일상을 만들어가세요"

💝 프로모션 문구:
- "첫 구매 고객 20% 할인"
- "무료배송 + 교환 서비스"
- "만족도 99% 보장"

#트렌디 #스타일링 #패션
            """
        else:
            sample_content = f"{content_type}에 대한 샘플 콘텐츠입니다.\n\n주제: {topic}\n\n이곳에 실제 생성된 콘텐츠가 표시됩니다."
        
        st.text_area("생성된 콘텐츠 (샘플)", sample_content, height=400)
    
    def show_revision_form(self, content_id: int):
        """수정 요청 폼 표시"""
        st.subheader("✏️ 수정 요청")
        revision_feedback = st.text_area(
            "수정 요청 사항을 입력해주세요",
            placeholder="예: 톤을 더 친근하게 변경해주세요. 타겟 연령층을 20대로 조정해주세요.",
            key=f"revision_{content_id}"
        )
        
        if st.button("수정 요청 전송", key=f"send_revision_{content_id}"):
            if revision_feedback:
                st.success("수정 요청이 전송되었습니다!")
                # 실제로는 워크플로우를 다시 실행하여 피드백을 반영
            else:
                st.error("수정 요청 사항을 입력해주세요.")

def main():
    """애플리케이션 실행"""
    app = FashionAIApp()
    app.main()

if __name__ == "__main__":
    main() 