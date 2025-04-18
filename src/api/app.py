import streamlit as st
import os
import sys
from pathlib import Path
import streamlit.components.v1 as components

# 상위 디렉토리 경로를 추가하여 core 모듈 임포트 가능하게 설정
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent))

from src.core.prompt_engine import PromptEngine

# 페이지 설정
st.set_page_config(
    page_title="프롬프트 엔지니어봇",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일 정의
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 20px;
    }
    .highlight {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        color: #9e9e9e;
        font-size: 0.8rem;
    }
    .custom-options {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 구성
with st.sidebar:
    st.markdown("## ⚙️ 설정")
    
    # API 키 입력
    openai_api_key = st.text_input(
        "OpenAI API 키",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="OpenAI API 키를 입력하세요. 환경 변수로 설정된 경우 자동으로 불러옵니다."
    )
    
    # 고급 설정 토글
    show_advanced = st.checkbox("고급 설정 표시", value=False)
    
    # 세션 상태에 설정 저장
    if 'model' not in st.session_state:
        st.session_state.model = "gpt-4.1-nano"
    
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    
    if show_advanced:
        st.markdown("### 고급 설정")
        
        # 모델 선택 - 옵션 변경
        model_options = ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"]
        selected_model = st.selectbox(
            "GPT 모델",
            options=model_options,
            index=model_options.index(st.session_state.model),
            help="사용할 OpenAI 모델을 선택하세요."
        )
        st.session_state.model = selected_model
        
        # 온도 설정
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
            help="높을수록 더 창의적인 결과를 생성합니다."
        )
    
    # API 호출 방식 선택
    api_call_method = st.radio(
        "API 호출 방식:",
        ["단일 호출 (보통 품질, 낮은 비용)", "다중 호출 (높은 품질, 높은 비용)"],
        index=0
    )
    
    # 전문성 수준 선택
    expertise_level = st.selectbox(
        "전문성 수준:",
        ["초급", "중급", "고급", "전문가"],
        index=2
    )
    
    # 범위 설정
    scope = st.text_input(
        "범위 (예: 최근 5년, 한국 시장 등):",
        help="특정 시간적, 공간적, 대상적 범위를 지정하세요."
    )
    
    # 출력 형식 선택
    output_format = st.selectbox(
        "출력 형식:",
        ["자동 감지", "목록", "단계별 가이드", "비교 분석", "요약", "상세 설명", "Q&A", "표", "다이어그램"],
        index=0
    )
    
    # 특별 요구사항
    special_requirements = st.text_area(
        "특별 요구사항:",
        help="프롬프트에 포함해야 할 특별한 요구사항을 자유롭게 입력하세요."
    )
    
    st.markdown("---")
    st.markdown("### 📚 사용 가이드")
    st.markdown("""
    1. OpenAI API 키를 입력하세요
    2. 간단한 요청을 입력하세요
    3. 필요하면 고급 옵션을 설정하세요
    4. '프롬프트 변환' 버튼을 클릭하세요
    5. 생성된 상세 프롬프트를 사용하세요
    """)
    
    st.markdown("---")
    st.markdown("### 🔍 예시 요청")
    example_requests = [
        "마케팅 전략에 대해 알려줘",
        "AI 윤리에 관한 에세이 작성 도와줘",
        "제품 기획 단계에서 고려할 사항",
        "효과적인 프레젠테이션 방법"
    ]
    
    for example in example_requests:
        if st.button(example, key=f"example_{example}"):
            st.session_state.user_input = example

# 메인 화면 구성
st.markdown('<h1 class="main-header">🧠 프롬프트 엔지니어봇</h1>', unsafe_allow_html=True)
st.markdown('<h5 class="sub-header">간단한 요청을 전문적인 프롬프트로 변환합니다</h5>', unsafe_allow_html=True)

# 사용자 입력 관리
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

user_input = st.text_area(
    "간단한 프롬프트로 초안을 입력하세요:",
    value=st.session_state.user_input,
    height=100,
    placeholder="예: 마케팅 전략에 대해 알려줘"
)

# 변환 버튼
transform_button = st.button("🔄 프롬프트 변환", type="primary")

# 결과 표시 영역
if transform_button and user_input:
    with st.spinner("프롬프트를 변환하는 중입니다..."):
        try:
            # OpenAI API 키 검증
            if not openai_api_key:
                st.error("⚠️ OpenAI API 키가 필요합니다. 사이드바에서 입력해주세요.")
            else:
                # 프롬프트 엔진 초기화 및 변환
                engine = PromptEngine(openai_api_key=openai_api_key)
                
                # 선택한 모델이 모든 API 호출에 적용되도록 설정
                engine.model = st.session_state.model
                engine.temperature = st.session_state.temperature
                
                # 변환 전 커스텀 옵션이 있으면 입력에 추가
                enhanced_input = user_input
                if scope:
                    enhanced_input += f"\n\n범위: {scope}"
                if output_format != "자동 감지":
                    enhanced_input += f"\n\n출력 형식: {output_format}"
                if special_requirements:
                    enhanced_input += f"\n\n특별 요구사항: {special_requirements}"
                
                # API 호출 방식 선택을 적용
                use_multi_call = api_call_method.startswith("다중 호출")
                transformed_prompt = engine.transform_prompt(enhanced_input, use_multi_call=use_multi_call)
                
                # 결과 표시
                st.markdown('<div class="highlight">', unsafe_allow_html=True)
                st.subheader("🎯 변환된 프롬프트")
                st.code(transformed_prompt, language="xml")
                
                # 사용된 설정 표시
                st.caption(f"사용 모델: {st.session_state.model}, Temperature: {st.session_state.temperature}")
                
                # 클립보드 복사 버튼과 다운로드 버튼을 가로로 배치
                col1, col2 = st.columns(2)
                
                # 버튼 공통 스타일
                button_style = """
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 10px 16px;
                    text-align: center;
                    text-decoration: none;
                    display: block;
                    font-size: 14px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 4px;
                    width: 100%;
                    height: 40px;
                    line-height: 20px;
                """
                
                with col1:
                    # 클립보드 복사 버튼 (JavaScript 사용)
                    copy_button_html = f"""
                    <div style="display: flex; align-items: center; height: 100%;">
                        <input type="hidden" id="copyText" value="{transformed_prompt.replace('"', '&quot;')}">
                        <button 
                            onclick="copyToClipboard()"
                            style="{button_style}"
                        >
                            📋 프롬프트 클립보드에 복사
                        </button>
                    </div>
                    <script>
                    function copyToClipboard() {{
                        var copyText = document.getElementById("copyText");
                        navigator.clipboard.writeText(copyText.value)
                            .then(() => {{
                                // 복사 성공 시 버튼 텍스트 변경
                                var button = document.querySelector("button");
                                var originalText = button.innerHTML;
                                button.innerHTML = "✓ 복사 완료!";
                                setTimeout(function() {{
                                    button.innerHTML = originalText;
                                }}, 2000);
                            }})
                            .catch(err => {{
                                console.error('복사 실패: ', err);
                            }});
                    }}
                    </script>
                    """
                    components.html(copy_button_html, height=50)
                
                with col2:
                    # 다운로드 버튼도 HTML로 구현
                    download_button_html = f"""
                    <div style="display: flex; align-items: center; height: 100%;">
                        <a 
                            href="data:text/plain;charset=utf-8,{transformed_prompt.replace('"', '&quot;')}" 
                            download="transformed_prompt.txt"
                            style="{button_style}"
                            onclick="this.innerHTML='✓ 다운로드 완료!'; setTimeout(() => this.innerHTML='📋 프롬프트 텍스트 파일로 다운로드', 2000)"
                        >
                            📋 프롬프트 텍스트 파일로 다운로드
                        </a>
                    </div>
                    """
                    components.html(download_button_html, height=50)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 설명 추가
                st.markdown("### 프롬프트 구조 설명")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**`<role>`**")
                    st.markdown("주제와 관련된 전문가의 역할, 경험, 전문성을 정의합니다.")
                    
                    st.markdown("**`<instructions>`**")
                    st.markdown("체계적인 분석과 접근을 위한 상세한 지시사항을 제공합니다.")
                
                with col2:
                    st.markdown("**`<response_style>`**")
                    st.markdown("응답의 톤, 스타일, 전문성 수준에 대한 지침을 제공합니다.")
                    
                    st.markdown("**`<reminder>`**")
                    st.markdown("고려해야 할 중요한 사항, 한계, 윤리적 측면을 상기시킵니다.")
                    
                    st.markdown("**`<output_format>`**")
                    st.markdown("사고 과정과 최종 결과물의 구조를 정의합니다.")
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# 사용 방법 및 설명
if not transform_button:
    st.markdown("""
    ### 🚀 프롬프트 엔지니어봇이란?
    
    AI 모델이 최고의 결과를 도출하도록 도와주는 도구입니다. 간단한 요청을 입력하면:
    
    1. **역할(Role)**: 관련 전문가의 자격, 경험, 전문성을 정의
    2. **지시사항(Instructions)**: 체계적인 접근 방식과 고려해야 할 요소
    3. **응답 스타일(Response Style)**: 원하는 응답의 톤, 깊이, 형식
    4. **주요 고려사항(Reminder)**: 다양한 관점, 윤리적 고려사항, 한계
    5. **출력 형식(Output Format)**: 사고 과정과 최종 결과의 구조
    
    이 모든 요소를 포함한 전문적인 프롬프트로 변환됩니다.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ 이럴 때 사용하세요")
        st.markdown("""
        - 전문적인 분석이나 조언이 필요할 때
        - 복잡한 주제에 대한 체계적인 접근이 필요할 때
        - AI의 응답 품질을 높이고 싶을 때
        - 특정 형식이나 구조의 결과물이 필요할 때
        """)
    
    with col2:
        st.markdown("#### 💡 활용 팁")
        st.markdown("""
        - 요청에 주제를 명확히 명시하세요
        - 커스텀 옵션을 활용해 특정 요구사항을 추가하세요
        - 원하는 출력 형식이나 범위를 직접 지정하세요
        - 특정 검색어를 지정하여 더 집중된 결과를 얻으세요
        """)

# 푸터
st.markdown('<div class="footer">© 2025 디엘토 | All Rights Reserved</div>', unsafe_allow_html=True)