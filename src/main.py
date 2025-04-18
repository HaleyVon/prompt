import os
import argparse
import streamlit.web.bootstrap as bootstrap
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

def parse_args():
    """명령줄 인자를 파싱합니다."""
    parser = argparse.ArgumentParser(description="프롬프트 변환 엔진 실행")
    parser.add_argument(
        "--port", 
        type=int, 
        default=8501,
        help="Streamlit 앱 실행 포트"
    )
    parser.add_argument(
        "--openai-api-key", 
        type=str, 
        help="OpenAI API 키 (미설정 시 환경 변수에서 가져옴)"
    )
    return parser.parse_args()

def main():
    """프롬프트 변환 엔진 메인 실행 함수"""
    args = parse_args()
    
    # API 키가 제공된 경우 환경 변수에 설정
    if args.openai_api_key:
        os.environ["OPENAI_API_KEY"] = args.openai_api_key
    
    # 현재 경로 기준으로 앱 파일 경로 설정
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api", "app.py")
    
    # Streamlit 앱 실행
    bootstrap.run(
        app_path,
        '',
        args=[
            "--server.port", str(args.port),
            "--server.headless", "true",
        ],
        flag_options={},
    )

if __name__ == "__main__":
    main() 