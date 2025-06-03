"""
뉴스 기사에 대한 질문 생성 모듈
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import List
from pydantic import BaseModel, Field
from .utils import load_prompt, load_model_config

class QuestionList(BaseModel):
    questions: List[str] = Field(description="List of questions about the news article")

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

    # YAML 파일에서 프롬프트 템플릿 불러오기
    prompt_template = load_prompt('news_question_generator_prompt.yaml')
    question_prompt = ChatPromptTemplate.from_template(prompt_template)

    # config에서 모델 설정 불러오기
    model_config = load_model_config('news_question_generator')
    
    # LLM 설정
    llm = ChatOpenAI(**model_config)

    # 체인 구성
    question_chain = question_prompt.partial(format_instructions=question_parser.get_format_instructions()) | llm | question_parser

    return question_chain.invoke({"content": content})
