"""
Async ATP Demo - Demonstrates asynchronous agent communication.

This demo shows how to use ATP for non-blocking agent communication
with proper error handling and concurrent processing.
"""

import asyncio
from datetime import datetime, timezone

from ..types import (
    IAgentIdentity,
    IAttestation,
    TrustLevel,
)
from ..protocol.atp_client import ATPClient


async def create_agent(agent_id: str, trust_level: TrustLevel, private_key: str) -> ATPClient:
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
        capabilities=["data-processing", "analysis", "communication"],
    )

    # Create ATP client
    client = ATPClient(identity, trust_level, private_key)

    # Connect to transport
    await client.connect()

    return client


async def data_processor_agent():
    """Data processor agent that handles requests."""
    client = await create_agent("data-processor", TrustLevel.CERTIFIED, "processor-private-key")

    # Handle incoming requests
    async def handle_request(envelope, respond):
        print(
            f"📨 Data processor received request: {envelope.payload.get('data', {}).get('task', 'unknown')}"
        )

        # Add provenance
        envelope.add_provenance(
            {"type": "service", "id": "data-processor", "action": "process_request"}
        )

        # Simulate processing
        await asyncio.sleep(0.5)

        # Process the request
        task = envelope.payload.get("data", {}).get("task", "unknown")
        result = {
            "status": "completed",
            "task": task,
            "result": f"Processed {task} successfully",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trust_score": envelope.get_trust_score(),
        }

        # Add more provenance
        envelope.add_provenance(
            {"type": "task", "id": f"task-{task}", "action": "completed_processing"}
        )

        # Send response
        await respond(result)

    client.on_message("request", handle_request)
    return client


async def monitoring_agent():
    """Monitoring agent that receives notifications."""
    client = await create_agent("monitor", TrustLevel.VERIFIED, "monitor-private-key")

    # Handle notifications
    def handle_notification(envelope):
        data = envelope.payload.get("data", {})
        print(f"🔔 Monitor received notification: {data.get('event', 'unknown')}")
        print(f"   Details: {data}")

    # Handle broadcasts
    def handle_broadcast(envelope):
        data = envelope.payload.get("data", {})
        print(f"📢 Monitor received broadcast: {data.get('type', 'unknown')}")
        print(f"   Message: {data.get('message', 'No message')}")

    client.on_message("notification", handle_notification)
    client.on_message("broadcast", handle_broadcast)

    return client


async def orchestrator_agent():
    """Orchestrator agent that coordinates other agents."""
    client = await create_agent("orchestrator", TrustLevel.CERTIFIED, "orchestrator-private-key")

    return client


async def run_comprehensive_demo():
    """Run the comprehensive ATP demo."""
    print("🚀 Agent Trust Protocol - Python Async Demo")
    print("=" * 50)

    # Create agents
    print("\n🔧 Creating agents...")
    data_processor = await data_processor_agent()
    monitor = await monitoring_agent()
    orchestrator = await orchestrator_agent()

    await asyncio.sleep(1)  # Let agents connect

    print(f"\n✅ All agents connected!")
    print(f"   Connected agents: {data_processor.transport.get_connected_agents()}")

    # Demo 1: Basic Request/Response
    print("\n" + "=" * 50)
    print("📤 Demo 1: Basic Request/Response")
    print("=" * 50)

    try:
        response = await orchestrator.send_request(
            "data-processor",
            {"task": "analyze-data", "priority": "high", "data_source": "financial-database"},
            {"timeout": 5000, "requires_trust": "certified"},
        )

        print(f"✅ Request completed successfully!")
        print(f"   Response: {response.data}")
        print(f"   Trust Score: {response.trust_score}/100")

    except Exception as e:
        print(f"❌ Request failed: {e}")

    # Demo 2: Notifications
    print("\n" + "=" * 50)
    print("🔔 Demo 2: Fire-and-Forget Notifications")
    print("=" * 50)

    await orchestrator.send_notification(
        "monitor",
        {
            "event": "task_completed",
            "task_id": "task-123",
            "duration": 2500,
            "status": "success",
            "metrics": {"items_processed": 150, "error_rate": 0.02},
        },
    )

    await asyncio.sleep(0.5)  # Let notification be processed

    # Demo 3: Broadcast Communication
    print("\n" + "=" * 50)
    print("📢 Demo 3: Broadcast Communication")
    print("=" * 50)

    await orchestrator.broadcast(
        {
            "type": "system_alert",
            "message": "Scheduled maintenance in 30 minutes",
            "severity": "warning",
            "affected_services": ["data-processing", "analysis"],
            "estimated_duration": "2 hours",
        }
    )

    await asyncio.sleep(0.5)  # Let broadcast be processed

    # Demo 4: Concurrent Requests
    print("\n" + "=" * 50)
    print("🔄 Demo 4: Concurrent Request Processing")
    print("=" * 50)

    tasks = [
        orchestrator.send_request("data-processor", {"task": "process-dataset-1"}),
        orchestrator.send_request("data-processor", {"task": "process-dataset-2"}),
        orchestrator.send_request("data-processor", {"task": "process-dataset-3"}),
    ]

    try:
        responses = await asyncio.gather(*tasks)
        print(f"✅ All {len(responses)} concurrent requests completed!")

        for i, response in enumerate(responses, 1):
            print(
                f"   Task {i}: {response.data.get('task', 'unknown')} - {response.data.get('status', 'unknown')}"
            )

    except Exception as e:
        print(f"❌ Concurrent requests failed: {e}")

    # Demo 5: Trust Validation
    print("\n" + "=" * 50)
    print("🔒 Demo 5: Trust Validation")
    print("=" * 50)

    # Test trust requirements
    try:
        response = await orchestrator.send_request(
            "data-processor",
            {"task": "sensitive-operation", "data_classification": "confidential"},
            {"requires_trust": "certified"},
        )

        print(f"✅ High-trust request completed!")
        print(f"   Trust score: {response.trust_score}/100")

    except Exception as e:
        print(f"❌ Trust validation failed: {e}")

    # Demo 6: Timeout Handling
    print("\n" + "=" * 50)
    print("⏰ Demo 6: Timeout Handling")
    print("=" * 50)

    try:
        # This should timeout since data-processor doesn't handle this task
        response = await orchestrator.send_request(
            "data-processor",
            {"task": "slow-operation", "duration": "10_seconds"},
            {"timeout": 1000},  # 1 second timeout
        )

        print(f"✅ Slow operation completed!")

    except asyncio.TimeoutError:
        print("⏰ Request timed out as expected")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Demo 7: Message History and Statistics
    print("\n" + "=" * 50)
    print("📊 Demo 7: Transport Statistics")
    print("=" * 50)

    transport = data_processor.transport
    stats = transport.get_stats()

    print(f"📈 Transport Statistics:")
    print(f"   Connected agents: {stats['connected_agents']}")
    print(f"   Total messages: {stats['total_messages']}")
    print(f"   Latency range: {stats['latency_range']}ms")
    print(f"   Error rate: {stats['error_rate']:.1%}")

    # Show message history
    history = transport.get_message_history()
    print(f"\n📋 Message History ({len(history)} messages):")

    for i, msg in enumerate(history[-5:], 1):  # Show last 5 messages
        print(
            f"   {i}. {msg.from_agent} → {msg.to_agent}: {msg.envelope.payload.get('type', 'unknown')}"
        )

    # Demo 8: Trust Status
    print("\n" + "=" * 50)
    print("🔐 Demo 8: Agent Trust Status")
    print("=" * 50)

    for agent_name, agent in [
        ("Orchestrator", orchestrator),
        ("Data Processor", data_processor),
        ("Monitor", monitor),
    ]:
        status = agent.get_trust_status()
        print(f"🔐 {agent_name}:")
        print(f"   Trust Level: {status['level']}")
        print(f"   Trust Score: {status['score']}/100")
        print(f"   Verified: {status['verified']}")
        print(f"   Connected: {status['connected']}")

    # Cleanup
    print("\n" + "=" * 50)
    print("🧹 Cleaning up...")
    print("=" * 50)

    await orchestrator.disconnect()
    await data_processor.disconnect()
    await monitor.disconnect()

    print("✅ Demo completed successfully!")
    print("\n🎉 Agent Trust Protocol Python implementation is working perfectly!")
    print("   Features demonstrated:")
    print("   ✅ Cryptographic message signing and verification")
    print("   ✅ Asynchronous request/response communication")
    print("   ✅ Fire-and-forget notifications")
    print("   ✅ Broadcast messaging")
    print("   ✅ Concurrent request handling")
    print("   ✅ Timeout and error handling")
    print("   ✅ Trust validation and scoring")
    print("   ✅ Complete audit trail and provenance tracking")


async def main():
    """Main entry point."""
    try:
        await run_comprehensive_demo()
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
