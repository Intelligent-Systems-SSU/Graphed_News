"""
뉴스 기사 크롤링 및 증강 메인 모듈
"""
import asyncio
import argparse
import httpx
from typing import Dict, Any

from core.news_crawler import crawl_news
from core.news_processor import extract_news_content
from core.news_qa_generator import generate_questions
from core.news_qa_agent import NewsQnAAgent
from core.news_accumulator import NewsAccumulator

async def process_news_article(url: str) -> Dict[str, Any]:
    """
    뉴스 기사 URL을 처리하여 증강된 결과를 반환합니다.
    
    Args:
        url (str): 처리할 뉴스 기사 URL
        
    Returns:
        Dict[str, Any]: 처리 결과
    """
    print(f"뉴스 기사 크롤링: {url}")
    content = await crawl_news(url)
    
    print("뉴스 정제 및 주제, 키워드 추출")
    extracted_content = extract_news_content(content)
    
    print(f"주제: {extracted_content.topic}")
    print(f"키워드: {', '.join(extracted_content.keywords)}")
    
    print("질문 생성")
    question_list = generate_questions(extracted_content.content)
    print(f"생성된 질문 수: {len(question_list)}")
    
    print("질문에 대한 답변 생성")
    qna_agent = NewsQnAAgent()
    answers = qna_agent.process_questions(extracted_content.content, question_list)
    
    print("최종 결과 생성")
    accumulator = NewsAccumulator()
    final_result = accumulator.process(extracted_content.content, answers)
    
    # 최종 결과물 출력
    print("\n=== 최종 결과 ===")
    print("\n키워드 및 설명:")
    for item in final_result["final_keywords_with_explanation"]:
        print(f"- 키워드: {item['keyword']}")
        print(f"  설명: {item['description']}")
    
    print("\n최종 요약:")
    print(final_result["final_summary"])
    
    # 전체 결과 반환
    return {
        "url": url,
        "original_content": content,
        "extracted_content": {
            "content": extracted_content.content,
            "topic": extracted_content.topic,
            "keywords": extracted_content.keywords
        },
        "questions": question_list,
        "answers": answers,
        "final_keywords": final_result["final_keywords_with_explanation"],
        "final_summary": final_result["final_summary"]
    }

async def main():
    """
    메인 실행 함수
    """
    parser = argparse.ArgumentParser(description="News article crawler and enhancer")
    parser.add_argument("--url", type=str, help="URL of the news article to process",
                        default="https://n.news.naver.com/mnews/article/028/0002746694")
    parser.add_argument("--news-id", type=str, help="News ID for the POST request", required=False)
    args = parser.parse_args()
    
    result = await process_news_article(args.url)
    
    # POST 요청으로 결과 전송
    if args.news_id:
        try:
            print(f"\nPOST 요청 전송 중... (newsId: {args.news_id})")
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    'https://graphed-news.pages.dev/ai',
                    json={
                        'newsId': args.news_id,
                        'summary': result["final_summary"],
                        'keyword': result["final_keywords"]
                    }
                )
                print(f"POST 요청 완료 - 상태 코드: {res.status_code}")
                if res.status_code == 200:
                    print("결과가 성공적으로 전송되었습니다.")
                else:
                    print(f"POST 요청 실패: {res.text}")
        except Exception as e:
            print(f"POST 요청 중 오류 발생: {e}")
    else:
        print("\n--news-id 인수가 제공되지 않아 POST 요청을 건너뜁니다.")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
