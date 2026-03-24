"""Intent router using LLM tool calling.

This module handles natural language queries by:
1. Sending the user's message + tool definitions to the LLM
2. Executing tool calls returned by the LLM
3. Feeding results back to the LLM
4. Returning the final response
"""

import json
import sys
from typing import Any, Callable

from config import load_config
from services.lms_client import LMSClient
from services.llm_client import LLMClient


# Tool definitions for the LLM
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all available labs and their tasks. Use this when user asks about available labs, what labs exist, or wants to see the catalog.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of all enrolled learners with their group information. Use this when user asks about students, enrollment, or how many people are in the course.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average pass rates and attempt counts for a specific lab. Use this when user asks about scores, pass rates, difficulty, or performance for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. Must be a valid lab ID.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab. Use this when user asks about score distribution, grade breakdown, or how scores are spread.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a specific lab. Use this when user asks about submission patterns, when people submitted, or activity over time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance and student counts for a specific lab. Use this when user asks about group comparison, which group is best, or group performance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab. Use this when user asks about best students, leaderboard, top performers, or who did best.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return (default: 5).",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a specific lab. Use this when user asks about completion rate, how many finished, or what percentage completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL pipeline sync to refresh data from autochecker. Use this when user asks to update data, refresh scores, or sync the pipeline.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for an LMS (Learning Management System). 
You have access to backend API tools that provide real data about labs, students, scores, and analytics.

When the user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. If one tool call is not enough, make additional tool calls
4. Once you have all the data, summarize it clearly for the user

Be specific and include numbers from the data. If you find interesting patterns (like a lab with very low pass rates), point them out.

If the user's message is a greeting or casual message, respond naturally without using tools.
If the user's message is unclear or ambiguous, ask for clarification about what they want to know.

Always be helpful and friendly. Use the actual data from tool results to provide accurate answers."""


def get_tool_executor(lms_client: LMSClient) -> Callable[[str, dict[str, Any]], Any]:
    """Create a tool executor function for the given LMS client.
    
    Args:
        lms_client: The LMS client to use for API calls
        
    Returns:
        A function that takes (tool_name, args) and returns the result
    """
    async def execute_tool(tool_name: str, args: dict[str, Any]) -> Any:
        """Execute a tool by name with the given arguments."""
        if tool_name == "get_items":
            return await lms_client.get_items()
        elif tool_name == "get_learners":
            return await lms_client.get_learners()
        elif tool_name == "get_pass_rates":
            return await lms_client.get_pass_rates(args.get("lab", ""))
        elif tool_name == "get_scores":
            return await lms_client.get_scores(args.get("lab", ""))
        elif tool_name == "get_timeline":
            return await lms_client.get_timeline(args.get("lab", ""))
        elif tool_name == "get_groups":
            return await lms_client.get_groups(args.get("lab", ""))
        elif tool_name == "get_top_learners":
            return await lms_client.get_top_learners(
                args.get("lab", ""), args.get("limit", 5)
            )
        elif tool_name == "get_completion_rate":
            return await lms_client.get_completion_rate(args.get("lab", ""))
        elif tool_name == "trigger_sync":
            return await lms_client.trigger_sync()
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    return execute_tool


async def route_natural_language(
    user_message: str,
    debug: bool = False,
) -> str:
    """Route a natural language query through the LLM to get a response.
    
    Args:
        user_message: The user's input message
        debug: If True, print debug info to stderr
        
    Returns:
        The final response text
    """
    config = load_config()
    
    # Check if LLM is configured
    if not config.llm_api_base_url or not config.llm_api_key:
        return "LLM is not configured. Please set LLM_API_BASE_URL and LLM_API_KEY in .env.bot.secret."
    
    # Create clients
    lms_client = LMSClient(
        base_url=config.lms_api_base_url,
        api_key=config.lms_api_key,
    )
    llm_client = LLMClient(
        base_url=config.llm_api_base_url,
        api_key=config.llm_api_key,
        model=config.llm_api_model,
    )
    
    # Build initial messages
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    
    # Tool execution loop
    max_iterations = 5
    iteration = 0
    
    tool_executor = get_tool_executor(lms_client)
    
    while iteration < max_iterations:
        iteration += 1
        
        try:
            # Call LLM with tools
            response = await llm_client.chat(messages, tools=TOOL_DEFINITIONS)
        except Exception as e:
            if debug:
                print(f"[llm_error] {type(e).__name__}: {e}", file=sys.stderr)
            return f"LLM error: {type(e).__name__}. Please try again later."
        
        # Get the assistant message
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        
        # If no tool calls, return the response
        if not tool_calls:
            return content or "I don't have enough information to answer that."
        
        # Add assistant message to conversation
        messages.append(message)
        
        # Execute each tool call
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name", "")
            tool_args_str = function.get("arguments", "{}")
            tool_call_id = tool_call.get("id", "")
            
            try:
                tool_args = json.loads(tool_args_str) if tool_args_str else {}
            except json.JSONDecodeError:
                tool_args = {}
            
            if debug:
                print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
            
            # Execute the tool
            try:
                result = await tool_executor(tool_name, tool_args)
                result_str = json.dumps(result, default=str)
                if debug:
                    print(f"[tool] Result: {result_str[:200]}...", file=sys.stderr)
            except Exception as e:
                result_str = json.dumps({"error": str(e)})
                if debug:
                    print(f"[tool] Error: {e}", file=sys.stderr)
            
            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result_str,
            })
        
        if debug:
            print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)
    
    # If we exit the loop without a response, something went wrong
    return "I had trouble processing your request. Please try rephrasing your question."
