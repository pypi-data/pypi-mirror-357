"""
ServerBase - Clean FastAPI server with agent decorators

A simplified server framework for creating OpenAI-compatible agent endpoints
using FastAPI's native dependency injection for request access and ContextVar
for inner function access.

Features:
* @agent decorator for creating agent endpoints
* Request access via FastAPI dependency injection
* Inner function access via get_current_request()
* before_request and finalize_request decorators
* Support for both static and dynamic agent resolution
* OpenAI-compatible streaming and non-streaming responses
"""

import uuid
import json
import asyncio
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Union, Tuple
from datetime import datetime
from contextvars import ContextVar
from functools import wraps

from fastapi import FastAPI, Request, Response, HTTPException, Path, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

# Set up logger
logger = logging.getLogger(__name__)

# ContextVar for inner function access
_current_request: ContextVar[Optional[Request]] = ContextVar('current_request', default=None)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None


class Pricing(BaseModel):
    """
    Pydantic model for usage pricing information returned by functions.
    
    This model is used when functions need to report custom pricing 
    information beyond the decorator's fixed pricing.
    
    Attributes:
        credits: Number of credits consumed by the operation
        reason: Human-readable explanation of what was done
        metadata: Additional metadata for the operation
    
    Example:
        ```python
        @pricing(credits_per_call=1000)
        def my_function(data: str) -> Tuple[str, Pricing]:
            result = process_data(data)
            pricing_info = Pricing(
                credits=1500,  # Override default pricing
                reason="Custom processing with additional features",
                metadata={"feature": "premium", "data_size": len(data)}
            )
            return result, pricing_info
        ```
    """
    credits: int
    reason: str
    metadata: Dict[str, Any] = {}


class RequestState:
    """Helper class for managing request state data."""
    
    def __init__(self, request: Request):
        self.request = request
        
        # Initialize state if not exists
        if not hasattr(request.state, 'data'):
            request.state.data = {}
        if not hasattr(request.state, 'usage_records'):
            request.state.usage_records = []
        if not hasattr(request.state, 'start_time'):
            request.state.start_time = datetime.utcnow()
    
    def set(self, key: str, value: Any) -> None:
        """Store data in request state."""
        self.request.state.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve data from request state."""
        return self.request.state.data.get(key, default)
    
    # Agent data helper methods for consistent access
    def get_agent_state(self) -> Optional[Dict[str, Any]]:
        """Get the complete agent state data."""
        return self.get('agent_state') or getattr(self.request.state, 'agent_state', None)
    
    def get_agent_name(self) -> str:
        """Get the current agent name."""
        return self.get('agent_name', 'unknown')
    
    def get_agent_instance(self) -> Optional[Any]:
        """Get the current agent instance."""
        return self.get('agent_instance')
    
    def get_agent_api_key(self) -> Optional[str]:
        """Get the current agent's API key."""
        return self.get('agent_api_key')
    
    def get_agent_type(self) -> str:
        """Get the current agent type (static/dynamic)."""
        return self.get('agent_type', 'unknown')
    
    # User identity helper methods - distinguish between different identity sources
    def get_peer_user_id(self) -> str:
        """
        Get the peer user ID (the user actually making the request).
        This comes from peer identity token validation.
        """
        identity_info = self.get("identity_info")
        if identity_info and isinstance(identity_info, dict):
            user_id = identity_info.get("userId", identity_info.get("user_id"))
            if user_id and user_id != "anonymous":
                return user_id
        return "anonymous"
    
    def get_payment_user_id(self) -> str:
        """
        Get the user ID from the payment token (who's paying for the request).
        This may be different from the peer user if someone else is funding the request.
        """
        token_info = self.get("token_info")
        if token_info and isinstance(token_info, dict):
            user_id = token_info.get("userId")
            if user_id and user_id != "anonymous":
                return user_id
        return "anonymous"
    
    def get_origin_user_id(self) -> str:
        """
        Get the origin user ID (from origin identity token).
        This represents the original user in a chain of requests.
        """
        # Extract from origin identity if available
        origin_identity = getattr(self.request.state, 'origin_identity', None)
        if origin_identity:
            # Would need to decode/validate origin identity token here
            # For now, return placeholder
            return "origin_user"  # TODO: Implement origin token decoding
        return "anonymous"
    
    def get_agent_owner_user_id(self) -> str:
        """
        Get the user ID of the agent owner.
        This comes from the agent's portal data.
        """
        agent_state = self.get_agent_state()
        if agent_state:
            portal_data = agent_state.get('portal_data')
            if portal_data and isinstance(portal_data, dict):
                return portal_data.get('userId', portal_data.get('ownerId', 'unknown'))
        return "unknown"
    
    def get_all_user_identities(self) -> Dict[str, Any]:
        """
        Get all user identities present in the request for debugging/logging.
        
        Returns:
            Dict containing all user identity information with clear labels
        """
        return {
            "peer_user_id": self.get_peer_user_id(),
            "payment_user_id": self.get_payment_user_id(), 
            "origin_user_id": self.get_origin_user_id(),
            "agent_owner_user_id": self.get_agent_owner_user_id(),
            
            # Raw identity data for debugging
            "identity_sources": {
                "peer_identity_info": self.get("identity_info"),
                "payment_token_info": self.get("token_info"),
                "context_user_id": self.get("user_id"),
                "agent_portal_data": self.get_agent_state().get('portal_data') if self.get_agent_state() else None
            },
            
            # Token availability
            "available_tokens": {
                "peer_identity_token": bool(self.get("peer_identity_token")),
                "payment_token": bool(self.get("payment_token")),
                "origin_token": bool(self.get("origin_token"))
            }
        }
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get complete user information with identity distinction."""
        return {
            "all_identities": self.get_all_user_identities(),
            "has_peer_identity": self.get_peer_user_id() != "anonymous",
            "has_payment_identity": self.get_payment_user_id() != "anonymous"
        }
    
    def track_usage(
        self, 
        credits: int,
        reason: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Track usage with credits, reason, and metadata.
        
        Args:
            credits: Number of credits consumed
            reason: Human-readable explanation of what was done
            metadata: Additional metadata for the operation
            
        Returns:
            Unique usage record ID
        """
        usage_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        usage_record = {
            "id": usage_id,
            "timestamp": timestamp.isoformat(),
            "credits": credits,
            "reason": reason,
            "metadata": metadata or {},
            # "request_info": {
            #     "user_id": self.get("user_id", "anonymous"),
            #     "session_id": self.get("session_data", {}).get("session_id", "unknown"),
            #     "user_agent": self.request.headers.get("user-agent", "unknown")[:100],
            #     "ip": getattr(self.request, 'client', None) and getattr(self.request.client, 'host', None) or "unknown"
            # }
        }
        
        self.request.state.usage_records.append(usage_record)
        return usage_id
    
    def get_duration(self) -> float:
        """Get request duration in seconds."""
        return (datetime.utcnow() - self.request.state.start_time).total_seconds()
    
    @property
    def usage(self) -> Dict[str, Any]:
        """Get comprehensive usage summary."""
        records = getattr(self.request.state, 'usage_records', [])
        
        total_credits = sum(record['credits'] for record in records)
        
        return {
            # Summary
            "total_credits": total_credits,
            "total_operations": len(records),
            "duration_seconds": self.get_duration(),
            
            # Receipt details
            "receipt": {
                "request_id": id(self.request),
                "started_at": self.request.state.start_time.isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "user_id": self.get("user_id", "anonymous"),
                "session_id": self.get("session_data", {}).get("session_id", "unknown"),
                
                # All operations with details
                "operations": records,
                
                # Cost breakdown
                "cost_breakdown": {
                    "total_credits": total_credits,
                    "average_credits_per_operation": total_credits / len(records) if records else 0,
                    "most_expensive_operation": max(records, key=lambda r: r['credits']) if records else None
                }
            }
        }


def get_context() -> Optional[RequestState]:
    """Get current request context - for use in inner functions."""
    request = _current_request.get()
    if request:
        return RequestState(request)
    return None


class StreamingWrapper(StreamingResponse):
    """Wrapper for streaming responses to ensure finalize callbacks run with final results."""
    
    def __init__(self, original_response: StreamingResponse, server: 'ServerBase', request: Request):
        self.original_response = original_response
        self.server = server
        self.request = request
        
        super().__init__(
            self._wrap_content(),
            status_code=original_response.status_code,
            headers=original_response.headers,
            media_type=original_response.media_type,
            background=original_response.background
        )
    
    async def _wrap_content(self):
        """Wrap content and ensure finalize callbacks run after streaming."""
        try:
            async for chunk in self.original_response.body_iterator:
                yield chunk
        finally:
            # Run finalize callbacks after streaming completes with the response
            await self.server._run_finalize_callbacks(self.request, self)


class AgentDecorator:
    """Helper class for agent-related decorators."""
    
    def __init__(self, server: 'ServerBase'):
        self.server = server
    
    def __call__(self, name_or_resolver: Union[str, Callable]):
        """Create agent endpoints."""
        return self.server._create_agent_decorator(name_or_resolver)
    
    def before_request(self, func: Callable) -> Callable:
        """Register before_request callback."""
        self.server.before_request_callbacks.append(func)
        return func
    
    def finalize_request(self, func: Callable) -> Callable:
        """Register finalize_request callback."""
        self.server.finalize_request_callbacks.append(func)
        return func


class ServerBase(FastAPI):
    """Clean FastAPI server with agent decorators using hybrid approach."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.before_request_callbacks: List[Callable] = []
        self.finalize_request_callbacks: List[Callable] = []
        self.agent_endpoints: Dict[str, Dict[str, Any]] = {}
        self.agent_handlers: Dict[str, Callable] = {}
        
        # Create agent decorator
        self.agent = AgentDecorator(self)
        
        # Add request state middleware for agent endpoints
        @self.middleware("http")
        async def request_state_middleware(request: Request, call_next):
            if self._is_agent_endpoint(request.url.path):
                # Set request in ContextVar for inner functions
                token = _current_request.set(request)
                
                try:
                    # Initialize request state
                    RequestState(request)
                    
                    # Add flag to track if finalize callbacks have been called
                    request.state.finalize_callbacks_called = False
                    
                    # Run before_request callbacks
                    for callback in self.before_request_callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(request)
                            else:
                                callback(request)
                        except Exception as e:
                            logger.error(f"Before request callback error: {e}")
                    
                    # Process request
                    response = await call_next(request)
                    
                    # Handle finalize callbacks
                    if isinstance(response, StreamingResponse):
                        # For streaming responses, wrap them and let the wrapper call finalize callbacks
                        # after streaming completes. Do NOT call them here.
                        wrapped_response = StreamingWrapper(response, self, request)
                        return wrapped_response
                    else:
                        # For non-streaming responses, call finalize callbacks immediately
                        await self._run_finalize_callbacks(request, response)
                        return response
                
                finally:
                    # Clean up ContextVar
                    _current_request.reset(token)
            
            # Non-agent endpoints proceed normally
            return await call_next(request)
    
    def _is_agent_endpoint(self, path: str) -> bool:
        """Check if path is an agent endpoint."""
        return "/chat/completions" in path or any(path.startswith(ep) for ep in self.agent_endpoints)
    
    async def _run_finalize_callbacks(self, request: Request, response: Optional[Response]):
        """Run finalize_request callbacks, ensuring they're only called once per request."""
        # Check if callbacks have already been called for this request
        if hasattr(request.state, 'finalize_callbacks_called') and request.state.finalize_callbacks_called:
            return
        
        # Mark callbacks as called
        request.state.finalize_callbacks_called = True
        
        for callback in self.finalize_request_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(request, response)
                else:
                    callback(request, response)
            except Exception as e:
                logger.error(f"Finalize callback error: {e}")
    
    def _create_agent_decorator(self, name_or_resolver: Union[str, Callable]):
        """Create agent decorator."""
        if isinstance(name_or_resolver, str):
            return self._create_static_agent_decorator(name_or_resolver)
        else:
            return self._create_dynamic_agent_decorator(name_or_resolver)
    
    def _create_static_agent_decorator(self, agent_name: str):
        """Create decorator for static agent."""
        def decorator(func: Callable) -> Callable:
            self.agent_handlers[func.__name__] = func
            self._create_static_agent_endpoints(agent_name, func)
            return func
        return decorator
    
    def _create_static_agent_endpoints(self, agent_name: str, handler_func: Callable):
        """Create 4 endpoints for static agent."""
        base_path = f"/{agent_name}"
        self.agent_endpoints[base_path] = {"type": "static", "name": agent_name}
        
        def _get_agent_data():
            """Get agent data for static agent."""
            # Import settings to get API key
            from robutler.settings import settings
            
            agent_data = {
                'name': agent_name,
                'api_key': settings.api_key
            }
            
            # Try to get agent instance from registered agents if this is a Server
            if hasattr(self, 'agents'):
                for agent in self.agents:
                    if getattr(agent, 'name', None) == agent_name:
                        agent_data['min_balance'] = getattr(agent, 'min_balance', 0)
                        agent_data['credits_per_token'] = getattr(agent, 'credits_per_token', None)
                        agent_data['model'] = getattr(agent, 'model', 'gpt-4o-mini')
                        agent_data['instructions'] = getattr(agent, 'instructions', '')
                        agent_data['intents'] = getattr(agent, 'intents', [])
                        break
            
            return agent_data
        
        # 1. Control endpoint (POST /{name})
        @self.post(base_path)
        async def control():
            agent_data = _get_agent_data()
            return {
                "agent": agent_name,
                "message": "Agent control endpoint",
                "agent_data": agent_data,
                "endpoints": {
                    "info": f"{base_path}",
                    "chat": f"{base_path}/chat/completions"
                }
            }
        
        # 2. Info endpoint (GET /{name})
        @self.get(base_path)
        async def info():
            agent_data = _get_agent_data()
            return {
                "agent": agent_name,
                "description": handler_func.__doc__ or "AI Agent",
                "agent_data": agent_data,
                "endpoints": {
                    "control": f"{base_path}",
                    "info": f"{base_path}",
                    "chat": f"{base_path}/chat/completions"
                }
            }
        
        # 3. Chat completions (POST /{name}/chat/completions)
        @self.post(f"{base_path}/chat/completions")
        async def chat_completions(chat_request: ChatCompletionRequest, request: Request):
            agent_data = _get_agent_data()
            return await self._handle_chat_completions(handler_func, chat_request, request, agent_data)
        
        # 4. Chat completions info (GET /{name}/chat/completions)
        @self.get(f"{base_path}/chat/completions")
        async def chat_info():
            agent_data = _get_agent_data()
            return {
                "endpoint": f"{base_path}/chat/completions",
                "agent": agent_name,
                "openai_compatible": True,
                "supports_streaming": True,
                "agent_data": agent_data
            }
    
    def _create_dynamic_agent_decorator(self, resolver_func: Callable):
        """Create decorator for dynamic agent."""
        def decorator(func: Callable) -> Callable:
            self.agent_handlers[func.__name__] = func
            self._create_dynamic_agent_endpoints(resolver_func, func)
            return func
        return decorator
    
    def _create_dynamic_agent_endpoints(self, resolver_func: Callable, handler_func: Callable):
        """Create 4 endpoints for dynamic agent."""
        base_path = "/{agent_name}"
        
        # 1. Control endpoint (POST /{agent_name})
        @self.post(base_path)
        async def control(agent_name: str = Path(...)):
            # Support both sync and async resolvers
            if asyncio.iscoroutinefunction(resolver_func):
                agent_data = await resolver_func(agent_name)
            else:
                agent_data = resolver_func(agent_name)
            if agent_data is False:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
            
            return {
                "agent": agent_name,
                "message": "Agent control endpoint",
                "agent_data": agent_data,
                "endpoints": {
                    "info": f"/{agent_name}",
                    "chat": f"/{agent_name}/chat/completions"
                }
            }
        
        # 2. Info endpoint (GET /{agent_name})
        @self.get(base_path)
        async def info(agent_name: str = Path(...)):
            # Support both sync and async resolvers
            if asyncio.iscoroutinefunction(resolver_func):
                agent_data = await resolver_func(agent_name)
            else:
                agent_data = resolver_func(agent_name)
            if agent_data is False:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
            
            return {
                "agent": agent_name,
                "description": handler_func.__doc__ or "Dynamic AI Agent",
                "agent_data": agent_data,
                "endpoints": {
                    "control": f"/{agent_name}",
                    "info": f"/{agent_name}",
                    "chat": f"/{agent_name}/chat/completions"
                }
            }
        
        # 3. Chat completions (POST /{agent_name}/chat/completions)
        @self.post(f"{base_path}/chat/completions")
        async def chat_completions(chat_request: ChatCompletionRequest, request: Request, agent_name: str = Path(...)):
            # Support both sync and async resolvers
            if asyncio.iscoroutinefunction(resolver_func):
                agent_data = await resolver_func(agent_name)
            else:
                agent_data = resolver_func(agent_name)
            if agent_data is False:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
            
            return await self._handle_chat_completions(handler_func, chat_request, request, agent_data)
        
        # 4. Chat completions info (GET /{agent_name}/chat/completions)
        @self.get(f"{base_path}/chat/completions")
        async def chat_info(agent_name: str = Path(...)):
            # Support both sync and async resolvers
            if asyncio.iscoroutinefunction(resolver_func):
                agent_data = await resolver_func(agent_name)
            else:
                agent_data = resolver_func(agent_name)
            if agent_data is False:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
            
            return {
                "endpoint": f"/{agent_name}/chat/completions",
                "agent": agent_name,
                "openai_compatible": True,
                "supports_streaming": True,
                "agent_data": agent_data
            }
    
    async def _handle_chat_completions(self, handler_func: Callable, chat_request: ChatCompletionRequest, request: Request, agent_data=None):
        """Handle chat completions request."""
        # Validate peer identity token for user information (always done)
        await self._validate_peer_identity_token(request)
        
        # Check for payment token in headers and validate if required
        await self._validate_payment_token(request, agent_data)
        
        # Convert messages to list format
        messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]
        
        # Prepare function arguments
        kwargs = {"messages": messages, "stream": chat_request.stream}
        
        # Check if function accepts request parameter
        sig = inspect.signature(handler_func)
        if "request" in sig.parameters:
            kwargs["request"] = request
        if "context" in sig.parameters:
            kwargs["context"] = get_context()
        if "agent_data" in sig.parameters and agent_data is not None:
            kwargs["agent_data"] = agent_data
        
        # Call handler function
        if asyncio.iscoroutinefunction(handler_func):
            result = await handler_func(**kwargs)
        else:
            result = handler_func(**kwargs)
        
        # Handle different result types
        if isinstance(result, StreamingResponse):
            return result
        elif hasattr(result, 'stream_events'):
            # Streaming agent result
            if chat_request.stream:
                return self._create_streaming_response(result, chat_request.model)
            else:
                # Collect streaming content
                content_parts = []
                async for event in result.stream_events():
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        if event.data.delta:
                            content_parts.append(event.data.delta)
                content = ''.join(content_parts)
                return self._create_chat_completion_response(content, chat_request.model)
        else:
            # String result
            content = str(result)
            if chat_request.stream:
                return self._create_string_streaming_response(content, chat_request.model)
            else:
                return self._create_chat_completion_response(content, chat_request.model)
    
    async def _validate_peer_identity_token(self, request: Request):
        """
        Validate peer identity token to extract user information.
        
        Args:
            request: FastAPI request object
            
        Note:
            This function extracts user identity but does not require authentication.
            If no identity token is provided, user remains anonymous.
        """
        # Extract peer identity token from headers
        identity_token = request.headers.get('x-peer-identity') or request.headers.get('X-Peer-Identity')
        
        # Store token in context for later use
        context = get_context()
        if context and identity_token:
            context.set('peer_identity_token', identity_token)
        
        # If no identity token provided, user remains anonymous (no error)
        if not identity_token:
            logger.debug("No peer identity token provided, user will be anonymous")
            return
        
        # Validate token using portal API
        try:
            # Import here to avoid circular dependencies
            import httpx
            from robutler.settings import settings
            
            portal_url = settings.robutler_portal_url
            
            # Get API key for authentication
            api_key = settings.api_key
            
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{portal_url}/api/identity/validate",
                        json={"token": identity_token},
                        headers=headers,
                        timeout=10.0
                    )
                except httpx.TimeoutException:
                    logger.warning("Peer identity token validation timeout, proceeding as anonymous")
                    return
                except httpx.ConnectError:
                    logger.warning("Unable to connect to identity service, proceeding as anonymous")
                    return
                
                if response.status_code != 200:
                    logger.warning(f"Peer identity token validation failed (HTTP {response.status_code}), proceeding as anonymous")
                    return
                
                identity_data = response.json()
                
                if not identity_data.get('valid', False):
                    logger.warning("Invalid peer identity token, proceeding as anonymous")
                    return
                
                # Extract user identity information
                identity_info = identity_data.get('identity', {})
                
                # Store identity info in context for later use
                if context and identity_info:
                    context.set('identity_info', identity_info)
                    user_id = identity_info.get('userId', identity_info.get('user_id', 'anonymous'))
                    logger.info(f"Validated peer identity token for user: {user_id}")
                    
        except Exception as e:
            logger.warning(f"Peer identity token validation failed: {str(e)}, proceeding as anonymous")
            return
    
    async def _validate_payment_token(self, request: Request, agent_data=None):
        """
        Validate payment token if agent requires minimum balance.
        
        Args:
            request: FastAPI request object
            agent_data: Agent data containing min_balance requirement
            
        Raises:
            HTTPException: 402 if payment token is invalid or insufficient balance
        """
        # Extract payment token from headers
        payment_token = request.headers.get('x-payment-token') or request.headers.get('X-Payment-Token')
        
        # Store token in context for later use
        context = get_context()
        if context and payment_token:
            context.set('payment_token', payment_token)
        
        # Check if agent has minimum balance requirement
        min_balance = 0
        if agent_data and hasattr(agent_data, 'min_balance'):
            min_balance = agent_data.min_balance
        elif agent_data and isinstance(agent_data, dict) and 'min_balance' in agent_data:
            min_balance = agent_data['min_balance']
        elif hasattr(self, '_current_agent') and hasattr(self._current_agent, 'min_balance'):
            min_balance = self._current_agent.min_balance
        else:
            # Try to get agent from request state (used by Server class)
            if hasattr(request, 'state') and hasattr(request.state, 'agent_state'):
                agent_state = request.state.agent_state
                if 'instance' in agent_state and hasattr(agent_state['instance'], 'min_balance'):
                    min_balance = agent_state['instance'].min_balance
        
        # If no minimum balance required, skip validation
        if min_balance <= 0:
            return
            
        # If minimum balance required but no token provided
        if not payment_token:
            raise HTTPException(
                status_code=402,
                detail=f"Payment token required. Minimum balance: {min_balance} credits. Include X-Payment-Token header."
            )
        
        # Validate token using portal API
        try:
            # Import here to avoid circular dependencies
            import httpx
            from robutler.settings import settings
            
            portal_url = settings.robutler_portal_url
            
            # Get API key for authentication
            api_key = None
            if agent_data and isinstance(agent_data, dict) and 'api_key' in agent_data:
                api_key = agent_data['api_key']
            elif hasattr(agent_data, 'api_key'):
                api_key = agent_data.api_key
            else:
                # Fallback to settings
                api_key = settings.api_key
            
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{portal_url}/api/token/validate",
                        json={"token": payment_token},
                        headers=headers,
                        timeout=10.0
                    )
                except httpx.TimeoutException:
                    raise HTTPException(
                        status_code=402,
                        detail="Payment token validation timeout. Please try again."
                    )
                except httpx.ConnectError:
                    raise HTTPException(
                        status_code=402,
                        detail="Unable to connect to payment service. Please check your token or try again later."
                    )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_message = error_data.get('message', 'Payment token validation failed')
                    except:
                        error_message = f"Payment token validation failed (HTTP {response.status_code})"
                    
                    raise HTTPException(
                        status_code=402,
                        detail=error_message
                    )
                
                token_data = response.json()
                
                if not token_data.get('valid', False):
                    message = token_data.get('message', 'Invalid payment token')
                    raise HTTPException(
                        status_code=402,
                        detail=message
                    )
                
                # Check available balance
                token_info = token_data.get('token', {})
                available_amount = token_info.get('availableAmount', 0)
                
                if available_amount < min_balance:
                    raise HTTPException(
                        status_code=402,
                        detail=f"Insufficient token balance. Available: {available_amount}, Required: {min_balance}"
                    )
                
                # Store token info in context for later use
                if context:
                    context.set('token_info', token_info)
                    context.set('available_balance', available_amount)
                    
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Payment token validation failed: {str(e)}"
            )
    
    def _create_streaming_response(self, stream_result, model: str) -> StreamingResponse:
        """Create streaming response from agent stream result."""
        async def stream_generator():
            call_id = str(uuid.uuid4())
            created = int(datetime.utcnow().timestamp())
            
            # Initial chunk
            yield f"data: {json.dumps({'id': f'chatcmpl-{call_id}', 'object': 'chat.completion.chunk', 'created': created, 'model': model, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
            
            final_usage = None
            final_finish_reason = "stop"
            
            try:
                async for event in stream_result.stream_events():
                    if event.type == "chunk" and hasattr(event.data, 'chunk'):
                        # Handle new MockAgent format
                        chunk_data = event.data.chunk
                        
                        # Extract usage information if present (final chunk)
                        if 'usage' in chunk_data:
                            final_usage = chunk_data['usage']
                        
                        # Extract finish_reason if present
                        if 'choices' in chunk_data and chunk_data['choices']:
                            choice = chunk_data['choices'][0]
                            if choice.get('finish_reason'):
                                final_finish_reason = choice['finish_reason']
                        
                        # Stream the chunk as-is (already in correct format)
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                        
                    elif event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        # Handle old format for backward compatibility
                        if event.data.delta:
                            chunk = {
                                'id': f'chatcmpl-{call_id}',
                                'object': 'chat.completion.chunk',
                                'created': created,
                                'model': model,
                                'choices': [{
                                    'index': 0,
                                    'delta': {'content': event.data.delta},
                                    'finish_reason': None
                                }]
                            }
                            yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                error_chunk = {
                    'id': f'chatcmpl-{call_id}',
                    'object': 'chat.completion.chunk',
                    'created': created,
                    'model': model,
                    'choices': [{
                        'index': 0,
                        'delta': {'content': f"Error: {str(e)}"},
                        'finish_reason': 'stop'
                    }]
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
            
            # Only send final chunk if we didn't already get one with usage
            if final_usage is None:
                final_chunk = {
                    'id': f'chatcmpl-{call_id}',
                    'object': 'chat.completion.chunk',
                    'created': created,
                    'model': model,
                    'choices': [{
                        'index': 0,
                        'delta': {},
                        'finish_reason': final_finish_reason
                    }]
                }
                yield f"data: {json.dumps(final_chunk)}\n\n"
            
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    def _create_string_streaming_response(self, content: str, model: str) -> StreamingResponse:
        """Create streaming response from string content."""
        async def stream_generator():
            call_id = str(uuid.uuid4())
            created = int(datetime.utcnow().timestamp())
            
            # Initial chunk
            yield f"data: {json.dumps({'id': f'chatcmpl-{call_id}', 'object': 'chat.completion.chunk', 'created': created, 'model': model, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
            
            # Stream content in chunks
            chunk_size = 20
            for i in range(0, len(content), chunk_size):
                chunk_text = content[i:i + chunk_size]
                chunk = {
                    'id': f'chatcmpl-{call_id}',
                    'object': 'chat.completion.chunk',
                    'created': created,
                    'model': model,
                    'choices': [{
                        'index': 0,
                        'delta': {'content': chunk_text},
                        'finish_reason': None
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.01)
            
            # Final chunk without fake usage data
            final_chunk = {
                'id': f'chatcmpl-{call_id}',
                'object': 'chat.completion.chunk',
                'created': created,
                'model': model,
                'choices': [{
                    'index': 0,
                    'delta': {},
                    'finish_reason': 'stop'
                }]
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    def _create_chat_completion_response(self, content: str, model: str) -> Dict[str, Any]:
        """Create OpenAI-compatible chat completion response."""
        call_id = str(uuid.uuid4())
        created = int(datetime.utcnow().timestamp())
        
        return {
            "id": f"chatcmpl-{call_id}",
            "object": "chat.completion",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": len(content.split()),
                "total_tokens": len(content.split())
            }
        }


# Dependency functions for agent handlers
def get_request_state(request: Request) -> RequestState:
    """Dependency to get request state helper."""
    return RequestState(request)


def pricing(credits_per_call: Optional[int] = None, reason: Optional[str] = None):
    """
    Enhanced pricing decorator that tracks usage via context usage_records.
    
    This decorator provides flexible pricing for functions:
    1. Fixed pricing: If credits_per_call is provided, tracks usage on every call
    2. Dynamic pricing: If function returns (result, Pricing), uses the Pricing object
    3. Automatic reason generation: Defaults to function name if not provided
    
    Args:
        credits_per_call: Fixed credits to charge per function call
        reason: Custom reason for the usage record (defaults to function name)
    
    Examples:
        Fixed pricing:
        ```python
        @pricing(credits_per_call=1000, reason="Weather API lookup")
        def get_weather(location: str) -> str:
            return f"Weather in {location}"
        ```
        
        Dynamic pricing:
        ```python
        @pricing()  # No fixed pricing, uses return value
        def process_data(data: str) -> Tuple[str, Pricing]:
            result = expensive_processing(data)
            pricing_info = Pricing(
                credits=len(data) * 10,
                reason=f"Processed {len(data)} characters",
                metadata={"processing_type": "premium"}
            )
            return result, pricing_info
        ```
        
        Mixed approach:
        ```python
        @pricing(credits_per_call=500)  # Base cost
        def smart_function(data: str) -> Union[str, Tuple[str, Pricing]]:
            result = process_data(data)
            if needs_premium_processing(data):
                # Override with custom pricing
                pricing_info = Pricing(
                    credits=2000,
                    reason="Premium processing applied",
                    metadata={"premium": True}
                )
                return result, pricing_info
            # Use base cost
            return result
        ```
    """
    def decorator(func: Callable) -> Callable:
        # Default reason is function name
        usage_reason = reason or f"Function '{func.__name__}' called"
        
        def _track_usage(result: Any, func_name: str) -> Any:
            """Track usage based on function result and pricing configuration."""
            context = get_context()
            if not context:
                return result
            
            # Check if result is a tuple/list with 2 elements (result, Pricing)
            if isinstance(result, (tuple, list)) and len(result) == 2:
                actual_result, pricing_info = result
                if isinstance(pricing_info, Pricing):
                    # Use dynamic pricing from function return
                    context.track_usage(
                        credits=pricing_info.credits,
                        reason=pricing_info.reason,
                        metadata=pricing_info.metadata
                    )
                    return actual_result
            
            # Use fixed pricing if configured
            if credits_per_call is not None:
                context.track_usage(
                    credits=credits_per_call,
                    reason=usage_reason,
                    metadata={"function": func_name, "pricing_type": "fixed"}
                )
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                return _track_usage(result, func.__name__)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return _track_usage(result, func.__name__)
            return sync_wrapper
    
    return decorator 