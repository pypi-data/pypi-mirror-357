"""
HTTP Transport Demo - Demonstrating ATP communication over HTTP.

This example shows:
1. A Flask-based agent server that receives ATP messages
2. An ATP client that sends messages via HTTP transport
3. Real message exchange between agents over HTTP
"""

import json
import threading
import time
from flask import Flask, request, jsonify
from atp.types import IAgentIdentity, TrustLevel, DataSensitivity
from atp.core.atp_envelope import ATPEnvelope
from atp.transport.http_transport import HTTPTransport

# Flask app for the receiving agent
app = Flask(__name__)
received_messages = []

@app.route('/agents/<agent_id>/inbox', methods=['POST'])
def agent_inbox(agent_id):
    """Receive ATP messages for an agent."""
    try:
        envelope_data = request.get_json(force=True)
        print(f"[HTTP Server] Agent {agent_id} received envelope:")
        print(f"  From: {envelope_data.get('ATP', {}).get('agentIdentity', {}).get('id', 'unknown')}")
        print(f"  Trust Level: {envelope_data.get('ATP', {}).get('trustLevel', 'unknown')}")
        print(f"  Payload: {envelope_data.get('ATP', {}).get('payload', {})}")
        
        received_messages.append({
            'agent_id': agent_id,
            'envelope': envelope_data,
            'timestamp': time.time()
        })
        
        return jsonify({
            "status": "received",
            "agent": agent_id,
            "message": "Envelope processed successfully"
        }), 200
        
    except Exception as e:
        print(f"[HTTP Server] Error processing message: {e}")
        return jsonify({"error": str(e)}), 400

def start_flask_server(host='0.0.0.0', port=5000):
    """Start the Flask server in a separate thread."""
    def run_server():
        app.run(host=host, port=port, debug=False, use_reloader=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print(f"[HTTP Server] Started on http://{host}:{port}")
    return server_thread

def create_agent_identity(agent_id: str, trust_level: TrustLevel) -> IAgentIdentity:
    """Create an agent identity for testing."""
    return IAgentIdentity(
        id=agent_id,
        public_key=f"public-key-{agent_id}",
        attestation={
            "issuer": "demo-authority",
            "level": trust_level,
            "issued_at": "2024-01-01T00:00:00Z",
            "expires_at": "2025-01-01T00:00:00Z",
        },
        capabilities=["http-communication", "data-processing"],
    )

def create_atp_envelope(agent_identity: IAgentIdentity, message_type: str, data: dict) -> ATPEnvelope:
    """Create an ATP envelope with the given data."""
    envelope = ATPEnvelope.__new__(ATPEnvelope)
    
    # Initialize all required attributes
    envelope.version = "1.0.0"
    envelope.message_id = f"msg-{int(time.time() * 1000)}"
    envelope.agent_identity = agent_identity
    envelope.trust_level = agent_identity.attestation["level"]
    envelope.policy_context = {
        "data_sensitivity": "internal",
        "allowed_tools": ["http", "data-processing"],
        "spawn_permission": False,
        "max_lifespan_seconds": 3600,
    }
    envelope.provenance = []
    envelope.timestamp = "2024-01-01T00:00:00Z"
    envelope.payload = {
        "messageType": message_type,
        "data": data,
        "timestamp": time.time()
    }
    envelope.signature = None
    
    return envelope

def demo_http_transport():
    """Demonstrate HTTP transport functionality."""
    print("HTTP Transport Demo")
    print("=" * 50)
    
    # 1. Start the Flask server
    print("\n1. Starting HTTP server...")
    server_thread = start_flask_server()
    time.sleep(2)  # Give server time to start
    
    # 2. Create agent identities
    print("\n2. Creating agent identities...")
    sender_agent = create_agent_identity("sender-agent", TrustLevel.VERIFIED)
    receiver_agent = create_agent_identity("receiver-agent", TrustLevel.CERTIFIED)
    
    print(f"Sender Agent: {sender_agent.id} (Trust: {sender_agent.attestation['level']})")
    print(f"Receiver Agent: {receiver_agent.id} (Trust: {receiver_agent.attestation['level']})")
    
    # 3. Create HTTP transport
    print("\n3. Creating HTTP transport...")
    http_transport = HTTPTransport("http://localhost:5000")
    
    # 4. Register agents
    print("\n4. Registering agents...")
    http_transport.register_agent(sender_agent.id, lambda msg: print(f"Sender received: {msg}"))
    http_transport.register_agent(receiver_agent.id, lambda msg: print(f"Receiver received: {msg}"))
    
    # 5. Send individual messages
    print("\n5. Sending individual messages...")
    
    # Message 1: Simple data request
    envelope1 = create_atp_envelope(
        sender_agent,
        "request",
        {"operation": "get_data", "resource": "user-profile"}
    )
    http_transport.send_message(sender_agent.id, receiver_agent.id, envelope1)
    
    time.sleep(1)  # Give time for message processing
    
    # Message 2: Data processing request
    envelope2 = create_atp_envelope(
        sender_agent,
        "request",
        {"operation": "process_data", "data": {"type": "analytics", "size": 1024}}
    )
    http_transport.send_message(sender_agent.id, receiver_agent.id, envelope2)
    
    time.sleep(1)
    
    # 6. Send broadcast message
    print("\n6. Sending broadcast message...")
    broadcast_envelope = create_atp_envelope(
        sender_agent,
        "broadcast",
        {"operation": "system_notification", "message": "System maintenance in 5 minutes"}
    )
    http_transport.broadcast(sender_agent.id, broadcast_envelope)
    
    time.sleep(1)
    
    # 7. Show results
    print("\n7. Results:")
    print(f"Messages sent: {len(http_transport.get_message_history())}")
    print(f"Messages received by server: {len(received_messages)}")
    print(f"Connected agents: {http_transport.get_connected_agents()}")
    
    # Show message history
    print("\nMessage History:")
    for i, (from_agent, to_agent, envelope) in enumerate(http_transport.get_message_history(), 1):
        print(f"  {i}. {from_agent} -> {to_agent}: {envelope.payload.get('data', {}).get('operation', 'unknown')}")
    
    # Show received messages
    print("\nReceived Messages:")
    for i, msg in enumerate(received_messages, 1):
        agent_id = msg['agent_id']
        operation = msg['envelope'].get('ATP', {}).get('payload', {}).get('data', {}).get('operation', 'unknown')
        print(f"  {i}. Agent {agent_id} received: {operation}")
    
    print("\nHTTP Transport Demo Complete!")
    print("Server will continue running. Press Ctrl+C to stop.")

if __name__ == "__main__":
    try:
        demo_http_transport()
        # Keep the server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down HTTP transport demo...") 