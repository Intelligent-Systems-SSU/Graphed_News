"""
뉴스 기사와 질의응답을 종합하여 최종 결과를 생성하는 모듈
"""
from typing import List, Dict, Any, TypedDict, Annotated
import operator

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.graph import StateGraph, START, END


class FinalKeywords(BaseModel):
    keywords: List[str] = Field(description="List of final keywords crucial for understanding the event.")

class KeywordExplanation(BaseModel):
    keyword: str = Field(description="The keyword being explained.")
    explanation: str = Field(description="Detailed explanation of the keyword in Korean, in the context of the news event.")

class AccumulatorOutput(BaseModel):
    final_keywords_with_explanation: List[KeywordExplanation] = Field(description="List of final keywords with their explanations.")
    final_summary: str = Field(description="Final comprehensive summary of the event in Korean.")


class AccumulatorState(TypedDict):
    extracted_content: str
    answers: List[Dict[str, str]]  # List of {"question": "answer"}
    
    selected_keywords: List[str]
    final_keywords_with_explanation: List[Dict[str, str]]  # List of {"keyword": "explanation"}
    final_summary: str


class NewsAccumulator:
    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        """
        뉴스 Accumulator 초기화
        
        Args:
            model_name (str): 사용할 OpenAI 모델명
            temperature (float): 생성 다양성 조절 값
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.search_tool = TavilySearchResults(max_results=3)
        self.accumulator_app = self._build_accumulator_graph()
    
    def _format_answers(self, answers: List[Dict[str, str]]) -> str:
        """질의응답 목록을 문자열 형태로 변환"""
        return "\n".join([f"Q: {list(item.keys())[0]}\nA: {list(item.values())[0]}" for item in answers])

    def _format_keyword_explanations(self, explanations: List[Dict[str, str]]) -> str:
        """키워드 설명 목록을 문자열 형태로 변환"""
        return "\n".join([f"Keyword: {item['keyword']}\nExplanation: {item['explanation']}" for item in explanations])

    def _select_final_keywords_node(self, state: AccumulatorState):
        """중요 키워드 선택 노드"""
        content = state["extracted_content"]
        answers_str = self._format_answers(state["answers"])
        
        parser = PydanticOutputParser(pydantic_object=FinalKeywords)
        
        prompt = ChatPromptTemplate.from_template(
            """뉴스 기사 내용과 관련 질의응답을 바탕으로, 사건을 포괄적으로 이해하는 데 가장 중요한 최종 키워드 3-5개를 선정해주세요.

    뉴스 내용:
    {extracted_content}

    질의응답:
    {answers}

    {format_instructions}""",
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | parser
        result = chain.invoke({
            "extracted_content": content,
            "answers": answers_str
        })
        
        return {"selected_keywords": result.keywords}

    def _explain_keywords_node(self, state: AccumulatorState):
        """선택된 키워드 설명 노드"""
        keywords = state["selected_keywords"]
        content = state["extracted_content"]
        explanations = []

        explanation_prompt = ChatPromptTemplate.from_template(
            """다음 키워드에 대해 뉴스 내용과 검색된 정보를 바탕으로 한국어로 상세히 설명해주세요. 설명은 뉴스 사건의 맥락에 초점을 맞춰 1-2문단으로 작성해주세요.

    키워드: {keyword}

    뉴스 원문 일부:
    {news_content}

    검색된 정보:
    {search_results}

    설명 (한국어):"""
        )
        explanation_chain = explanation_prompt | self.llm | StrOutputParser()

        for keyword in keywords:
            search_results = self.search_tool.invoke(keyword)
            explanation = explanation_chain.invoke({
                "keyword": keyword,
                "news_content": content,  # Provide a snippet for context
                "search_results": search_results
            })
            explanations.append({"keyword": keyword, "description": explanation})
            
        return {"final_keywords_with_explanation": explanations}

    def _generate_final_summary_node(self, state: AccumulatorState):
        """최종 요약 생성 노드"""
        content = state["extracted_content"]
        answers_str = self._format_answers(state["answers"])
        keyword_explanations_str = self._format_keyword_explanations(state["final_keywords_with_explanation"])
        
        prompt = ChatPromptTemplate.from_template(
            """다음 뉴스 원문, 질의응답, 그리고 주요 키워드 설명을 종합하여 사건 전체를 아우르는 최종 보고서을 한국어로 작성해주세요. 
    이 요약문은 초기 기사 내용을 넘어서, 제공된 모든 정보를 통합하여 사건에 대한 깊이 있는 이해를 제공해야 합니다. 질의응답의 내용을 최대한 포함하여 최종 보고서에 설명해주세요.

    뉴스 원문:
    {extracted_content}

    질의응답:
    {answers}

    주요 키워드 및 설명:
    {keyword_explanations}

    최종 종합 보고서 (한국어):"""
        )
        
        chain = prompt | self.llm | StrOutputParser()
        summary = chain.invoke({
            "extracted_content": content,
            "answers": answers_str,
            "keyword_explanations": keyword_explanations_str
        })
        
        return {"final_summary": summary}

    def _build_accumulator_graph(self):
        """Accumulator 그래프 구축"""
        accumulator_graph_builder = StateGraph(AccumulatorState)

        accumulator_graph_builder.add_node("select_keywords", self._select_final_keywords_node)
        accumulator_graph_builder.add_node("explain_keywords", self._explain_keywords_node)
        accumulator_graph_builder.add_node("generate_summary", self._generate_final_summary_node)

        accumulator_graph_builder.add_edge(START, "select_keywords")
        accumulator_graph_builder.add_edge("select_keywords", "explain_keywords")
        accumulator_graph_builder.add_edge("explain_keywords", "generate_summary")
        accumulator_graph_builder.add_edge("generate_summary", END)

        return accumulator_graph_builder.compile()

    def process(self, news_content: str, answers: List[Dict[str, str]]):
        """
        뉴스 내용과 질의응답을 바탕으로 최종 결과 생성
        
        Args:
            news_content (str): 정제된 뉴스 기사 내용
            answers (List[Dict[str, str]]): 질문과 답변 쌍의 목록
            
        Returns:
            Dict: 최종 키워드, 설명, 요약 정보
        """
        initial_state = {
            "extracted_content": news_content,
            "answers": answers
        }
        
        final_state = self.accumulator_app.invoke(initial_state)

        # 최종 상태에서 필요한 정보 추출하고 형태 변환
        keywords_with_explanation = final_state.get("final_keywords_with_explanation", [])

        return {
            "final_keywords_with_explanation": keywords_with_explanation,
            "final_summary": final_state.get("final_summary", "")
        }
