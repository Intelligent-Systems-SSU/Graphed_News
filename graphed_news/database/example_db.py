import sqlite3
import json
import os
import datetime
from typing import Dict, List, Any, Optional, Tuple
import re

class NewsDatabase:
    def __init__(self, db_path="news_data.db"):
        """
        뉴스 데이터베이스 초기화
        
        Args:
            db_path (str): 데이터베이스 파일 경로
        """
        # 데이터베이스 디렉토리 확인 및 생성
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 반환
        self.cursor = self.conn.cursor()
        
        # 데이터베이스 테이블 생성
        self._create_tables()
    
    def _create_tables(self):
        """데이터베이스 테이블 생성"""
        
        # 뉴스 기사 테이블
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            content TEXT,
            keywords TEXT,
            published_date TEXT,
            crawled_date TEXT
        )
        ''')
        
        # 용어 설명 테이블
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            term TEXT,
            explanation TEXT,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
        ''')
        
        # 추가 정보 테이블
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS background_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            topic TEXT,
            content TEXT,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
        ''')
        
        # 타임라인 데이터 테이블
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            event_date TEXT,
            description TEXT,
            importance INTEGER DEFAULT 1,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
        ''')
        
        # 관련 뉴스 테이블
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS related_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            keyword TEXT,
            related_title TEXT,
            related_description TEXT,
            related_url TEXT,
            related_date TEXT,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
        ''')
        
        self.conn.commit()
    
    def save_article(self, url: str, title: str, content: str, keywords: List[str], 
                    published_date: Optional[str] = None) -> int:
        """
        뉴스 기사 정보를 저장
        
        Args:
            url (str): 뉴스 기사 URL
            title (str): 뉴스 기사 제목
            content (str): 뉴스 기사 내용
            keywords (List[str]): 추출된 키워드 목록
            published_date (str, optional): 발행일 (없으면 현재 날짜 사용)
            
        Returns:
            int: 저장된 기사의 ID
        """
        # 기사가 이미 존재하는지 확인
        self.cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
        result = self.cursor.fetchone()
        
        if result:
            # 기존 기사 업데이트
            article_id = result['id']
            self.cursor.execute('''
            UPDATE articles 
            SET title = ?, content = ?, keywords = ?, published_date = ?, crawled_date = ?
            WHERE id = ?
            ''', (
                title, 
                content, 
                json.dumps(keywords, ensure_ascii=False), 
                published_date or datetime.datetime.now().isoformat(),
                datetime.datetime.now().isoformat(),
                article_id
            ))
        else:
            # 새 기사 삽입
            self.cursor.execute('''
            INSERT INTO articles (url, title, content, keywords, published_date, crawled_date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                url, 
                title, 
                content, 
                json.dumps(keywords, ensure_ascii=False), 
                published_date or datetime.datetime.now().isoformat(),
                datetime.datetime.now().isoformat()
            ))
            article_id = self.cursor.lastrowid
        
        self.conn.commit()
        return article_id
    
    def save_terms(self, article_id: int, terms_data: List[Dict[str, str]]):
        """
        용어 설명 정보 저장
        
        Args:
            article_id (int): 기사 ID
            terms_data (List[Dict]): 용어와 설명 데이터 리스트
                [{"term": "용어1", "explanation": "설명1"}, ...]
        """
        # 해당 기사의 기존 용어 삭제
        self.cursor.execute("DELETE FROM terms WHERE article_id = ?", (article_id,))
        
        # 새 용어 데이터 삽입
        for term_data in terms_data:
            self.cursor.execute('''
            INSERT INTO terms (article_id, term, explanation)
            VALUES (?, ?, ?)
            ''', (article_id, term_data["term"], term_data["explanation"]))
        
        self.conn.commit()
    
    def save_background_info(self, article_id: int, background_data: List[Dict[str, str]]):
        """
        배경 정보 저장
        
        Args:
            article_id (int): 기사 ID
            background_data (List[Dict]): 배경 정보 데이터 리스트
                [{"topic": "주제1", "content": "내용1"}, ...]
        """
        # 해당 기사의 기존 배경 정보 삭제
        self.cursor.execute("DELETE FROM background_info WHERE article_id = ?", (article_id,))
        
        # 새 배경 정보 삽입
        for bg_data in background_data:
            self.cursor.execute('''
            INSERT INTO background_info (article_id, topic, content)
            VALUES (?, ?, ?)
            ''', (article_id, bg_data["topic"], bg_data["content"]))
        
        self.conn.commit()
    
    def save_timeline(self, article_id: int, timeline_data: List[Dict[str, Any]]):
        """
        타임라인 데이터 저장
        
        Args:
            article_id (int): 기사 ID
            timeline_data (List[Dict]): 타임라인 데이터 리스트
                [{"event_date": "2023-01-01", "description": "설명", "importance": 2}, ...]
        """
        # 해당 기사의 기존 타임라인 삭제
        self.cursor.execute("DELETE FROM timeline_events WHERE article_id = ?", (article_id,))
        
        # 새 타임라인 데이터 삽입
        for event in timeline_data:
            importance = event.get("importance", 1)
            self.cursor.execute('''
            INSERT INTO timeline_events (article_id, event_date, description, importance)
            VALUES (?, ?, ?, ?)
            ''', (article_id, event["event_date"], event["description"], importance))
        
        self.conn.commit()
    
    def save_related_news(self, article_id: int, related_news: Dict[str, List[Dict[str, str]]]):
        """
        관련 뉴스 정보 저장
        
        Args:
            article_id (int): 기사 ID
            related_news (Dict): 키워드별 관련 뉴스 정보
                {"키워드1": [{"title": "제목", "description": "설명", "link": "URL", "pubDate": "날짜"}, ...], ...}
        """
        # 해당 기사의 기존 관련 뉴스 삭제
        self.cursor.execute("DELETE FROM related_news WHERE article_id = ?", (article_id,))
        
        # 새 관련 뉴스 데이터 삽입
        for keyword, news_list in related_news.items():
            if "items" in news_list:  # API 응답 구조에 맞게 처리
                for news in news_list["items"]:
                    self.cursor.execute('''
                    INSERT INTO related_news (article_id, keyword, related_title, related_description, 
                                              related_url, related_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        article_id, 
                        keyword, 
                        news["title"].replace('<b>', '').replace('</b>', ''), 
                        news["description"].replace('<b>', '').replace('</b>', ''), 
                        news["link"], 
                        news["pubDate"]
                    ))
        
        self.conn.commit()
    
    def extract_terms_from_enhanced_context(self, enhanced_context: str) -> List[Dict[str, str]]:
        """
        LLM이 생성한 향상된 컨텍스트에서 용어와 설명을 추출합니다.
        
        Args:
            enhanced_context (str): LLM이 생성한 향상된 컨텍스트 텍스트
            
        Returns:
            List[Dict]: 추출된 용어와 설명 목록
        """
        terms_data = []
        
        # 개념 섹션 찾기
        sections = enhanced_context.split("###")
        
        for section in sections[1:]:  # 첫 번째 섹션은 일반적으로 헤더이므로 건너뜀
            lines = section.strip().split("\n")
            if not lines:
                continue
                
            # 첫 번째 줄은 개념 이름
            term = lines[0].strip()
            
            # 나머지 줄은 설명
            explanation = "\n".join(lines[1:]).strip()
            
            if term and explanation:
                terms_data.append({"term": term, "explanation": explanation})
        
        return terms_data
    
    def extract_background_info(self, enhanced_context: str) -> List[Dict[str, str]]:
        """
        LLM이 생성한 향상된 컨텍스트에서 배경 정보를 추출합니다.
        
        Args:
            enhanced_context (str): LLM이 생성한 향상된 컨텍스트 텍스트
            
        Returns:
            List[Dict]: 추출된 배경 정보 목록
        """
        background_data = []
        
        # "Detailed Background Information" 섹션 찾기
        if "## Detailed Background Information" in enhanced_context:
            detailed_section = enhanced_context.split("## Detailed Background Information")[1]
            
            # "How This Context Helps" 섹션 전까지의 내용만 사용
            if "## How This Context Helps" in detailed_section:
                detailed_section = detailed_section.split("## How This Context Helps")[0]
            
            # 각 개념(###로 시작)별로 분리
            concepts = detailed_section.split("###")
            
            for concept in concepts[1:]:  # 첫 번째는 빈 문자열일 수 있으므로 건너뜀
                lines = concept.strip().split("\n")
                if not lines:
                    continue
                
                # 첫 번째 줄은 주제
                topic = lines[0].strip()
                
                # 나머지 줄은 내용
                content = "\n".join(lines[1:]).strip()
                
                if topic and content:
                    background_data.append({"topic": topic, "content": content})
        
        return background_data
    
    def extract_timeline_events(self, content: str, enhanced_context: str = None) -> List[Dict[str, Any]]:
        """
        기사 내용과 향상된 컨텍스트에서 타임라인 이벤트를 추출합니다.
        
        Args:
            content (str): 뉴스 기사 내용
            enhanced_context (str, optional): LLM이 생성한 향상된 컨텍스트
            
        Returns:
            List[Dict]: 추출된 타임라인 이벤트 목록
        """
        timeline_events = []
        
        # 날짜 패턴 (YYYY-MM-DD 또는 YYYY년 MM월 DD일 등)
        date_patterns = [
            r'(\d{4})[년\-\.\/][ ]*(\d{1,2})[월\-\.\/][ ]*(\d{1,2})일?',  # YYYY-MM-DD 또는 YYYY년 MM월 DD일
            r'(\d{4})[년\-\.\/][ ]*(\d{1,2})월?'                           # YYYY-MM 또는 YYYY년 MM월
        ]
        
        # 전체 텍스트 (기사 내용 + 향상된 컨텍스트)
        full_text = content
        if enhanced_context:
            full_text += "\n" + enhanced_context
        
        # 문장 단위로 분리
        sentences = re.split(r'(?<=[.!?])\s+', full_text)
        
        for sentence in sentences:
            # 날짜 탐색
            for pattern in date_patterns:
                matches = re.findall(pattern, sentence)
                for match in matches:
                    if len(match) >= 3:  # YYYY-MM-DD 형식
                        year, month, day = match
                        event_date = f"{year}-{int(month):02d}-{int(day):02d}"
                    elif len(match) >= 2:  # YYYY-MM 형식
                        year, month = match
                        event_date = f"{year}-{int(month):02d}-01"  # 일자는 1일로 기본 설정
                    else:
                        continue
                    
                    # 타임라인 이벤트 추가
                    timeline_events.append({
                        "event_date": event_date,
                        "description": sentence.strip(),
                        "importance": 1  # 기본 중요도
                    })
        
        # 날짜 기준 정렬
        timeline_events.sort(key=lambda x: x["event_date"])
        
        return timeline_events
    
    def store_enhanced_news(self, url: str, title: str, content: str, 
                           keywords: List[str], related_news: Dict, 
                           enhanced_context: str, published_date: str = None):
        """
        뉴스 기사 데이터와 향상된 컨텍스트를 데이터베이스에 저장합니다.
        
        Args:
            url (str): 뉴스 기사 URL
            title (str): 뉴스 기사 제목
            content (str): 뉴스 기사 내용
            keywords (List[str]): 추출된 키워드 목록
            related_news (Dict): 관련 뉴스 정보
            enhanced_context (str): LLM이 생성한 향상된 컨텍스트
            published_date (str, optional): 발행일
        """
        # 1. 기사 정보 저장
        article_id = self.save_article(url, title, content, keywords, published_date)
        
        # 2. 용어 설명 추출 및 저장
        terms_data = self.extract_terms_from_enhanced_context(enhanced_context)
        self.save_terms(article_id, terms_data)
        
        # 3. 배경 정보 추출 및 저장
        background_data = self.extract_background_info(enhanced_context)
        self.save_background_info(article_id, background_data)
        
        # 4. 타임라인 이벤트 추출 및 저장
        timeline_data = self.extract_timeline_events(content, enhanced_context)
        self.save_timeline(article_id, timeline_data)
        
        # 5. 관련 뉴스 저장
        self.save_related_news(article_id, related_news)
    
    def get_article_by_url(self, url: str) -> Dict:
        """URL로 기사 정보 조회"""
        self.cursor.execute("""
        SELECT id, url, title, content, keywords, published_date, crawled_date 
        FROM articles WHERE url = ?
        """, (url,))
        article = self.cursor.fetchone()
        
        if not article:
            return None
        
        article_dict = dict(article)
        article_dict['keywords'] = json.loads(article_dict['keywords'])
        
        return article_dict
    
    def get_article_with_all_data(self, url: str) -> Dict:
        """URL로 기사와 모든 관련 데이터 조회"""
        article = self.get_article_by_url(url)
        
        if not article:
            return None
        
        article_id = article['id']
        
        # 용어 정보 조회
        self.cursor.execute("SELECT term, explanation FROM terms WHERE article_id = ?", (article_id,))
        terms = [dict(row) for row in self.cursor.fetchall()]
        
        # 배경 정보 조회
        self.cursor.execute("SELECT topic, content FROM background_info WHERE article_id = ?", (article_id,))
        background_info = [dict(row) for row in self.cursor.fetchall()]
        
        # 타임라인 정보 조회
        self.cursor.execute("""
        SELECT event_date, description, importance 
        FROM timeline_events 
        WHERE article_id = ? 
        ORDER BY event_date
        """, (article_id,))
        timeline = [dict(row) for row in self.cursor.fetchall()]
        
        # 관련 뉴스 조회
        self.cursor.execute("""
        SELECT keyword, related_title, related_description, related_url, related_date 
        FROM related_news 
        WHERE article_id = ?
        """, (article_id,))
        related_news_rows = self.cursor.fetchall()
        
        # 키워드별로 관련 뉴스 그룹화
        related_news = {}
        for row in related_news_rows:
            keyword = row['keyword']
            if keyword not in related_news:
                related_news[keyword] = []
            
            related_news[keyword].append({
                'title': row['related_title'],
                'description': row['related_description'],
                'url': row['related_url'],
                'date': row['related_date']
            })
        
        # 결과 조합
        return {
            'article': article,
            'terms': terms,
            'background_info': background_info,
            'timeline': timeline,
            'related_news': related_news
        }
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
