"""
로깅 설정 모듈

애플리케이션 전반에 걸친 로깅 설정을 관리합니다.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
import os

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    로거 설정
    
    Args:
        name: 로거 이름
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        설정된 로거 객체
    """
    
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정된 경우 중복 방지
    if logger.handlers:
        return logger
    
    # 로그 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 포매터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (환경에 따라 조건부 설정)
    try:
        if not os.environ.get('STREAMLIT_SHARING_MODE'):  # Streamlit Cloud가 아닌 경우만
            today = datetime.now().strftime('%Y%m%d')
            log_file = log_dir / f"fashion_ai_{today}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    except Exception as e:
        # 파일 핸들러 설정 실패 시 콘솔에만 출력
        logger.warning(f"파일 핸들러 설정 실패: {e}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    기존 로거 가져오기
    
    Args:
        name: 로거 이름
    
    Returns:
        로거 객체
    """
    return logging.getLogger(name)

class LoggerMixin:
    """로거 믹스인 클래스"""
    
    @property
    def logger(self) -> logging.Logger:
        """클래스 이름으로 로거 반환"""
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger 