from fastapi import FastAPI, HTTPException, Query

import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
import re

# FastAPI 앱 생성 시 한국어 메타데이터 설정
app = FastAPI(
    title="Graphed News API",
    description="뉴스 기사와 관련 정보를 제공하는 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 한국어 OpenAPI 스키마 커스터마이징
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Graphed News API",
        version="1.0.0",
        description="뉴스 기사와 관련 정보를 제공하는 API",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포에서는 특정 도메인으로 제한하는 것이 좋습니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 문서 경로 패턴
docs_url_pattern = re.compile(r'^/docs|^/redoc|^/openapi\.json')

# 미들웨어를 더 정교하게 개선
@app.middleware("http")
async def content_type_middleware(request, call_next):
    path = request.url.path
    response = await call_next(request)
    
    # API 문서 관련 경로는 처리하지 않음
    if docs_url_pattern.match(path) or path.startswith("/static"):
        return response
        
    # 나머지 경로는 JSON으로 처리
    if "Content-Type" not in response.headers or "text/html" not in response.headers["Content-Type"]:
        response.headers["Content-Type"] = "application/json; charset=utf-8"
    
    return response

# 응답 처리를 위한 커스텀 함수
def create_response(data):
    json_compatible_data = jsonable_encoder(data)
    return JSONResponse(
        content=json_compatible_data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# 뉴스 기사 데이터
fake_articles_db = [
    {
        "id": 1,
        "url": "https://example.com/ai-news",
        "title": "AI 기술의 발전",
        "content": "최근 인공지능 기술이 빠르게 발전하고 있습니다.",
        "keywords": "AI,기술,혁신,인공지능",
        "published_date": "2023-10-15",
        "crawled_date": "2023-10-16"
    },
    {
        "id": 2,
        "url": "https://example.com/climate-article",
        "title": "기후 변화의 영향",
        "content": "전 세계적으로 기후 변화가 다양한 환경 문제를 일으키고 있습니다.",
        "keywords": "기후변화,환경,지구온난화",
        "published_date": "2023-10-14",
        "crawled_date": "2023-10-15"
    },
    {
        "id": 3,
        "url": "https://example.com/economy-forecast",
        "title": "경제 전망 분석",
        "content": "올해 4분기 경제 전망에 대한 전문가들의 분석입니다.",
        "keywords": "경제,전망,분석,금융",
        "published_date": "2023-10-13",
        "crawled_date": "2023-10-14"
    }
]

# 용어 설명 데이터
fake_terms_db = [
    {
        "id": 1,
        "article_id": 1,
        "term": "인공지능",
        "explanation": "컴퓨터가 인간의 학습 능력과 추론 능력을 흉내 내는 기술"
    },
    {
        "id": 2,
        "article_id": 1,
        "term": "머신러닝",
        "explanation": "데이터로부터 패턴을 학습하여 예측이나 결정을 내리는 AI의 한 분야"
    },
    {
        "id": 3,
        "article_id": 2,
        "term": "지구온난화",
        "explanation": "대기 중 온실가스 증가로 인해 지구의 평균 기온이 상승하는 현상"
    }
]

# 추가 정보 데이터
fake_background_info_db = [
    {
        "id": 1,
        "article_id": 1,
        "topic": "AI 발전 역사",
        "content": "AI의 역사는 1950년대부터 시작되었으며, 여러 번의 겨울과 봄을 거쳐왔습니다."
    },
    {
        "id": 2,
        "article_id": 2,
        "topic": "파리 기후 협약",
        "content": "2015년 채택된 국제 협약으로, 지구 온도 상승을 제한하기 위한 목표를 설정했습니다."
    }
]

# 타임라인 데이터
fake_timeline_events_db = [
    {
        "id": 1,
        "article_id": 1,
        "event_date": "2012-06-15",
        "description": "구글 딥마인드 설립",
        "importance": 3
    },
    {
        "id": 2,
        "article_id": 1,
        "event_date": "2016-03-15",
        "description": "알파고가 이세돌 9단에게 승리",
        "importance": 5
    },
    {
        "id": 3,
        "article_id": 2,
        "event_date": "2015-12-12",
        "description": "파리 기후 협약 체결",
        "importance": 4
    }
]

# 관련 뉴스 데이터
fake_related_news_db = [
    {
        "id": 1,
        "article_id": 1,
        "keyword": "인공지능",
        "related_title": "ChatGPT, 사용자 1억명 돌파",
        "related_description": "OpenAI의 챗봇 서비스가 출시 2개월 만에 사용자 1억명을 돌파했습니다.",
        "related_url": "https://example.com/chatgpt-users",
        "related_date": "2023-01-30"
    },
    {
        "id": 2,
        "article_id": 2,
        "keyword": "기후변화",
        "related_title": "2023년, 역대 가장 더운 해로 기록될 전망",
        "related_description": "올해는 관측 이래 가장 더운 해가 될 것으로 예상됩니다.",
        "related_url": "https://example.com/hottest-year",
        "related_date": "2023-09-20"
    }
]

@app.get("/")
def read_root():
    return create_response({"message": "Welcome to Graphed News API"})

@app.get("/articles/")
def get_all_articles():
    return create_response(fake_articles_db)

@app.get("/articles/{article_id}")
def get_article(article_id: int):
    for article in fake_articles_db:
        if article["id"] == article_id:
            return create_response(article)
    return create_response({"error": "Article not found"})

@app.get("/articles/{article_id}/terms")
def get_article_terms(article_id: int):
    return create_response([term for term in fake_terms_db if term["article_id"] == article_id])

@app.get("/articles/{article_id}/background")
def get_article_background(article_id: int):
    return create_response([info for info in fake_background_info_db if info["article_id"] == article_id])

@app.get("/articles/{article_id}/timeline")
def get_article_timeline(article_id: int):
    return create_response([event for event in fake_timeline_events_db if event["article_id"] == article_id])

@app.get("/articles/{article_id}/related")
def get_article_related_news(article_id: int):
    return create_response([news for news in fake_related_news_db if news["article_id"] == article_id])

@app.get("/articles/by-url/")
def get_article_by_url(url: str = Query(..., description="기사 URL")):
    """URL을 통해 기사를 찾는 엔드포인트"""
    for article in fake_articles_db:
        if article["url"] == url:
            return create_response(article)
    raise HTTPException(status_code=404, detail="Article not found")

@app.get("/articles/{article_id}/all")
def get_article_with_all_info(article_id: int):
    """기사의 모든 관련 정보를 한 번에 가져오는 엔드포인트"""
    article = None
    for a in fake_articles_db:
        if a["id"] == article_id:
            article = a
            break
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    terms = [term for term in fake_terms_db if term["article_id"] == article_id]
    background = [info for info in fake_background_info_db if info["article_id"] == article_id]
    timeline = [event for event in fake_timeline_events_db if event["article_id"] == article_id]
    related = [news for news in fake_related_news_db if news["article_id"] == article_id]
    
    return create_response({
        "article": article,
        "terms": terms,
        "background_info": background,
        "timeline": timeline,
        "related_news": related
    })

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # 현재 파일 경로와 디렉토리 정보 출력
    print(f"현재 실행 파일: {__file__}")
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    
    # UTF-8 환경 보장
    os.environ["LANG"] = "C.UTF-8"
    os.environ["LC_ALL"] = "C.UTF-8"
    
    # 명시적으로 호스트와 포트를 지정
    host = "0.0.0.0"
    port = 8501
    
    print(f"서버 시작: http://{host}:{port}")
    print(f"API 문서: http://{host}:{port}/docs")
    print(f"ReDoc 문서: http://{host}:{port}/redoc")
    
    # 직접 app 객체 전달 방식으로 변경
    uvicorn.run(
        app,  # 모듈 경로 대신 직접 app 객체 전달
        host=host, 
        port=port, 
        log_level="info"
    )
