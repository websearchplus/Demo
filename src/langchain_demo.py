import os
from dotenv import load_dotenv
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor, initialize_agent
from langchain.agents import AgentType
from pydantic import SecretStr
import httpx
import logging

# Load .env
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "❌ OPENAI_API_KEY is not set!"
WEB_SEARCH_PLUS_API_KEY = os.getenv("WEB_SEARCH_PLUS_API_KEY")
WEB_SEARCH_PLUS_ENDPOINT = os.getenv("WEB_SEARCH_PLUS_ENDPOINT", "https://api.websearch.plus/v1/web_search_plus")

# Define the web search tool
def web_search_plus(query: str) -> str:
    """Perform a real-time web search using WebSearch Plus API."""
    try:
        logger.info(f"🔍 Web search for: {query}")
        headers = {
            "Authorization": f"Bearer {WEB_SEARCH_PLUS_API_KEY}",
            "Content-Type": "application/json"
        }
        with httpx.Client() as client:
            resp = client.post(
                WEB_SEARCH_PLUS_ENDPOINT,
                json={"query": query},
                headers=headers,
                timeout=1000
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "completed":
                return data.get("results", "No content returned.")
            return f"Search failed: {data.get('status')}"
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Search failed: {str(e)}"

# Wrap tool as LangChain Tool
tools = [
    Tool.from_function(
        name="web_search_plus",
        func=web_search_plus,
        description="Perform a real-time web search. Input is a single query string."
    )
]

# ✅ Build agent with ReAct logic
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=SecretStr(OPENAI_API_KEY))

# ✅ Wrap into executor
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Ask a question
if __name__ == "__main__":
    question = "What were the highlights of Apple 2025 WWDC?"
    logger.info(f"🧠 Asking: {question}")
    answer = agent_executor.invoke({"input": question})
    print("✅ Final Answer:", answer["output"])
