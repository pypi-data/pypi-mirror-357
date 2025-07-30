from .base_transport import BaseTransport
from ..core.atp_envelope import ATPEnvelope
from typing import Any, Callable, Dict

class KafkaTransport(BaseTransport):
    """
    Simulated Kafka Transport for ATP. Stores agent handlers and simulates message delivery.
    TODO: Integrate with a real Kafka broker for production use.
    """
    def __init__(self, endpoint: str, options: dict = None):
        self.endpoint = endpoint
        self.options = options or {}
        self.message_history = []
        self.connected_agents: Dict[str, Callable[[ATPEnvelope], None]] = {}

    def register_agent(self, agent_id: str, handler: Callable[[ATPEnvelope], None]) -> None:
        """Register an agent and its message handler."""
        self.connected_agents[agent_id] = handler

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        self.connected_agents.pop(agent_id, None)

    def send_message(self, from_agent: str, to_agent: str, envelope: ATPEnvelope) -> None:
        """Simulate sending a message to a specific agent via Kafka."""
        self.message_history.append((from_agent, to_agent, envelope))
        print(f"[Kafka] Message sent from {from_agent} to {to_agent} via Kafka endpoint {self.endpoint}")
        handler = self.connected_agents.get(to_agent)
        if handler:
            try:
                handler(envelope)
            except Exception as e:
                print(f"[Kafka] Error delivering message to {to_agent}: {e}")
        else:
            print(f"[Kafka] No handler registered for agent {to_agent}")

    def broadcast(self, from_agent: str, envelope: ATPEnvelope) -> None:
        """Simulate broadcasting a message to all agents except the sender."""
        for agent_id, handler in self.connected_agents.items():
            if agent_id != from_agent:
                self.send_message(from_agent, agent_id, envelope)

    def get_message_history(self) -> list:
        return self.message_history

    def get_connected_agents(self) -> list:
        return list(self.connected_agents.keys()) 