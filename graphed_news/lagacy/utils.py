import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import List, Dict, Any
from pydantic import BaseModel, Field

def crawl_news(url):
    """
    웹 페이지의 내용을 크롤링하여 마크다운 형식으로 반환합니다. (동기식 버전)
    
    Args:
        url (str): 크롤링할 웹 페이지의 URL
        
    Returns:
        str: 크롤링된 내용의 마크다운 텍스트
    """
    async def async_crawl_news(url):
        browser_config = BrowserConfig()  # Default browser configuration
        run_config = CrawlerRunConfig(
            excluded_tags=['form', 'header', 'footer', 'nav'],
            keep_data_attributes=False,
            only_text=True,
            exclude_external_links=True,    
            exclude_social_media_links=True,
            exclude_external_images=True
        )
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=run_config
            )
            return result.markdown  # Return clean markdown content
    return asyncio.run(async_crawl_news(url))


class NewsArticle(BaseModel):
    content: str = Field(description="정제된 뉴스 기사 내용")
    topic: str = Field(description="뉴스 기사의 주제")
    keywords: List[str] = Field(description="기사에서 추출한 관련 뉴스기사 검색용 핵심 키워드 또는 문장")
    
    def to_dict(self) -> Dict[str, Any]:
        return {"content": self.content, "keywords": self.keywords}

def extract_news_content(content):
    """
    LLM을 사용하여 뉴스 내용에서 필요한 부분만 추출합니다.
    
    Args:
        content (str): 뉴스 내용 (마크다운 형식)
        llm (LLM, optional): 사용할 LLM 객체
        
    Returns:
        str: 필요한 부분만 추출된 뉴스 내용
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
        아래 두 가지 작업을 수행해주세요:
        
        1. 뉴스 기사의 실제 내용(제목, 본문, 날짜, 작성자 등)만 추출하고, 
           광고, 메뉴, 푸터, 사이드바 등의 불필요한 내용은 모두 제거해주세요.
        2. 관련 기사를 검색하기 위한 핵심 키워드를 5-10개 추출해주세요. 짧은 문장도 가능합니다. 
        
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

def process_news_from_url(url):
    """
    URL에서 뉴스를 크롤링하고 LLM으로 필요한 부분만 추출합니다.
    
    Args:
        url (str): 뉴스 기사 URL
        llm (LLM, optional): 사용할 LLM 객체
        
    Returns:
        str: 필요한 부분만 추출된 뉴스 내용
    """
    # 뉴스 크롤링
    content = crawl_news(url)
    
    # 내용 추출
    extracted_content = extract_news_content(content)
    
    return extracted_content

if __name__ == "__main__":
    url = "https://www.hankyung.com/article/2025040632927"
    # markdown = crawl_news(url)
    # print("동기식 호출 결과:", markdown)

    result = process_news_from_url(url)
    print("처리 결과:")
    print("추출된 주제:", result.topic)
    print("추출된 내용:", result.content)
    print("추출된 키워드:", result.keywords)