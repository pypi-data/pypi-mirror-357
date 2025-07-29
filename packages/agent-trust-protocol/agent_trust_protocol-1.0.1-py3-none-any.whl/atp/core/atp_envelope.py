"""
ATP Envelope - Core message container for Agent Trust Protocol.

This module provides the ATPEnvelope class which encapsulates all
message data with cryptographic signing, validation, and provenance tracking.
"""

import json
import uuid
import jwt
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from ..types import (
    IATPConfig,
    IAgentIdentity,
    IAttestation,
    IPolicyContext,
    IProvenanceEntry,
    IValidationResult,
    TrustLevel,
    DataSensitivity,
)


@dataclass
class ATPEnvelope:
    """
    ATP Envelope - Core message container with security and trust metadata.
    """

    # Core envelope properties
    version: str = field(default="1.0.0", init=False)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    agent_identity: IAgentIdentity = field(init=False)
    trust_level: TrustLevel = field(init=False)
    policy_context: Optional[IPolicyContext] = field(default=None, init=False)
    provenance: List[IProvenanceEntry] = field(default_factory=list, init=False)
    timestamp: str = field(init=False)
    payload: Dict[str, Any] = field(default_factory=dict, init=False)
    signature: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize envelope from config."""
        if hasattr(self, "_config"):
            self._initialize_from_config(self._config)

    def _initialize_from_config(self, config: IATPConfig):
        """Initialize envelope from ATP configuration."""
        self.agent_identity = config.agent_identity
        self.trust_level = config.trust_level
        self.policy_context = config.policy_context
        self.payload = config.payload or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

        # Sign the envelope if private key is provided
        if config.private_key:
            self.sign(config.private_key)

    def sign(self, private_key: str) -> None:
        """Sign the envelope with JWT."""
        try:
            # Create signature payload
            signature_payload = {
                "messageId": self.message_id,
                "agentId": self.agent_identity.id,
                "trustLevel": self.trust_level.value,
                "timestamp": self.timestamp,
                "payloadHash": self._calculate_payload_hash(),
            }

            # Sign with JWT (using HS256 for demo, RS256 for production)
            self.signature = jwt.encode(signature_payload, private_key, algorithm="HS256")
        except Exception as e:
            raise ValueError(f"Failed to sign envelope: {e}")

    def verify_signature(self) -> bool:
        """Verify the envelope signature."""
        if not self.signature:
            return False

        try:
            # Decode and verify signature
            decoded = jwt.decode(
                self.signature, self.agent_identity.public_key, algorithms=["HS256"]
            )

            # Verify payload hash
            return decoded.get("payloadHash") == self._calculate_payload_hash()
        except jwt.InvalidTokenError:
            return False

    def _calculate_payload_hash(self) -> str:
        """Calculate hash of payload for integrity checking."""
        # Convert bytes to base64 strings for JSON serialization
        serializable_payload = self._make_payload_serializable(self.payload)
        payload_str = json.dumps(serializable_payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    def _make_payload_serializable(self, obj: Any) -> Any:
        """Convert payload to JSON-serializable format."""
        if isinstance(obj, dict):
            return {key: self._make_payload_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_payload_serializable(item) for item in obj]
        elif isinstance(obj, bytes):
            return {"type": "Buffer", "data": list(obj)}
        else:
            return obj

    def validate(self) -> IValidationResult:
        """Validate the envelope for security and compliance."""
        errors = []
        warnings = []
        trust_score = 0

        # Basic validation
        if not self.agent_identity:
            errors.append("Missing agent identity")

        if not self.timestamp:
            errors.append("Missing timestamp")

        if not self.payload:
            warnings.append("Empty payload")

        # Trust score calculation
        trust_score = self._calculate_trust_score()

        # Signature validation
        if self.signature and not self.verify_signature():
            errors.append("Invalid signature")
            trust_score -= 10

        # Attestation validation
        if self.agent_identity.attestation:
            attestation_errors = self._validate_attestation()
            errors.extend(attestation_errors)

        # Policy validation
        if self.policy_context:
            policy_warnings = self._validate_policy()
            warnings.extend(policy_warnings)

        return IValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            trust_score=max(0, min(100, trust_score)),
        )

    def _calculate_trust_score(self) -> int:
        """Calculate trust score based on various factors."""
        score = 0

        # Identity verification (40 points)
        if self.agent_identity.attestation:
            level_scores = {
                TrustLevel.CERTIFIED: 40,
                TrustLevel.VERIFIED: 30,
                TrustLevel.UNVERIFIED: 20,
                TrustLevel.SANDBOXED: 10,
            }
            score += level_scores.get(self.agent_identity.attestation.level, 0)

        # Credential freshness (20 points)
        if self.agent_identity.attestation.expires_at:
            try:
                expiry = datetime.fromisoformat(
                    self.agent_identity.attestation.expires_at.replace("Z", "+00:00")
                )
                now = datetime.now(timezone.utc)
                days_until_expiry = (expiry - now).days

                if days_until_expiry > 365:
                    score += 20
                elif days_until_expiry > 180:
                    score += 15
                elif days_until_expiry > 30:
                    score += 10
                elif days_until_expiry > 0:
                    score += 5
            except (ValueError, TypeError):
                pass

        # Capability alignment (15 points)
        if self.agent_identity.capabilities:
            score += min(15, len(self.agent_identity.capabilities) * 3)

        # Policy compliance (15 points)
        if self.policy_context:
            score += 15

        # Cryptographic security (10 points)
        if self.signature and self.verify_signature():
            score += 10

        return score

    def _validate_attestation(self) -> List[str]:
        """Validate agent attestation."""
        errors = []
        attestation = self.agent_identity.attestation

        if attestation.expires_at:
            try:
                expiry = datetime.fromisoformat(attestation.expires_at.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > expiry:
                    errors.append("Attestation has expired")
            except (ValueError, TypeError):
                errors.append("Invalid attestation expiry date")

        return errors

    def _validate_policy(self) -> List[str]:
        """Validate policy context."""
        warnings = []

        if self.policy_context:
            if self.policy_context.max_lifespan_seconds:
                # Check if envelope is within lifespan
                try:
                    created = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    age_seconds = (now - created).total_seconds()

                    if age_seconds > self.policy_context.max_lifespan_seconds:
                        warnings.append("Envelope exceeds maximum lifespan")
                except (ValueError, TypeError):
                    warnings.append("Invalid timestamp format")

        return warnings

    def add_provenance(self, entry: Dict[str, str]) -> None:
        """Add a provenance entry to the audit trail."""
        provenance_entry = IProvenanceEntry(
            type=entry["type"],
            id=entry["id"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=entry["action"],
        )
        self.provenance.append(provenance_entry)

    def meets_trust_threshold(self, threshold: int) -> bool:
        """Check if envelope meets minimum trust threshold."""
        return self.get_trust_score() >= threshold

    def get_trust_score(self) -> int:
        """Get the current trust score."""
        return self._calculate_trust_score()

    def serialize(self) -> str:
        """Serialize the envelope to JSON."""
        envelope_data = {
            "ATP": {
                "version": self.version,
                "messageId": self.message_id,
                "agentIdentity": {
                    "id": self.agent_identity.id,
                    "publicKey": self.agent_identity.public_key,
                    "attestation": {
                        "issuer": self.agent_identity.attestation.issuer,
                        "level": self.agent_identity.attestation.level.value,
                        "issuedAt": self.agent_identity.attestation.issued_at,
                        "expiresAt": self.agent_identity.attestation.expires_at,
                    },
                    "capabilities": self.agent_identity.capabilities,
                },
                "trustLevel": self.trust_level.value,
                "policyContext": {
                    "allowedTools": self.policy_context.allowed_tools
                    if self.policy_context
                    else None,
                    "dataSensitivity": self.policy_context.data_sensitivity.value
                    if self.policy_context and self.policy_context.data_sensitivity
                    else None,
                    "spawnPermission": self.policy_context.spawn_permission
                    if self.policy_context
                    else None,
                    "maxLifespanSeconds": self.policy_context.max_lifespan_seconds
                    if self.policy_context
                    else None,
                }
                if self.policy_context
                else None,
                "provenance": [
                    {
                        "type": entry.type,
                        "id": entry.id,
                        "timestamp": entry.timestamp,
                        "action": entry.action,
                    }
                    for entry in self.provenance
                ],
                "timestamp": self.timestamp,
                "payload": self._make_payload_serializable(self.payload),
                "trustScore": self.get_trust_score(),
                "signature": self.signature,
            }
        }

        return json.dumps(envelope_data, indent=2)

    @classmethod
    def from_serialized(cls, data: str) -> "ATPEnvelope":
        """Create an ATP envelope from serialized data."""
        try:
            envelope_data = json.loads(data)
            atp_data = envelope_data["ATP"]

            # Reconstruct agent identity
            agent_data = atp_data["agentIdentity"]
            attestation = IAttestation(
                issuer=agent_data["attestation"]["issuer"],
                level=TrustLevel(agent_data["attestation"]["level"]),
                issued_at=agent_data["attestation"].get("issuedAt"),
                expires_at=agent_data["attestation"].get("expiresAt"),
            )

            agent_identity = IAgentIdentity(
                id=agent_data["id"],
                public_key=agent_data["publicKey"],
                attestation=attestation,
                capabilities=agent_data.get("capabilities"),
            )

            # Reconstruct policy context
            policy_data = atp_data.get("policyContext")
            policy_context = None
            if policy_data:
                policy_context = IPolicyContext(
                    allowed_tools=policy_data.get("allowedTools"),
                    data_sensitivity=DataSensitivity(policy_data["dataSensitivity"])
                    if policy_data.get("dataSensitivity")
                    else None,
                    spawn_permission=policy_data.get("spawnPermission"),
                    max_lifespan_seconds=policy_data.get("maxLifespanSeconds"),
                )

            # Reconstruct provenance
            provenance = []
            for entry_data in atp_data.get("provenance", []):
                provenance.append(
                    IProvenanceEntry(
                        type=entry_data["type"],
                        id=entry_data["id"],
                        timestamp=entry_data["timestamp"],
                        action=entry_data["action"],
                    )
                )

            # Create envelope
            envelope = cls()
            envelope.version = atp_data["version"]
            envelope.message_id = atp_data["messageId"]
            envelope.agent_identity = agent_identity
            envelope.trust_level = TrustLevel(atp_data["trustLevel"])
            envelope.policy_context = policy_context
            envelope.provenance = provenance
            envelope.timestamp = atp_data["timestamp"]
            envelope.payload = atp_data["payload"]
            envelope.signature = atp_data.get("signature")

            return envelope

        except Exception as e:
            raise ValueError(f"Failed to deserialize envelope: {e}")

    def __str__(self) -> str:
        """String representation of the envelope."""
        return f"ATPEnvelope(id={self.message_id}, agent={self.agent_identity.id}, trust={self.trust_level.value})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ATPEnvelope(message_id='{self.message_id}', agent_identity={self.agent_identity}, trust_level={self.trust_level})"


# Factory function for creating envelopes from config
def create_envelope(config: IATPConfig) -> ATPEnvelope:
    """Create an ATP envelope from configuration."""
    envelope = ATPEnvelope()
    envelope._config = config
    envelope.__post_init__()
    return envelope
