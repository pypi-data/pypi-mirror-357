"""
Type definitions for Agent Trust Protocol (ATP).

This module contains all the type definitions, enums, and interfaces
used throughout the ATP implementation.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Forward reference for ATPEnvelope to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core.atp_envelope import ATPEnvelope


class TrustLevel(str, Enum):
    """Trust levels for agents."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    CERTIFIED = "certified"
    SANDBOXED = "sandboxed"


class DataSensitivity(str, Enum):
    """Data sensitivity levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class MessageType(str, Enum):
    """Message types for ATP communication."""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"


class TransportType(str, Enum):
    """Transport layer types."""

    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    KAFKA = "kafka"
    IN_MEMORY = "in-memory"


class MediaType(str, Enum):
    """Media types for rich content support."""

    TEXT = "text"
    JSON = "json"
    FILE = "file"
    FORM = "form"
    STREAM = "stream"


@dataclass
class IAttestation:
    """Agent attestation information."""

    issuer: str
    level: TrustLevel
    issued_at: Optional[str] = None
    expires_at: Optional[str] = None


@dataclass
class IAgentIdentity:
    """Agent identity information."""

    id: str
    public_key: str
    attestation: IAttestation
    capabilities: Optional[List[str]] = None


@dataclass
class IPolicyContext:
    """Policy context for ATP envelopes."""

    allowed_tools: Optional[List[str]] = None
    data_sensitivity: Optional[DataSensitivity] = None
    spawn_permission: Optional[bool] = None
    max_lifespan_seconds: Optional[int] = None


@dataclass
class IProvenanceEntry:
    """Provenance entry for audit trail."""

    type: str  # 'agent', 'task', 'decision', 'service'
    id: str
    timestamp: str
    action: str


@dataclass
class IATPConfig:
    """Configuration for ATP envelope creation."""

    agent_identity: IAgentIdentity
    trust_level: TrustLevel
    policy_context: Optional[IPolicyContext] = None
    payload: Optional[Dict[str, Any]] = None
    private_key: Optional[str] = None


@dataclass
class IValidationResult:
    """Result of envelope validation."""

    valid: bool
    trust_score: int
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class IATPResponse:
    """Response from ATP request."""

    success: bool
    trust_score: int
    data: Optional[Any] = None
    error: Optional[str] = None
    envelope: Optional["ATPEnvelope"] = None


@dataclass
class ITransportConfig:
    """Configuration for transport layer."""

    type: TransportType
    endpoint: str
    options: Optional[Dict[str, Any]] = None


@dataclass
class ITransportMessage:
    """Message in transport layer."""

    from_agent: str
    to_agent: str
    envelope: "ATPEnvelope"
    timestamp: str


# Advanced feature types
@dataclass
class IAgentCard:
    """Agent information for discovery and registry."""

    agent_id: str
    name: str
    description: str
    capabilities: List[str]
    trust_level: TrustLevel
    trust_score: int
    interaction_modalities: List["IInteractionModality"]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class IInteractionModality:
    """Supported interaction modality for an agent."""

    type: MediaType
    description: str
    max_size: Optional[int] = None  # in bytes
    supported_formats: Optional[List[str]] = None


@dataclass
class ICapabilityQuery:
    """Query for capability negotiation."""

    agent_id: str
    required_capabilities: List[str]
    trust_level: TrustLevel
    interaction_type: Optional[Dict[str, Any]] = None


@dataclass
class ICapabilityResult:
    """Result of capability negotiation."""

    can_handle: bool
    trust_score: int
    supported_capabilities: List[str]
    missing_capabilities: List[str]
    interaction_modalities: List[IInteractionModality]


@dataclass
class IMediaPayload:
    """Rich media payload for file, form, and stream content."""

    type: MediaType
    content: Any
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class IFileMetadata:
    """Metadata for file uploads."""

    filename: str
    mime_type: str
    size: int
    checksum: str
    encoding: str = "binary"


@dataclass
class IFormField:
    """Form field definition."""

    name: str
    value: Any
    validation: Optional[Dict[str, Any]] = None


@dataclass
class IFormValidation:
    """Form validation rules."""

    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    enum: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None


# Type aliases for backward compatibility
AgentIdentity = IAgentIdentity
Attestation = IAttestation
PolicyContext = IPolicyContext
ProvenanceEntry = IProvenanceEntry
ATPConfig = IATPConfig
ValidationResult = IValidationResult
ATPResponse = IATPResponse
TransportConfig = ITransportConfig
TransportMessage = ITransportMessage
AgentCard = IAgentCard
InteractionModality = IInteractionModality
CapabilityQuery = ICapabilityQuery
CapabilityResult = ICapabilityResult
MediaPayload = IMediaPayload
FileMetadata = IFileMetadata
FormField = IFormField
FormValidation = IFormValidation
