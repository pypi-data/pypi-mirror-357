"""
ATP Client - Main client for Agent Trust Protocol communication.

This module provides the ATPClient class which handles all agent communication
including requests, responses, notifications, and broadcast messaging.
"""

import asyncio
import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from ..types import (
    IAgentIdentity,
    TrustLevel,
    MessageType,
    MediaType,
    IAgentCard,
    ICapabilityQuery,
    ICapabilityResult,
    IMediaPayload,
    IFileMetadata,
    IInteractionModality,
    IATPConfig,
    IATPResponse,
    ITransportConfig,
)
from ..core.atp_envelope import ATPEnvelope, create_envelope
from ..transport.in_memory_transport import InMemoryTransport
from ..registry.agent_registry import registry


@dataclass
class ATPClient:
    """
    ATP Client - Primary interface for agents to communicate using the ATP protocol.
    """

    # Agent identity and configuration
    identity: IAgentIdentity
    trust_level: TrustLevel
    private_key: Optional[str] = None

    # Transport layer
    transport: InMemoryTransport = field(default_factory=InMemoryTransport.get_instance)

    # Message handling
    message_handlers: Dict[MessageType, List[Callable]] = field(default_factory=dict)

    # Connection state
    connected: bool = False
    message_queue: Optional[asyncio.Queue] = None

    # Request tracking
    pending_requests: Dict[str, asyncio.Future] = field(default_factory=dict)

    # Configuration
    default_timeout: int = 30000  # milliseconds
    debug: bool = False

    # Agent card for discovery
    agent_card: Optional[IAgentCard] = None

    def __post_init__(self):
        """Initialize the client."""
        # Create message queue
        self.message_queue = asyncio.Queue()

        # Initialize message handlers
        for message_type in MessageType:
            self.message_handlers[message_type] = []

        # Create default interaction modalities
        default_modalities = [
            IInteractionModality(
                type=MediaType.TEXT,
                description="Plain text content",
                max_size=100 * 1024 * 1024,  # 100MB
            ),
            IInteractionModality(
                type=MediaType.JSON,
                description="JSON structured data",
                max_size=100 * 1024 * 1024,  # 100MB
            ),
            IInteractionModality(
                type=MediaType.FILE,
                description="File upload and download",
                max_size=100 * 1024 * 1024,  # 100MB
                supported_formats=[
                    "text/plain",
                    "text/json",
                    "application/json",
                    "image/jpeg",
                    "image/png",
                    "image/gif",
                    "application/pdf",
                    "text/csv",
                    "application/xml",
                ],
            ),
            IInteractionModality(
                type=MediaType.FORM, description="Structured form data", max_size=1024 * 1024  # 1MB
            ),
            IInteractionModality(
                type=MediaType.STREAM,
                description="Real-time data streaming",
                max_size=100 * 1024 * 1024,  # 100MB
            ),
        ]

        # Create agent card
        self.agent_card = IAgentCard(
            agent_id=self.identity.id,
            name=f"{self.identity.id.replace('-', ' ').title()}",
            description=f"ATP agent with {self.trust_level.value} trust level",
            capabilities=self.identity.capabilities or [],
            trust_level=self.trust_level,
            trust_score=0,  # Will be calculated when envelope is created
            interaction_modalities=default_modalities,
        )

    async def connect(self) -> None:
        """Connect to the transport layer."""
        if self.connected:
            print("⚠️  Client already connected")
            return

        # Register with transport layer
        self.transport.register_agent(self.identity.id, self.message_queue)

        # Start message processing
        asyncio.create_task(self._process_messages())

        self.connected = True
        print(f"✅ Agent {self.identity.id} connected to ATP network")

    async def disconnect(self) -> None:
        """Disconnect from the transport layer."""
        if not self.connected:
            print("⚠️  Client not connected")
            return

        # Unregister from transport layer
        self.transport.unregister_agent(self.identity.id)

        # Unregister from discovery system
        if self.agent_card:
            registry.unregister_agent(self.identity.id)

        # Cancel pending requests
        for request_id, future in self.pending_requests.items():
            if not future.done():
                future.cancel()

        self.connected = False
        print(f"🔌 Agent {self.identity.id} disconnected from ATP network")

    def register_with_discovery(self, name: str, description: str, capabilities: List[str]) -> None:
        """Register this agent with the discovery system."""
        if not self.agent_card:
            return

        # Update agent card
        self.agent_card.name = name
        self.agent_card.description = description
        self.agent_card.capabilities = capabilities

        # Calculate trust score
        config = IATPConfig(
            agent_identity=self.identity,
            trust_level=self.trust_level,
            payload={"test": "trust_score"},
            private_key=self.private_key,
        )
        envelope = create_envelope(config)
        self.agent_card.trust_score = envelope.get_trust_score()

        # Register with discovery system
        registry.register_agent(self.agent_card)

    async def discover_agents_by_capability(self, capability: str) -> List[IAgentCard]:
        """Discover agents with a specific capability."""
        return registry.discover_agents_by_capability(capability)

    async def discover_agents_by_name(self, name_pattern: str) -> List[IAgentCard]:
        """Discover agents by name pattern."""
        return registry.discover_agents_by_name(name_pattern)

    async def negotiate_capabilities(
        self, target_agent: str, required_capabilities: List[str], min_trust_level: TrustLevel
    ) -> ICapabilityResult:
        """Negotiate capabilities with another agent."""
        query = ICapabilityQuery(
            agent_id=target_agent,
            required_capabilities=required_capabilities,
            trust_level=min_trust_level,
        )
        return registry.negotiate_capabilities(query)

    async def get_best_agent_for_task(
        self, required_capabilities: List[str], min_trust_level: TrustLevel
    ) -> Optional[IAgentCard]:
        """Find the best agent for a specific task."""
        return registry.get_best_agent_for_task(required_capabilities, min_trust_level)

    async def get_trust_score(self, agent_id: str) -> int:
        """Get the trust score of another agent."""
        agent_card = registry.get_agent(agent_id)
        return agent_card.trust_score if agent_card else 0

    async def validate_agent_trust(self, agent_id: str, min_trust_score: int) -> bool:
        """Validate if an agent meets minimum trust requirements."""
        trust_score = await self.get_trust_score(agent_id)
        return trust_score >= min_trust_score

    def get_supported_modalities(self) -> List[IInteractionModality]:
        """Get the supported interaction modalities for this agent."""
        return self.agent_card.interaction_modalities if self.agent_card else []

    async def send_request(
        self, target_agent: str, payload: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> IATPResponse:
        """Send an asynchronous request to another agent."""
        if not self.connected:
            raise ConnectionError("Client not connected")

        options = options or {}
        timeout = options.get("timeout", self.default_timeout)
        requires_trust = options.get("requires_trust")

        # Generate request ID
        request_id = f"req_{int(datetime.now().timestamp() * 1000)}_{str(uuid.uuid4())[:8]}"

        # Create request payload
        request_payload = {
            "messageType": "request",
            "targetAgent": target_agent,
            "data": payload,
            "requestId": request_id,
            "requiresResponse": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Create envelope
        config = IATPConfig(
            agent_identity=self.identity,
            trust_level=self.trust_level,
            payload=request_payload,
            private_key=self.private_key,
        )
        envelope = create_envelope(config)

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future

        try:
            # Send request
            await self.transport.send_message(self.identity.id, target_agent, envelope)

            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout / 1000.0)

            # Validate trust requirements
            if requires_trust and response.envelope:
                required_trust = TrustLevel(requires_trust)
                if response.envelope.trust_level.value < required_trust.value:
                    raise ValueError(
                        f"Insufficient trust level. Required: {required_trust.value}, Got: {response.envelope.trust_level.value}"
                    )

            return response

        except asyncio.TimeoutError:
            # Remove from pending requests
            self.pending_requests.pop(request_id, None)
            raise TimeoutError(f"Request to {target_agent} timed out after {timeout}ms")

        except Exception as e:
            # Remove from pending requests
            self.pending_requests.pop(request_id, None)
            raise e

    async def send_file_request(
        self,
        target_agent: str,
        filename: str,
        content: bytes,
        mime_type: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> IATPResponse:
        """Send a file request to another agent."""
        # Calculate checksum
        checksum = hashlib.sha256(content).hexdigest()

        # Create file metadata
        file_metadata = IFileMetadata(
            filename=filename, mime_type=mime_type, size=len(content), checksum=checksum
        )

        # Create media payload
        media_payload = IMediaPayload(
            type=MediaType.FILE, content=content, metadata=file_metadata.__dict__
        )

        # Create request payload
        payload = {"mediaPayload": media_payload.__dict__}

        return await self.send_request(target_agent, payload, options)

    async def send_form_request(
        self,
        target_agent: str,
        fields: Dict[str, Any],
        validation: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> IATPResponse:
        """Send a form request to another agent."""
        # Create form content
        form_content = {
            "fields": fields,
            "validation": validation or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Create media payload
        media_payload = IMediaPayload(type=MediaType.FORM, content=form_content)

        # Create request payload
        payload = {"mediaPayload": media_payload.__dict__}

        return await self.send_request(target_agent, payload, options)

    async def send_notification(self, target_agent: str, payload: Dict[str, Any]) -> None:
        """Send a notification (fire-and-forget message)."""
        if not self.connected:
            raise ConnectionError("Client not connected")

        # Create notification payload
        notification_payload = {"type": "notification", "data": payload}

        # Create envelope
        config = IATPConfig(
            agent_identity=self.identity,
            trust_level=self.trust_level,
            payload=notification_payload,
            private_key=self.private_key,
        )
        envelope = create_envelope(config)

        # Send notification
        await self.transport.send_message(self.identity.id, target_agent, envelope)

    async def broadcast(self, payload: Dict[str, Any]) -> None:
        """Broadcast a message to all connected agents."""
        if not self.connected:
            raise ConnectionError("Client not connected")

        # Create broadcast payload
        broadcast_payload = {"type": "broadcast", "data": payload}

        # Create envelope
        config = IATPConfig(
            agent_identity=self.identity,
            trust_level=self.trust_level,
            payload=broadcast_payload,
            private_key=self.private_key,
        )
        envelope = create_envelope(config)

        # Send broadcast
        await self.transport.broadcast_message(self.identity.id, envelope)

    def on_message(self, message_type: MessageType, handler: Callable) -> None:
        """Register a message handler for incoming messages."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []

        self.message_handlers[message_type].append(handler)

    async def _process_messages(self) -> None:
        """Process incoming messages."""
        while self.connected:
            try:
                # Get message from queue
                transport_message = await self.message_queue.get()
                envelope = transport_message.envelope

                if self.debug:
                    print(
                        f"📨 Received message from {transport_message.from_agent}: {envelope.payload.get('type', envelope.payload.get('messageType', 'unknown'))}"
                    )

                # Determine message type - check both 'type' and 'messageType' fields
                message_type_str = envelope.payload.get("type") or envelope.payload.get(
                    "messageType", "notification"
                )
                message_type = MessageType(message_type_str)

                # Handle request messages
                if message_type == MessageType.REQUEST:
                    await self._handle_request(envelope, transport_message.from_agent)

                # Handle response messages
                elif message_type == MessageType.RESPONSE:
                    await self._handle_response(envelope)

                # Handle other message types
                else:
                    await self._handle_message(message_type, envelope)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error processing message: {e}")

    async def _handle_request(self, envelope: ATPEnvelope, from_agent: str) -> None:
        """Handle incoming request messages."""
        request_id = envelope.payload.get("requestId")

        # Find request handler
        handlers = self.message_handlers.get(MessageType.REQUEST, [])

        if handlers:
            # Call the first handler (could be extended to support multiple handlers)
            handler = handlers[0]

            try:
                # Create response function
                async def respond(response_data: Any) -> None:
                    # Create response payload
                    response_payload = {
                        "requestId": request_id,
                        "type": "response",
                        "data": response_data,
                    }

                    # Create response envelope
                    config = IATPConfig(
                        agent_identity=self.identity,
                        trust_level=self.trust_level,
                        payload=response_payload,
                        private_key=self.private_key,
                    )
                    response_envelope = create_envelope(config)

                    # Send response
                    await self.transport.send_message(
                        self.identity.id, from_agent, response_envelope
                    )

                # Call handler
                if asyncio.iscoroutinefunction(handler):
                    await handler(envelope, respond)
                else:
                    handler(envelope, respond)

            except Exception as e:
                print(f"❌ Error in request handler: {e}")
                # Send error response
                await respond({"error": str(e)})
        else:
            print(f"⚠️  No request handler registered for message from {from_agent}")

    async def _handle_response(self, envelope: ATPEnvelope) -> None:
        """Handle incoming response messages."""
        request_id = envelope.payload.get("requestId")

        if request_id in self.pending_requests:
            future = self.pending_requests[request_id]

            # Create response object
            response = IATPResponse(
                success=True,
                data=envelope.payload.get("data"),
                trust_score=envelope.get_trust_score(),
                envelope=envelope,
            )

            # Resolve future
            if not future.done():
                future.set_result(response)

            # Remove from pending requests
            del self.pending_requests[request_id]
        else:
            print(f"⚠️  Received response for unknown request: {request_id}")

    async def _handle_message(self, message_type: MessageType, envelope: ATPEnvelope) -> None:
        """Handle other message types (notifications, broadcasts)."""
        handlers = self.message_handlers.get(message_type, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(envelope)
                else:
                    handler(envelope)
            except Exception as e:
                print(f"❌ Error in {message_type.value} handler: {e}")

    def get_trust_status(self) -> Dict[str, Any]:
        """Get the current trust status of the agent."""
        # Create a test envelope to calculate trust score
        config = IATPConfig(
            agent_identity=self.identity,
            trust_level=self.trust_level,
            payload={"test": "status"},
            private_key=self.private_key,
        )
        envelope = create_envelope(config)

        return {
            "level": self.trust_level.value,
            "score": envelope.get_trust_score(),
            "verified": envelope.verify_signature() if self.private_key else False,
            "connected": self.connected,
        }

    def add_transport(self, name: str, config: ITransportConfig) -> None:
        """Add a transport layer (placeholder for future implementations)."""
        print(f"🔧 Transport {name} configured: {config.type.value} -> {config.endpoint}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    def __str__(self) -> str:
        """String representation of the client."""
        return f"ATPClient(agent={self.identity.id}, trust={self.trust_level.value}, connected={self.connected})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ATPClient(identity={self.identity}, trust_level={self.trust_level}, connected={self.connected})"
