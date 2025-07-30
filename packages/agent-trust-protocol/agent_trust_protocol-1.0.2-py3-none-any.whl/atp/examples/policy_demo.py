"""
Policy Demo - Demonstrating comprehensive policy enforcement in Python ATP.

This example shows how to use the policy engine and manager to:
1. Define custom policies using templates
2. Create agents and evaluate policies
3. Handle allow/deny results and violations
4. Monitor policy statistics and audit logs
"""

from atp.types import IAgentIdentity, TrustLevel, DataSensitivity
from atp.core.atp_envelope import ATPEnvelope
from atp.policy import get_policy_manager, PolicyManagerConfig

def main():
    # Initialize policy manager with configuration
    config = PolicyManagerConfig(
        enable_default_policies=True,
        enable_audit_logging=True,
        enable_real_time_monitoring=True
    )
    policy_manager = get_policy_manager(config)
    
    print("ATP Policy Engine Demo")
    print("=" * 50)
    
    # 1. Create a policy from template: Only certified agents can access confidential data
    print("\n1. Creating policy from template...")
    policy = policy_manager.create_policy_from_template(
        'restrict-sensitive-data',
        'Confidential Data Access Restriction',
        {
            'sensitivity_level': 'confidential',
            'required_trust_level': 'certified',
        }
    )
    print(f"Policy created: {policy.name} (ID: {policy.id})")
    
    # 2. Create an agent identity with verified trust level
    print("\n2. Creating agent identity...")
    agent = IAgentIdentity(
        id="agent-123",
        public_key="demo-public-key",
        attestation={
            "issuer": "trust-authority",
            "level": TrustLevel.VERIFIED,  # Try changing to TrustLevel.CERTIFIED to see the difference
            "issued_at": "2024-01-01T00:00:00Z",
            "expires_at": "2025-01-01T00:00:00Z",
        },
        capabilities=["data-processing"],
    )
    print(f"Agent created: {agent.id} (Trust Level: {agent.attestation['level']})")
    
    # 3. Create an ATP envelope with confidential data
    print("\n3. Creating ATP envelope with confidential data...")
    envelope = ATPEnvelope.__new__(ATPEnvelope)  # Bypass __init__ for demo
    envelope.agent_identity = agent
    envelope.trust_level = agent.attestation["level"]
    envelope.policy_context = {
        "data_sensitivity": "confidential",
        "allowed_tools": ["read", "write"],
        "spawn_permission": False,
        "max_lifespan_seconds": 3600,
    }
    envelope.payload = {
        "messageType": "request",
        "data": {"operation": "read", "resource": "confidential-report"},
    }
    envelope.timestamp = "2024-01-01T00:00:00Z"
    envelope.signature = None
    print("Envelope created with confidential data sensitivity")
    
    # 4. Evaluate the policy before allowing the operation
    print("\n4. Evaluating policies...")
    result = policy_manager.evaluate_envelope(envelope, 'read')
    
    print(f"Policy Evaluation Result:")
    print(f"  Allowed: {result.allowed}")
    print(f"  Rule ID: {result.rule_id}")
    print(f"  Rule Name: {result.rule_name}")
    print(f"  Trust Score Impact: {result.trust_score_impact}")
    print(f"  Violations: {result.violations}")
    print(f"  Warnings: {result.warnings}")
    
    if result.allowed:
        print("Operation allowed. Proceeding with action.")
    else:
        print("Operation denied. Reason:", "; ".join(result.violations))
    
    # 5. Show policy statistics
    print("\n5. Policy Statistics:")
    stats = policy_manager.get_policy_stats()
    print(f"  Total Policies: {stats['total_policies']}")
    print(f"  Enabled Policies: {stats['enabled_policies']}")
    print(f"  Total Violations: {stats['violations']}")
    print(f"  Recent Violations (1 hour): {stats['recent_violations']}")
    print(f"  Total Templates: {stats['total_templates']}")
    print(f"  Audit Log Entries: {stats['audit_log_size']}")
    
    # 6. Show available templates
    print("\n6. Available Policy Templates:")
    templates = policy_manager.get_templates()
    for template in templates:
        print(f"  - {template.name} ({template.category}): {template.description}")
    
    # 7. Show violation history
    print("\n7. Violation History:")
    violations = policy_manager.get_violation_history()
    if violations:
        for violation in violations[-3:]:  # Show last 3 violations
            print(f"  - {violation.rule_name} ({violation.severity.value}): {violation.description}")
    else:
        print("  No violations recorded")
    
    # 8. Test with a certified agent (should be allowed)
    print("\n8. Testing with certified agent...")
    certified_agent = IAgentIdentity(
        id="certified-agent-456",
        public_key="certified-public-key",
        attestation={
            "issuer": "trust-authority",
            "level": TrustLevel.CERTIFIED,
            "issued_at": "2024-01-01T00:00:00Z",
            "expires_at": "2025-01-01T00:00:00Z",
        },
        capabilities=["data-processing", "confidential-access"],
    )
    
    # Create envelope for certified agent
    certified_envelope = ATPEnvelope.__new__(ATPEnvelope)
    certified_envelope.agent_identity = certified_agent
    certified_envelope.trust_level = certified_agent.attestation["level"]
    certified_envelope.policy_context = {
        "data_sensitivity": "confidential",
        "allowed_tools": ["read", "write"],
        "spawn_permission": False,
        "max_lifespan_seconds": 3600,
    }
    certified_envelope.payload = {
        "messageType": "request",
        "data": {"operation": "read", "resource": "confidential-report"},
    }
    certified_envelope.timestamp = "2024-01-01T00:00:00Z"
    certified_envelope.signature = None
    
    certified_result = policy_manager.evaluate_envelope(certified_envelope, 'read')
    print(f"Certified Agent Result: {'ALLOWED' if certified_result.allowed else 'DENIED'}")
    
    # 9. Show final statistics
    print("\n9. Final Statistics:")
    final_stats = policy_manager.get_policy_stats()
    print(f"  Total Violations: {final_stats['violations']}")
    print(f"  Audit Log Entries: {final_stats['audit_log_size']}")
    
    print("\nPolicy Engine Demo Complete!")

if __name__ == "__main__":
    main() 