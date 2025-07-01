import asyncio
from datetime import datetime
from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings
import os



async def run(mcp_server: MCPServer):
    now = datetime.now()
    current_date = now.strftime("%Y.%m.%d")
    current_time = now.strftime("%H:%M:%S")
    
    agent = Agent(
        name="Assistant",
        instructions="You are a knowledgeable and helpful assistant.You have access to external tools, but you should only call a tool when the information is time-sensitive, "
                        "real-time, or you are unsure of the answer.For general knowledge, historical facts, or widely known facts, please answer directly without using tools. Avoid guessing," 
                        f"but use your internal knowledge confidently if the answer is clear. current date is {current_date}, current time is {current_time}",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="auto"),
    )

    message = "What were the highlights of Apple 2025 WWDC?"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
     async with MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        params={
            "url": "https://mcp.websearch.plus",
            "headers": {
                "Authorization": f"Bearer {os.getenv('WEB_SEARCH_PLUS_API_KEY')}",
                "Content-Type": "application/json",
            },
        },
        client_session_timeout_seconds=600
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Streamable HTTP Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())