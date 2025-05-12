from typing import List, Dict, Optional, Annotated, Any
from dataclasses import dataclass, field
from utils import crawl_news, extract_news_content
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
import json

# ------------------------
# Custom Message Type for Entities
# ------------------------
class EntityMessage(BaseMessage):
    """Custom message type to store keyword and description for an entity."""
    keyword: str
    description: str
    # 'type'은 클래스 변수로 메시지 타입을 지정합니다.
    type: str = "entity_message"

    def __init__(self, keyword: str, description: str, **kwargs: Any):
        # keyword와 description으로부터 content 문자열을 생성합니다.
        content_str = json.dumps({"keyword": keyword, "description": description})
        # BaseMessage의 __init__을 호출하면서 content, keyword, description 인자를 전달합니다.
        # Pydantic이 keyword와 description 필드를 초기화할 수 있도록 전달합니다.
        super().__init__(content=content_str, keyword=keyword, description=description, **kwargs)
        # Pydantic이 super().__init__에서 keyword와 description을 이미 설정했으므로,
        # 다음 두 줄은 사실상 중복이지만, 명시적으로 남겨둘 수도 있습니다. (또는 제거 가능)
        # self.keyword = keyword
        # self.description = description

    def __repr__(self) -> str:
        return f"EntityMessage(keyword='{self.keyword}', description='{self.description}')"

# ------------------------
# 상태 정의
# ------------------------

@dataclass
class ArticleState:
    url: str # www.naver.com/news/article/123456
    article_text: str # 뉴스 본문
    main_topic: Optional[str] = None # 기사 주제
    related_articles: Optional[List[Dict]] = None  # [{'url', 'title', 'summary', 'main_topic', 'article_text', 'entities': List[str]}]
    is_duplicate: Optional[bool] = None # 중복 여부
    existing_summaries: Optional[List[Dict]] = None  # [{'url', 'title', 'summary'}]
    entities: Annotated[List[EntityMessage], add_messages] = field(default_factory=list)
    contextual_background: Optional[List[Dict]] = None  # [{'url', 'title', 'summary'}]
    timeline: Optional[List[Dict]] = None  # [{'date': '2024-01', 'event': '...'}]
    summary: Optional[str] = None # -> output
    timeline_summary: Optional[str] = None # -> output

# ------------------------
# 함수 템플릿들
# ------------------------

def extract_article(state: ArticleState) -> Dict[str, Any]:
    """
    기사 URL을 기반으로 뉴스 본문 크롤링 및 텍스트 추출, 주제, 엔티티(키워드) 추출.
    주어진 URL에서 뉴스 본문을 크롤링하고, 광고 및 불필요한 정보를 제거하여
    기사 텍스트를 추출합니다. 추출된 키워드는 EntityMessage 형태로 변환됩니다.

    Args:
        state (ArticleState): 상태 객체, URL 포함
    Returns:
        Dict[str, Any]: 상태 업데이트를 위한 딕셔너리 (main_topic, article_text, entities)
    """

    crawled_news = crawl_news(state.url)
    extracted_data = extract_news_content(crawled_news)

    new_entities = []
    if extracted_data.keywords:
        for kw in extracted_data.keywords:
            new_entities.append(EntityMessage(keyword=kw, description="")) 
    
    return {
        "main_topic": extracted_data.topic,
        "article_text": extracted_data.content,
        "entities": new_entities
    }

def search_related_articles(main_topic: Optional[str], article_text: str, entities: List[str]) -> List[Dict[str, str]]:
    """
    main_topic, article_text, entities(keywords)를 바탕으로 관련 뉴스 기사 리스트(url, title)를 검색합니다.
    실제 구현에서는 검색 API, DB, 또는 RAG 등을 사용할 수 있습니다.
    여기서는 예시로 빈 리스트 반환.
    """
    # TODO: 실제 관련 기사 검색 로직 구현
    print(f"Searching related articles for topic: {main_topic}, entities: {entities}")
    return []  # 예시: [{'url': 'http://example.com/related1', 'title': 'Related Article 1'}]

def retrieve_related(state: ArticleState) -> Dict[str, List[Dict[str, Any]]]:
    """
    URL에서 추출한 정보를 바탕으로 관련 기사 검색하고, 각 관련 기사의 정보도 추출합니다.
    결과는 state.related_articles에 저장될 딕셔너리 형태로 반환합니다.
    """
    related_articles_data = []
    current_keywords = [entity.keyword for entity in state.entities] if state.entities else []
    
    candidate_articles = search_related_articles(state.main_topic, state.article_text, current_keywords)
    
    for article_meta in candidate_articles:
        url = article_meta.get('url')
        if not url:
            continue 
            
        crawled_related_news = crawl_news(url)
        extracted_related_info = extract_news_content(crawled_related_news)
        
        related_articles_data.append({
            'url': url,
            'title': article_meta.get('title', ''), 
            'main_topic': extracted_related_info.topic,
            'article_text': extracted_related_info.content,
            'entities': extracted_related_info.keywords
        })
    return {"related_articles": related_articles_data}

if __name__ == "__main__":

    example_url = "https://www.hankyung.com/article/2025040632927"

    initial_state = ArticleState(url=example_url, article_text="") 

    builder = StateGraph(ArticleState)
    
    builder.add_node("extract_article", extract_article)
    # builder.add_node("retrieve_related_articles", retrieve_related)

    builder.set_entry_point("extract_article")
    # builder.add_edge("extract_article", "retrieve_related_articles")
    builder.add_edge("extract_article", "__end__")

    graph = builder.compile()

    print("Invoking graph...")
    for s in graph.stream(initial_state, {"recursion_limit": 100}):
        node_name = list(s.keys())[0]
        print(f"--- Current State after node: {node_name} ---")
        current_state_as_dict = s[node_name]

        print("URL:", current_state_as_dict.get("url"))
        print("Main Topic:", current_state_as_dict.get("main_topic"))
        
        entities_list = current_state_as_dict.get("entities", [])
        print(f"Entities ({len(entities_list)}):")
        for entity_msg in entities_list: # entity_msg is an EntityMessage object
            print(f"  - Keyword: {entity_msg.keyword}, Description: {entity_msg.description}")
        
        related_articles_list = current_state_as_dict.get("related_articles")
        if related_articles_list:
            print(f"Related Articles ({len(related_articles_list)}):")
            for rel_article in related_articles_list: # rel_article is a dict
                print(f"  - URL: {rel_article.get('url')}, Title: {rel_article.get('title')}, Topic: {rel_article.get('main_topic')}")
        print("-" * 30)

    final_result = graph.invoke(initial_state) # final_result is an ArticleState object
    print("\n=== Final State ===")
    print("Main Topic:", final_result.main_topic)
    print("Entities:")
    for entity_msg in final_result.entities:
        print(f"  - Keyword: {entity_msg.keyword}, Description: {entity_msg.description}")
    if final_result.related_articles:
        print("Related Articles:")
        for rel_article in final_result.related_articles:
            print(f"  - URL: {rel_article.get('url')}, Title: {rel_article.get('title')}, Topic: {rel_article.get('main_topic')}")
            print(f"    Related Entities: {rel_article.get('entities')}")
