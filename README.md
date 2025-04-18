# 프롬프트 변환 엔진

간단한 입력을 상세하고 전문적인 프롬프트로 변환해주는 프롬프트 엔진입니다. 사용자의 특정 요구사항, 검색어, 범위, 출력 형식 등을 정확히 반영합니다.

## 개요

이 프롬프트 엔진은 사용자의 간단한 요청을 분석하여 다음과 같은 구조화된 프롬프트로 변환합니다:

- **역할 (Role)**: 주제 관련 전문가의 역할, 전문성, 경험 정의
- **지시사항 (Instructions)**: 전문적이고 체계적인 접근을 위한 5-7개의 상세 지시사항
- **응답 스타일 (Response Style)**: 응답의 톤, 전문성 수준, 형식에 대한 가이드라인
- **주요 고려사항 (Reminder)**: 중요한 원칙, 윤리적 측면, 한계 등을 상기
- **출력 형식 (Output Format)**: 사고 과정과 최종 결과물의 구체적인 구조 정의

## 주요 특징

- 간단한 요청을 분석하여 핵심 요소 파악
- 특정 요구사항 및 범위 정확히 반영
- 사용자 지정 검색어 및 출력 형식 적용
- 웹 인터페이스를 통한 커스텀 옵션 제공
- 생성된 프롬프트 다운로드 가능

## 설치 방법

1. 저장소 클론
```bash
git clone [저장소 URL]
cd prompt-engine
```

2. 가상 환경 생성 및 활성화 (선택사항)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

4. OpenAI API 키 설정
```bash
export OPENAI_API_KEY=your_api_key_here  # Windows: set OPENAI_API_KEY=your_api_key_here
```

## 사용 방법

### 방법 1: Streamlit 직접 실행

```bash
streamlit run src/api/app.py
```

### 방법 2: 메인 스크립트 실행

```bash
python src/main.py
```

추가 옵션:
```bash
python src/main.py --port 8080 --openai-api-key your_api_key_here
```

## 웹 인터페이스 사용법

1. OpenAI API 키 입력
2. 간단한 요청 입력
3. 필요한 경우 커스텀 옵션 설정:
   - 전문성 수준 지정
   - 특정 범위 설정
   - 원하는 출력 형식 선택
   - 중점적으로 다룰 검색어 입력
   - 특별 요구사항 추가
4. '프롬프트 변환' 버튼 클릭
5. 생성된 상세 프롬프트 확인 및 다운로드

## 프로젝트 구조

```
prompt-engine/
├── docs/              # 문서화 파일
├── src/               # 소스 코드
│   ├── api/           # Streamlit 웹 인터페이스
│   │   └── app.py     # Streamlit 애플리케이션
│   ├── core/          # 핵심 비즈니스 로직
│   │   └── prompt_engine.py  # 프롬프트 변환 엔진 클래스
│   └── main.py        # 메인 실행 파일
├── tests/             # 테스트 파일
├── README.md          # 프로젝트 설명
└── requirements.txt   # 의존성 패키지 목록
```

## 요청 형식 예시

### 기본 요청
```
마케팅 전략에 대해 알려줘
```

### 특정 요구사항이 포함된 요청
```
2023년 이후 온라인 소매업체의 마케팅 전략에 대해 단계별로 설명해줘. ROI와 고객 유지율에 중점을 두고 실제 사례를 포함해서 알려줘.
```

### 웹 UI를 통한 커스텀 옵션 사용
사용자 요청: "마케팅 전략에 대해 알려줘"
커스텀 옵션:
- 전문성 수준: 고급
- 특정 범위: 2023년 이후 스타트업
- 출력 형식: 단계별 가이드
- 중점 검색어: ROI, 고객 유지, 성장 해킹
- 특별 요구사항: 실제 사례 포함, 적은 예산으로 효과적인 전략 중심

## 변환 결과 예시

간단한 입력인 "마케팅 전략에 대해 알려줘"가 다음과 같은 상세한 프롬프트로 변환됩니다:

```
<prompt>
<role>
You are a seasoned Chief Marketing Officer with over 20 years of experience...
</role>
<instructions>
1. Analyze current marketing landscape:
   - Evaluate the latest trends in digital and traditional marketing
   - Assess the impact of emerging technologies on marketing strategies
   ...
</instructions>
<response_style>
Your response should be strategic, analytical, and practical...
</response_style>
<reminder>
- Consider diverse business contexts including B2B, B2C, services, products...
</reminder>
<output_format>
<thinking_process>
[Outline your approach to developing comprehensive marketing strategy recommendations...]
</thinking_process>
<final_response>
# Comprehensive Marketing Strategy Framework
...
</final_response>
</output_format>
</prompt>
```

## 라이선스

Copyright © 2025 디엘토. All Rights Reserved.

이 프로젝트와 관련 파일은 저작권자의 명시적인 서면 허가 없이 어떠한 형태로든 사용, 복제, 수정, 배포가 금지됩니다. 