"""  
뉴스 기사 질문에 답변하는 에이전트 모듈 (LangGraph 버전)  
"""  
from dotenv import load_dotenv  
from langchain_openai import ChatOpenAI  
from langchain_core.tools import Tool  
from langgraph.prebuilt import create_react_agent  
from langchain_community.tools.tavily_search import TavilySearchResults  
from langgraph.checkpoint.memory import MemorySaver  
from typing import List, Dict, Optional
import asyncio  
from .utils import load_model_config, load_prompt  
  
load_dotenv()  
  
def get_background_info_search(query: str) -> str:  
    """Searches for background information related to a keyword."""  
    search = TavilySearchResults()  
    results = search.run(query)  
    return results  
  
class NewsKnAAgent:  
    def __init__(self):  
        """  
        뉴스 키워드 QnA 에이전트 초기화 (LangGraph 버전)  
        """  
        model_config = load_model_config('news_ka_agent')  
          
        self.llm = ChatOpenAI(**model_config)  
        self.tools = [  
            Tool(  
            name="search_keyword_explanation",
            func=get_background_info_search,  
            description="Useful for finding explanations and definitions of keywords or terms mentioned in news articles",  
            )  
        ]
          
        # LangGraph의 create_react_agent 사용  
        self.graph = create_react_agent(  
            model=self.llm,  
            tools=self.tools,  
            checkpointer=MemorySaver(),  # 상태 지속성  
            debug=True  
        )  
  
    def answer_keyword(self, news_content: str, keyword: str, thread_id: Optional[str] = None):  
        """  
        뉴스 기사에 대한 키워드를 설명합니다.  
        """  
        # YAML 파일에서 프롬프트 템플릿 불러오기
        prompt_template = load_prompt('news_ka_agent_prompt.yaml')
        context_prompt = prompt_template.format(
            news_content=news_content,
            keyword=keyword
        )  
                    
        result = self.graph.invoke(  
            {"messages": [{"role": "user", "content": context_prompt}]},  
            config={"configurable": {"thread_id": thread_id or "default"}}  
        )  
          
        return result["messages"][-1].content  
  
    async def process_keywords_async(self, news_content: str, keywords: List[str]) -> List[Dict[str, str]]:  
        """  
        뉴스 기사의 키워드 대한 설명을 생성합니다. (비동기 병렬 처리)  
        """  
        if not keywords:  
            return []  
          
        async def answer_single_keyword(keyword: str, index: int):  
            try:  
                answer = self.answer_keyword(news_content, keyword, f"thread_{index}")  
                return {keyword: answer}  
            except Exception as e:  
                return {keyword: f"답변 생성 중 오류가 발생했습니다: {str(e)}"}  
          
        tasks = [answer_single_keyword(k, i) for i, k in enumerate(keywords)]  
        results = await asyncio.gather(*tasks)  
          
        return results