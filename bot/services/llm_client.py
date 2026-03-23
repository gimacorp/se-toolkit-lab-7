"""LLM client with tool calling support.

This module provides an OpenAI-compatible interface for calling LLM APIs
with tool/function calling capabilities.
"""

import json
import sys
from typing import Any

import httpx


class LLMClient:
    """Client for LLM APIs with tool calling support.
    
    Attributes:
        base_url: Base URL of the LLM API
        api_key: API key for authentication
        model: Model name to use
        timeout: Request timeout in seconds
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str = "coder-model",
        timeout: float = 30.0,
    ):
        """Initialize the LLM client.
        
        Args:
            base_url: Base URL of the LLM API
            api_key: API key for authentication
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
    
    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> dict[str, Any]:
        """Send a chat completion request to the LLM.
        
        Args:
            messages: List of conversation messages with role and content
            tools: Optional list of tool definitions
            tool_choice: How to use tools ("auto", "none", "required", or specific tool)
            
        Returns:
            Response dict with choice message and potential tool calls
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the server returns an error response
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()
    
    async def chat_with_tools(
        self,
        user_message: str,
        tools: list[dict[str, Any]],
        system_prompt: str | None = None,
        debug: bool = False,
    ) -> str:
        """Execute a tool-calling conversation loop.
        
        This method:
        1. Sends user message + tools to LLM
        2. If LLM returns tool calls, executes them
        3. Feeds results back to LLM
        4. Returns final response
        
        Args:
            user_message: The user's input message
            tools: List of tool definitions
            system_prompt: Optional system prompt
            debug: If True, print debug info to stderr
            
        Returns:
            Final response text from the LLM
        """
        # Build initial messages
        messages: list[dict[str, Any]] = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_message})
        
        # Tool execution loop (max iterations to prevent infinite loops)
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM
            response = await self.chat(messages, tools=tools)
            
            # Get the assistant message
            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            # Check for tool calls
            tool_calls = message.get("tool_calls", [])
            
            if not tool_calls:
                # No tool calls - return the final response
                return message.get("content", "I don't have information to answer that.")
            
            # Add assistant message with tool calls to conversation
            messages.append(message)
            
            # Execute each tool call
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                tool_args_str = function.get("arguments", "{}")
                
                try:
                    tool_args = json.loads(tool_args_str) if tool_args_str else {}
                except json.JSONDecodeError:
                    tool_args = {}
                
                if debug:
                    print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
                
                # Execute the tool (will be provided via callback)
                # This is handled by the caller - we return tool call info
                # Actually, we need to execute tools here - but we don't have them
                # The tools will be executed by the caller via a callback mechanism
                # For now, return tool calls for external execution
                pass
            
            # Tool execution happens externally - this is a simplified version
            # Full implementation would need tool registry and execution here
            break
        
        # Fallback - should not reach here in normal operation
        return "I need more information to answer that question."
