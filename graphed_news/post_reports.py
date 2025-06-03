"""
뉴스 기사 크롤링 및 증강 메인 모듈 - POST 전송용
"""
import argparse
import httpx
from typing import Dict, Any

from main import analyze_articles, print_results


def prepare_post_data(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    analyze_articles 결과를 POST 요청용 데이터로 변환
    
    Args:
        results: analyze_articles 함수의 결과
        
    Returns:
        POST 요청용 데이터
    """
    # ka_pairs에서 키워드 정보 추출
    keywords = []
    for ka_pair in results.get('ka_pairs', []):
        keyword = list(ka_pair.keys())[0]
        explanation = list(ka_pair.values())[0]
        keywords.append({
            'keyword': keyword,
            'description': explanation
        })
    
    return {
        'summary': results['final_result'],
        'keyword': keywords
    }


async def send_post_request(news_id: str, post_data: Dict[str, Any]) -> bool:
    """
    POST 요청 전송
    
    Args:
        news_id: 뉴스 ID
        post_data: 전송할 데이터
        
    Returns:
        성공 여부
    """
    try:
        print(f"\nPOST 요청 전송 중... (newsId: {news_id})")
        async with httpx.AsyncClient() as client:
            payload = {
                'newsId': news_id,
                **post_data
            }
            res = await client.post(
                'https://graphed-news.pages.dev/ai',
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            print(f"POST 요청 완료 - 상태 코드: {res.status_code}")
            if res.status_code == 200:
                print("결과가 성공적으로 전송되었습니다.")
                return True
            else:
                print(f"POST 요청 실패: {res.text}")
                return False
    except Exception as e:
        print(f"POST 요청 중 오류 발생: {e}")
        return False


def main():
    """
    메인 실행 함수
    """
    parser = argparse.ArgumentParser(description="News article crawler and enhancer with POST")
    parser.add_argument("--url", type=str, help="URL of the news article to process",
                        default="https://n.news.naver.com/mnews/article/421/0008261200")
    parser.add_argument("--news-id", type=str, help="News ID for the POST request", required=False)
    args = parser.parse_args()
    
    try:
        results = analyze_articles(args.url)
        
        # 결과 출력
        print_results(results)
        
        # POST 요청 전송
        if args.news_id:
            import asyncio
            post_data = prepare_post_data(results)
            success = asyncio.run(send_post_request(args.news_id, post_data))
            if not success:
                print("POST 요청 전송에 실패했습니다.")
        else:
            print("\n--news-id 인수가 제공되지 않아 POST 요청을 건너뜁니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
