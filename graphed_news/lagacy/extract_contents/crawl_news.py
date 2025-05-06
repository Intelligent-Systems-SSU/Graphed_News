import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def async_crawl_news(url):
    """
    웹 페이지의 내용을 크롤링하여 마크다운 형식으로 반환합니다. (비동기 버전)
    
    Args:
        url (str): 크롤링할 웹 페이지의 URL
        
    Returns:
        str: 크롤링된 내용의 마크다운 텍스트
    """
    browser_config = BrowserConfig()  # Default browser configuration
    run_config = CrawlerRunConfig(
        excluded_tags=['form', 'header', 'footer', 'nav'],
        keep_data_attributes=False,
        only_text=True,
        # Link filtering
        exclude_external_links=True,    
        exclude_social_media_links=True,
        # Media filtering
        exclude_external_images=True
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_config
        )
        return result.markdown  # Return clean markdown content

def crawl_news(url):
    """
    웹 페이지의 내용을 크롤링하여 마크다운 형식으로 반환합니다. (동기식 버전)
    
    Args:
        url (str): 크롤링할 웹 페이지의 URL
        
    Returns:
        str: 크롤링된 내용의 마크다운 텍스트
    """
    return asyncio.run(async_crawl_news(url))

async def main(url):
    # 비동기 함수 사용 예시
    markdown = await async_crawl_news(url)
    print("비동기 호출 결과:", markdown[:100])  # 결과 일부 출력

if __name__ == "__main__":
    url = "https://www.hankyung.com/article/2025040632927"

    # 비동기식 호출 예시
    # asyncio.run(main())

    # 동기식 호출 예시
    markdown = crawl_news(url)
    print("동기식 호출 결과:", markdown)  