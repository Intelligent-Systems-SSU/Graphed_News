"""
뉴스 기사 질문에 답변하는 에이전트 모듈
"""
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import load_model_config

load_dotenv()

def get_background_info_search(query: str) -> str:
    """Searches for background information related to a question."""
    search = TavilySearchResults()
    results = search.run(query)
    return results

class NewsQnAAgent:
    def __init__(self):
        """
        뉴스 QnA 에이전트 초기화
        
        config에서 모델 설정을 자동으로 불러옵니다.
        """
        # config에서 모델 설정 불러오기
        model_config = load_model_config('news_qa_agent')
        
        self.llm = ChatOpenAI(**model_config)
        self.tools = [
            Tool(
                name="Search Background Information",
                func=get_background_info_search,
                description="Useful for finding background information, context, or explanations for concepts mentioned in the question",
            )
        ]
        react_prompt = hub.pull("hwchase17/react")
        self.agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=react_prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )

    def answer_question(self, news_content, question):
        """
        뉴스 기사에 대한 질문에 답변합니다.
        
        Args:
            news_content (str): 정제된 뉴스 기사 내용
            question (str): 뉴스 기사에서 생성된 질문
            
        Returns:
            str: 상세한 답변 (한국어)
        """
        context_prompt = """
        You are an expert news explainer. Given a news article and a question about it, your job is to answer the question in detail, using the search tool for any facts, background, or context you need.
        
        News Content:
        {news_content}
        
        Question:
        {question}
        
        Your task:
        1. Use the search tool to find relevant, specific information to answer the question.
        2. Make targeted search queries for any concepts, people, events, or terms you need to explain.
        3. For each search, follow the ReAct format: Thought, Action, Observation.
        4. Repeat the cycle as needed until you have enough information.
        5. When ready, give your final answer in Korean, with clear, factual, and detailed explanation (at least 2 paragraphs).
        
        IMPORTANT: Always use the search tool for factual information. Do not rely on your own knowledge.
        
        Final answer must be in Korean.
        """
        prompt_template = PromptTemplate(
            template=context_prompt,
            input_variables=["news_content", "question"]
        )
        formatted_prompt = prompt_template.format_prompt(
            news_content=news_content,
            question=question,
        )
        result = self.agent_executor.invoke(
            input={"input": formatted_prompt}
        )
        return result["output"]

    def process_questions(self, news_content: str, questions: List[str]) -> List[Dict[str, str]]:
        """
        뉴스 기사에 대한 여러 질문에 답변합니다. (병렬 처리)
        
        Args:
            news_content (str): 정제된 뉴스 기사 내용
            questions (List[str]): 질문 목록
            
        Returns:
            List[Dict[str, str]]: 질문과 답변 쌍의 목록 (원래 순서 유지)
        """
        if not questions:
            return []
        
        answers = [{}] * len(questions)  # 원래 순서를 유지하기 위한 리스트
        
        # ThreadPoolExecutor를 사용하여 병렬 처리
        with ThreadPoolExecutor(max_workers=min(len(questions), 5)) as executor:
            # 각 질문을 인덱스와 함께 제출
            future_to_index = {
                executor.submit(self.answer_question, news_content, question): i
                for i, question in enumerate(questions)
            }
            
            # 완료된 작업들을 처리
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                question = questions[index]
                try:
                    answer = future.result()
                    answers[index] = {question: answer}
                except Exception as e:
                    print(f"질문 '{question}'에 대한 답변 생성 중 오류 발생: {str(e)}")
                    answers[index] = {question: f"답변 생성 중 오류가 발생했습니다: {str(e)}"}
        
        return answers
