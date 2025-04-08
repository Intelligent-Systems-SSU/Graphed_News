import os
import sys
from pathlib import Path
import json

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from graphed_news.database.example_db import NewsDatabase

def query_examples():
    """데이터베이스 쿼리 예제"""
    
    # 데이터베이스 인스턴스 생성
    db_path = os.path.join(project_root, "graphed_news", "database", "example_news.db")
    db = NewsDatabase(db_path)
    
    # 예제 URL
    url = "https://www.hankyung.com/article/2025040632927"
    
    # 1. 기사 정보만 조회
    article = db.get_article_by_url(url)
    if article:
        print("===== 기사 정보 =====")
        print(f"제목: {article['title']}")
        print(f"키워드: {', '.join(article['keywords'])}")
        print(f"발행일: {article['published_date']}")
        print(f"수집일: {article['crawled_date']}")
        print(f"내용: {article['content'][:200]}...\n")
    
    # 2. 용어 설명 목록 조회
    if article:
        article_id = article['id']
        db.cursor.execute("SELECT term, explanation FROM terms WHERE article_id = ?", (article_id,))
        terms = db.cursor.fetchall()
        
        print("===== 용어 설명 =====")
        for term in terms:
            print(f"용어: {term['term']}")
            print(f"설명: {term['explanation'][:100]}...\n")
    
    # 3. 특정 키워드의 관련 뉴스 조회
    if article:
        article_id = article['id']
        keyword_example = article['keywords'][0] if article['keywords'] else ""
        
        if keyword_example:
            db.cursor.execute("""
            SELECT related_title, related_url, related_date 
            FROM related_news 
            WHERE article_id = ? AND keyword = ?
            """, (article_id, keyword_example))
            related_news = db.cursor.fetchall()
            
            print(f"===== 키워드 '{keyword_example}'의 관련 뉴스 =====")
            for news in related_news:
                print(f"제목: {news['related_title']}")
                print(f"URL: {news['related_url']}")
                print(f"날짜: {news['related_date']}\n")
    
    # 4. 모든 관련 정보 조회
    all_data = db.get_article_with_all_data(url)
    if all_data:
        print("===== 기사 전체 정보 구조 =====")
        print(f"기사 정보: {type(all_data['article'])}")
        print(f"용어 설명: {len(all_data['terms'])} 항목")
        print(f"배경 정보: {len(all_data['background_info'])} 항목")
        print(f"타임라인: {len(all_data['timeline'])} 이벤트")
        print(f"관련 뉴스: {len(all_data['related_news'])} 키워드\n")
        
        # 타임라인 정보 예시
        print("===== 타임라인 예시 =====")
        for event in all_data['timeline'][:3]:  # 처음 3개만 표시
            print(f"날짜: {event['event_date']}")
            print(f"설명: {event['description']}")
            print(f"중요도: {event['importance']}\n")
    
    db.close()

if __name__ == "__main__":
    query_examples()
