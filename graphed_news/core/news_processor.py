"""
뉴스 정제 및 주제, 키워드 추출 모듈
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class NewsArticle(BaseModel):
    content: str = Field(description="Refined news article content")
    topic: str = Field(description="Topics for news articles")
    keywords: List[str] = Field(description="Key words or sentences extracted from articles to search for news on similar topics")
    
    def to_dict(self) -> Dict[str, Any]:
        return {"content": self.content, "keywords": self.keywords}

def extract_news_content(content):
    """
    LLM을 사용하여 뉴스 내용에서 필요한 부분만 추출합니다.
    
    Args:
        content (str): 뉴스 내용 (마크다운 형식)
        
    Returns:
        NewsArticle: 필요한 부분만 추출된 뉴스 기사 객체 (content, topic, keywords)
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )
    
    # Pydantic 출력 파서 설정
    article_parser = PydanticOutputParser(pydantic_object=NewsArticle)
    
    # LLM에 보낼 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_template(
        """다음은 웹 크롤링을 통해 얻은 뉴스 기사 내용입니다. 
        아래 세 가지 작업을 수행해주세요:
        
        1. 뉴스 기사의 실제 내용(제목, 본문, 날짜)만 추출하고, 
           광고, 메뉴, 푸터, 사이드바 등의 불필요한 내용은 모두 제거해주세요.
        2. 뉴스 기사의 주제를 추출해주세요. 주제는 기사를 요약하는 단어 또는 짧은 문장으로 작성해주세요.
        3. 관련 주제의 기사를 검색하기 위한 핵심 키워드를 5-10개 추출해주세요. 짧은 문장도 가능합니다. 
        
        원본 내용:
        {content}
        
        {format_instructions}
        """
    )
    
    # 체인 구성 - 형식 지침 포함
    chain = prompt.partial(format_instructions=article_parser.get_format_instructions()) | llm | article_parser
    
    # 체인 실행
    result = chain.invoke({"content": content})
    
    return result
