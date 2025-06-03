"""
뉴스 정제 및 주제, 키워드 추출 모듈
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import List
from pydantic import BaseModel, Field
from .utils import load_prompt, load_model_config

class NewsArticle(BaseModel):
    topic: str = Field(description="Topics for news articles")
    keywords: List[str] = Field(description="Key words or sentences extracted from articles to search for news on similar topics")
    content: str = Field(description="Refined news article content")

def extract_news_content(raw_content: str) -> NewsArticle:
    """
    LLM을 사용하여 뉴스 내용에서 필요한 부분만 추출합니다.
    
    Args:
        raw_content (str): 뉴스 내용 (마크다운 형식)
        
    Returns:
        NewsArticle: 필요한 부분만 추출된 뉴스 기사 객체 (topic, keywords, content)
    """
    # config에서 모델 설정 불러오기
    model_config = load_model_config('news_processor')
    
    llm = ChatOpenAI(**model_config)
    
    # Pydantic 출력 파서 설정
    article_parser = PydanticOutputParser(pydantic_object=NewsArticle)
    
    # YAML 파일에서 프롬프트 템플릿 불러오기
    prompt_template = load_prompt('news_processor_prompt.yaml')
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # 체인 구성 - 형식 지침 포함
    chain = prompt.partial(format_instructions=article_parser.get_format_instructions()) | llm | article_parser

    return chain.invoke({"raw_content": raw_content})
