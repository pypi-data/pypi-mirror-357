"""
Simple HTTP Transport Demo - Basic ATP communication over HTTP.

This example demonstrates:
1. Creating an HTTP transport
2. Sending ATP envelopes via HTTP
3. Receiving and processing messages
"""

import time
import json
from atp.types import IAgentIdentity, TrustLevel
from atp.core.atp_envelope import ATPEnvelope
from atp.transport.http_transport import HTTPTransport

def main():
    print("Simple HTTP Transport Demo")
    print("=" * 40)
    
    # Create agent identities
    sender = IAgentIdentity(
        id="http-sender",
        public_key="sender-public-key",
        attestation={
            "issuer": "demo-authority",
            "level": TrustLevel.VERIFIED,
            "issued_at": "2024-01-01T00:00:00Z",
            "expires_at": "2025-01-01T00:00:00Z",
        },
        capabilities=["http-communication"],
    )
    
    receiver = IAgentIdentity(
        id="http-receiver", 
        public_key="receiver-public-key",
        attestation={
            "issuer": "demo-authority",
            "level": TrustLevel.CERTIFIED,
            "issued_at": "2024-01-01T00:00:00Z",
            "expires_at": "2025-01-01T00:00:00Z",
        },
        capabilities=["http-communication"],
    )
    
    # Create HTTP transport
    http_transport = HTTPTransport("http://localhost:5000")
    
    # Create ATP envelope
    envelope = ATPEnvelope.__new__(ATPEnvelope)
    envelope.version = "1.0.0"
    envelope.message_id = f"msg-{int(time.time() * 1000)}"
    envelope.agent_identity = sender
    envelope.trust_level = sender.attestation["level"]
    envelope.policy_context = {
        "data_sensitivity": "internal",
        "allowed_tools": ["http"],
        "spawn_permission": False,
        "max_lifespan_seconds": 3600,
    }
    envelope.provenance = []
    envelope.timestamp = "2024-01-01T00:00:00Z"
    envelope.payload = {
        "messageType": "request",
        "data": {
            "operation": "hello",
            "message": "Hello from HTTP transport!",
            "timestamp": time.time()
        }
    }
    envelope.signature = None
    
    # Send message
    print(f"Sending message from {sender.id} to {receiver.id}...")
    http_transport.send_message(sender.id, receiver.id, envelope)
    
    # Show results
    print(f"Message history: {len(http_transport.get_message_history())} messages")
    print(f"Connected agents: {http_transport.get_connected_agents()}")
    
    print("HTTP transport demo complete!")
    print("Note: This demo expects a server running on http://localhost:5000")
    print("Run the Flask server in http_transport.py to see full communication.")

if __name__ == "__main__":
    main() 