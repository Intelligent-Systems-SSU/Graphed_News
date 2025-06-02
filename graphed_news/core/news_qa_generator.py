"""
뉴스 기사에 대한 질문 생성 모듈
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import List
from pydantic import BaseModel, Field

class QuestionList(BaseModel):
    questions: List[str] = Field(description="뉴스 기사에 대한 질문 목록")

def generate_questions(content):
    """
    뉴스 기사 내용에 대한 질문 목록을 생성합니다.
    
    Args:
        content (str): 정제된 뉴스 기사 내용
        
    Returns:
        List[str]: 생성된 질문 목록
    """
    # 출력 파서 설정
    question_parser = PydanticOutputParser(pydantic_object=QuestionList)

    # 프롬프트 템플릿 생성
    question_prompt = ChatPromptTemplate.from_template(
        """다음은 뉴스 기사 내용입니다:

        {content}

        이 기사를 읽고 이해가 안되는 부분에 대한 질문을 여러 개 생성해주세요.
        질문은 명확하고 구체적이어야 하며, 기사의 내용을 바탕으로 해야 합니다.
        각 질문은 독립적이어야 합니다.

        {format_instructions}
        """
    )

    # LLM 설정
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0
    )

    # 체인 구성
    question_chain = question_prompt.partial(format_instructions=question_parser.get_format_instructions()) | llm | question_parser

    # 프롬프트 실행
    question_response = question_chain.invoke({"content": content})
    
    # 결과 반환
    return question_response.questions if hasattr(question_response, 'questions') else []
