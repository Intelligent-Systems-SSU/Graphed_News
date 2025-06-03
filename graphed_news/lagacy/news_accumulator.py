"""
뉴스 기사와 질의응답을 종합하여 최종 결과를 생성하는 모듈
"""
from typing import List, Dict, Any, TypedDict, Annotated
import operator

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END

class AccumulatorState(TypedDict):
    extracted_content: str
    answers: List[Dict[str, str]]  # List of {"question": "answer"}
    
    final_summary: str


class NewsAccumulator:
    def __init__(self, model_name="gpt-4.1-mini", temperature=0):
        """
        뉴스 Accumulator 초기화
        
        Args:
            model_name (str): 사용할 OpenAI 모델명
            temperature (float): 생성 다양성 조절 값
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.accumulator_app = self._build_accumulator_graph()
    
    def _format_answers(self, answers: List[Dict[str, str]]) -> str:
        """질의응답 목록을 문자열 형태로 변환"""
        return "\n".join([f"Q: {list(item.keys())[0]}\nA: {list(item.values())[0]}" for item in answers])

    def _generate_final_summary_node(self, state: AccumulatorState):
        """최종 요약 생성 노드"""
        content = state["extracted_content"]
        answers_str = self._format_answers(state["answers"])
        
        prompt = ChatPromptTemplate.from_template(
            """다음 뉴스 원문과 질의응답을 종합하여 사건 전체를 아우르는 최종 보고서를 한국어로 작성해주세요. 
    이 요약문은 초기 기사 내용을 넘어서, 제공된 모든 정보를 통합하여 사건에 대한 깊이 있는 이해를 제공해야 합니다. 질의응답의 내용을 최대한 포함하여 최종 보고서에 설명해주세요.

    뉴스 원문:
    {extracted_content}

    질의응답:
    {answers}

    최종 종합 보고서는 사건 개요로 시작해서 질의응답으로 끝나야 합니다. 

    최종 종합 보고서 (한국어):"""
        )
        
        chain = prompt | self.llm | StrOutputParser()
        summary = chain.invoke({
            "extracted_content": content,
            "answers": answers_str
        })
        
        return {"final_summary": summary}

    def _build_accumulator_graph(self):
        """Accumulator 그래프 구축"""
        accumulator_graph_builder = StateGraph(AccumulatorState)

        accumulator_graph_builder.add_node("generate_summary", self._generate_final_summary_node)

        accumulator_graph_builder.add_edge(START, "generate_summary")
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

        return {
            "final_summary": final_state.get("final_summary", "")
        }
