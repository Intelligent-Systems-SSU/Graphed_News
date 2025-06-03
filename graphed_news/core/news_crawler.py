"""
뉴스 기사 크롤링 모듈
"""
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def crawl_news(url):
    """
    웹 페이지의 내용을 크롤링하여 마크다운 형식으로 반환합니다.
    
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
        exclude_external_links=True,    
        exclude_social_media_links=True,
        exclude_external_images=True
    )
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_config
        )
        return result.markdown
