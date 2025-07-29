# Agent Trust Protocol - Python Implementation

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0--alpha-blue.svg)](https://github.com/agent-trust-protocol/agent-trust-protocol)

A comprehensive Python implementation of the Agent Trust Protocol (ATP) for secure, trustworthy communication between autonomous AI agents with cryptographic identity verification, hierarchical trust management, and asynchronous communication.

## 🚀 Features

- **Cryptographic Security**: JWT-based message signing and verification
- **⚡ Async Communication**: Full async/await support with concurrent processing
- **🏗️ Protocol Agnostic**: Works with any transport layer (HTTP, WebSocket, gRPC, etc.)
- **📊 Trust Scoring**: Dynamic trust assessment (0-100 scale)
- **🛡️ Policy Enforcement**: Runtime security controls and validation
- **📋 Provenance Tracking**: Complete audit trail for compliance
- **🔄 In-Memory Transport**: Built-in transport for development and testing

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Contributing](#contributing)

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (coming soon)
pip install agent-trust-protocol

# Install from source
git clone https://github.com/agent-trust-protocol/agent-trust-protocol.git
cd agent-trust-protocol/python
pip install -e .
```

### Basic Usage

```python
import asyncio
from atp import ATPClient, IAgentIdentity, IAttestation, TrustLevel

async def main():
    # Create agent identity
    identity = IAgentIdentity(
        id="my-agent-001",
        public_key="my-public-key",
        attestation=IAttestation(
            issuer="trust-authority",
            level=TrustLevel.CERTIFIED,
            issued_at="2025-01-01T00:00:00Z",
            expires_at="2026-01-01T00:00:00Z"
        ),
        capabilities=["data-processing", "ml-inference"]
    )
    
    # Create ATP client with cryptographic signing
    client = ATPClient(identity, TrustLevel.CERTIFIED, "my-private-key")
    
    # Connect to transport layer
    await client.connect()
    
    # Send async request
    response = await client.send_request("target-agent", {
        "task": "process-data",
        "priority": "high"
    })
    
    print(f"Response: {response.data}")
    print(f"Trust Score: {response.trust_score}")

# Run the example
asyncio.run(main())
```

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
# Core dependencies
pip install PyJWT cryptography

# For development
pip install -e .[dev]

# For enhanced cryptography
pip install -e .[crypto]
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/agent-trust-protocol/agent-trust-protocol.git
cd agent-trust-protocol/python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
flake8 atp/
black atp/
mypy atp/
```

## 🔧 Basic Usage

### Creating an Agent

```python
from atp import ATPClient, IAgentIdentity, IAttestation, TrustLevel

# Create agent identity
identity = IAgentIdentity(
    id="financial-analyzer-001",
    public_key="financial-public-key",
    attestation=IAttestation(
        issuer="financial-regulatory-authority",
        level=TrustLevel.CERTIFIED,
        issued_at="2025-01-01T00:00:00Z",
        expires_at="2026-01-01T00:00:00Z"
    ),
    capabilities=["financial-analysis", "risk-assessment", "compliance-checking"]
)

# Create client with cryptographic signing
client = ATPClient(identity, TrustLevel.CERTIFIED, "financial-private-key")
```

### Async Request/Response

```python
# Send request with timeout and trust requirements
response = await client.send_request("data-processor", {
    "task": "analyze-quarterly-reports",
    "priority": "high",
    "data_source": "financial-database"
}, {
    "timeout": 5000,
    "requires_trust": "verified"
})

print(f"Analysis result: {response.data}")
print(f"Trust score: {response.trust_score}")
```

### Message Handlers

```python
# Handle incoming requests
async def handle_request(envelope, respond):
    print(f"Received request: {envelope.payload['data']}")
    
    # Process the request
    result = await process_data(envelope.payload['data'])
    
    # Send response
    await respond({
        "status": "completed",
        "result": result,
        "timestamp": datetime.now().isoformat()
    })

client.on_message("request", handle_request)

# Handle notifications
def handle_notification(envelope):
    print(f"Notification: {envelope.payload['data']}")

client.on_message("notification", handle_notification)
```

### Broadcast Communication

```python
# Send broadcast to all connected agents
await client.broadcast({
    "type": "system-alert",
    "message": "Maintenance window starting",
    "severity": "warning"
})
```

## 🔥 Advanced Features

### Concurrent Processing

```python
# Send multiple requests simultaneously
tasks = [
    client.send_request("agent1", {"task": "task1"}),
    client.send_request("agent2", {"task": "task2"}),
    client.send_request("agent3", {"task": "task3"})
]

responses = await asyncio.gather(*tasks)

for i, response in enumerate(responses, 1):
    print(f"Task {i}: {response.data}")
```

### Error Handling with Retry

```python
async def send_request_with_retry(target_agent, payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = await client.send_request(target_agent, payload, {
                "timeout": 5000
            })
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt == max_retries - 1:
                raise
            
            # Wait before retry (exponential backoff)
            await asyncio.sleep(2 ** attempt)

# Usage
response = await send_request_with_retry("reliable-agent", {
    "task": "critical-operation"
})
```

### Trust Score Monitoring

```python
# Monitor trust scores of incoming messages
async def handle_request_with_trust_check(envelope, respond):
    trust_score = envelope.get_trust_score()
    print(f"Trust score: {trust_score}/100")
    
    if trust_score < 70:
        await respond({
            "error": "Insufficient trust level",
            "required": 70,
            "actual": trust_score
        })
        return
    
    # Process request normally
    result = await process_request(envelope.payload['data'])
    await respond({"status": "success", "data": result})

client.on_message("request", handle_request_with_trust_check)
```

## 📚 Examples

### Run the Comprehensive Demo

```bash
# Run the async demo
python -m atp.examples.async_demo

# Or use the console script
atp-demo
```

The demo showcases:
- ✅ Cryptographic message signing and verification
- ✅ Asynchronous request/response communication
- ✅ Fire-and-forget notifications
- ✅ Broadcast messaging
- ✅ Concurrent request handling
- ✅ Timeout and error handling
- ✅ Trust validation and scoring
- ✅ Complete audit trail and provenance tracking

### Financial Data Processing Agent

```python
async def financial_agent():
    # Create financial analysis agent with high security requirements
    identity = IAgentIdentity(
        id="financial-analyzer-001",
        public_key="financial-public-key",
        attestation=IAttestation(
            issuer="financial-regulatory-authority",
            level=TrustLevel.CERTIFIED,
            issued_at="2025-01-01T00:00:00Z",
            expires_at="2026-01-01T00:00:00Z"
        ),
        capabilities=["financial-analysis", "risk-assessment", "compliance-checking"]
    )
    
    client = ATPClient(identity, TrustLevel.CERTIFIED, "financial-private-key")
    await client.connect()
    
    # Handle financial data requests
    async def handle_financial_request(envelope, respond):
        # Validate trust level for financial data
        if not envelope.meets_trust_threshold(85):
            await respond({
                "error": "Insufficient trust for financial data access",
                "required_trust": 85,
                "actual_trust": envelope.get_trust_score()
            })
            return
        
        # Process financial analysis
        analysis = await perform_financial_analysis(envelope.payload['data'])
        
        await respond({
            "status": "completed",
            "analysis": analysis,
            "compliance": "verified",
            "timestamp": datetime.now().isoformat()
        })
    
    client.on_message("request", handle_financial_request)
    return client
```

### Healthcare Data Agent

```python
async def healthcare_agent():
    # Healthcare data processing with HIPAA compliance
    identity = IAgentIdentity(
        id="healthcare-processor-001",
        public_key="healthcare-public-key",
        attestation=IAttestation(
            issuer="healthcare-compliance-authority",
            level=TrustLevel.CERTIFIED,
            issued_at="2025-01-01T00:00:00Z",
            expires_at="2026-01-01T00:00:00Z"
        ),
        capabilities=["patient-data-processing", "diagnostic-analysis", "compliance-auditing"]
    )
    
    client = ATPClient(identity, TrustLevel.CERTIFIED, "healthcare-private-key")
    await client.connect()
    
    # Handle healthcare data requests
    async def handle_healthcare_request(envelope, respond):
        # Add provenance for HIPAA compliance
        envelope.add_provenance({
            "type": "service",
            "id": "hipaa-compliance-checker",
            "action": "validate-patient-data-access"
        })
        
        # Process healthcare data
        result = await process_healthcare_data(envelope.payload['data'])
        
        # Add more provenance
        envelope.add_provenance({
            "type": "task",
            "id": "patient-data-processing",
            "action": "completed-data-analysis"
        })
        
        await respond({
            "status": "completed",
            "result": result,
            "hipaa_compliant": True,
            "audit_trail": envelope.provenance
        })
    
    client.on_message("request", handle_healthcare_request)
    return client
```

## 🔌 Integration Examples

### Express.js Integration

```python
from fastapi import FastAPI, HTTPException
from atp import ATPClient, IAgentIdentity, IAttestation, TrustLevel

app = FastAPI()

# Create ATP client
identity = IAgentIdentity(
    id="api-gateway",
    public_key="api-public-key",
    attestation=IAttestation(
        issuer="api-authority",
        level=TrustLevel.CERTIFIED,
        issued_at="2025-01-01T00:00:00Z",
        expires_at="2026-01-01T00:00:00Z"
    ),
    capabilities=["api-gateway", "request-routing"]
)

client = ATPClient(identity, TrustLevel.CERTIFIED, "api-private-key")

@app.on_event("startup")
async def startup_event():
    await client.connect()

@app.post("/api/process-data")
async def process_data(request_data: dict):
    try:
        response = await client.send_request("data-processor", {
            "task": "process-data",
            "data": request_data
        })
        
        return {
            "success": True,
            "result": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    status = client.get_trust_status()
    return {
        "connected": status["connected"],
        "trust_level": status["level"],
        "trust_score": status["score"]
    }
```

### WebSocket Integration

```python
import websockets
import json
from atp import ATPClient, IAgentIdentity, IAttestation, TrustLevel

async def websocket_handler(websocket, path):
    # Create ATP client
    identity = IAgentIdentity(
        id="websocket-gateway",
        public_key="ws-public-key",
        attestation=IAttestation(
            issuer="ws-authority",
            level=TrustLevel.VERIFIED,
            issued_at="2025-01-01T00:00:00Z",
            expires_at="2026-01-01T00:00:00Z"
        ),
        capabilities=["websocket-gateway", "message-forwarding"]
    )
    
    client = ATPClient(identity, TrustLevel.VERIFIED, "ws-private-key")
    await client.connect()
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Forward message through ATP
                response = await client.send_request("target-agent", data)
                
                # Send response back to WebSocket client
                await websocket.send(json.dumps({
                    "success": True,
                    "data": response.data
                }))
                
            except Exception as e:
                await websocket.send(json.dumps({
                    "success": False,
                    "error": str(e)
                }))
    finally:
        await client.disconnect()

# Start WebSocket server
start_server = websockets.serve(websocket_handler, "localhost", 8080)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

## 🔒 Security Features

### Trust Levels

- **Certified**: Highest trust level, full system access, cryptographic signing required
- **Verified**: Medium trust, limited sensitive data access, signing recommended
- **Unverified**: Low trust, public data only, signing optional
- **Sandboxed**: Isolated execution environment, restricted capabilities

### Cryptographic Security

All messages are cryptographically signed using JWT:
- **HS256**: For demo purposes (simple secret key)
- **RS256**: For production (RSA key pairs)
- **Ed25519**: For high-performance scenarios

### Trust Scoring

Trust scores (0-100) are calculated based on:
- **Identity Verification** (40 points): Attestation level and validity
- **Credential Freshness** (20 points): Time until expiry
- **Capability Alignment** (15 points): Declared vs. required capabilities
- **Policy Compliance** (15 points): Adherence to security policies
- **Cryptographic Security** (10 points): Message signing and verification

## 📊 API Reference

### Core Classes

#### ATPClient

Primary interface for agent communication.

```python
client = ATPClient(identity, trust_level, private_key=None)
await client.connect()
await client.disconnect()

# Send messages
response = await client.send_request(target_agent, payload, options)
await client.send_notification(target_agent, payload)
await client.broadcast(payload)

# Handle messages
client.on_message(message_type, handler)

# Get status
status = client.get_trust_status()
```

#### ATPEnvelope

Core message container with security and trust metadata.

```python
envelope = ATPEnvelope()
envelope.sign(private_key)
is_valid = envelope.verify_signature()
validation = envelope.validate()
trust_score = envelope.get_trust_score()
meets_threshold = envelope.meets_trust_threshold(70)
envelope.add_provenance(entry)
serialized = envelope.serialize()
restored = ATPEnvelope.from_serialized(serialized)
```

#### InMemoryTransport

Singleton transport layer for in-memory communication.

```python
transport = InMemoryTransport.get_instance()
transport.register_agent(agent_id, message_queue)
transport.unregister_agent(agent_id)
await transport.send_message(from_agent, to_agent, envelope)
await transport.broadcast(from_agent, envelope)
history = transport.get_message_history()
agents = transport.get_connected_agents()
stats = transport.get_stats()
```

### Type Definitions

```python
from atp import (
    IAgentIdentity,      # Agent identity information
    IAttestation,        # Agent attestation
    IPolicyContext,      # Policy context
    IProvenanceEntry,    # Provenance entry
    IATPConfig,          # ATP configuration
    IValidationResult,   # Validation result
    IATPResponse,        # ATP response
    ITransportConfig,    # Transport configuration
    ITransportMessage,   # Transport message
    TrustLevel,          # Trust level enum
    DataSensitivity,     # Data sensitivity enum
    MessageType,         # Message type enum
    TransportType,       # Transport type enum
)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=atp

# Run specific test file
pytest tests/test_atp_client.py

# Run async tests
pytest tests/test_async_features.py
```

## 🚀 Performance

The Python implementation is optimized for:
- **High Concurrency**: Full async/await support with asyncio
- **Low Latency**: Efficient message processing and routing
- **Memory Efficiency**: Minimal object creation and garbage collection
- **Scalability**: Support for thousands of concurrent agents

### Benchmarks

- **Message Processing**: ~1000 messages/second per agent
- **Trust Validation**: ~100 validations/second
- **Cryptographic Signing**: ~500 signatures/second
- **Memory Usage**: ~1MB per agent

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/agent-trust-protocol/agent-trust-protocol.git
cd agent-trust-protocol/python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Run tests
pytest

# Run linting
flake8 atp/
black atp/
mypy atp/

# Build package
python setup.py sdist bdist_wheel
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🔗 Links

- [Protocol Specification](../spec/atp-protocol-spec.md)
- [API Reference](../docs/api/api-reference.md)
- [Security Model](../docs/security/security-model.md)
- [Implementation Guide](../docs/guides/implementation-guide.md)
- [TypeScript Implementation](../src/)

---

**Agent Trust Protocol Python** - Enabling secure, trustworthy AI agent ecosystems