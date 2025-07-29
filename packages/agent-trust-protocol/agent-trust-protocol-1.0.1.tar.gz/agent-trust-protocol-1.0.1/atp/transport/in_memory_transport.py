"""
In-Memory Transport Layer for Agent Trust Protocol.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..types import ITransportMessage
from ..core.atp_envelope import ATPEnvelope


@dataclass
class InMemoryTransport:
    """
    Singleton in-memory transport layer for agent communication.
    """

    # Singleton instance
    _instance: Optional["InMemoryTransport"] = None

    # Agent registry
    agents: Dict[str, asyncio.Queue] = field(default_factory=dict)

    # Message history
    message_history: List[ITransportMessage] = field(default_factory=list)

    # Network simulation
    latency_range: tuple = field(default=(50, 150))  # milliseconds
    error_rate: float = field(default=0.01)  # 1% error rate

    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "InMemoryTransport":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_agent(self, agent_id: str, message_queue: asyncio.Queue) -> None:
        """Register an agent with the transport layer."""
        self.agents[agent_id] = message_queue
        print(f"🔗 Agent {agent_id} registered with transport layer")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the transport layer."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            print(f"🔌 Agent {agent_id} unregistered from transport layer")

    async def send_message(self, from_agent: str, to_agent: str, envelope: ATPEnvelope) -> None:
        """Send a message to a specific agent."""
        if to_agent not in self.agents:
            raise ValueError(f"Agent {to_agent} not found in transport layer")

        # Simulate network latency
        latency = self._simulate_latency()
        await asyncio.sleep(latency / 1000.0)

        # Simulate network errors
        if self._should_simulate_error():
            raise ConnectionError(f"Network error while sending message to {to_agent}")

        # Create transport message
        transport_message = ITransportMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            envelope=envelope,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Add to message history
        self.message_history.append(transport_message)

        # Send to target agent
        await self.agents[to_agent].put(transport_message)

        print(f"📨 Message sent from {from_agent} to {to_agent} (latency: {latency}ms)")

    async def broadcast(self, from_agent: str, envelope: ATPEnvelope) -> None:
        """Broadcast a message to all registered agents."""
        if not self.agents:
            print("⚠️  No agents registered for broadcast")
            return

        # Simulate network latency
        latency = self._simulate_latency()
        await asyncio.sleep(latency / 1000.0)

        # Create transport message
        transport_message = ITransportMessage(
            from_agent=from_agent,
            to_agent="*",  # Broadcast indicator
            envelope=envelope,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Add to message history
        self.message_history.append(transport_message)

        # Send to all agents except sender
        for agent_id, queue in self.agents.items():
            if agent_id != from_agent:
                await queue.put(transport_message)

        print(
            f"📢 Broadcast sent from {from_agent} to {len(self.agents) - 1} agents (latency: {latency}ms)"
        )

    def get_message_history(self) -> List[ITransportMessage]:
        """Get the complete message history."""
        return self.message_history.copy()

    def get_connected_agents(self) -> List[str]:
        """Get list of currently connected agents."""
        return list(self.agents.keys())

    def _simulate_latency(self) -> int:
        """Simulate realistic network latency."""
        import random

        return random.randint(*self.latency_range)

    def _should_simulate_error(self) -> bool:
        """Determine if we should simulate a network error."""
        import random

        return random.random() < self.error_rate

    def clear_history(self) -> None:
        """Clear message history (useful for testing)."""
        self.message_history.clear()

    def set_latency_range(self, min_ms: int, max_ms: int) -> None:
        """Set the latency range for network simulation."""
        self.latency_range = (min_ms, max_ms)

    def set_error_rate(self, rate: float) -> None:
        """Set the error rate for network simulation."""
        self.error_rate = max(0.0, min(1.0, rate))

    def get_stats(self) -> Dict[str, Any]:
        """Get transport layer statistics."""
        return {
            "connected_agents": len(self.agents),
            "total_messages": len(self.message_history),
            "latency_range": self.latency_range,
            "error_rate": self.error_rate,
            "agent_ids": list(self.agents.keys()),
        }

    async def broadcast_message(self, from_agent: str, envelope: ATPEnvelope) -> None:
        """Broadcast a message to all registered agents (alias for broadcast)."""
        await self.broadcast(from_agent, envelope)


# Convenience function to get transport instance
def get_transport() -> InMemoryTransport:
    """Get the singleton transport instance."""
    return InMemoryTransport.get_instance()
