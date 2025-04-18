#!/usr/bin/env python
"""
프롬프트 변환 엔진 실행 스크립트
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리 설정
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# src 디렉토리에서 main 모듈 임포트
from src.main import main

if __name__ == "__main__":
    # 명령줄에서 전달된 인자를 main 함수로 전달
    main() 