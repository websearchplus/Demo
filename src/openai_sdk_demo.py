import openai
import httpx
import json
import os
import logging
from dotenv import load_dotenv
from openai.types.chat import (
    ChatCompletionToolParam,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEB_SEARCH_PLUS_ENDPOINT = os.getenv("WEB_SEARCH_PLUS_ENDPOINT", "https://api.websearch.plus/v1/web_search_plus")
WEB_SEARCH_PLUS_API_KEY = os.getenv("WEB_SEARCH_PLUS_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

openai.api_key = OPENAI_API_KEY

# ✅ Define the tool using raw dict (compatible with SDK v1.86+)
tools:list[ChatCompletionToolParam]  = [
    {
        "type": "function",
        "function": {
            "name": "web_search_plus",
            "description": "Perform a real-time web search for the latest information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to retrieve information about."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def fetch_web_search(query: str) -> str:
    """Perform synchronous web search"""
    try:
        logger.info(f"🔍 Performing web search for: {query}")
        headers = {
        "Authorization": f"Bearer {WEB_SEARCH_PLUS_API_KEY}",
        "Content-Type": "application/json"
    }
        
        with httpx.Client(timeout=600) as client:
            resp = client.post(
                WEB_SEARCH_PLUS_ENDPOINT,
                json={"query": query,},
                headers=headers
            )
            resp.raise_for_status()
            resp_json = resp.json()
            if resp_json.get("status","") == "completed":
                return resp_json.get("results","")
            else:
                raise 
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during web search: {e}")
        return f"Web search failed: {str(e)}"
    except json.JSONDecodeError:
        logger.error("Invalid JSON response from web search API")
        return "Web search failed: Invalid response format"
    except Exception as e:
        logger.error(f"Unexpected error during web search: {e}")
        return f"Web search failed: {str(e)}"

def main():
    messages: list[ChatCompletionMessageParam]  = [
        {
            "role": "system",
            "content": ( "You are a smart AI assistant with access to a real-time web search tool named `web_search_plus`. "
            "If the user asks about recent events or requests up-to-date information, always call the `web_search_plus` tool "
            "with the appropriate query to retrieve fresh results from the internet. Do not respond with static or outdated information. "
            "You are connected to the internet via this tool.")
        },
        {
            "role": "user",
            "content": "What were the highlights of the Apple 2025 WWDC? Please search the web for the latest updates."
        }
    ]
    
    try:
        logger.info("🚀 Sending request to OpenAI API")
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return

    choice = response.choices[0]
    
    if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
        for tool_call in choice.message.tool_calls:
            function_name = tool_call.function.name
            try:
                function_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                logger.error("Failed to parse tool call arguments")
                continue
                
            if function_name == "web_search_plus":
                query = function_args.get("query")
                if not query:
                    logger.warning("Missing 'query' parameter in tool call")
                    continue
                    
                logger.info(f"🛠️ Calling tool: {function_name} with query: {query}")
                tool_result = fetch_web_search(query)

                # Append assistant's tool_call message
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            }
                        }
                    ]
                })

                # Append tool's result message
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
        
        try:
            logger.info("🔄 Sending updated messages to OpenAI")
            final_response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            final_message = final_response.choices[0].message.content
            logger.info("🧠 Final model response")
            print("🧠 Final model response:", final_message)
        except openai.APIError as e:
            logger.error(f"OpenAI API error on final request: {e}")
        except Exception as e:
            logger.error(f"Unexpected error on final request: {e}")
    else:
        if choice.message.content:
            logger.info("🎯 Direct model response")
            print("🎯 Direct model response:", choice.message.content)
        else:
            logger.warning("No content in direct response")

if __name__ == "__main__":
    main()
