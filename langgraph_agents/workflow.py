"""
Fashion AI Automation System - LangGraph Workflow Definition
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from .state import FashionState, update_state_step
from .nodes.data_collection import DataCollectionNode
from .nodes.trend_analysis import TrendAnalysisNode
from .nodes.sentiment_analysis import SentimentAnalysisNode
from .nodes.content_generation import ContentGenerationNode
from .nodes.human_feedback import HumanFeedbackNode


class FashionWorkflow:
    """패션 AI 자동화 시스템의 메인 워크플로우"""
    
    def __init__(self):
        self.graph = None
        self._build_workflow()
    
    def _build_workflow(self):
        """LangGraph 워크플로우를 구성합니다"""
        
        # StateGraph 생성
        workflow = StateGraph(FashionState)
        
        # 노드 추가
        workflow.add_node("data_collection", self._data_collection_step)
        workflow.add_node("trend_analysis", self._trend_analysis_step)
        workflow.add_node("sentiment_analysis", self._sentiment_analysis_step)
        workflow.add_node("content_generation", self._content_generation_step)
        workflow.add_node("human_feedback", self._human_feedback_step)
        
        # 시작점 설정
        workflow.set_entry_point("data_collection")
        
        # 엣지 연결 (플로우 정의)
        workflow.add_edge("data_collection", "trend_analysis")
        workflow.add_edge("trend_analysis", "sentiment_analysis")
        workflow.add_edge("sentiment_analysis", "content_generation")
        
        # 조건부 엣지: 휴먼 피드백 필요 여부에 따라 분기
        workflow.add_conditional_edges(
            "content_generation",
            self._should_get_human_feedback,
            {
                "human_feedback": "human_feedback",
                "end": END
            }
        )
        
        # 휴먼 피드백 후 다시 콘텐츠 생성으로 돌아가거나 종료
        workflow.add_conditional_edges(
            "human_feedback",
            self._should_continue_after_feedback,
            {
                "continue": "content_generation",
                "end": END
            }
        )
        
        # 워크플로우 컴파일
        self.graph = workflow.compile()
    
    async def run(self, initial_state: FashionState, config: RunnableConfig = None) -> FashionState:
        """워크플로우를 실행합니다"""
        try:
            final_state = await self.graph.ainvoke(initial_state, config)
            return final_state
        except Exception as e:
            initial_state["errors"].append(f"워크플로우 실행 중 오류: {str(e)}")
            return initial_state
    
    def _data_collection_step(self, state: FashionState) -> FashionState:
        """데이터 수집 단계"""
        state = update_state_step(state, "데이터 수집 시작")
        
        try:
            collector = DataCollectionNode()
            return collector.execute(state)
        except Exception as e:
            state["errors"].append(f"데이터 수집 오류: {str(e)}")
            return state
    
    def _trend_analysis_step(self, state: FashionState) -> FashionState:
        """트렌드 분석 단계"""
        state = update_state_step(state, "트렌드 분석 시작")
        
        try:
            analyzer = TrendAnalysisNode()
            return analyzer.execute(state)
        except Exception as e:
            state["errors"].append(f"트렌드 분석 오류: {str(e)}")
            return state
    
    def _sentiment_analysis_step(self, state: FashionState) -> FashionState:
        """감성 분석 단계"""
        state = update_state_step(state, "감성 분석 시작")
        
        try:
            analyzer = SentimentAnalysisNode()
            return analyzer.execute(state)
        except Exception as e:
            state["errors"].append(f"감성 분석 오류: {str(e)}")
            return state
    
    def _content_generation_step(self, state: FashionState) -> FashionState:
        """콘텐츠 생성 단계"""
        state = update_state_step(state, "콘텐츠 생성 시작")
        
        try:
            generator = ContentGenerationNode()
            return generator.execute(state)
        except Exception as e:
            state["errors"].append(f"콘텐츠 생성 오류: {str(e)}")
            return state
    
    def _human_feedback_step(self, state: FashionState) -> FashionState:
        """Human-in-the-loop 피드백 단계"""
        state = update_state_step(state, "휴먼 피드백 처리 시작")
        
        try:
            feedback_handler = HumanFeedbackNode()
            return feedback_handler.execute(state)
        except Exception as e:
            state["errors"].append(f"휴먼 피드백 처리 오류: {str(e)}")
            return state
    
    def _should_get_human_feedback(self, state: FashionState) -> str:
        """휴먼 피드백이 필요한지 판단"""
        
        # 다음 조건들 중 하나라도 만족하면 휴먼 피드백 요청
        conditions = [
            state.get("requires_human_input", False),  # 명시적 요청
            len(state.get("errors", [])) > 0,          # 에러 발생
            state.get("feedback_iteration", 0) == 0,   # 첫 번째 실행
        ]
        
        if any(conditions):
            return "human_feedback"
        else:
            return "end"
    
    def _should_continue_after_feedback(self, state: FashionState) -> str:
        """피드백 후 계속 진행할지 판단"""
        
        # 최대 3번까지만 피드백 반복
        max_iterations = 3
        current_iteration = state.get("feedback_iteration", 0)
        
        if current_iteration < max_iterations and state.get("human_feedback"):
            return "continue"
        else:
            return "end"
    
    def get_workflow_diagram(self) -> str:
        """워크플로우 다이어그램을 Mermaid 형식으로 반환"""
        return """
        graph TD
            A[데이터 수집] --> B[트렌드 분석]
            B --> C[감성 분석]
            C --> D[콘텐츠 생성]
            D --> E{휴먼 피드백<br/>필요?}
            E -->|예| F[휴먼 피드백]
            E -->|아니오| G[종료]
            F --> H{계속 진행?}
            H -->|예| D
            H -->|아니오| G
        """ 