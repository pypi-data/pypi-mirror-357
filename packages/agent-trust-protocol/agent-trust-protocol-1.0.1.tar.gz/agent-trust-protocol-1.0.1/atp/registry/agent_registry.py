"""
Agent Registry - Central registry for agent discovery and capability negotiation.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from ..types import (
    IAgentCard,
    ICapabilityQuery,
    ICapabilityResult,
    TrustLevel,
)


@dataclass
class AgentRegistry:
    """
    Central registry for agent discovery and capability negotiation.
    Implements singleton pattern for global access.
    """

    _agents: Dict[str, IAgentCard] = field(default_factory=dict)
    _capability_index: Dict[str, List[str]] = field(default_factory=dict)
    _name_index: Dict[str, str] = field(default_factory=dict)

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
        return cls._instance

    def register_agent(self, agent_card: IAgentCard) -> None:
        """Register an agent with the discovery system."""
        self._agents[agent_card.agent_id] = agent_card
        self._name_index[agent_card.name] = agent_card.agent_id

        # Index by capabilities
        for capability in agent_card.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            self._capability_index[capability].append(agent_card.agent_id)

        print(f"✅ Agent {agent_card.agent_id} registered with trust score {agent_card.trust_score}")
        print(
            f"✅ Agent {agent_card.agent_id} registered with capabilities: {', '.join(agent_card.capabilities)}"
        )

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the discovery system."""
        if agent_id in self._agents:
            agent_card = self._agents[agent_id]

            # Remove from capability index
            for capability in agent_card.capabilities:
                if capability in self._capability_index:
                    self._capability_index[capability] = [
                        aid for aid in self._capability_index[capability] if aid != agent_id
                    ]
                    if not self._capability_index[capability]:
                        del self._capability_index[capability]

            # Remove from name index
            if agent_card.name in self._name_index:
                del self._name_index[agent_card.name]

            # Remove from agents
            del self._agents[agent_id]

            print(f"🗑️  Agent {agent_id} unregistered from discovery system")

    def discover_agents_by_capability(self, capability: str) -> List[IAgentCard]:
        """Discover agents that have a specific capability."""
        agent_ids = self._capability_index.get(capability, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def discover_agents_by_name(self, name_pattern: str) -> List[IAgentCard]:
        """Discover agents by name pattern matching."""
        matching_agents = []
        name_lower = name_pattern.lower()

        for agent_card in self._agents.values():
            if name_lower in agent_card.name.lower():
                matching_agents.append(agent_card)

        return matching_agents

    def get_agent(self, agent_id: str) -> Optional[IAgentCard]:
        """Get agent information by ID."""
        return self._agents.get(agent_id)

    def get_agent_by_name(self, name: str) -> Optional[IAgentCard]:
        """Get agent information by name."""
        agent_id = self._name_index.get(name)
        return self._agents.get(agent_id) if agent_id else None

    def negotiate_capabilities(self, query: ICapabilityQuery) -> ICapabilityResult:
        """Negotiate capabilities with a specific agent."""
        agent_card = self._agents.get(query.agent_id)

        if not agent_card:
            return ICapabilityResult(
                can_handle=False,
                trust_score=0,
                supported_capabilities=[],
                missing_capabilities=query.required_capabilities,
                interaction_modalities=[],
            )

        # Check trust level
        if agent_card.trust_level.value < query.trust_level.value:
            return ICapabilityResult(
                can_handle=False,
                trust_score=agent_card.trust_score,
                supported_capabilities=[],
                missing_capabilities=query.required_capabilities,
                interaction_modalities=[],
            )

        # Check capabilities
        supported = []
        missing = []

        for capability in query.required_capabilities:
            if capability in agent_card.capabilities:
                supported.append(capability)
            else:
                missing.append(capability)

        can_handle = len(missing) == 0

        return ICapabilityResult(
            can_handle=can_handle,
            trust_score=agent_card.trust_score,
            supported_capabilities=supported,
            missing_capabilities=missing,
            interaction_modalities=agent_card.interaction_modalities,
        )

    def get_best_agent_for_task(
        self,
        required_capabilities: List[str],
        min_trust_level: TrustLevel,
        interaction_type: Optional[Dict[str, Any]] = None,
    ) -> Optional[IAgentCard]:
        """Find the best agent for a specific task."""
        candidates = []

        for agent_card in self._agents.values():
            # Check trust level
            if agent_card.trust_level.value < min_trust_level.value:
                continue

            # Check capabilities
            has_all_capabilities = all(
                capability in agent_card.capabilities for capability in required_capabilities
            )

            if has_all_capabilities:
                candidates.append(agent_card)

        if not candidates:
            return None

        # Sort by trust score (highest first)
        candidates.sort(key=lambda x: x.trust_score, reverse=True)

        return candidates[0]

    def get_all_agents(self) -> List[IAgentCard]:
        """Get all registered agents."""
        return list(self._agents.values())

    def get_agent_count(self) -> int:
        """Get the total number of registered agents."""
        return len(self._agents)

    def get_capability_count(self) -> int:
        """Get the total number of unique capabilities."""
        return len(self._capability_index)

    def clear(self) -> None:
        """Clear all registered agents."""
        self._agents.clear()
        self._capability_index.clear()
        self._name_index.clear()
        print("🧹 Agent registry cleared")

    def __str__(self) -> str:
        """String representation of the registry."""
        return (
            f"AgentRegistry(agents={len(self._agents)}, capabilities={len(self._capability_index)})"
        )

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"AgentRegistry(agents={list(self._agents.keys())}, capabilities={list(self._capability_index.keys())})"


# Global instance
registry = AgentRegistry()
