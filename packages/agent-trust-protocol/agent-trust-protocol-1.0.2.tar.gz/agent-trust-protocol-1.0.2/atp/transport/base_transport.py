from abc import ABC, abstractmethod
from typing import Any, Dict
from ..core.atp_envelope import ATPEnvelope

class BaseTransport(ABC):
    """Abstract base class for ATP transport layers."""

    @abstractmethod
    def register_agent(self, agent_id: str, handler: Any) -> None:
        pass

    @abstractmethod
    def unregister_agent(self, agent_id: str) -> None:
        pass

    @abstractmethod
    def send_message(self, from_agent: str, to_agent: str, envelope: ATPEnvelope) -> None:
        pass

    @abstractmethod
    def broadcast(self, from_agent: str, envelope: ATPEnvelope) -> None:
        pass

    @abstractmethod
    def get_message_history(self) -> list:
        pass

    @abstractmethod
    def get_connected_agents(self) -> list:
        pass 