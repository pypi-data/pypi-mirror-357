"""
OOP LLM tracer implementation.
"""

import json
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from ..base.tracer import BaseTracer
from ..config.context_util import generation_id_context, request_context
from ..config.langfuse_service import _LangfuseService
from ..utils.token_costs import get_token_costs
from ..utils.tool_call_parser import get_anthropic_response_summary
from ..utils.tracer_utils import (
    convert_anthropic_messages_to_langfuse_format,
    convert_groq_messages_to_langfuse_format,
    extract_tool_names_from_tools,
    get_tool_call_summary_from_messages,
)


class LLMTracer(BaseTracer):
    """OOP implementation of LLM tracing."""

    def __init__(
        self,
        provider,
        variable_mapping: Optional[Dict[str, str]] = None,
        metadata_config: Optional[List[str]] = None,
    ):
        super().__init__(provider, variable_mapping, metadata_config)

    async def trace(self, func: Callable, *args, **kwargs) -> Any:
        """Execute LLM tracing for the function call."""
        if not self.should_trace():
            return await func(*args, **kwargs)

        trace_id = request_context.get()
        start_time = datetime.now()

        result = None
        try:
            result = await func(*args, **kwargs)
            end_time = datetime.now()

            # Handle different result formats
            if isinstance(result, tuple):
                response_data = result[0] if len(result) > 0 else None
                raw_response = result[1] if len(result) > 1 else None
                llm_response = (
                    self.provider.extract_response(raw_response)
                    if raw_response
                    else response_data
                )
                tokens_data = (
                    self.provider.parse_tokens(raw_response)
                    if raw_response
                    else {}
                )
                completion_start_time = (
                    self.provider.get_completion_start_time(raw_response)
                    if raw_response
                    else None
                )
            else:
                raw_response = result
                llm_response = self.provider.extract_response(raw_response)
                tokens_data = self.provider.parse_tokens(raw_response)
                completion_start_time = self.provider.get_completion_start_time(
                    raw_response
                )

            # Get mapped parameter values
            model_name = self.get_mapped_param_value(
                kwargs, "model_name"
            ) or self.get_mapped_param_value(kwargs, "model")
            system_prompt = self.get_mapped_param_value(kwargs, "system_prompt")
            user_prompt = self.get_mapped_param_value(
                kwargs, "chat_messages"
            ) or self.get_mapped_param_value(kwargs, "user_prompt")
            operation_name = self.get_mapped_param_value(
                kwargs, "operation_name"
            )
            max_tokens = self.get_mapped_param_value(kwargs, "max_tokens")
            temperature = self.get_mapped_param_value(kwargs, "temperature")
            tools = self.get_mapped_param_value(kwargs, "tools")
            if tools:
                tool_names = extract_tool_names_from_tools(tools)
            else:
                tool_names = []

            # Calculate cost
            cost_details = {}
            if tokens_data and model_name:
                try:
                    cost_details = self.provider.calculate_cost(
                        tokens_data, model_name
                    )
                except ValueError as e:
                    raise e

            # Extract tool call information for Anthropic provider
            tool_call_metadata = {}
            if self.provider.name == "anthropic" and raw_response:
                response_summary = get_anthropic_response_summary(raw_response)
                tool_call_metadata = {
                    "hasToolCalls": response_summary["has_tool_calls"],
                    "toolCallCount": response_summary["tool_call_count"],
                    "hasToolResults": response_summary["has_tool_results"],
                    "toolResultCount": response_summary["tool_result_count"],
                }
            input_messages = []
            input_messages.append({"role": "system", "content": system_prompt})
            # Convert Anthropic messages to Langfuse format
            if self.provider.name == "anthropic":
                input_messages += convert_anthropic_messages_to_langfuse_format(
                    user_prompt
                )
            elif self.provider.name == "groq":
                input_messages += convert_groq_messages_to_langfuse_format(
                    user_prompt
                )
            else:
                input_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]

            generation_data = {
                "model_name": model_name,
                "service_provider": self.provider.name,
                "input": input_messages,
                "output": llm_response,
                "usage": tokens_data,
                "cost_details": cost_details,
                "start_time": start_time,
                "end_time": end_time,
                "tool_call_metadata": tool_call_metadata,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "tool_names": tool_names,
            }

            # Build complete metadata
            complete_metadata = {
                "model": model_name,
                "provider": self.provider.name,
                "maxTokens": max_tokens,
                "temperature": temperature,
                "tool": tool_names,
                "timeTaken": (end_time - start_time).total_seconds(),
                "inputTokens": tokens_data.get("prompt_tokens", 0),
                "outputTokens": tokens_data.get("completion_tokens", 0),
                "inputCost": cost_details.get("input", 0.0),
                "outputCost": cost_details.get("output", 0.0),
                "totalCost": cost_details.get("total", 0.0),
                **tool_call_metadata,
            }

            # Filter metadata if metadata_config is provided
            filtered_metadata = self.filter_metadata(complete_metadata)

            generation_id = await _LangfuseService.create_generation_for_LLM(
                trace_id,
                generation_data,
                (
                    operation_name.replace("_", " ").title()
                    if operation_name
                    else f"{self.provider.name.capitalize()} Generation"
                ),
                filtered_metadata,
            )

            generation_id_context.set(generation_id)
            return result

        except Exception as e:
            print(f"[LLM Observability] Error in LLM Tracer: {e}")
            print(f"[LLM Observability] Stack trace:\n{traceback.format_exc()}")
            return result


class _SimpleSDKStreamWrapper:
    """Simple wrapper for Anthropic SDK stream that creates trace after completion."""
    
    def __init__(self, func, args, kwargs, tracer, model_name, system_prompt, 
                 user_prompt, operation_name, max_tokens, temperature, tool_names, input_tool_summary):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.tracer = tracer
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.operation_name = operation_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.tool_names = tool_names
        self.input_tool_summary = input_tool_summary
        self.stream_manager = None
        self.inner_stream = None
        self.start_time = datetime.now()

    async def __aenter__(self):
        """Enter the stream context manager."""
        self.stream_manager = await self.func(*self.args, **self.kwargs)
        self.inner_stream = await self.stream_manager.__aenter__()
        return self.inner_stream

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the stream and create trace using get_final_message()."""
        try:
            # Let the original stream exit first
            result = await self.stream_manager.__aexit__(exc_type, exc_val, exc_tb)
            
            # Create trace using the SDK's built-in methods
            await self._create_trace_from_final_message()
            
            return result
        except Exception as e:
            print(f"Error in SDK stream tracing: {e}")
            return await self.stream_manager.__aexit__(exc_type, exc_val, exc_tb)

    async def _create_trace_from_final_message(self):
        """Create trace using stream.get_final_message() - much simpler!"""
        try:
            trace_id = request_context.get()
            end_time = datetime.now()
            
            # Use Anthropic SDK's built-in method to get all the data we need
            # get_final_message() is called on the inner stream object, not the manager
            final_message = await self.inner_stream.get_final_message()
            
            # Extract data from the final message (Message object from Anthropic SDK)
            collected_response = ""
            collected_tool_calls = []
            
            # Handle content blocks (list of ContentBlock objects)
            for content_block in final_message.content:
                if hasattr(content_block, 'type'):
                    if content_block.type == "text":
                        # TextBlock object
                        collected_response += getattr(content_block, 'text', '')
                    elif content_block.type == "tool_use":
                        # ToolUseBlock object
                        tool_call = {
                            "id": getattr(content_block, 'id', ''),
                            "name": getattr(content_block, 'name', ''),
                            "input": getattr(content_block, 'input', {}),
                            "type": "tool_use",
                        }
                        collected_tool_calls.append(tool_call)

            # Get token usage from final message (Usage object)
            usage = getattr(final_message, 'usage', None)
            if usage:
                input_tokens = getattr(usage, 'input_tokens', 0)
                output_tokens = getattr(usage, 'output_tokens', 0)
            else:
                input_tokens = 0
                output_tokens = 0
            
            tokens_data = {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }

            # Calculate cost
            cost_details = {}
            if tokens_data and self.model_name:
                try:
                    # Try to use provider's calculate_cost method if available
                    if hasattr(self.tracer.provider, 'calculate_cost'):
                        cost_details = self.tracer.provider.calculate_cost(
                            tokens_data, self.model_name
                        )
                    else:
                        # Fallback: Use token_costs utility directly
                        if isinstance(self.tracer.provider, dict):
                            provider_name = self.tracer.provider.get('name', 'anthropic')
                        else:
                            provider_name = getattr(self.tracer.provider, 'name', 'anthropic')
                        model_pricing = get_token_costs(self.model_name, provider_name)
                        prompt_tokens = tokens_data.get("prompt_tokens", 0)
                        completion_tokens = tokens_data.get("completion_tokens", 0)
                        
                        input_price = prompt_tokens * model_pricing["input_cost_per_token"]
                        output_price = completion_tokens * model_pricing["output_cost_per_token"]
                        total_price = input_price + output_price
                        
                        cost_details = {
                            "input": input_price,
                            "output": output_price,
                            "total": total_price,
                        }
                except (ValueError, AttributeError):
                    # If cost calculation fails, provide empty cost details
                    cost_details = {"input": 0.0, "output": 0.0, "total": 0.0}

            # Create tool call metadata
            tool_call_metadata = {
                "currentStreamHasToolCalls": len(collected_tool_calls) > 0,
                "currentStreamToolCallCount": len(collected_tool_calls),
                "currentStreamToolCalls": collected_tool_calls,
                "inputContextHasToolCalls": self.input_tool_summary.get("has_tool_calls", False),
                "inputContextToolCallCount": self.input_tool_summary.get("tool_call_count", 0),
                "inputContextHasToolResults": self.input_tool_summary.get("has_tool_results", False),
                "inputContextToolResultCount": self.input_tool_summary.get("tool_result_count", 0),
                "hasToolCalls": len(collected_tool_calls) > 0,
                "toolCallCount": len(collected_tool_calls),
                "hasToolResults": self.input_tool_summary.get("has_tool_results", False),
                "toolResultCount": self.input_tool_summary.get("tool_result_count", 0),
                "toolCalls": collected_tool_calls,
                "toolResults": self.input_tool_summary.get("tool_results", []),
                "sdkStreamMode": True,
                "isAnthropicSDKStream": True,
                "finalMessageId": getattr(final_message, 'id', ''),
                "stopReason": getattr(final_message, 'stop_reason', ''),
            }

            await self.tracer._create_generation(
                trace_id,
                self.model_name,
                self.system_prompt,
                self.user_prompt,
                self.operation_name,
                self.max_tokens,
                self.temperature,
                self.tool_names,
                self.input_tool_summary,
                collected_response,
                tokens_data,
                cost_details,
                tool_call_metadata,
                self.start_time,
                end_time,
            )

        except Exception as e:
            print(f"Error creating trace from final message: {e}")


class LLMStreamingTracer(BaseTracer):
    """
    OOP implementation of LLM streaming tracing with CLEAN SEPARATION logic.

    LOGIC:
    ==========
    - This tracer is used ONLY on the pure LLM streaming service
    - Each call to the service creates ONE focused trace
    - Tool execution happens OUTSIDE the trace (in orchestrator)
    - Each trace focuses purely on LLM interaction
    - Multiple traces for multi-step conversations
    - Supports both streaming and SDK modes based on is_sdk parameter
    """

    def __init__(
        self,
        provider,
        variable_mapping: Optional[Dict[str, str]] = None,
        metadata_config: Optional[List[str]] = None,
        is_sdk: bool = False,
    ):
        super().__init__(provider, variable_mapping, metadata_config)
        self.is_sdk = is_sdk
        
        # Handle both object providers and dict providers
        provider_name = getattr(provider, 'name', provider.get('name', str(provider)) if isinstance(provider, dict) else str(provider))
        if provider_name != "anthropic":
            raise ValueError(
                "Streaming tracing currently only supports Anthropic provider"
            )

    def trace(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute streaming LLM tracing for PURE LLM service calls.

        APPROACH:
        - Each call creates ONE focused trace
        - Only tracks LLM input/output for THIS call
        - Tool calls are noted but not executed here
        - Tool results from previous calls are in input for context
        - Supports both streaming mode (is_sdk=False) and SDK mode (is_sdk=True)
        """
        if self.is_sdk:
            # SDK mode: Handle complete response object - return coroutine
            return self._trace_sdk_mode(func, *args, **kwargs)
        else:
            # Streaming mode: Handle stream chunks - return async generator
            return self._trace_streaming_mode(func, *args, **kwargs)

    def trace_sdk_stream(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute streaming LLM tracing for Anthropic SDK stream responses.
        
        This decorator is specifically designed for functions that return
        Anthropic SDK stream objects (from client.messages.stream()).
        
        APPROACH:
        - Wraps functions that return MessageStreamManager context managers
        - Processes structured event objects (not raw JSON strings)
        - Handles events like 'text', 'content_block_start', 'content_block_stop', etc.
        - Creates focused traces for SDK streaming responses
        
        USAGE EXAMPLE:
        ```python
        tracer = LLMStreamingTracer(provider=anthropic_provider)
        
        @tracer.trace_sdk_stream
        async def anthropic_sdk_stream_call(**kwargs):
            # This should return client.messages.stream()
            return client.messages.stream(
                model=kwargs["model_name"],
                max_tokens=kwargs["max_tokens"],
                messages=kwargs["chat_messages"],
                system=kwargs["system_prompt"],
                tools=kwargs.get("tools"),
                temperature=kwargs.get("temperature", 0.7)
            )
        
        # Use as context manager - tracing happens automatically
        async with anthropic_sdk_stream_call(**params) as stream:
            async for event in stream:
                if event.type == "text":
                    print(event.text, end="", flush=True)
            # Trace is created using stream.get_final_message() when exiting context
        ```
        """
        return self._trace_anthropic_sdk_stream(func, *args, **kwargs)

    def _trace_anthropic_sdk_stream(self, func: Callable, *args, **kwargs):
        """Handle Anthropic SDK streaming mode - returns a wrapper function."""
        def wrapper(*wrapper_args, **wrapper_kwargs):
            if not self.should_trace():
                return func(*wrapper_args, **wrapper_kwargs)

            # Get mapped parameter values for tracing
            model_name = self.get_mapped_param_value(wrapper_kwargs, "model_name")
            system_prompt = self.get_mapped_param_value(wrapper_kwargs, "system_prompt")
            user_prompt = self.get_mapped_param_value(wrapper_kwargs, "chat_messages")
            operation_name = self.get_mapped_param_value(wrapper_kwargs, "operation_name")
            max_tokens = self.get_mapped_param_value(wrapper_kwargs, "max_tokens")
            temperature = self.get_mapped_param_value(wrapper_kwargs, "temperature")
            tools = self.get_mapped_param_value(wrapper_kwargs, "tools")
            if tools:
                tool_names = extract_tool_names_from_tools(tools)
            else:
                tool_names = []

            input_tool_summary = {}
            if user_prompt and isinstance(user_prompt, list):
                input_tool_summary = get_tool_call_summary_from_messages(user_prompt)

            # Return a simple wrapper context manager
            return _SimpleSDKStreamWrapper(
                func, wrapper_args, wrapper_kwargs, self, model_name, system_prompt, user_prompt,
                operation_name, max_tokens, temperature, tool_names, input_tool_summary
            )
        
        return wrapper

    async def _trace_sdk_mode(self, func: Callable, *args, **kwargs) -> Any:
        """Handle SDK mode tracing - expects complete response object."""
        if not self.should_trace():
            return await func(*args, **kwargs)

        trace_id = request_context.get()
        start_time = datetime.now()

        # Get mapped parameter values
        model_name = self.get_mapped_param_value(kwargs, "model_name")
        system_prompt = self.get_mapped_param_value(kwargs, "system_prompt")
        user_prompt = self.get_mapped_param_value(kwargs, "chat_messages")
        operation_name = self.get_mapped_param_value(kwargs, "operation_name")
        max_tokens = self.get_mapped_param_value(kwargs, "max_tokens")
        temperature = self.get_mapped_param_value(kwargs, "temperature")
        tools = self.get_mapped_param_value(kwargs, "tools")
        if tools:
            tool_names = extract_tool_names_from_tools(tools)
        else:
            tool_names = []

        input_tool_summary = {}
        if user_prompt and isinstance(user_prompt, list):
            input_tool_summary = get_tool_call_summary_from_messages(
                user_prompt
            )

        try:
            # SDK mode: Expect complete response object
            result = await func(*args, **kwargs)
            end_time = datetime.now()

            # Extract data from SDK response
            total_input_tokens = result.get("usage", {}).get("input_tokens", 0)
            total_output_tokens = result.get("usage", {}).get(
                "output_tokens", 0
            )

            # Extract response content and tool calls
            collected_response = ""
            collected_tool_calls = []

            content = result.get("content", [])
            if isinstance(content, list):
                for content_block in content:
                    if isinstance(content_block, dict):
                        if content_block.get("type") == "text":
                            collected_response += content_block.get("text", "")
                        elif content_block.get("type") == "tool_use":
                            tool_call = {
                                "id": content_block.get("id", ""),
                                "name": content_block.get("name", ""),
                                "input": content_block.get("input", {}),
                                "type": "tool_use",
                            }
                            collected_tool_calls.append(tool_call)

            # Calculate tokens and cost
            tokens_data = {
                "prompt_tokens": total_input_tokens,
                "completion_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
            }

            cost_details = {}
            if tokens_data and model_name:
                try:
                    cost_details = self.provider.calculate_cost(
                        tokens_data, model_name
                    )
                except ValueError as e:
                    raise e

            # Create FOCUSED tool call metadata for THIS trace only
            tool_call_metadata = {
                # PRIMARY: Current stream - what THIS LLM call produced
                "currentStreamHasToolCalls": len(collected_tool_calls) > 0,
                "currentStreamToolCallCount": len(collected_tool_calls),
                "currentStreamToolCalls": collected_tool_calls,
                # CONTEXT: Input message context (for reference only)
                "inputContextHasToolCalls": input_tool_summary.get(
                    "has_tool_calls", False
                ),
                "inputContextToolCallCount": input_tool_summary.get(
                    "tool_call_count", 0
                ),
                "inputContextHasToolResults": input_tool_summary.get(
                    "has_tool_results", False
                ),
                "inputContextToolResultCount": input_tool_summary.get(
                    "tool_result_count", 0
                ),
                # LEGACY: For backward compatibility (focused on current stream)
                "hasToolCalls": len(collected_tool_calls) > 0,
                "toolCallCount": len(collected_tool_calls),
                "hasToolResults": input_tool_summary.get(
                    "has_tool_results", False
                ),
                "toolResultCount": input_tool_summary.get(
                    "tool_result_count", 0
                ),
                "toolCalls": collected_tool_calls,
                "toolResults": input_tool_summary.get("tool_results", []),
                # SDK specific metadata
                "sdkMode": True,
                "sdkResponseId": result.get("id", ""),
                "sdkStopReason": result.get("stop_reason", ""),
            }

            await self._create_generation(
                trace_id,
                model_name,
                system_prompt,
                user_prompt,
                operation_name,
                max_tokens,
                temperature,
                tool_names,
                input_tool_summary,
                collected_response,
                tokens_data,
                cost_details,
                tool_call_metadata,
                start_time,
                end_time,
            )

            return result

        except Exception as e:
            # Log error but don't break the flow
            print(f"Error in LLMStreamingTracer SDK mode: {e}")
            return await func(*args, **kwargs)

    async def _trace_streaming_mode(self, func: Callable, *args, **kwargs):
        """Handle streaming mode tracing - expects async generator yielding chunks."""
        if not self.should_trace():
            async for chunk in func(*args, **kwargs):
                yield chunk
            return

        trace_id = request_context.get()
        start_time = datetime.now()
        total_input_tokens = 0
        total_output_tokens = 0
        collected_response = ""
        collected_tool_calls = []  # Tool calls from CURRENT stream only

        # Get mapped parameter values
        model_name = self.get_mapped_param_value(kwargs, "model_name")
        system_prompt = self.get_mapped_param_value(kwargs, "system_prompt")
        user_prompt = self.get_mapped_param_value(kwargs, "chat_messages")
        operation_name = self.get_mapped_param_value(kwargs, "operation_name")
        max_tokens = self.get_mapped_param_value(kwargs, "max_tokens")
        temperature = self.get_mapped_param_value(kwargs, "temperature")
        tools = self.get_mapped_param_value(kwargs, "tools")
        if tools:
            tool_names = extract_tool_names_from_tools(tools)
        else:
            tool_names = []

        input_tool_summary = {}
        if user_prompt and isinstance(user_prompt, list):
            input_tool_summary = get_tool_call_summary_from_messages(
                user_prompt
            )

        try:
            # Streaming mode: Original logic for processing stream chunks
            async for response_line in func(*args, **kwargs):
                if response_line.startswith("data: "):
                    response_data = json.loads(response_line[6:])

                    # Handle streaming events
                    if response_data["type"] == "message_start":
                        total_input_tokens = response_data["message"]["usage"][
                            "input_tokens"
                        ]
                        total_output_tokens = response_data["message"]["usage"][
                            "output_tokens"
                        ]
                    elif response_data["type"] == "content_block_start":
                        content_block = response_data.get("content_block", {})
                        if content_block.get("type") == "tool_use":
                            # Track tool calls from THIS stream
                            tool_call = {
                                "id": content_block.get("id", ""),
                                "name": content_block.get("name", ""),
                                "input": content_block.get("input", {}),
                                "type": "tool_use",
                            }
                            collected_tool_calls.append(tool_call)
                    elif response_data["type"] == "content_block_delta":
                        if (
                            response_data.get("delta", {}).get("type")
                            == "text_delta"
                        ):
                            collected_response += response_data["delta"]["text"]
                    elif response_data["type"] == "message_delta":
                        if "usage" in response_data:
                            total_output_tokens += response_data["usage"].get(
                                "output_tokens", 0
                            )

                    yield response_line
                else:
                    yield response_line

            end_time = datetime.now()

            # Calculate tokens and cost
            tokens_data = {
                "prompt_tokens": total_input_tokens,
                "completion_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
            }

            cost_details = {}
            if tokens_data and model_name:
                try:
                    cost_details = self.provider.calculate_cost(
                        tokens_data, model_name
                    )
                except ValueError as e:
                    raise e

            # Create FOCUSED tool call metadata for THIS trace only
            tool_call_metadata = {
                # PRIMARY: Current stream - what THIS LLM call produced
                "currentStreamHasToolCalls": len(collected_tool_calls) > 0,
                "currentStreamToolCallCount": len(collected_tool_calls),
                "currentStreamToolCalls": collected_tool_calls,
                # CONTEXT: Input message context (for reference only)
                "inputContextHasToolCalls": input_tool_summary.get(
                    "has_tool_calls", False
                ),
                "inputContextToolCallCount": input_tool_summary.get(
                    "tool_call_count", 0
                ),
                "inputContextHasToolResults": input_tool_summary.get(
                    "has_tool_results", False
                ),
                "inputContextToolResultCount": input_tool_summary.get(
                    "tool_result_count", 0
                ),
                # LEGACY: For backward compatibility (focused on current stream)
                "hasToolCalls": len(collected_tool_calls) > 0,
                "toolCallCount": len(collected_tool_calls),
                "hasToolResults": input_tool_summary.get(
                    "has_tool_results", False
                ),
                "toolResultCount": input_tool_summary.get(
                    "tool_result_count", 0
                ),
                "toolCalls": collected_tool_calls,
                "toolResults": input_tool_summary.get("tool_results", []),
                # Streaming specific metadata
                "sdkMode": False,
            }

            await self._create_generation(
                trace_id,
                model_name,
                system_prompt,
                user_prompt,
                operation_name,
                max_tokens,
                temperature,
                tool_names,
                input_tool_summary,
                collected_response,
                tokens_data,
                cost_details,
                tool_call_metadata,
                start_time,
                end_time,
            )

        except Exception as e:
            # Log error but don't break the flow - for streaming we need to fallback to original function
            print(f"[LLM Observability] Error in LLM Streaming Tracer: {e}")
            print(f"[LLM Observability] Stack trace:\n{traceback.format_exc()}")
            # FIX: This may execute original Function in loop until it succeeds
            # async for chunk in func(*args, **kwargs):
            #     yield chunk

    async def _create_generation(
        self,
        trace_id,
        model_name,
        system_prompt,
        user_prompt,
        operation_name,
        max_tokens,
        temperature,
        tool_names,
        input_tool_summary,
        collected_response,
        tokens_data,
        cost_details,
        tool_call_metadata,
        start_time,
        end_time,
    ):
        """Common method to create generation for both SDK and streaming modes."""
        # Create input messages for trace
        input_messages = []
        input_messages.append({"role": "system", "content": system_prompt})

        # Convert messages to Langfuse format
        provider_name = getattr(self.provider, 'name', self.provider.get('name', str(self.provider)) if isinstance(self.provider, dict) else str(self.provider))
        if provider_name == "anthropic":
            input_messages += convert_anthropic_messages_to_langfuse_format(
                user_prompt
            )
        elif provider_name == "groq":
            input_messages += convert_groq_messages_to_langfuse_format(
                user_prompt
            )
        else:
            input_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

        generation_data = {
            "model_name": model_name,
            "service_provider": provider_name,
            "input": input_messages,
            "output": collected_response,
            "usage": tokens_data,
            "cost_details": cost_details,
            "start_time": start_time,
            "end_time": end_time,
            "tool_call_metadata": tool_call_metadata,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "tool_names": tool_names,
        }

        # Build complete metadata
        complete_metadata = {
            "model": model_name,
            "provider": provider_name,
            "maxTokens": max_tokens,
            "temperature": temperature,
            "tool": tool_names,
            "timeTaken": (end_time - start_time).total_seconds(),
            "inputTokens": tokens_data.get("prompt_tokens", 0),
            "outputTokens": tokens_data.get("completion_tokens", 0),
            "inputCost": cost_details.get("input", 0.0),
            "outputCost": cost_details.get("output", 0.0),
            "totalCost": cost_details.get("total", 0.0),
            **tool_call_metadata,
        }

        # Filter metadata if metadata_config is provided
        filtered_metadata = self.filter_metadata(complete_metadata)

        generation_id = await _LangfuseService.create_generation_for_LLM(
            trace_id,
            generation_data,
            (
                operation_name.replace("_", " ").title()
                if operation_name
                else f"{provider_name.capitalize()} Generation"
            ),
            filtered_metadata,
        )

        generation_id_context.set(generation_id)
