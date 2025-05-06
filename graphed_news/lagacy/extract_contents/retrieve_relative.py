from extract_essence import process_news_from_url
import os
import json
import urllib.request
import urllib.parse

def search_naver_news(keywords, client_id=None, client_secret=None, display=10):
    """
    네이버 뉴스 API를 사용하여 키워드 기반 검색을 수행합니다.
    
    Args:
        keywords (list): 검색할 키워드 리스트
        client_id (str, optional): 네이버 API 클라이언트 ID
        client_secret (str, optional): 네이버 API 클라이언트 시크릿
        display (int, optional): 각 키워드당 표시할 검색 결과 수
        
    Returns:
        dict: 키워드별 검색 결과
    """
    # 환경 변수나 매개변수에서 API 인증 정보 가져오기
    client_id = client_id or os.environ.get("NAVER_CLIENT_ID")
    client_secret = client_secret or os.environ.get("NAVER_CLIENT_SECRET")
    print(client_id, client_secret)
    
    if not client_id or not client_secret:
        raise ValueError("네이버 API 클라이언트 ID와 시크릿이 필요합니다.")
    
    search_results = {}
    
    for keyword in keywords:
        # 키워드 인코딩
        encText = urllib.parse.quote(keyword)
        
        # API URL 생성 (검색 결과 수와 정렬 방식 지정)
        url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={display}&sort=sim"
        
        # HTTP 요청 생성
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        
        try:
            # API 호출 및 응답 처리
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            
            if rescode == 200:  # 성공
                response_body = response.read()
                result_json = json.loads(response_body.decode('utf-8'))
                search_results[keyword] = result_json
            else:
                print(f"키워드 '{keyword}' 검색 실패: Error Code {rescode}")
                search_results[keyword] = {"error": f"API Error Code: {rescode}"}
        except Exception as e:
            print(f"키워드 '{keyword}' 검색 중 오류 발생: {str(e)}")
            search_results[keyword] = {"error": str(e)}
    
    return search_results

def get_related_news(url, client_id=None, client_secret=None, max_keywords=5, display=3):
    """
    뉴스 URL로부터 키워드를 추출하고 관련 뉴스를 검색합니다.
    
    Args:
        url (str): 분석할 뉴스 기사 URL
        client_id (str, optional): 네이버 API 클라이언트 ID
        client_secret (str, optional): 네이버 API 클라이언트 시크릿
        max_keywords (int, optional): 사용할 최대 키워드 수
        display (int, optional): 각 키워드당 표시할 검색 결과 수
        
    Returns:
        dict: 키워드별 관련 뉴스 검색 결과
    """
    # 뉴스 처리 및 키워드 추출
    results = process_news_from_url(url)
    
    # 사용할 키워드 선택 (최대 max_keywords개)
    selected_keywords = results.keywords[:max_keywords] if len(results.keywords) > max_keywords else results.keywords

    # 키워드로 관련 뉴스 검색
    related_news = search_naver_news(selected_keywords, client_id, client_secret, display)
    
    return {
        "original_content": results.content,
        "all_keywords": results.keywords,
        "selected_keywords": selected_keywords,
        "related_news": related_news
    }

if __name__ == "__main__":
    # 예시 URL
    url = "https://www.hankyung.com/article/2025040632927"
    
    # 환경 변수에서 API 키 설정
    # os.environ["NAVER_CLIENT_ID"] = "YOUR_CLIENT_ID"
    # os.environ["NAVER_CLIENT_SECRET"] = "YOUR_CLIENT_SECRET"
    
    # 관련 뉴스 검색
    related_news_results = get_related_news(url)
    
    # 결과 출력
    print("원본 기사 내용:")
    print(related_news_results["original_content"][:200] + "...")  # 내용 일부만 출력
    print("\n추출된 키워드:")
    print(related_news_results["all_keywords"])
    print("\n선택된 키워드로 검색한 관련 뉴스:")
    
    for keyword, results in related_news_results["related_news"].items():
        print(f"\n키워드: {keyword}")
        if "items" in results:
            for idx, item in enumerate(results["items"], 1):
                print(f"{idx}. {item['title'].replace('<b>', '').replace('</b>', '')}")
                print(f"   설명: {item['description'].replace('<b>', '').replace('</b>', '')}")
                print(f"   링크: {item['link']}")
                print(f"   날짜: {item['pubDate']}")
                print()
        else:
            print("검색 결과 없음 또는 오류 발생")