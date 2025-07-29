import logging
import os
import json
from typing import Dict, Any, List, Union, AsyncGenerator, Optional, Callable

# 使用官方 OpenAI 库
from openai import AsyncOpenAI

from isa_model.inference.services.llm.base_llm_service import BaseLLMService
from isa_model.inference.providers.base_provider import BaseProvider
from isa_model.inference.billing_tracker import ServiceType

logger = logging.getLogger(__name__)

class OpenAILLMService(BaseLLMService):
    """OpenAI LLM service implementation with unified invoke interface"""
    
    def __init__(self, provider: 'BaseProvider', model_name: str = "gpt-4.1-nano"):
        super().__init__(provider, model_name)
        
        # Get full configuration from provider (including sensitive data)
        provider_config = provider.get_full_config()
        
        # Initialize AsyncOpenAI client with provider configuration
        try:
            if not provider_config.get("api_key"):
                raise ValueError("OpenAI API key not found in provider configuration")
            
            self.client = AsyncOpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config.get("base_url", "https://api.openai.com/v1"),
                organization=provider_config.get("organization")
            )
            
            logger.info(f"Initialized OpenAILLMService with model {self.model_name} and endpoint {self.client.base_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize OpenAI client. Check your API key configuration: {e}") from e
            
        self.last_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        self.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "requests_count": 0}
        
        # Tool binding attributes
        self._bound_tools: List[Dict[str, Any]] = []
        self._tool_binding_kwargs: Dict[str, Any] = {}
        self._tool_functions: Dict[str, Callable] = {}
    
    def _create_bound_copy(self) -> 'OpenAILLMService':
        """Create a copy of this service for tool binding"""
        bound_service = OpenAILLMService(self.provider, self.model_name)
        bound_service._bound_tools = self._bound_tools.copy()
        bound_service._tool_binding_kwargs = self._tool_binding_kwargs.copy()
        bound_service._tool_functions = self._tool_functions.copy()
        return bound_service
    
    def bind_tools(self, tools: List[Any], **kwargs) -> 'OpenAILLMService':
        """
        Bind tools to this LLM service for function calling
        
        Args:
            tools: List of tools (functions, dicts, or LangChain tools)
            **kwargs: Additional arguments for tool binding
            
        Returns:
            New LLM service instance with tools bound
        """
        # Create a copy of this service
        bound_service = self._create_bound_copy()
        
        # Use the adapter manager to handle tools
        bound_service._bound_tools = tools
        
        return bound_service
    
    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any]) -> Union[str, Any]:
        """Unified invoke method for all input types"""
        try:
            # Use adapter manager to prepare messages
            messages = self._prepare_messages(input_data)
            
            # Prepare request kwargs
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.config.get("temperature", 0.7),
                "max_tokens": self.config.get("max_tokens", 1024)
            }
            
            # Add tools if bound using adapter manager
            tool_schemas = await self._prepare_tools_for_request()
            if tool_schemas:
                kwargs["tools"] = tool_schemas
                kwargs["tool_choice"] = "auto"
            
            # Handle streaming vs non-streaming
            if self.streaming:
                # Streaming mode - collect all chunks
                content_chunks = []
                async for chunk in await self._stream_response(kwargs):
                    content_chunks.append(chunk)
                content = "".join(content_chunks)
                
                # Create a mock usage object for tracking
                class MockUsage:
                    def __init__(self):
                        self.prompt_tokens = len(str(messages)) // 4  # Rough estimate
                        self.completion_tokens = len(content) // 4   # Rough estimate  
                        self.total_tokens = self.prompt_tokens + self.completion_tokens
                
                usage = MockUsage()
                self._update_token_usage(usage)
                self._track_billing(usage)
                
                return self._format_response(content, input_data)
            else:
                # Non-streaming mode
                response = await self.client.chat.completions.create(**kwargs)
                message = response.choices[0].message
                
                # Update usage tracking
                if response.usage:
                    self._update_token_usage(response.usage)
                    self._track_billing(response.usage)
                
                # Handle tool calls if present
                if message.tool_calls:
                    final_content = await self._handle_tool_calls(message, messages)
                    return self._format_response(final_content, input_data)
                
                # Return appropriate format based on input type
                return self._format_response(message.content or "", input_data)
            
        except Exception as e:
            logger.error(f"Error in ainvoke: {e}")
            raise
    
    def _prepare_messages(self, input_data: Union[str, List[Dict[str, str]], Any]) -> List[Dict[str, str]]:
        """使用适配器管理器转换消息格式（覆盖基类方法以保持兼容性）"""
        return self.adapter_manager.convert_messages(input_data)
    
    def _format_response(self, content: str, original_input: Any) -> Union[str, Any]:
        """使用适配器管理器格式化响应（覆盖基类方法以保持兼容性）"""
        return self.adapter_manager.format_response(content, original_input)
    
    async def _stream_response(self, kwargs: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Handle streaming responses"""
        kwargs["stream"] = True
        
        async def stream_generator():
            try:
                stream = await self.client.chat.completions.create(**kwargs)
                async for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                raise
        
        return stream_generator()
    
    async def _handle_tool_calls(self, assistant_message, original_messages: List[Dict[str, str]]) -> str:
        """Handle tool calls from the assistant using adapter manager"""
        # Add assistant message with tool calls to conversation
        messages = original_messages + [{
            "role": "assistant", 
            "content": assistant_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in assistant_message.tool_calls
            ]
        }]
        
        # Execute each tool call using adapter manager
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            try:
                # Use adapter manager to execute tool
                result = await self._execute_tool_call(function_name, arguments)
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call.id
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {function_name}: {e}")
                messages.append({
                    "role": "tool",
                    "content": f"Error executing {function_name}: {str(e)}",
                    "tool_call_id": tool_call.id
                })
        
        # Get final response from the model
        try:
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.config.get("temperature", 0.7),
                "max_tokens": self.config.get("max_tokens", 1024)
            }
            
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
            
        except Exception as e:
            logger.error(f"Error getting final response after tool calls: {e}")
            raise
    
    def _update_token_usage(self, usage):
        """Update token usage statistics"""
        self.last_token_usage = {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }
        
        # Update total usage
        self.total_token_usage["prompt_tokens"] += self.last_token_usage["prompt_tokens"]
        self.total_token_usage["completion_tokens"] += self.last_token_usage["completion_tokens"]
        self.total_token_usage["total_tokens"] += self.last_token_usage["total_tokens"]
        self.total_token_usage["requests_count"] += 1
    
    def _track_billing(self, usage):
        """Track billing information"""
        self._track_usage(
            service_type=ServiceType.LLM,
            operation="chat",
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            metadata={
                "temperature": self.config.get("temperature", 0.7), 
                "max_tokens": self.config.get("max_tokens", 1024)
            }
        )
    
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
            "max_tokens": self.config.get("max_tokens", 1024),
            "supports_streaming": True,
            "supports_functions": True,
            "provider": "openai"
        }
    
    def _has_bound_tools(self) -> bool:
        """Check if this service has bound tools"""
        return bool(self._bound_tools)
    
    def _get_bound_tools(self) -> List[Dict[str, Any]]:
        """Get the bound tools schema"""
        return self._bound_tools
        
    async def close(self):
        """Close the backend client"""
        await self.client.close()