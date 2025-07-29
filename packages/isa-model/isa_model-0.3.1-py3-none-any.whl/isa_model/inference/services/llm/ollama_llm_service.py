import logging
import httpx
import json
from typing import Dict, Any, List, Union, AsyncGenerator, Optional, Callable
from isa_model.inference.services.llm.base_llm_service import BaseLLMService
from isa_model.inference.providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)

class OllamaLLMService(BaseLLMService):
    """Ollama LLM service with unified invoke interface"""
    
    def __init__(self, provider: 'BaseProvider', model_name: str = "llama3.2:3b-instruct-fp16"):
        super().__init__(provider, model_name)
        
        # Create HTTP client for Ollama API
        base_url = self.config.get("base_url", "http://localhost:11434")
        timeout = self.config.get("timeout", 60)
        
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout
        )
            
        self.last_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "requests_count": 0}
        
        # Tool binding attributes
        self._bound_tools: List[Any] = []
        self._tool_binding_kwargs: Dict[str, Any] = {}
        self._tool_functions: Dict[str, Callable] = {}
        
        logger.info(f"Initialized OllamaLLMService with model {model_name} at {base_url}")
    
    def _ensure_client(self):
        """Ensure the HTTP client is available and not closed"""
        if not hasattr(self, 'client') or not self.client or self.client.is_closed:
            base_url = self.config.get("base_url", "http://localhost:11434")
            timeout = self.config.get("timeout", 60)
            self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
    
    def _create_bound_copy(self) -> 'OllamaLLMService':
        """Create a copy of this service for tool binding"""
        bound_service = OllamaLLMService(self.provider, self.model_name)
        bound_service._bound_tools = self._bound_tools.copy()
        bound_service._tool_binding_kwargs = self._tool_binding_kwargs.copy()
        bound_service._tool_functions = self._tool_functions.copy()
        return bound_service
    
    def bind_tools(self, tools: List[Union[Dict[str, Any], Callable]], **kwargs) -> 'OllamaLLMService':
        """Bind tools to this LLM service for function calling"""
        bound_service = self._create_bound_copy()
        # 使用基类的适配器管理器方法
        bound_service._bound_tools = tools
        bound_service._tool_binding_kwargs = kwargs
        
        return bound_service
    
    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any]) -> Union[str, Any]:
        """
        Universal async invocation method that handles different input types
        
        Args:
            input_data: Can be:
                - str: Simple text prompt
                - list: Message history like [{"role": "user", "content": "hello"}]
                - Any: LangChain message objects or other formats
            
        Returns:
            Model response (string for simple cases, object for complex cases)
        """
        try:
            # Ensure client is available
            self._ensure_client()
            
            # Convert input to messages format
            messages = self._prepare_messages(input_data)
            
            # Prepare request parameters
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": self.streaming,
                "options": {
                    "temperature": self.config.get("temperature", 0.7),
                    "top_p": self.config.get("top_p", 0.9),
                    "num_predict": self.config.get("max_tokens", 2048)
                }
            }
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                payload["tools"] = tool_schemas
            
            # Handle streaming
            if self.streaming:
                return self._stream_response(payload)
            
            # Regular request
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Update token usage if available
            if "eval_count" in result:
                self._update_token_usage(result)
            
            # Handle tool calls if present
            message = result["message"]
            if "tool_calls" in message and message["tool_calls"]:
                return await self._handle_tool_calls(message, messages)
            
            # Return appropriate format based on input type
            return self._format_response(message["content"], input_data)
            
        except httpx.RequestError as e:
            logger.error(f"HTTP request error in ainvoke: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in ainvoke: {e}")
            raise
    
    def _prepare_messages(self, input_data: Union[str, List[Dict[str, str]], Any]) -> List[Dict[str, str]]:
        """Convert various input formats to Ollama messages format (same as OpenAI)"""
        if isinstance(input_data, str):
            # Simple string prompt
            return [{"role": "user", "content": input_data}]
        
        elif isinstance(input_data, list):
            if not input_data:
                raise ValueError("Empty message list provided")
            
            # Check if it's LangChain messages or standard messages
            first_msg = input_data[0]
            if hasattr(first_msg, 'content') and hasattr(first_msg, 'type'):
                # LangChain message objects - use base class method
                return self._convert_langchain_to_openai(input_data)
            elif isinstance(first_msg, dict):
                # Standard message dictionaries
                return input_data
            else:
                # List of strings or other formats
                messages = []
                for i, msg in enumerate(input_data):
                    if isinstance(msg, str):
                        role = "user" if i % 2 == 0 else "assistant"
                        messages.append({"role": role, "content": msg})
                    elif isinstance(msg, dict):
                        messages.append(msg)
                    else:
                        messages.append({"role": "user", "content": str(msg)})
                return messages
        
        else:
            # Handle single LangChain message objects or other objects
            if hasattr(input_data, 'content') and hasattr(input_data, 'type'):
                return self._convert_langchain_to_openai([input_data])
            else:
                return [{"role": "user", "content": str(input_data)}]
    
    def _format_response(self, content: str, original_input: Any) -> Union[str, Any]:
        """Format response based on original input type"""
        # For LangGraph compatibility, return AIMessage object if needed
        if hasattr(original_input, 'type') or (isinstance(original_input, list) and 
                                               original_input and hasattr(original_input[0], 'type')):
            try:
                from langchain_core.messages import AIMessage
                return AIMessage(content=content)
            except ImportError:
                # Fallback to simple object
                class SimpleAIMessage:
                    def __init__(self, content):
                        self.content = content
                        self.type = "ai"
                return SimpleAIMessage(content)
        
        # Default to string
        return content
    
    async def _stream_response(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Handle streaming responses"""
        async def stream_generator():
            try:
                async with self.client.stream("POST", "/api/chat", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                if "message" in chunk and "content" in chunk["message"]:
                                    content = chunk["message"]["content"]
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                raise
        
        return stream_generator()
    
    async def _handle_tool_calls(self, assistant_message: Dict[str, Any], original_messages: List[Dict[str, str]]) -> str:
        """Handle tool calls from the assistant using adapter manager"""
        tool_calls = assistant_message.get("tool_calls", [])
        
        # Add assistant message with tool calls to conversation
        messages = original_messages + [assistant_message]
        
        # Execute each tool call using adapter manager
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            
            try:
                # Parse arguments if they're a string
                arguments = tool_call["function"]["arguments"]
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                
                # Use adapter manager to execute tool
                result = await self._execute_tool_call(function_name, arguments)
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call.get("id", function_name)
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {function_name}: {e}")
                messages.append({
                    "role": "tool",
                    "content": f"Error executing {function_name}: {str(e)}",
                    "tool_call_id": tool_call.get("id", function_name)
                })
        
        # Get final response from the model
        return await self.ainvoke(messages)
    
    def _update_token_usage(self, result: Dict[str, Any]):
        """Update token usage statistics"""
        self.last_token_usage = {
            "prompt_tokens": result.get("prompt_eval_count", 0),
            "completion_tokens": result.get("eval_count", 0),
            "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
        }
        
        # Update total usage
        self.total_token_usage["prompt_tokens"] += self.last_token_usage["prompt_tokens"]
        self.total_token_usage["completion_tokens"] += self.last_token_usage["completion_tokens"]
        self.total_token_usage["total_tokens"] += self.last_token_usage["total_tokens"]
        self.total_token_usage["requests_count"] += 1
    
    def get_token_usage(self) -> Dict[str, Any]:
        """Get total token usage statistics"""
        return self.total_token_usage
    
    def get_last_token_usage(self) -> Dict[str, int]:
        """Get token usage from last request"""
        return self.last_token_usage
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "name": self.model_name,
            "max_tokens": self.config.get("max_tokens", 2048),
            "supports_streaming": True,
            "supports_functions": True,
            "provider": "ollama"
        }
    
    def _has_bound_tools(self) -> bool:
        """Check if this service has bound tools"""
        return bool(self._bound_tools)
    
    def _get_bound_tools(self) -> List[Any]:
        """Get the bound tools schema"""
        return self._bound_tools
        
    async def close(self):
        """Close the HTTP client"""
        if hasattr(self, 'client') and self.client:
            try:
                if not self.client.is_closed:
                    await self.client.aclose()
            except Exception as e:
                logger.warning(f"Error closing Ollama client: {e}") 