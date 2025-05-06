from typing import List, Dict, Optional
from dataclasses import dataclass


# ------------------------
# 상태 정의
# ------------------------

@dataclass
class ArticleState:
    url: str # www.naver.com/news/article/123456
    article_text: str # 뉴스 본문
    main_topic: Optional[str] = None # 기사 주제
    is_duplicate: Optional[bool] = None # 중복 여부
    existing_summaries: Optional[List[Dict]] = None  # [{url, title, summary}]
    entities: Optional[Dict[str, List[str]]] = None  # {'person': [...], 'event': [...], ...}
    entity_infos: Optional[Dict[str, str]] = None  # {'이재명': '...', ...} -> output
    contextual_background: Optional[List[Dict]] = None  # [{url, title, summary}]
    timeline: Optional[List[Dict]] = None  # [{'date': '2024-01', 'event': '...'}]
    summary: Optional[str] = None # -> output
    timeline_summary: Optional[str] = None # -> output


# ------------------------
# 함수 템플릿들
# ------------------------

def extract_article(state: ArticleState) -> ArticleState:
    """
    기사 URL을 기반으로 본문만 정제하여 추출

    구현할 기능:
    - 주어진 URL로부터 뉴스 본문 크롤링
    - 광고, 댓글 등 불필요한 정보 제거
    - 기사 텍스트만 추출하여 state.article_text에 저장
    """
    return state


def extract_topic(state: ArticleState) -> ArticleState:
    """
    기사 본문에서 메인 주제 추출

    구현할 기능:
    - 텍스트 요약 또는 키워드 추출 기반 주제 선정
    - state.main_topic에 저장
    """
    return state


def check_duplicate(state: ArticleState) -> str:
    """
    이미 같은 주제가 있는지 중복 확인

    구현할 기능:
    - state.main_topic 임베딩 생성
    - 기존 topic DB 또는 vector DB와 유사도 비교
    - 중복 여부를 state.is_duplicate로 저장하고, 분기 ('Yes' or 'No') 반환
    """
    return 'No'


def fetch_existing_summaries(state: ArticleState) -> ArticleState:
    """
    이미 처리된 같은 주제의 요약 결과들을 가져옵니다.
    
    구현할 기능:
    - vector DB or DB에서 동일 주제의 이전 생성 요약 조회
    - state.existing_summaries에 저장
    """
    return state


def extract_entities(state: ArticleState) -> ArticleState:
    """
    기사에서 주요 인물, 단체, 사건 등 엔티티 추출

    구현할 기능:
    - NER 모델을 이용해 person, org, event 등 분류
    - 결과를 state.entities에 저장 (Dict[str, List[str]])
    """
    return state


def augment_entities(state: ArticleState) -> ArticleState:
    """
    추출된 엔티티별 설명/배경 정보를 외부에서 수집

    구현할 기능:
    - Wikipedia, 뉴스 검색 등을 통해 엔티티별 설명 요약
    - 결과를 state.entity_infos에 저장
    """
    return state


def augment_context(state: ArticleState) -> ArticleState:
    """
    주제 전체에 대한 맥락 보강

    구현할 기능:
    - state.main_topic 및 entity_infos 기반으로 사건 전후 맥락 설명 생성
    - state.contextual_background에 저장
    """
    return state


def generate_summary(state: ArticleState) -> ArticleState:
    """
    기사 요약문 생성

    구현할 기능:
    - 본문 및 보강된 정보 기반 요약문 생성
    - state.summary에 저장
    """
    return state


def update_timeline(state: ArticleState) -> ArticleState:
    """
    기사 및 관련 정보에서 시간 정보를 추출하고 정렬

    구현할 기능:
    - 날짜 정보 파싱 및 사건별 정렬
    - state.timeline에 저장
    """
    return state


def generate_tl_summary(state: ArticleState) -> ArticleState:
    """
    타임라인 기반의 요약문 생성, 또는 Mermaid로 시각화

    구현할 기능:
    - state.timeline을 기반으로 시계열 중심 요약 작성
    - state.timeline_summary에 저장
    """
    return state
