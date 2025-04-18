import re
import os
import json
from typing import Dict, List, Optional, Tuple
from openai import OpenAI

class PromptEngine:
    """프롬프트 변환 엔진 클래스
    
    사용자의 간단한 입력을 구조화된 상세 프롬프트로 변환합니다.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4.1-nano", temperature: float = 0.7):
        """초기화 함수
        
        Args:
            openai_api_key: OpenAI API 키 (없으면 환경 변수에서 가져옴)
            model: 사용할 OpenAI 모델
            temperature: 생성 시 사용할 temperature 값
        """
        # OpenAI 클라이언트 초기화
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API 키가 제공되지 않았습니다. 환경 변수 OPENAI_API_KEY를 설정하거나 직접 제공해주세요.")
            self.client = OpenAI(api_key=api_key)
            
        # 모델과 temperature 설정
        self.model = model
        self.temperature = temperature
    
    def analyze_input(self, user_input: str) -> Dict:
        """사용자 입력을 분석하여 핵심 요소와 특정 요구사항을 추출
        
        Args:
            user_input: 사용자가 입력한 간단한 프롬프트
            
        Returns:
            Dict: 입력에서 추출한 핵심 요소들과 특정 요구사항
        """
        # OpenAI API를 사용하여 입력 분석
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": """당신은 텍스트 분석 전문가입니다. 사용자의 입력을 상세히 분석하여 다음 정보를 JSON 형식으로 추출해주세요:

1. 주제 (topic): 입력의 주요 주제
2. 분야 (domain): 관련된 전문 분야
3. 목적 (purpose): 사용자가 원하는 정보 또는 도움의 종류
4. 핵심어 (keywords): 입력에서 중요한 핵심 단어들 (최대 5개)
5. 전문성 수준 (expertise_level): 필요한 전문성 수준 (초급, 중급, 고급)
6. 특정 범위 (scope): 사용자가 언급한 특정 범위, 시간적/공간적 제약 (없으면 "광범위")
7. 특정 검색어 (search_terms): 사용자가 명시적으로 검색하거나 강조한 용어들 (없으면 빈 배열)
8. 원하는 출력 형식 (output_format): 사용자가 요청한 특정 출력 형식이나 구조 (예: "목록", "단계별 가이드", "비교 분석" 등)
9. 특별 요구사항 (special_requirements): 기타 사용자가 언급한 특별 요구사항들

입력을 세밀하게
"""
                },
                {"role": "user", "content": user_input}
            ]
        )
        
        # JSON 응답 파싱
        try:
            analysis = response.choices[0].message.content
            # 문자열에서 JSON 부분만 추출
            json_match = re.search(r'{.*}', analysis, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group(0))
            else:
                # JSON이 감지되지 않으면 원본 응답을 반환
                return {"raw_analysis": analysis}
        except Exception as e:
            print(f"분석 응답 처리 오류: {e}")
            return {"error": str(e), "raw_analysis": response.choices[0].message.content}

    def generate_expert_role(self, user_input: str, analysis: Dict) -> str:
        """분석 결과를 바탕으로 전문가 역할 생성
        
        Args:
            user_input: 사용자가 입력한 간단한 프롬프트
            analysis: 입력 분석 결과
            
        Returns:
            str: 생성된 전문가 역할 설명
        """
        # 특정 검색어나 범위가 있으면 포함
        special_focus = ""
        if analysis.get('scope') and analysis.get('scope') != "광범위":
            special_focus += f"\n특정 범위: {analysis.get('scope')}"
        
        if analysis.get('search_terms') and len(analysis.get('search_terms', [])) > 0:
            special_focus += f"\n특정 검색어: {', '.join(analysis.get('search_terms'))}"
        
        # OpenAI API를 사용하여 전문가 역할 생성
        role_prompt = f"""
        다음 주제에 관한 최고 수준의 전문가 역할을 상세하게 설명해주세요:
        
        주제: {analysis.get('topic', '일반 주제')}
        분야: {analysis.get('domain', '다양한 분야')}
        필요 전문성: {analysis.get('expertise_level', '고급')}{special_focus}
        
        이 역할에는 관련 경험, 자격, 전문 지식, 접근 방식 등이 포함되어야 합니다.
        전문가의 배경, 경력, 성과 등을 구체적으로 설명하세요.
        1-2단락 정도의 상세한 설명으로 작성해주세요.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": "당신은 전문 분야별 역할 정의를 작성하는 전문가입니다."},
                {"role": "user", "content": role_prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def generate_instructions(self, user_input: str, analysis: Dict) -> str:
        """분석 결과를 바탕으로 상세 지시사항 생성
        
        Args:
            user_input: 사용자가 입력한 간단한 프롬프트
            analysis: 입력 분석 결과
            
        Returns:
            str: 생성된 지시사항
        """
        # 특정 요구사항이나 형식 포함
        special_requirements = ""
        
        if analysis.get('special_requirements'):
            special_requirements += f"\n특별 요구사항: {analysis.get('special_requirements')}"
        
        if analysis.get('output_format'):
            special_requirements += f"\n원하는 출력 형식: {analysis.get('output_format')}"
            
        if analysis.get('scope') and analysis.get('scope') != "광범위":
            special_requirements += f"\n분석 범위: {analysis.get('scope')}"
        
        # OpenAI API를 사용하여 지시사항 생성
        instructions_prompt = f"""
        다음 주제에 관한 상세하고 체계적인 지시사항을 작성해주세요:
        
        주제: {analysis.get('topic', '일반 주제')}
        분야: {analysis.get('domain', '다양한 분야')}
        목적: {analysis.get('purpose', '정보 제공')}
        핵심어: {', '.join(analysis.get('keywords', ['관련 키워드']))}{special_requirements}
        
        최소 5-7개의 주요 지시사항을 작성하고, 각 항목마다 2-3개의 하위 지시사항을 포함해주세요.
        지시사항은 다음 형식을 따라야 합니다:
        
        1. [첫 번째 주요 지시사항]:
           - [하위 지시사항 1]
           - [하위 지시사항 2]
        2. [두 번째 주요 지시사항]:
           - [하위 지시사항 1]
           - [하위 지시사항 2]
           - [하위 지시사항 3]
        
        각 지시사항은 논리적 순서로 배치하고, 포괄적이면서도 구체적이어야 합니다.
        특히 사용자가 언급한 특정 검색어나 요구사항에 집중하세요.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": "당신은 체계적이고 전문적인 지시사항을 작성하는 전문가입니다."},
                {"role": "user", "content": instructions_prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def generate_response_style(self, user_input: str, analysis: Dict) -> str:
        """분석 결과를 바탕으로 응답 스타일 가이드라인 생성
        
        Args:
            user_input: 사용자가 입력한 간단한 프롬프트
            analysis: 입력 분석 결과
            
        Returns:
            str: 생성된 응답 스타일 가이드라인
        """
        # 원하는 출력 형식이 있으면 포함
        format_requirements = ""
        if analysis.get('output_format'):
            format_requirements = f"\n원하는 출력 형식: {analysis.get('output_format')}"
        
        # OpenAI API를 사용하여 응답 스타일 생성
        style_prompt = f"""
        다음 주제에 관한 전문적인 응답 스타일 가이드라인을 작성해주세요:
        
        주제: {analysis.get('topic', '일반 주제')}
        분야: {analysis.get('domain', '다양한 분야')}
        전문성 수준: {analysis.get('expertise_level', '고급')}{format_requirements}
        
        응답의 톤, 접근 방식, 전문성 수준, 용어 사용, 구성 방식 등에 대한 구체적인 지침을 포함해주세요.
        한 단락 정도의 구체적인 설명으로 작성해주세요.
        사용자가 요청한 특정 출력 형식이 있다면 이를 반영하세요.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": "당신은 전문적인 커뮤니케이션 스타일 가이드를 작성하는 전문가입니다."},
                {"role": "user", "content": style_prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def generate_reminders(self, user_input: str, analysis: Dict) -> str:
        """분석 결과를 바탕으로 주요 고려사항 생성
        
        Args:
            user_input: 사용자가 입력한 간단한 프롬프트
            analysis: 입력 분석 결과
            
        Returns:
            str: 생성된 주요 고려사항
        """
        # 특정 요구사항이나 범위 포함
        special_considerations = ""
        if analysis.get('special_requirements'):
            special_considerations += f"\n특별 요구사항: {analysis.get('special_requirements')}"
            
        if analysis.get('scope') and analysis.get('scope') != "광범위":
            special_considerations += f"\n분석 범위: {analysis.get('scope')}"
            
        if analysis.get('search_terms') and len(analysis.get('search_terms', [])) > 0:
            special_considerations += f"\n중점적으로 다룰 검색어: {', '.join(analysis.get('search_terms'))}"
        
        # OpenAI API를 사용하여 주요 고려사항 생성
        reminders_prompt = f"""
        다음 주제에 관한 주요 고려사항 목록을 작성해주세요:
        
        주제: {analysis.get('topic', '일반 주제')}
        분야: {analysis.get('domain', '다양한 분야')}
        목적: {analysis.get('purpose', '정보 제공')}{special_considerations}
        
        최소 5-7개의 중요한 고려사항, 주의점, 윤리적 측면, 한계, 다양한 관점 등을 포함해주세요.
        각 항목은 간결하고 명확하게 불릿 포인트(-)로 작성해주세요.
        사용자가 언급한 특정 범위, 검색어 또는 요구사항을 고려하세요.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": "당신은 주제별 중요 고려사항을 정리하는 전문가입니다."},
                {"role": "user", "content": reminders_prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def generate_output_format(self, analysis: Dict) -> str:
        """분석 결과를 바탕으로 출력 형식 생성
        
        Args:
            analysis: 입력 분석 결과
            
        Returns:
            str: 생성된 출력 형식
        """
        # 원하는 출력 형식이 있으면 포함
        format_guidance = ""
        if analysis.get('output_format'):
            format_guidance = f"\n원하는 출력 형식: {analysis.get('output_format')}"
            
        # 특정 검색어나 범위가 있으면 포함
        if analysis.get('scope') and analysis.get('scope') != "광범위":
            format_guidance += f"\n분석 범위: {analysis.get('scope')}"
            
        if analysis.get('search_terms') and len(analysis.get('search_terms', [])) > 0:
            format_guidance += f"\n중점적으로 다룰 검색어: {', '.join(analysis.get('search_terms'))}"
        
        # OpenAI API를 사용하여 출력 형식 생성
        format_prompt = f"""
        다음 주제에 관한 체계적인 출력 형식을 작성해주세요:
        
        주제: {analysis.get('topic', '일반 주제')}
        분야: {analysis.get('domain', '다양한 분야')}
        목적: {analysis.get('purpose', '정보 제공')}{format_guidance}
        
        다음 두 부분으로 나누어 작성해주세요:
        
        1. <thinking_process> - 사고 과정과 접근 방식에 대한 구체적인 설명 형식
        2. <final_response> - 최종 결과물의 구체적인 형식과 구조 (목차 형태로 제시)
        
        특히 <final_response> 부분은 주제에 가장 적합한 구조화된 목차 형태로 제시해주세요.
        사용자가 요청한 특정 출력 형식이 있다면 이를 정확히 반영하세요.
        섹션 제목과 간략한 각 섹션의 내용 설명을 포함해야 합니다.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": "당신은 체계적인 문서 구조와 출력 형식을 설계하는 전문가입니다."},
                {"role": "user", "content": format_prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def extract_format_requirements(self, user_input: str) -> Dict:
        """사용자 입력에서 명시적인 형식 요구사항을 추출
        
        Args:
            user_input: 사용자가 입력한 간단한 프롬프트
            
        Returns:
            Dict: 추출된 형식 요구사항
        """
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": """당신은 텍스트에서 형식 요구사항을 추출하는 전문가입니다.
                사용자의 입력을 분석하여 다음을 JSON 형식으로 추출해주세요:
                
                1. format_type: 요청된 형식 유형 (예: 목록, 에세이, 단계별 가이드, 비교표 등)
                2. sections: 명시적으로 요청된 섹션이나 구성 요소 (배열)
                3. style: 언급된 스타일 (예: 학술적, 대화형, 설명적 등)
                4. special_requirements: 기타 형식 관련 특별 요청사항
                
                JSON 형식으로만 응답하세요. 추가 설명이나 텍스트는 포함하지 마세요."""},
                {"role": "user", "content": user_input}
            ]
        )
        
        try:
            content = response.choices[0].message.content
            json_match = re.search(r'{.*}', content, re.DOTALL)
            if json_match:
                import json
                return json.loads(json_match.group(0))
            else:
                return {}
        except Exception as e:
            print(f"형식 요구사항 추출 오류: {e}")
            return {}
    
    def transform_prompt_single_call(self, user_input: str) -> str:
        """사용자 입력을 상세한 프롬프트로 변환합니다 (단일 API 호출 방식).
        
        이 메서드는 단일 API 호출을 사용하여 사용자 입력을 상세한 프롬프트로 변환합니다.
        모든 섹션(분석, 전문가 역할, 지시사항, 응답 스타일, 주요 고려사항, 출력 형식)을 한 번에 생성하여
        비용을 절감하고 처리 속도를 향상시킵니다.
        
        Args:
            user_input: 사용자가 입력한 간단한 프롬프트
            
        Returns:
            str: 변환된 상세 프롬프트
        """
        # 시스템 프롬프트 정의
        system_prompt = """사용자 입력을 분석하고 여러 섹션으로 이루어진 상세한 프롬프트를 생성하세요.
각 섹션은 명확한 헤더로 시작해야 합니다. 아래 섹션을 생성하세요:

1. 분석: 사용자 입력의 의도와 목적을 분석하고, 주요 측면과 요구사항을 식별하세요.
제목은 "### 분석:"으로 시작하세요.

2. 전문가 역할: 사용자 요청을 처리하기 위한 가장 적합한 전문가 역할을 정의하세요.
제목은 "### 전문가 역할:"로 시작하세요.

3. 지시사항: 전문가를 위한 명확하고 구체적인 지시사항을 제공하세요. 이는 전문가가 응답을 생성할 때 따라야 할 단계, 고려해야 할 요소, 필요한 정보 등을 포함해야 합니다.
제목은 "### 지시사항:"으로 시작하세요.

4. 응답 스타일: 응답의 스타일, 형식, 톤을 정의하세요.
제목은 "### 응답 스타일:"로 시작하세요.

5. 주요 고려사항: 모델이 응답을 생성할 때 반드시 고려해야 할 중요한 사항들을 강조하세요.
제목은 "### 주요 고려사항:"으로 시작하세요.

6. 출력 형식(선택적): 사용자 입력에 특정 출력 형식이 필요한 경우, 출력 형식에 대한 상세한 지침을 제공하세요.
제목은 "### 출력 형식:"으로 시작하세요.

각 섹션을 명확하게 분릿하고, 내용은 구체적이고 상세해야 합니다."""

        # API 호출로 프롬프트 생성
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        
        # 각 섹션을 추출하기 위한 정규식 패턴
        patterns = {
            "analysis": r"### 분석:(.*?)(?=### |$)",
            "expert_role": r"### 전문가 역할:(.*?)(?=### |$)",
            "instructions": r"### 지시사항:(.*?)(?=### |$)",
            "response_style": r"### 응답 스타일:(.*?)(?=### |$)",
            "reminders": r"### 주요 고려사항:(.*?)(?=### |$)",
            "output_format": r"### 출력 형식:(.*?)(?=### |$)"
        }
        
        # 각 섹션 추출
        sections = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, response.choices[0].message.content, re.DOTALL)
            if match:
                # 추출된 내용 앞뒤 공백 제거
                sections[key] = match.group(1).strip()
            else:
                sections[key] = None
        
        # 최종 프롬프트 구성
        final_prompt = "<prompt>\n"
        
        # 필수 섹션 추가
        if sections["analysis"]:
            final_prompt += f"<analysis>\n{sections['analysis']}\n</analysis>\n\n"
        
        if sections["expert_role"]:
            final_prompt += f"<role>\n당신은 {sections['expert_role']}\n</role>\n\n"
            
        if sections["instructions"]:
            final_prompt += f"<instructions>\n{sections['instructions']}\n</instructions>\n\n"
            
        if sections["response_style"]:
            final_prompt += f"<response_style>\n{sections['response_style']}\n</response_style>\n\n"
            
        if sections["reminders"]:
            final_prompt += f"<reminder>\n{sections['reminders']}\n</reminder>\n\n"
        
        # 선택적 섹션 추가
        if sections["output_format"]:
            final_prompt += f"<output_format>\n{sections['output_format']}\n</output_format>\n\n"
        
        final_prompt += "</prompt>"
        
        return final_prompt.strip()
        
    def transform_prompt(self, user_input: str, use_multi_call: bool = False) -> str:
        """사용자 입력을 상세한 프롬프트로 변환합니다.
        
        이 메서드는 사용자의 간단한 입력을 상세하고 구조화된 프롬프트로 변환합니다.
        
        Args:
            user_input: 사용자가 입력한 간단한 프롬프트
            use_multi_call: 여러 API 호출을 사용할지 여부. 
                            True인 경우 여러 API 호출을 통해 고품질 결과를 생성합니다(비용 증가).
                            False인 경우 단일 API 호출을 사용하여 비용을 절감합니다(품질 저하 가능성).
            
        Returns:
            str: 변환된 상세 프롬프트
        """
        if use_multi_call:
            return self.transform_prompt_multi_call(user_input)
        else:
            return self.transform_prompt_single_call(user_input)

    def transform_prompt_multi_call(self, user_input: str) -> str:
        """사용자 입력을 여러 API 호출을 통해 상세한 프롬프트로 변환합니다.
        
        이 메서드는 각 섹션을 별도의 API 호출로 생성하여 높은 품질의 결과를 제공합니다.
        (비용이 더 많이 발생합니다)
        
        Args:
            user_input: 사용자가 입력한 간단한 프롬프트
            
        Returns:
            str: 변환된 상세 프롬프트
        """
        # 입력 분석
        analysis = self.analyze_input(user_input)
        
        # 출력 형식 요구사항 추출
        format_requirements = self.extract_format_requirements(user_input)
        
        # 전문가 역할 생성
        expert_role = self.generate_expert_role(user_input, analysis)
        
        # 지시사항 생성
        instructions = self.generate_instructions(user_input, analysis)
        
        # 응답 스타일 생성
        response_style = self.generate_response_style(user_input, analysis)
        
        # 주요 고려사항 생성
        key_considerations = self.generate_reminders(user_input, analysis)
        
        # 출력 형식 생성 (있는 경우)
        output_format = ""
        if format_requirements:
            output_format = self.generate_output_format(format_requirements)
        
        # 최종 프롬프트 구성
        final_prompt = f"""<prompt>

<analysis>
{analysis}
</analysis>

<role>
{expert_role}
</role>

<instructions>
{instructions}
</instructions>

<response_style>
{response_style}
</response_style>

<reminder>
{key_considerations}
</reminder>"""

        # 출력 형식이 있는 경우 추가
        if output_format:
            final_prompt += f"""

<output_format>
{output_format}
</output_format>"""
            
        final_prompt += "\n</prompt>"
        
        return final_prompt 