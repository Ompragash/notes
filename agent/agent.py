import os
from crewai import Agent, Task, Crew, Process
from utils import get_serper_api_key
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from langchain_anthropic import ChatAnthropic
 
# Set environment variables
anthropic_api_key = "sk-ant-api03-AxEXXXXXXXXXXXXQAA"  # Ensure this is your correct Anthropic API key
serper_api_key = get_serper_api_key()
os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
os.environ["SERPER_API_KEY"] = serper_api_key
 
# Initialize tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
 
# Initialize ChatAnthropic
ClaudeHaiku = ChatAnthropic(
    model="claude-3-haiku-20240307",
    anthropic_api_key=anthropic_api_key  # Explicitly set the Anthropic API key here
)
 
# Define agents
data_analyst_agent = Agent(
    role="Data Analyst",
    goal="Monitor and analyze market data in real-time to identify trends and predict market movements.",
    backstory=(
        "Specializing in financial markets, this agent uses statistical modeling and machine learning to provide crucial insights. "
        "With a knack for data, the Data Analyst Agent is the cornerstone for informing trading decisions."
    ),
    verbose=True,
    allow_delegation=True,
    tools=[scrape_tool, search_tool],
    llm=ClaudeHaiku  # Explicitly use ChatAnthropic
)
 
trading_strategy_agent = Agent(
    role="Trading Strategy Developer",
    goal="Develop and test various trading strategies based on insights from the Data Analyst Agent.",
    backstory=(
        "Equipped with a deep understanding of financial markets and quantitative analysis, this agent devises and refines trading strategies. "
        "It evaluates the performance of different approaches to determine the most profitable and risk-averse options."
    ),
    verbose=True,
    allow_delegation=True,
    tools=[scrape_tool, search_tool],
    llm=ClaudeHaiku  # Explicitly use ChatAnthropic
)
 
execution_agent = Agent(
    role="Trade Advisor",
    goal="Suggest optimal trade execution strategies based on approved trading strategies.",
    backstory=(
        "This agent specializes in analyzing the timing, price, and logistical details of potential trades. By evaluating these factors, "
        "it provides well-founded suggestions for when and how trades should be executed to maximize efficiency and adherence to strategy."
    ),
    verbose=True,
    allow_delegation=True,
    tools=[scrape_tool, search_tool],
    llm=ClaudeHaiku  # Explicitly use ChatAnthropic
)
 
risk_management_agent = Agent(
    role="Risk Advisor",
    goal="Evaluate and provide insights on the risks associated with potential trading activities.",
    backstory=(
        "Armed with a deep understanding of risk assessment models and market dynamics, this agent scrutinizes the potential risks of proposed trades. "
        "It offers a detailed analysis of risk exposure and suggests safeguards to ensure that trading activities align with the firm’s risk tolerance."
    ),
    verbose=True,
    allow_delegation=True,
    tools=[scrape_tool, search_tool],
    llm=ClaudeHaiku  # Explicitly use ChatAnthropic
)
 
# Define tasks
data_analysis_task = Task(
    description="Continuously monitor and analyze market data for the selected stock ({stock_selection}). Use statistical modeling and machine learning to identify trends and predict market movements.",
    expected_output="Insights and alerts about significant market opportunities or threats for {stock_selection}.",
    agent=data_analyst_agent
)
 
strategy_development_task = Task(
    description="Develop and refine trading strategies based on the insights from the Data Analyst and user-defined risk tolerance ({risk_tolerance}). Consider trading preferences ({trading_strategy_preference}).",
    expected_output="A set of potential trading strategies for {stock_selection} that align with the user's risk tolerance.",
    agent=trading_strategy_agent
)
 
execution_planning_task = Task(
    description="Analyze approved trading strategies to determine the best execution methods for {stock_selection}, considering current market conditions and optimal pricing.",
    expected_output="Detailed execution plans suggesting how and when to execute trades for {stock_selection}.",
    agent=execution_agent
)
 
risk_assessment_task = Task(
    description="Evaluate the risks associated with the proposed trading strategies and execution plans for {stock_selection}. Provide a detailed analysis of potential risks and suggest mitigation strategies.",
    expected_output="A comprehensive risk analysis report detailing potential risks and mitigation recommendations for {stock_selection}.",
    agent=risk_management_agent
)
 
# Define the crew with agents and tasks
financial_trading_crew = Crew(
    agents=[
        data_analyst_agent,
        trading_strategy_agent,
        execution_agent,
        risk_management_agent
    ],
    tasks=[
        data_analysis_task,
        strategy_development_task,
        execution_planning_task,
        risk_assessment_task
    ],
    manager_llm=ClaudeHaiku,
    process=Process.hierarchical,
    verbose=True
)
 
# Example data for kicking off the process
financial_trading_inputs = {
    'stock_selection': 'AAPL',
    'initial_capital': '100000',
    'risk_tolerance': 'Medium',
    'trading_strategy_preference': 'Day Trading',
    'news_impact_consideration': True
}
 
# Kickoff the process
result = financial_trading_crew.kickoff(inputs=financial_trading_inputs)
 
# Output the result
print(result)
 
