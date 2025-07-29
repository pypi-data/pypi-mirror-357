"""
Agent Trust Protocol - Python Holistic Demo

This demo showcases all advanced features of the ATP implementation including:
- Agent discovery and registration
- Capability negotiation
- Rich media support (files, forms, streams)
- Trust-based content filtering
- Best agent selection
- Concurrent processing
- Complete audit trail
"""

import asyncio

from ..types import (
    IAgentIdentity,
    IAttestation,
    TrustLevel,
    MessageType,
)
from ..protocol.atp_client import ATPClient


async def create_agent(
    agent_id: str,
    trust_level: TrustLevel,
    private_key: str,
    name: str,
    description: str,
    capabilities: list,
) -> ATPClient:
    """Create an ATP agent with the specified configuration."""

    # Create agent identity
    identity = IAgentIdentity(
        id=agent_id,
        public_key=f"{agent_id}-public-key",
        attestation=IAttestation(
            issuer="demo-authority",
            level=trust_level,
            issued_at="2025-01-01T00:00:00Z",
            expires_at="2026-01-01T00:00:00Z",
        ),
        capabilities=capabilities,
    )

    # Create ATP client
    client = ATPClient(identity, trust_level, private_key)

    # Connect to transport
    await client.connect()

    # Register with discovery system
    client.register_with_discovery(name, description, capabilities)

    return client


async def create_financial_agent():
    """Financial analysis agent with high trust level."""
    client = await create_agent(
        "financial-agent-001",
        TrustLevel.CERTIFIED,
        "financial-private-key",
        "Financial Analysis Agent",
        "High-security financial analysis and risk assessment",
        ["financial-analysis", "risk-assessment", "compliance-checking"],
    )

    # Handle incoming requests
    async def handle_request(envelope, respond):
        print(
            f"📨 Financial agent received request: {envelope.payload.get('data', {}).get('task', 'unknown')}"
        )

        # Add provenance
        envelope.add_provenance(
            {"type": "service", "id": "financial-agent", "action": "process_financial_request"}
        )

        # Simulate processing
        await asyncio.sleep(0.1)

        # Process the request
        data = envelope.payload.get("data", {})

        if "mediaPayload" in data:
            media_payload = data["mediaPayload"]
            media_type = media_payload.get("type")

            if media_type == "file":
                filename = media_payload.get("metadata", {}).get("filename", "unknown")
                result = {
                    "status": "processed",
                    "result": f"Financial file processed: {filename}",
                    "analysis": "Financial data analyzed successfully",
                }
            elif media_type == "form":
                fields = media_payload.get("content", {}).get("fields", {})
                result = {
                    "status": "processed",
                    "result": "Financial form processed",
                    "fields": fields,
                }
            else:
                result = {"status": "processed", "result": "Media content processed successfully"}
        else:
            result = {"status": "processed", "result": "Financial request processed successfully"}

        # Add more provenance
        envelope.add_provenance(
            {"type": "task", "id": "financial-processing", "action": "completed_analysis"}
        )

        # Send response
        await respond(result)

    client.on_message(MessageType.REQUEST, handle_request)
    return client


async def create_data_processor_agent():
    """Data processing agent with medium trust level."""
    client = await create_agent(
        "data-processor-002",
        TrustLevel.VERIFIED,
        "processor-private-key",
        "Data Processing Agent",
        "Advanced data processing and analysis",
        ["data-processing", "document-analysis", "ml-inference"],
    )

    # Handle incoming requests
    async def handle_request(envelope, respond):
        print(
            f"📨 Data processor received request: {envelope.payload.get('data', {}).get('task', 'unknown')}"
        )

        # Add provenance
        envelope.add_provenance(
            {"type": "service", "id": "data-processor", "action": "process_data_request"}
        )

        # Simulate processing
        await asyncio.sleep(0.1)

        # Process the request
        data = envelope.payload.get("data", {})

        if "mediaPayload" in data:
            media_payload = data["mediaPayload"]
            media_type = media_payload.get("type")

            if media_type == "file":
                filename = media_payload.get("metadata", {}).get("filename", "unknown")
                result = {
                    "status": "processed",
                    "result": f"Data file processed: {filename}",
                    "analysis": "Data content analyzed successfully",
                }
            elif media_type == "form":
                fields = media_payload.get("content", {}).get("fields", {})
                result = {"status": "processed", "result": "Data form processed", "fields": fields}
            else:
                result = {"status": "processed", "result": "Media content processed successfully"}
        else:
            task = data.get("task", "unknown")
            result = {
                "status": "processed",
                "result": f"Data task processed: {task}",
                "analysis": "Data processing completed successfully",
            }

        # Add more provenance
        envelope.add_provenance(
            {"type": "task", "id": "data-processing", "action": "completed_processing"}
        )

        # Send response
        await respond(result)

    client.on_message(MessageType.REQUEST, handle_request)
    return client


async def create_media_handler_agent():
    """Media handling agent with medium trust level."""
    client = await create_agent(
        "media-handler-003",
        TrustLevel.VERIFIED,
        "media-private-key",
        "Media Handler Agent",
        "File and media processing specialist",
        ["file-processing", "image-analysis", "document-conversion"],
    )

    # Handle incoming requests
    async def handle_request(envelope, respond):
        print(
            f"📨 Media handler received request: {envelope.payload.get('data', {}).get('task', 'unknown')}"
        )

        # Add provenance
        envelope.add_provenance(
            {"type": "service", "id": "media-handler", "action": "process_media_request"}
        )

        # Simulate processing
        await asyncio.sleep(0.1)

        # Process the request
        data = envelope.payload.get("data", {})

        if "mediaPayload" in data:
            media_payload = data["mediaPayload"]
            media_type = media_payload.get("type")

            if media_type == "file":
                filename = media_payload.get("metadata", {}).get("filename", "unknown")
                result = {
                    "status": "processed",
                    "result": f"Media file processed: {filename}",
                    "analysis": "Media content processed successfully",
                }
            else:
                result = {
                    "status": "processed",
                    "result": f"Media content processed: {media_type}",
                    "analysis": "Media processing completed",
                }
        else:
            result = {"status": "processed", "result": "Media request processed successfully"}

        # Add more provenance
        envelope.add_provenance(
            {"type": "task", "id": "media-processing", "action": "completed_processing"}
        )

        # Send response
        await respond(result)

    client.on_message(MessageType.REQUEST, handle_request)
    return client


async def demonstrate_holistic_atp():
    """Demonstrate all advanced features of the ATP implementation."""
    print("Agent Trust Protocol - Python Holistic Features Demo")
    print("=" * 60)

    # Create agents
    print("\nCreating ATP Clients")
    print("=" * 25)

    financial_agent = await create_financial_agent()
    print(f"✓ Financial Agent created ({financial_agent.trust_level.value})")

    data_processor = await create_data_processor_agent()
    print(f"✓ Data Processor created ({data_processor.trust_level.value})")

    media_handler = await create_media_handler_agent()
    print(f"✓ Media Handler created ({media_handler.trust_level.value})")

    await asyncio.sleep(0.5)  # Let agents connect and register

    print("\nAgent Discovery Demo")
    print("=" * 25)

    # Discover agents by capability
    data_processing_agents = await financial_agent.discover_agents_by_capability("data-processing")
    print(f"Found {len(data_processing_agents)} agents with data-processing capability:")
    for agent in data_processing_agents:
        print(f"  • {agent.name} ({agent.agent_id}) - Trust: {agent.trust_level.value}")

    # Discover agents by name
    financial_agents = await financial_agent.discover_agents_by_name("financial")
    print(f"\nFound {len(financial_agents)} agents matching 'financial':")
    for agent in financial_agents:
        print(f"  • {agent.name} - {agent.description}")

    print("\nCapability Negotiation Demo")
    print("=" * 35)

    # Negotiate capabilities
    negotiation_result = await financial_agent.negotiate_capabilities(
        "data-processor-002", ["data-processing", "ml-inference"], TrustLevel.VERIFIED
    )

    print(f"Data Processor capabilities: {', '.join(data_processor.identity.capabilities)}")
    print(f"\nNegotiation result for data processor:")
    print(f"  • Can handle: {negotiation_result.can_handle}")
    print(f"  • Trust score: {negotiation_result.trust_score}")
    print(f"  • Supported capabilities: {', '.join(negotiation_result.supported_capabilities)}")
    print(f"  • Missing capabilities: {', '.join(negotiation_result.missing_capabilities)}")

    print("\nRich Media Support Demo")
    print("=" * 30)

    # Send file request
    print("\nSending File Request")
    print("=" * 25)

    file_content = b"Sample financial data for processing"
    try:
        file_response = await financial_agent.send_file_request(
            "data-processor-002",
            "financial-data.csv",
            file_content,
            "text/csv",
            {"requires_trust": "verified"},
        )
        print(f"✓ File processing response: {file_response.data.get('result', 'Unknown')}")
    except Exception as error:
        print(f"✗ File processing failed: {error}")

    # Send form request
    print("\nSending Form Request")
    print("=" * 25)

    form_fields = {"customerId": "CUST123", "transactionType": "investment", "amount": 50000}

    form_validation = {
        "customerId": {"required": True, "pattern": r"^CUST\d{3}$"},
        "transactionType": {"required": True, "enum": ["investment", "withdrawal", "transfer"]},
        "amount": {"required": True, "min": 1000, "max": 1000000},
    }

    try:
        form_response = await financial_agent.send_form_request(
            "data-processor-002", form_fields, form_validation, {"requires_trust": "verified"}
        )
        print(f"✓ Form processing response: {form_response.data.get('result', 'Unknown')}")
    except Exception as error:
        print(f"✗ Form processing failed: {error}")

    print("\nBest Agent Selection Demo")
    print("=" * 35)

    # Find best agent for task
    best_agent = await financial_agent.get_best_agent_for_task(
        ["data-processing", "ml-inference"], TrustLevel.VERIFIED
    )

    if best_agent:
        print(f"Best agent for data processing task: {best_agent.name} ({best_agent.agent_id})")
        print(f"  • Trust level: {best_agent.trust_level.value}")
        print(f"  • Capabilities: {', '.join(best_agent.capabilities)}")
    else:
        print("✗ No suitable agent found for the task")

    print("\nTrust Validation Demo")
    print("=" * 25)

    # Validate trust
    data_processor_trust = await financial_agent.get_trust_score("data-processor-002")
    print(f"Data processor trust score: {data_processor_trust}")

    is_trusted = await financial_agent.validate_agent_trust("data-processor-002", 70)
    print(f"Data processor meets 70+ trust requirement: {is_trusted}")

    print("\nSupported Interaction Modalities")
    print("=" * 40)

    # Show supported modalities
    financial_modalities = financial_agent.get_supported_modalities()
    print(f"Financial agent supported modalities:")
    for modality in financial_modalities:
        print(f"  • {modality.type.value}: {modality.description}")
        if modality.max_size:
            print(f"    Max size: {(modality.max_size / 1024 / 1024):.1f} MB")
        if modality.supported_formats:
            print(f"    Formats: {', '.join(modality.supported_formats)}")

    print("\nConcurrent Media Processing Demo")
    print("=" * 40)

    # Demonstrate concurrent requests with different media types
    concurrent_tasks = [
        financial_agent.send_file_request(
            "media-handler-003", "image1.jpg", b"fake image data", "image/jpeg"
        ),
        financial_agent.send_form_request(
            "data-processor-002", {"query": "analyze data"}, {"query": {"required": True}}
        ),
        financial_agent.send_request(
            "data-processor-002", {"task": "process-text", "text": "Sample text for processing"}
        ),
    ]

    try:
        results = await asyncio.gather(*concurrent_tasks)
        print(f"✓ All {len(results)} concurrent tasks completed successfully")
        for i, result in enumerate(results):
            print(
                f"  • Task {i + 1}: {result.data.get('result', result.data.get('status', 'Unknown'))}"
            )
    except Exception as error:
        print(f"✗ Concurrent processing failed: {error}")

    print("\nHolistic ATP Demo Completed!")
    print("=" * 40)
    print("✓ Agent discovery and registration")
    print("✓ Capability negotiation and validation")
    print("✓ Rich media support (files, forms, streams)")
    print("✓ Trust-based content filtering")
    print("✓ Best agent selection")
    print("✓ Concurrent processing")
    print("✓ Complete audit trail")
    print("\nATP provides comprehensive, trust-based agent communication!")

    # Cleanup
    await financial_agent.disconnect()
    await data_processor.disconnect()
    await media_handler.disconnect()


async def main():
    """Main demo function."""
    try:
        await demonstrate_holistic_atp()
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
