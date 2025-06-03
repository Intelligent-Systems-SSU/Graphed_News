"""
뉴스 기사 크롤링 및 증강 메인 모듈 - LangGraph 워크플로우 버전
"""
import asyncio
from typing import Dict, Any, List, TypedDict

from langgraph.graph import StateGraph, START, END

from core.news_crawler import crawl_news
from core.news_processor import extract_news_content
from core.news_question_generator import generate_questions
from core.news_qa_agent import NewsQnAAgent
from core.news_ka_agent import NewsKnAAgent
from core.news_accumulator import NewsAccumulator


class NewsAnalysisState(TypedDict):
    """뉴스 처리 워크플로우 상태"""
    url: str
    crawled_content: str
    extracted_content: Dict[str, Any]
    questions: List[str]
    qa_pairs: List[Dict[str, str]]
    ka_pairs: List[Dict[str, str]]
    final_result: str
    

class NewsAnalysisGraph:
    """LangGraph 기반 뉴스 처리 워크플로우"""
    
    def __init__(self):
        """워크플로우 초기화"""
        self.qa_agent = NewsQnAAgent()
        self.ka_agent = NewsKnAAgent()
        self.accumulator = NewsAccumulator()
        self.app = self._build_workflow_graph()
    
    def _crawl_news_node(self, state: NewsAnalysisState):
        """1단계: 뉴스 크롤링 노드"""
        print(f"🕷️ 뉴스 기사 크롤링: {state['url']}")
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            crawled_content = loop.run_until_complete(crawl_news(state["url"]))
        finally:
            loop.close()
        
        return {"crawled_content": crawled_content}
    
    def _extract_content_node(self, state: NewsAnalysisState):
        """2단계: 뉴스 내용 정제 및 키워드 추출 노드"""
        print("📝 뉴스 정제 및 주제, 키워드 추출")
        
        extracted_result = extract_news_content(state["crawled_content"])
        
        extracted_content = {
            "content": extracted_result.content,
            "topic": extracted_result.topic,
            "keywords": extracted_result.keywords
        }
        
        print(f"📌 주제: {extracted_result.topic}")
        print(f"🔍 키워드: {', '.join(extracted_result.keywords)}")
        
        return {"extracted_content": extracted_content}
    
    def _generate_questions_node(self, state: NewsAnalysisState):
        """3단계: 질문 생성 노드"""
        print("❓ 질문 생성")
        
        question_result = generate_questions(state["extracted_content"]["content"])
        questions = question_result.questions if hasattr(question_result, 'questions') else question_result
        
        print(f"📋 생성된 질문 수: {len(questions)}")
        for i, question in enumerate(questions, 1):
            print(f"  {i}. {question}")
        
        return {"questions": questions}
    
    def _answer_questions_node(self, state: NewsAnalysisState):
        """4단계: 질문 답변 노드"""
        print("💬 질문에 대한 답변 생성")
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            qa_pairs = loop.run_until_complete(
                self.qa_agent.process_questions_async(
                    state["extracted_content"]["content"], 
                    state["questions"]
                )
            )
        finally:
            loop.close()
        
        print(f"✅ 답변 완료: {len(qa_pairs)}개 질문")
        
        return {"qa_pairs": qa_pairs}
    
    def _answer_keywords_node(self, state: NewsAnalysisState):
        """4단계: 질문 답변 노드"""
        print("💬 질문에 대한 답변 생성")
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            ka_pairs = loop.run_until_complete(
                self.ka_agent.process_keywords_async(
                    state["extracted_content"]["content"], 
                    state["extracted_content"]["keywords"]
                )
            )
        finally:
            loop.close()
        
        print(f"✅ 답변 완료: {len(ka_pairs)}개 질문")
        
        return {"ka_pairs": ka_pairs}
    
    def _accumulate_results_node(self, state: NewsAnalysisState):
        """5단계: 최종 결과 생성 노드"""
        print("🔄 최종 결과 생성")
        
        final_result = self.accumulator.process(
            state["extracted_content"],
            state["qa_pairs"],
            state["ka_pairs"]
        )
        
        print("✨ 최종 결과 생성 완료")
        
        return {"final_result": final_result}
    
    def _build_workflow_graph(self):
        """워크플로우 그래프 구축"""
        workflow_builder = StateGraph(NewsAnalysisState)
        
        # 노드 추가
        workflow_builder.add_node("crawl_news", self._crawl_news_node)
        workflow_builder.add_node("extract_content", self._extract_content_node)
        workflow_builder.add_node("generate_questions", self._generate_questions_node)
        workflow_builder.add_node("answer_questions", self._answer_questions_node)
        workflow_builder.add_node("answer_keywords", self._answer_keywords_node)
        workflow_builder.add_node("accumulate_results", self._accumulate_results_node)
        
        # 엣지 연결 (순차적 실행)
        workflow_builder.add_edge(START, "crawl_news")
        workflow_builder.add_edge("crawl_news", "extract_content")
        workflow_builder.add_edge("extract_content", "generate_questions")
        workflow_builder.add_edge("extract_content", "answer_keywords")
        workflow_builder.add_edge("generate_questions", "answer_questions")
        workflow_builder.add_edge(["answer_questions", "answer_keywords"], "accumulate_results")  
        workflow_builder.add_edge("accumulate_results", END)
        
        return workflow_builder.compile()


def analyze_articles(url: str):
    """
    뉴스 기사 URL을 처리하여 증강된 결과를 반환합니다.
    
    Args:
        url (str): 처리할 뉴스 기사 URL
        
    Returns:
        Dict[str, Any]: 처리 결과
    """
    workflow = NewsAnalysisGraph()

    print("🚀 뉴스 처리 워크플로우 시작")
    print("=" * 50)

    initial_state = {"url": url}
    final_state = workflow.app.invoke(initial_state)

    print("=" * 50)
    print("🎉 워크플로우 완료")
    
    # 최종 결과 정리
    return {
        "url": url,
        "original_content": final_state["crawled_content"],
        "extracted_content": final_state["extracted_content"],
        "questions": final_state["questions"],
        "qa_pairs": final_state["qa_pairs"],
        "ka_pairs": final_state["ka_pairs"],
        "final_result": final_state["final_result"]
    }


def print_results(results: Dict[str, Any]):
    """결과를 보기 좋게 출력"""
    print("\n" + "=" * 60)
    print("📊 최종 결과")
    print("=" * 60)
    
    print(f"\n🌐 URL: {results['url']}")
    
    print(f"\n📰 주제: {results['extracted_content']['topic']}")
    
    print(f"\n🔍 키워드: {', '.join(results['extracted_content']['keywords'])}")

    print(f"\n📝 원본 기사 내용: {results['original_content'][:300]}..." if len(results['original_content']) > 300 else results['original_content'])

    print(f"\n📝 정제된 기사 내용: {results['extracted_content']['content'][:300]}..." if len(results['extracted_content']['content']) > 300 else results['extracted_content']['content'])

    print("\n" + "=" * 60)
    
    print(f"\n❓ 질문 수: {len(results['questions'])}")
    for i, question in enumerate(results['questions'], 1):
        print(f"  {i}. {question}")
    
    print("\n💬 질의응답:")
    for i, qa_pair in enumerate(results['qa_pairs'], 1):
        question = list(qa_pair.keys())[0]
        answer = list(qa_pair.values())[0]
        print(f"\n  {i}. Q: {question}")
        print(f"     A: {answer}")


    print("\n🔑 키워드 설명:")
    for i, ka_pair in enumerate(results['ka_pairs'], 1):
        keyword = list(ka_pair.keys())[0]
        explanation = list(ka_pair.values())[0]
        print(f"\n  {i}. 키워드: {keyword}")
        print(f"     설명: {explanation}")
        

    print(f"\n📋 최종 보고서:")
    final_report = results['final_result']
    print(f"   {final_report}")


if __name__ == "__main__":
    url = "https://n.news.naver.com/mnews/article/421/0008261200"
    
    try:
        results = analyze_articles(url)
        print_results(results)
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()