"""
Robutler Server - Enhanced ServerBase with agent management

This module provides the main Server class that extends ServerBase with basic
agent management functionality.

Key Features:
    * Automatic agent registration and endpoint creation
    * Agent lifecycle management
    * Pricing decorator for cost tracking
    * Usage tracking for finalize callbacks

Example Usage:
    Basic server with agents:
    
    ```python
    from robutler.server import Server
    
    # Create server with agents
    app = Server(agents=[agent1, agent2])
    ```
    
    Using the pricing decorator:
    
    ```python
    from robutler.server import pricing
    
    @pricing(credits_per_call=1000)
    async def my_agent(messages, stream=False):
        return "Response"
    ```
"""

from typing import List, Optional, Callable, Any
from functools import wraps
import os
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional - if not installed, just continue
    pass

from .base import ServerBase, _current_request, pricing


# pricing decorator is now imported from base module


class Server(ServerBase):
    """
    Enhanced server that extends ServerBase with basic agent functionality.
    
    This class adds automatic agent registration and endpoint creation
    on top of the base server.
    """
    
    def __init__(self, agents: Optional[List] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.agents = agents or []
        
        # Register usage tracking callback
        self._register_usage_tracking_callback()
        
        # Create agent endpoints
        if self.agents:
            self._create_agent_endpoints(self.agents)
    
    def _register_usage_tracking_callback(self):
        """
        Register a single finalize callback that handles usage tracking for all agent types.
        """
        @self.agent.finalize_request
        def usage_tracker(request, response):
            """
            Usage tracking for all agent types.
            Handles RobutlerAgent, dynamic portal agents, and other agent types.
            """
            try:
                # Extract usage information
                usage_data = self._extract_usage(request)
                
                # Route to appropriate logging method
                self._log_usage(request, response, usage_data)
            except Exception as e:
                logger.error(f"⚠️ Error in usage tracker: {e}")
        
        logger.info("✅ Registered usage tracking callback for all agent types")
    
    def _extract_usage(self, request):
        """
        Extract usage information from agent execution results.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dict containing usage information (tokens, costs, AI response)
        """
        usage_info = {
            'ai_response': None,
            'prompt_tokens': None,
            'completion_tokens': None,
            'total_tokens': None
        }
        
        try:
            # Get streaming info from agent state
            agent_state = getattr(request.state, 'agent_state', {})
            is_streaming = agent_state.get('is_streaming', False)
            
            # Debug logging
            logger.debug(f"🔍 Extracting usage - streaming: {is_streaming}")
            
            # Try to get usage from stored results
            if is_streaming:
                streaming_result = getattr(request.state, 'streaming_result', None)
                logger.debug(f"🔍 Streaming result: {streaming_result is not None}")
                if streaming_result:
                    usage_info['ai_response'] = getattr(streaming_result, 'final_output', None)
                    logger.debug(f"🔍 AI response: {usage_info['ai_response'] is not None}")
                    usage_data = self._get_usage_from_result(streaming_result)
                    if usage_data:
                        usage_info.update(usage_data)
                        logger.debug(f"🔍 Usage data: {usage_data}")
            else:
                agent_result = getattr(request.state, 'agent_result', None)
                logger.debug(f"🔍 Agent result: {agent_result is not None}")
                if agent_result:
                    usage_info['ai_response'] = getattr(agent_result, 'final_output', None)
                    logger.debug(f"🔍 AI response: {usage_info['ai_response'] is not None}")
                    usage_data = self._get_usage_from_result(agent_result)
                    if usage_data:
                        usage_info.update(usage_data)
                        logger.debug(f"🔍 Usage data: {usage_data}")
        except Exception as e:
            logger.error(f"⚠️ Error extracting usage info: {e}")
        
        logger.debug(f"🔍 Final usage info: {usage_info}")
        return usage_info
    
    def _log_usage(self, request, response, usage_data):
        """Log agent usage and charge payment token if applicable."""
        import time
        
        # Get agent state
        agent_state = getattr(request.state, 'agent_state', None)
        if not agent_state:
            return
        
        # Calculate duration
        start_time = getattr(request.state, 'start_time', None)
        duration = f"{(time.time() - start_time):.3f}s" if start_time else "unknown"
        status_code = response.status_code if response else "unknown"
        
        # Update agent state with response info
        agent_state['status_code'] = status_code
        agent_state['duration'] = duration
        
        # Calculate costs before charging
        agent_instance = agent_state.get('instance')
        cost_info = {'total_credits': 0}
        if agent_instance:
            cost_info = self._calculate_costs(agent_instance, usage_data)
        
        # Charge payment token if applicable
        if cost_info['total_credits'] > 0:
            # Handle async payment token charging in sync context
            import asyncio
            try:
                # Try to get the current event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, create a task
                    asyncio.create_task(self._charge_payment_token(request, cost_info['total_credits'], agent_state.get('api_key')))
                else:
                    # If no loop is running, run the async function
                    asyncio.run(self._charge_payment_token(request, cost_info['total_credits'], agent_state.get('api_key')))
            except RuntimeError:
                # No event loop, run the async function
                asyncio.run(self._charge_payment_token(request, cost_info['total_credits'], agent_state.get('api_key')))
            except Exception as e:
                logger.error(f"⚠️ Error scheduling payment token charge: {e}")
        
        # Log agent usage
        self._log_agent_state(agent_state, usage_data)
    
    def _log_agent_state(self, agent_state, usage_data):
        """Log agent usage using agent state."""
        agent_type_label = "Portal Agent" if agent_state.get('type') == 'dynamic' else "Agent"
        
        logger.info(f"\n💰 Agent Usage - {agent_state['timestamp']}")
        logger.info(f"   Agent: {agent_state['name']} ({agent_type_label})")
        logger.info(f"   Request: {agent_state['method']} {agent_state['path']} -> {agent_state['status_code']} ({agent_state['duration']})")
        
        # User message
        messages = agent_state.get('messages', [])
        if messages and len(messages) > 0:
            last_message = messages[-1]
            if isinstance(last_message, dict) and last_message.get('role') == 'user':
                user_message = last_message.get('content', '')
                logger.info(f"   User: {user_message}")
        
        # AI response
        ai_response = usage_data.get('ai_response')
        if ai_response:
            logger.info(f"   AI: {ai_response}")
        
        # Usage and cost info
        agent_instance = agent_state.get('instance')
        if agent_instance:
            cost_info = self._calculate_costs(agent_instance, usage_data)
            
            total_tokens = usage_data.get('total_tokens', 0)
            if total_tokens:
                logger.info(f"   Prompt tokens: {usage_data.get('prompt_tokens', 0)}")
                logger.info(f"   Completion tokens: {usage_data.get('completion_tokens', 0)}")
                logger.info(f"   Total tokens: {total_tokens}")
                
                if cost_info['total_credits'] > 0:
                    logger.info(f"   💳 Cost Breakdown:")
                    if cost_info['token_credits'] > 0:
                        logger.info(f"      Token cost: {cost_info['token_credits']} credits ({total_tokens} tokens)")
                    if cost_info['call_credits'] > 0:
                        logger.info(f"      Call cost: {cost_info['call_credits']} credits")
                    logger.info(f"      Total cost: {cost_info['total_credits']} credits")
        
        logger.info(f"   Streaming: {'Yes' if agent_state.get('is_streaming') else 'No'}")
        logger.info("   " + "─" * 60)
    
    async def _charge_payment_token(self, request, credits_to_charge, agent_api_key=None):
        """
        Charge the payment token for the calculated usage.
        
        Args:
            request: FastAPI request object
            credits_to_charge: Number of credits to charge
            agent_api_key: Agent's specific API key for authentication
        """
        try:
            # Get payment token from request context
            payment_token = None
            if hasattr(request, 'state') and hasattr(request.state, 'payment_token'):
                payment_token = request.state.payment_token
            
            logger.debug(f"💳 Charging payment token: {credits_to_charge} credits, token: {'found' if payment_token else 'not found'}")
            
            if not payment_token:
                logger.debug("💳 No payment token to charge")
                return
            
            # Import here to avoid circular dependencies
            import httpx
            from robutler.settings import settings
            
            portal_url = settings.robutler_portal_url
            
            # Use agent's API key if provided, otherwise fall back to settings
            api_key = agent_api_key or settings.api_key
            
            logger.debug(f"💳 Charging token via portal: {portal_url}/api/token/redeem")
            logger.debug(f"💳 Request payload: amount={credits_to_charge}, token=***")
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{portal_url}/api/token/redeem",
                        json={
                            "token": payment_token,
                            "amount": credits_to_charge,
                            "receipt": f"Agent usage: {credits_to_charge} credits"
                        },
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}"
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        redeem_data = response.json()
                        logger.debug(f"💳 Portal redeem response: {redeem_data}")
                        
                        # Extract remaining balance from token response
                        token_data = redeem_data.get('token', {})
                        remaining_balance = token_data.get('availableAmount', 'unknown')
                        
                        logger.info(f"💳 Payment token charged: {credits_to_charge} credits")
                        logger.info(f"   Remaining balance: {remaining_balance} credits")
                    else:
                        logger.error(f"⚠️ Failed to charge payment token: {response.status_code} - {response.text}")
                        
                except httpx.TimeoutException:
                    logger.error("⚠️ Timeout charging payment token")
                except httpx.RequestError as e:
                    logger.error(f"⚠️ Request error charging payment token: {e}")
                    
        except Exception as e:
            logger.error(f"⚠️ Error charging payment token: {e}")
    
    def _extract_usage_info(self, agent, request, is_streaming):
        """Extract usage information from agent results."""
        usage_info = {}
        
        try:
            if is_streaming:
                streaming_result = getattr(request.state, 'streaming_result', None)
                if streaming_result and hasattr(streaming_result, 'final_output'):
                    usage_info['ai_response'] = str(streaming_result.final_output)
                
                # Try to extract usage from streaming result
                if streaming_result:
                    usage = self._get_usage_from_result(streaming_result)
                    if usage:
                        usage_info.update(usage)
            else:
                agent_result = getattr(request.state, 'agent_result', None)
                if agent_result and hasattr(agent_result, 'final_output'):
                    usage_info['ai_response'] = str(agent_result.final_output)
                
                # Try to extract usage from non-streaming result
                if agent_result:
                    usage = self._get_usage_from_result(agent_result)
                    if usage:
                        usage_info.update(usage)
                        
        except Exception as e:
            logger.error(f"⚠️ Error extracting usage info: {e}")
        
        return usage_info
    
    def _get_usage_from_result(self, result):
        """Extract usage information from a result object, trying multiple approaches."""
        usage_data = {}
        
        try:
            # Try different ways to access usage information
            usage = None
            
            # Method 1: Direct usage attribute
            if hasattr(result, 'usage'):
                usage = result.usage
            
            # Method 3: Usage in raw_responses (THIS IS WHERE IT IS!)
            if hasattr(result, 'raw_responses') and result.raw_responses:
                for response in result.raw_responses:
                    if hasattr(response, 'usage') and response.usage:
                        usage = response.usage
                        break
                    elif isinstance(response, dict) and 'usage' in response:
                        usage = response['usage']
                        break
            
            # Method 4: Usage in messages (for streaming results)
            elif hasattr(result, 'messages') and result.messages:
                for message in result.messages:
                    if hasattr(message, 'usage') and message.usage:
                        usage = message.usage
                        break
            
            # Method 5: Check if result itself has token attributes
            elif hasattr(result, 'prompt_tokens'):
                usage_data = {
                    'prompt_tokens': getattr(result, 'prompt_tokens', None),
                    'completion_tokens': getattr(result, 'completion_tokens', None),
                    'total_tokens': getattr(result, 'total_tokens', None)
                }
                return usage_data
            
            # If we found a usage object, extract tokens from it
            if usage:
                # Try as attributes first
                if hasattr(usage, 'prompt_tokens'):
                    usage_data = {
                        'prompt_tokens': getattr(usage, 'prompt_tokens', None),
                        'completion_tokens': getattr(usage, 'completion_tokens', None),
                        'total_tokens': getattr(usage, 'total_tokens', None)
                    }
                # Try as dictionary keys
                elif isinstance(usage, dict):
                    usage_data = {
                        'prompt_tokens': usage.get('prompt_tokens'),
                        'completion_tokens': usage.get('completion_tokens'),
                        'total_tokens': usage.get('total_tokens')
                    }
                # Try different attribute names
                elif hasattr(usage, 'input_tokens'):
                    usage_data = {
                        'prompt_tokens': getattr(usage, 'input_tokens', None),
                        'completion_tokens': getattr(usage, 'output_tokens', None),
                        'total_tokens': getattr(usage, 'total_tokens', None)
                    }
                    # Calculate total if not provided
                    if not usage_data['total_tokens'] and usage_data['prompt_tokens'] and usage_data['completion_tokens']:
                        usage_data['total_tokens'] = usage_data['prompt_tokens'] + usage_data['completion_tokens']
            
        except Exception as e:
            logger.error(f"⚠️ Error getting usage from result: {e}")
        
        return usage_data
    
    def _calculate_costs(self, agent, usage_info):
        """Calculate costs for RobutlerAgent instances."""
        cost_info = {
            'call_credits': 0,
            'token_credits': 0,
            'total_credits': 0
        }
        
        try:
            pricing_info = agent.get_pricing_info()
            
            if pricing_info.get('has_pricing'):
                # Call-based cost
                if pricing_info.get('credits_per_call'):
                    cost_info['call_credits'] = pricing_info['credits_per_call']
                
                # Token-based cost
                if pricing_info.get('credits_per_token') and usage_info.get('total_tokens'):
                    cost_info['token_credits'] = pricing_info['credits_per_token'] * usage_info['total_tokens']
                
                cost_info['total_credits'] = cost_info['call_credits'] + cost_info['token_credits']
        except Exception as e:
            logger.error(f"⚠️ Error calculating costs: {e}")
        
        return cost_info
    
    def _populate_agent_state(self, request, agent_instance, agent_name, messages, stream):
        """Populate unified agent state for both static and dynamic agents."""
        import time
        from datetime import datetime
        from robutler.settings import settings
        from robutler.server.base import RequestState
        
        # Store timing info
        request.state.start_time = time.time()
        
        # Extract payment token from request headers for charging
        payment_token = request.headers.get('x-payment-token') or request.headers.get('X-Payment-Token')
        if payment_token:
            request.state.payment_token = payment_token
        
        # Extract origin identity from request headers
        origin_identity = request.headers.get('x-origin-identity') or request.headers.get('X-Origin-Identity')
        if origin_identity:
            request.state.origin_identity = origin_identity
        
        # Extract peer identity from request headers
        peer_identity = request.headers.get('x-peer-identity') or request.headers.get('X-Peer-Identity')
        if peer_identity:
            request.state.peer_identity = peer_identity
        
        # Determine agent type and get appropriate API key
        agent_type = getattr(agent_instance, '_agent_type', 'static')
        
        # Get API key - prefer agent's own API key, fallback to settings
        api_key = settings.api_key  # Default fallback
        if hasattr(agent_instance, 'api_key') and agent_instance.api_key:
            api_key = agent_instance.api_key
        elif hasattr(agent_instance, '_portal_data'):
            portal_data = agent_instance._portal_data
            if portal_data and portal_data.get('api_key'):
                api_key = portal_data['api_key']
        
        # Create agent state data
        agent_state = {
            'name': agent_name,
            'instance': agent_instance,
            'messages': messages,
            'is_streaming': stream,
            'type': agent_type,
            'method': request.method,
            'path': request.url.path,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'api_key': api_key  # Use agent-specific API key for charging
        }
        
        # Add portal data for dynamic agents
        if agent_type == 'dynamic' and hasattr(agent_instance, '_portal_data'):
            agent_state['portal_data'] = agent_instance._portal_data
            # Extract agent owner info for easier access
            portal_data = agent_instance._portal_data
            if portal_data:
                agent_state['agent_owner_user_id'] = portal_data.get('userId', portal_data.get('ownerId', 'unknown'))
        else:
            # For static agents, owner is typically the system/service
            agent_state['agent_owner_user_id'] = 'system'
        
        # Agent pricing info (all agents are RobutlerAgents)
        if hasattr(agent_instance, 'get_pricing_info'):
            agent_state['pricing_info'] = agent_instance.get_pricing_info()
        
        # Store agent state using BOTH methods for backward compatibility and consistency
        request.state.agent_state = agent_state  # Direct assignment (existing code compatibility)
        
        # Also store through RequestState for consistent context.get() access
        context = RequestState(request)
        context.set('agent_state', agent_state)
        context.set('agent_name', agent_name)
        context.set('agent_instance', agent_instance)
        context.set('agent_api_key', api_key)
        context.set('agent_type', agent_type)
    
    def _create_agent_endpoints(self, agents: List):
        """Create endpoints for registered agents."""
        for agent in agents:
            agent_name = getattr(agent, 'name', str(agent))
            
            # Create agent-specific endpoints using base class functionality
            @self.agent(agent_name)
            async def agent_handler(messages, stream=False, current_agent=agent, current_agent_name=agent_name):
                # Store agent state for usage tracking
                request = _current_request.get()
                if request:
                    self._populate_agent_state(request, current_agent, current_agent_name, messages, stream)
                
                # Check if this is an OpenAI Agent
                try:
                    from agents import Agent
                    if isinstance(current_agent, Agent):
                        # This is an OpenAI Agent - use Runner to execute it
                        from agents import Runner
                        
                        if stream:
                            # For streaming, use run_streamed (returns RunResultStreaming)
                            result = Runner.run_streamed(current_agent, messages)
                            # Store the result for finalize callback access
                            if request:
                                request.state.streaming_result = result
                            return result
                        else:
                            # For non-streaming, use run
                            result = await Runner.run(current_agent, messages)
                            # Store the result for finalize callback access
                            if request:
                                request.state.agent_result = result
                            return result.final_output
                except ImportError:
                    # OpenAI agents library not available, fall through to other checks
                    pass
                
                # Check for RobutlerAgent or similar with run method
                if hasattr(current_agent, 'run'):
                    if stream:
                        return await current_agent.run_streamed(messages)
                    else:
                        result = await current_agent.run(messages)
                        return getattr(result, 'final_output', str(result))
                
                # Fallback for other agent types
                else:
                    # Return OpenAI-compatible response for agents without run methods
                    from datetime import datetime
                    import uuid
                    
                    response_content = f"Agent {current_agent_name} processed: {messages[-1]['content'] if messages else 'no messages'}"
                    
                    return {
                        "id": f"chatcmpl-{str(uuid.uuid4())[:8]}",
                        "object": "chat.completion", 
                        "created": int(datetime.utcnow().timestamp()),
                        "model": getattr(current_agent, 'model', 'gpt-4'),
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response_content
                            },
                            "finish_reason": "stop"
                        }]
                    } 