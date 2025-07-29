from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, AsyncGenerator, Callable
from isa_model.inference.services.base_service import BaseService
from isa_model.inference.services.llm.llm_adapter import AdapterManager

class BaseLLMService(BaseService):
    """Base class for Large Language Model services with unified invoke interface"""
    
    def __init__(self, provider, model_name: str):
        super().__init__(provider, model_name)
        self._bound_tools: List[Any] = []  # 改为存储原始工具对象
        self._tool_mappings: Dict[str, tuple] = {}  # 工具名到(工具, 适配器)的映射
        
        # 初始化适配器管理器
        self.adapter_manager = AdapterManager()
        
        # Get streaming config from provider config
        self.streaming = self.config.get("streaming", False)
    
    def bind_tools(self, tools: List[Any], **kwargs) -> 'BaseLLMService':
        """
        Bind tools to this LLM service for function calling
        
        Args:
            tools: List of tools to bind (functions, LangChain tools, etc.)
            **kwargs: Additional tool binding parameters
            
        Returns:
            Self for method chaining
        """
        self._bound_tools = tools
        return self
    
    async def _prepare_tools_for_request(self) -> List[Dict[str, Any]]:
        """准备工具用于请求"""
        if not self._bound_tools:
            return []
        
        schemas, self._tool_mappings = await self.adapter_manager.convert_tools_to_schemas(self._bound_tools)
        return schemas
    
    def _prepare_messages(self, input_data: Union[str, List[Dict[str, str]], Any]) -> List[Dict[str, str]]:
        """使用适配器管理器转换消息格式"""
        return self.adapter_manager.convert_messages(input_data)
    
    def _format_response(self, response: str, original_input: Any) -> Union[str, Any]:
        """使用适配器管理器格式化响应"""
        return self.adapter_manager.format_response(response, original_input)
    
    async def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """使用适配器管理器执行工具调用"""
        return await self.adapter_manager.execute_tool(tool_name, arguments, self._tool_mappings)
    
    @abstractmethod
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
        pass
    
    def invoke(self, input_data: Union[str, List[Dict[str, str]], Any]) -> Union[str, Any]:
        """
        Synchronous wrapper for ainvoke
        
        Args:
            input_data: Same as ainvoke
            
        Returns:
            Model response
        """
        import asyncio
        try:
            # Try to get current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.ainvoke(input_data))
                return future.result()
        except RuntimeError:
            # No event loop running, create a new one
            return asyncio.run(self.ainvoke(input_data))
    
    # 保留旧的方法以保持向后兼容
    def _convert_tools_to_schema(self, tools: List[Union[Dict[str, Any], Callable]]) -> List[Dict[str, Any]]:
        """Convert tools to OpenAI function calling schema (deprecated, use adapter manager)"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            schemas, _ = loop.run_until_complete(self.adapter_manager.convert_tools_to_schemas(tools))
            return schemas
        except RuntimeError:
            schemas, _ = asyncio.run(self.adapter_manager.convert_tools_to_schemas(tools))
            return schemas
    
    def _has_bound_tools(self) -> bool:
        """Check if this service has bound tools"""
        return bool(self._bound_tools)
    
    def _get_bound_tools(self) -> List[Dict[str, Any]]:
        """Get the bound tools schema"""
        return self._bound_tools
    
    def _convert_langchain_to_openai(self, messages: List[Any]) -> List[Dict[str, str]]:
        """Convert LangChain message objects to OpenAI format"""
        converted_messages = []
        
        for msg in messages:
            # Handle different LangChain message types
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                # LangChain message object
                msg_dict = {"content": str(msg.content)}
                
                # Map LangChain types to OpenAI roles
                if msg.type == "system":
                    msg_dict["role"] = "system"
                elif msg.type == "human":
                    msg_dict["role"] = "user"
                elif msg.type == "ai":
                    msg_dict["role"] = "assistant"
                    # Handle tool calls if present
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        # Handle tool calls - need to store as separate key since it's not a string
                        tool_calls = [
                            {
                                "id": tc.get("id", f"call_{i}"),
                                "type": "function",
                                "function": {
                                    "name": tc["name"],
                                    "arguments": tc.get("args", {}) if isinstance(tc.get("args"), dict) else tc.get("args", "{}")
                                }
                            } for i, tc in enumerate(msg.tool_calls)
                        ]
                        # Store tool_calls separately to avoid type issues
                        msg_dict["tool_calls"] = tool_calls  # type: ignore
                elif msg.type == "tool":
                    msg_dict["role"] = "tool"
                    if hasattr(msg, 'tool_call_id'):
                        msg_dict["tool_call_id"] = msg.tool_call_id
                elif msg.type == "function":  # Legacy function message
                    msg_dict["role"] = "function"
                    if hasattr(msg, 'name'):
                        msg_dict["name"] = msg.name
                else:
                    msg_dict["role"] = "user"  # Default fallback
                
                converted_messages.append(msg_dict)
                
            elif isinstance(msg, dict):
                # Already in OpenAI format
                converted_messages.append(msg)
            else:
                # Fallback: treat as user message
                converted_messages.append({"role": "user", "content": str(msg)})
        
        return converted_messages
    
    @abstractmethod
    def get_token_usage(self) -> Dict[str, Any]:
        """Get cumulative token usage statistics"""
        pass
    
    @abstractmethod
    def get_last_token_usage(self) -> Dict[str, int]:
        """Get token usage from the last request"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources and close connections"""
        pass
    
    def get_last_usage_with_cost(self) -> Dict[str, Any]:
        """Get last request usage with cost information"""
        usage = self.get_last_token_usage()
        
        # Calculate cost using provider
        if hasattr(self.provider, 'calculate_cost'):
            cost = getattr(self.provider, 'calculate_cost')(
                self.model_name,
                usage["prompt_tokens"],
                usage["completion_tokens"]
            )
        else:
            cost = 0.0
        
        return {
            **usage,
            "cost_usd": cost,
            "model": self.model_name,
            "provider": getattr(self.provider, 'name', 'unknown')
        }
