"""  
뉴스 기사와 질의응답을 종합하여 최종 결과를 생성하는 모듈  
"""  
from typing import List, Dict, Any, Optional  
from pydantic import BaseModel, Field  
from langchain_core.prompts import ChatPromptTemplate  
from langchain_openai import ChatOpenAI  
from .utils import load_model_config, load_prompt  

  
class FinalReport(BaseModel):  
    """구조화된 최종 보고서 스키마"""  
    overview: str = Field(description="사건의 개요 및 배경")
    key_points: str = Field(description="주요 포인트들") 
    main_reports: str = Field(description="사실 정리 및 주요 내용 설명")  
    analysis: str = Field(description="분석 및 원인")  
    impact: str = Field(description="영향 및 문제점")  
    resolution_nextsteps: str = Field(description="해결 조치 또는 향후 조치")  
    summary_recommendations: str = Field(description="요약 및 제언")  
    
    qa_insights: str = Field(description="질의응답에서 얻은 통찰")  
  
  
class NewsAccumulator:  
    def __init__(self):  
        """  
        뉴스 Accumulator 초기화  
          
        Args:  
            model_name (str): 사용할 OpenAI 모델명  
            temperature (float): 생성 다양성 조절 값  
        """  
        config = load_model_config('news_accumulator')
        self.llm = ChatOpenAI(**config)  
      
    def _format_qa(self, answers: List[Dict[str, str]]) -> str:  
        """질의응답 목록을 문자열 형태로 변환"""  
        return "\n".join([f"Q: {list(item.keys())[0]}\nA: {list(item.values())[0]}" for item in answers])  
  
    def _generate_structured_report(self, news_content: Dict[str, Any], qa: List[Dict[str, str]], ka: List[Dict[str, str]]) -> FinalReport:  
        """최종 요약 생성"""            
        prompt_template = load_prompt('news_accumulator_prompt.yaml')
        prompt = ChatPromptTemplate.from_template(prompt_template)  
          
        # 구조화된 출력을 위한 LLM 설정
        structured_llm = self.llm.with_structured_output(FinalReport)

        # 실제 입력 데이터 준비
        input_data = {
            "extracted_content": news_content['content'],  
            "qa": self._format_qa(qa),
            "ka": self._format_qa(ka)
        }
        
        """debug용: 프롬프트 포맷팅 확인"""
        # 실제 프롬프트 포맷팅해서 확인
        formatted_messages = prompt.format_messages(**input_data)
        
        print("=" * 80)
        print("🔍 실제 LLM에 전송되는 프롬프트:")
        print("=" * 80)
        for i, message in enumerate(formatted_messages):
            print(f"Message {i+1} ({message.type}):")
            print(f"{message.content}")
            print("-" * 60)
        print("=" * 80)
        """debug용: 프롬프트 포맷팅 확인"""
        
        chain = prompt | structured_llm  
        result = chain.invoke(input_data)  
            
        # 결과가 딕셔너리인 경우 FinalReport로 변환
        if isinstance(result, dict):
            return FinalReport(**result)
        return result
            
    def process(self, news_content: Dict[str, Any], qa: List[Dict[str, str]], ka: List[Dict[str, str]]) -> str:  
        """  
        뉴스 내용과 질의응답을 바탕으로 최종 결과 생성  
          
        Args:  
            news_content (Dict[str, Any]): 정제된 뉴스 기사 내용  
            answers (List[Dict[str, str]]): 질문과 답변 쌍의 목록  
              
        Returns:  
            FinalReport: 구조화된 최종 보고서  
        """  
        report = self._generate_structured_report(news_content, qa, ka)  

        # 최종 보고서를 문자열로 변환하여 반환
        doc = f"""
### {news_content['topic']}

#### 개요 및 배경
{report.overview}

#### 주요 포인트
{report.key_points}

#### 사실 정리 및 주요 내용
{report.main_reports}

#### 분석 및 원인
{report.analysis}

#### 영향 및 문제점
{report.impact}

#### 해결 조치 또는 향후 조치
{report.resolution_nextsteps}

#### 요약 및 제언
{report.summary_recommendations}

#### 질의응답 통찰
{report.qa_insights}
    """

        return doc
  