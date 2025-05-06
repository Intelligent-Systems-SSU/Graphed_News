import os
import sys
import json
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from graphed_news.extract_contents.extract_essence import process_news_from_url
from graphed_news.extract_contents.retrieve_relative import get_related_news
from graphed_news.extract_contents.rag_agent import enhance_news_understanding
from graphed_news.database.example_db import NewsDatabase

def generate_example_data():
    """뉴스 URL 목록에서 데이터를 생성하고 데이터베이스에 저장"""
    
    # 샘플 뉴스 URL 목록
    urls = [
        "https://www.hankyung.com/article/2025040632927",
        "https://www.yna.co.kr/view/AKR20240512039800001",
        "https://www.donga.com/news/article/all/20240512/123372450/1"
    ]
    
    # 데이터베이스 인스턴스 생성
    db_path = os.path.join(project_root, "graphed_news", "database", "example_news.db")
    db = NewsDatabase(db_path)
    
    # 각 URL에 대해 처리
    for url in urls:
        try:
            print(f"Processing URL: {url}")
            
            # 1. 기사 내용 및 키워드 추출
            news_result = process_news_from_url(url)
            
            # 2. 관련 뉴스 검색
            # 환경 변수에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET 설정 필요
            related_news_data = get_related_news(url)
            
            # 3. 향상된 이해 컨텍스트 생성
            # 환경 변수에 OPENAI_API_KEY 설정 필요
            enhanced_data = enhance_news_understanding(url)
            
            # 기사 제목 (첫 번째 줄 또는 기본값)
            lines = news_result.content.strip().split('\n')
            title = lines[0] if lines else "제목 없음"
            
            # 데이터베이스에 정보 저장
            db.store_enhanced_news(
                url=url,
                title=title,
                content=news_result.content,
                keywords=news_result.keywords,
                related_news=related_news_data["related_news"],
                enhanced_context=enhanced_data["enhanced_context"]
            )
            
            print(f"Successfully stored data for URL: {url}")
            
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
    
    # 저장된 데이터 확인
    for url in urls:
        try:
            data = db.get_article_with_all_data(url)
            if data:
                print(f"\nStored data for: {data['article']['title']}")
                print(f"  Terms: {len(data['terms'])}")
                print(f"  Background info topics: {len(data['background_info'])}")
                print(f"  Timeline events: {len(data['timeline'])}")
                print(f"  Related news keywords: {len(data['related_news'])}")
            else:
                print(f"No data found for URL: {url}")
        except Exception as e:
            print(f"Error retrieving data for URL {url}: {str(e)}")
    
    db.close()

if __name__ == "__main__":
    generate_example_data()
