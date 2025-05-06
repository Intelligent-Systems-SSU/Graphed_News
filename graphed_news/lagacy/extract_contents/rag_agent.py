import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_community.tools.tavily_search import TavilySearchResults
from extract_essence import process_news_from_url

load_dotenv()

def get_background_info_search(query: str) -> str:
    """Searches for background information related to news article topics."""
    search = TavilySearchResults()
    results = search.run(query)
    return results

class NewsContextAgent:
    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        self.llm = ChatOpenAI(
            temperature=temperature,
            model_name=model_name,
        )
        
        # Define tools for the agent
        self.tools = [
            Tool(
                name="Search Background Information",
                func=get_background_info_search,
                description="Useful for finding background information, context, or explanations for concepts mentioned in the news article",
            )
        ]
        
        # Create the agent
        react_prompt = hub.pull("hwchase17/react")        
        
        self.agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=react_prompt)
        # Add handle_parsing_errors=True to handle LLM output parsing errors
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True,
            handle_parsing_errors=True
        )
    
    def analyze_news_context(self, news_content, keywords):
        """
        Analyze the news article to identify and retrieve necessary background information
        
        Args:
            news_content (str): The extracted news content
            keywords (list): Keywords extracted from the news article
            
        Returns:
            dict: Background information and context to enhance understanding of the article
        """
        context_prompt = """
        You are an expert news researcher helping readers understand complex news articles by providing comprehensive background information. You have been given a news article and important keywords.
        
        News Content:
        {news_content}
        
        Important Keywords:
        {keywords}
        
        Your task is to:
        1. Identify 3-5 specific key concepts, events, people, or terms from the article that would benefit from additional explanation
        2. For EACH identified concept, you MUST use the search tool to find detailed, specific information about it
           - Make separate, targeted search queries for each concept
           - Be specific in your queries (e.g., "Samsung Electronics supply chain disruption 2023" instead of just "Samsung Electronics")
           - You MUST use the search tool for EVERY concept, even if you think you already know about it
           - DO NOT rely on your existing knowledge - all information must come from search results
        3. Provide in-depth background for each concept (at least 2-3 paragraphs per concept)
        4. Focus on facts, data, historical context, and relevant current events
        5. Include dates, statistics, and specific details whenever possible
        
        Your goal is to provide NEW information that would help someone understand the full context behind the news.

        IMPORTANT FORMATTING INSTRUCTIONS:
        You MUST strictly follow the ReAct format of Thought, Action, Observation cycle:
        1. Start with "Thought:" to express your reasoning
        2. Then use "Action:" followed by the tool name and input
        3. Wait for the "Observation:" with the tool result
        4. Repeat the cycle until you have enough information
        5. When ready to give final answer, use "Thought:" followed by "Final Answer:"

        NEVER skip any of these steps or mix the format. Always complete one full cycle before starting another.

        
        For your final answer, format your response with clear headings and sections:
        
        Final Answer:
        ## Key Concepts Requiring Background
        - [List the key concepts you identified]
        
        ## Detailed Background Information
        
        ### [Concept 1]
        [2-3 paragraphs of specific background information, including facts, figures, dates, and historical context]
        
        ### [Concept 2]
        [2-3 paragraphs of specific background information, including facts, figures, dates, and historical context]
        
        [Continue for all identified concepts]
        
        ## How This Context Helps Understand the News
        [Explain how this background information helps the reader better understand the significance and implications of the news article]        
        """
        
        # Using a slightly higher temperature to encourage more exploratory, detailed responses
        original_temp = self.llm.temperature
        self.llm.temperature = 0.2
        
        prompt_template = PromptTemplate(
            template=context_prompt,
            input_variables=["news_content", "keywords"]
        )
        
        formatted_prompt = prompt_template.format_prompt(
            news_content=news_content,
            keywords=", ".join(keywords) if isinstance(keywords, list) else keywords,
        )
        
        result = self.agent_executor.invoke(
            input={"input": formatted_prompt}
        )
        
        # Reset temperature to original value
        self.llm.temperature = original_temp
        
        return result["output"]

def enhance_news_understanding(url):
    """
    Process a news article and enhance it with necessary background context.
    
    Args:
        url (str): URL of the news article
        
    Returns:
        dict: Original news content and enhanced background context
    """
    # Extract the news content using the existing function
    news_result = process_news_from_url(url)
    
    # Create and run the context agent
    agent = NewsContextAgent()
    enhanced_context = agent.analyze_news_context(
        news_result.content, 
        news_result.keywords
    )
    
    # Return both the original content and the enhanced understanding
    return {
        "original_content": news_result.to_dict(),
        "enhanced_context": enhanced_context
    }

if __name__ == "__main__":
    # Example usage
    url = "https://www.hankyung.com/article/2025040632927"
    result = enhance_news_understanding(url)
    
    print("=== 원본 뉴스 내용 ===")
    print(result["original_content"]["content"])
    print("\n=== 핵심 키워드 ===")
    print(result["original_content"]["keywords"])
    print("\n=== 향상된 이해 컨텍스트 ===")
    print(result["enhanced_context"])
