"""
Agent Trust Protocol (ATP) - Python Implementation

A comprehensive security and provenance framework for secure, trustworthy
communication between autonomous AI agents with cryptographic identity
verification, hierarchical trust management, and asynchronous communication.
"""

__version__ = "1.0.0"
__author__ = "Agent Trust Protocol Team"
__email__ = "team@agent-trust-protocol.org"

# Core ATP components
from .core.atp_envelope import ATPEnvelope, create_envelope
from .protocol.atp_client import ATPClient
from .registry.agent_registry import AgentRegistry
from .transport.in_memory_transport import InMemoryTransport

# Type definitions
from .types import (
    IAgentIdentity,
    IAttestation,
    TrustLevel,
    MessageType,
    MediaType,
    IInteractionModality,
    IPolicyContext,
    DataSensitivity,
    IATPConfig,
    TransportType,
    ITransportConfig,
)


# Convenience functions
def create_agent_identity(
    agent_id: str,
    public_key: str,
    attestation_issuer: str,
    trust_level: TrustLevel,
    capabilities: list[str],
) -> IAgentIdentity:
    """Create a new agent identity with the specified parameters."""
    from datetime import datetime, timezone

    return IAgentIdentity(
        id=agent_id,
        public_key=public_key,
        attestation=IAttestation(
            issuer=attestation_issuer,
            level=trust_level,
            issued_at=datetime.now(timezone.utc).isoformat(),
            expires_at=datetime.now(timezone.utc).replace(year=datetime.now().year + 1).isoformat(),
        ),
        capabilities=capabilities,
    )


# Export main classes and types
__all__ = [
    "ATPEnvelope",
    "create_envelope",
    "ATPClient",
    "AgentRegistry",
    "InMemoryTransport",
    "IAgentIdentity",
    "IAttestation",
    "TrustLevel",
    "MessageType",
    "MediaType",
    "IInteractionModality",
    "IPolicyContext",
    "DataSensitivity",
    "IATPConfig",
    "TransportType",
    "ITransportConfig",
    "create_agent_identity",
]
