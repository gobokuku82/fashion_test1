"""
LangGraph State Key 충돌 디버깅 테스트
"""

from typing import Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END

# 문제가 되는 State 정의
class TestState(TypedDict):
    trend_analysis: Optional[Dict[str, Any]]
    sentiment_analysis: Optional[Dict[str, Any]]
    human_feedback: Optional[str]
    data: Dict[str, Any]

def test_node_names():
    """다양한 노드 이름 패턴을 테스트"""
    
    print("🧪 LangGraph 노드 이름 충돌 테스트 시작...")
    
    # 테스트 케이스들
    test_cases = [
        ("trend_analysis", "trend_analysis와 동일한 이름"),
        ("step_trend_analysis", "step_ 접두사 추가"),
        ("analyze_trends", "동사_명사 패턴"),
        ("step_2_trends", "step_숫자_명사 패턴"),
        ("node_trends", "완전히 다른 패턴"),
        ("process_data", "state key와 무관한 이름")
    ]
    
    for node_name, description in test_cases:
        try:
            workflow = StateGraph(TestState)
            workflow.add_node(node_name, lambda state: state)
            print(f"✅ '{node_name}' - {description}: 성공")
        except ValueError as e:
            print(f"❌ '{node_name}' - {description}: 실패 - {e}")
        except Exception as e:
            print(f"🔥 '{node_name}' - {description}: 예상치 못한 오류 - {e}")

def test_function_names():
    """함수 이름이 영향을 주는지 테스트"""
    
    print("\n🔬 함수 이름 영향 테스트...")
    
    def _trend_analysis_step(state):
        return state
    
    def _process_trends_step(state):
        return state
    
    def _step_two_handler(state):
        return state
    
    test_functions = [
        ("test_node_1", _trend_analysis_step, "함수명에 trend_analysis 포함"),
        ("test_node_2", _process_trends_step, "함수명에 trends만 포함"),
        ("test_node_3", _step_two_handler, "완전히 다른 함수명")
    ]
    
    for node_name, func, description in test_functions:
        try:
            workflow = StateGraph(TestState)
            workflow.add_node(node_name, func)
            print(f"✅ '{node_name}' with {func.__name__} - {description}: 성공")
        except ValueError as e:
            print(f"❌ '{node_name}' with {func.__name__} - {description}: 실패 - {e}")
        except Exception as e:
            print(f"🔥 '{node_name}' with {func.__name__} - {description}: 예상치 못한 오류 - {e}")

if __name__ == "__main__":
    test_node_names()
    test_function_names()
    print("\n🏁 테스트 완료!") 