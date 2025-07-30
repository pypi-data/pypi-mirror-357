import requests
from .base_transport import BaseTransport
from ..core.atp_envelope import ATPEnvelope
from typing import Any, Callable, Dict

class HTTPTransport(BaseTransport):
    def __init__(self, endpoint: str, options: dict = None):
        self.endpoint = endpoint.rstrip('/')
        self.options = options or {}
        self.message_history = []
        self.connected_agents = {}  # agent_id -> handler (callable)

    def register_agent(self, agent_id: str, handler: Callable[[Dict], None]) -> None:
        self.connected_agents[agent_id] = handler

    def unregister_agent(self, agent_id: str) -> None:
        if agent_id in self.connected_agents:
            del self.connected_agents[agent_id]

    def send_message(self, from_agent: str, to_agent: str, envelope: ATPEnvelope) -> None:
        url = f"{self.endpoint}/agents/{to_agent}/inbox"
        data = envelope.serialize() if hasattr(envelope, 'serialize') else str(envelope)
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, data=data, headers=headers, timeout=5)
            response.raise_for_status()
            print(f"[HTTP] Message sent from {from_agent} to {to_agent} via {url}")
        except Exception as e:
            print(f"[HTTP] Failed to send message to {to_agent} at {url}: {e}")
        self.message_history.append((from_agent, to_agent, envelope))

    def broadcast(self, from_agent: str, envelope: ATPEnvelope) -> None:
        for agent_id in self.connected_agents:
            if agent_id != from_agent:
                self.send_message(from_agent, agent_id, envelope)

    def get_message_history(self) -> list:
        return self.message_history

    def get_connected_agents(self) -> list:
        return list(self.connected_agents.keys())

# --- Flask-based demo server for receiving messages ---
# To use: run this Flask app in a separate process
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    app = Flask(__name__)

    @app.route('/agents/<agent_id>/inbox', methods=['POST'])
    def agent_inbox(agent_id):
        envelope_json = request.get_json(force=True)
        print(f"[HTTP] Agent {agent_id} received envelope:", envelope_json)
        # Here you would deserialize and process the envelope
        return jsonify({"status": "received", "agent": agent_id}), 200

    app.run(host='0.0.0.0', port=5000) 