#!/usr/bin/env python3
"""
Fashion AI Automation System 실행 스크립트

이 스크립트를 통해 Streamlit 웹 애플리케이션을 실행할 수 있습니다.
"""

import subprocess
import sys
import os

def main():
    """메인 실행 함수"""
    
    # 현재 디렉토리를 프로젝트 루트로 설정
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print("🚀 Fashion AI Automation System 시작 중...")
    print(f"📂 프로젝트 경로: {project_root}")
    
    # 환경 확인
    try:
        import streamlit
        print("✅ Streamlit 설치 확인됨")
    except ImportError:
        print("❌ Streamlit이 설치되지 않았습니다.")
        print("💡 설치 명령어: pip install streamlit")
        return
    
    # Streamlit 앱 실행
    try:
        print("🌐 웹 브라우저에서 http://localhost:8501 로 접속하세요")
        print("⏹️  종료하려면 Ctrl+C를 누르세요")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_ui/app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 애플리케이션이 종료되었습니다.")
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main() 