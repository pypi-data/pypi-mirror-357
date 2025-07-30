"""
Policy Manager - High-level policy management for Agent Trust Protocol.

This module provides the PolicyManager class which offers convenient interfaces
for managing policies, templates, and integration with ATP.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from .policy_engine import PolicyEngine, PolicyRule, PolicyContext, PolicyEvaluationResult, PolicyViolation
from ..types import IAgentIdentity, TrustLevel, DataSensitivity
from ..core.atp_envelope import ATPEnvelope


@dataclass
class PolicyTemplate:
    """A policy template for common use cases."""
    id: str
    name: str
    description: str
    category: str  # 'security', 'compliance', 'performance', 'access', 'custom'
    template: Dict[str, Any]
    parameters: List[str]


@dataclass
class PolicyManagerConfig:
    """Configuration for policy manager."""
    enable_default_policies: bool = True
    enable_audit_logging: bool = True
    enable_real_time_monitoring: bool = True
    max_violation_history: int = 1000


class PolicyManager:
    """
    High-level policy manager for ATP.
    
    Provides convenient interfaces for managing policies, templates,
    and integration with ATP envelopes and contexts.
    """
    
    def __init__(self, config: Optional[PolicyManagerConfig] = None):
        self.config = config or PolicyManagerConfig()
        self.engine = PolicyEngine()
        self.templates: Dict[str, PolicyTemplate] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        self._initialize_templates()
        self._setup_event_handlers()
    
    def _initialize_templates(self):
        """Initialize policy templates for common use cases."""
        
        # Security templates
        self.add_template(PolicyTemplate(
            id="restrict-sensitive-data",
            name="Restrict Sensitive Data Access",
            description="Restrict access to sensitive data based on trust level",
            category="security",
            template={
                "priority": 95,
                "conditions": [
                    {
                        "type": "data",
                        "field": "sensitivity",
                        "operator": "equals",
                        "value": "${sensitivity_level}"
                    },
                    {
                        "type": "agent",
                        "field": "trust_level",
                        "operator": "not_equals",
                        "value": "${required_trust_level}",
                        "logical_operator": "and"
                    }
                ],
                "actions": [
                    {
                        "type": "deny",
                        "parameters": {"reason": "Insufficient trust level for restricted data"}
                    }
                ]
            },
            parameters=["sensitivity_level", "required_trust_level"]
        ))
        
        # Compliance templates
        self.add_template(PolicyTemplate(
            id="gdpr-data-protection",
            name="GDPR Data Protection",
            description="Enforce GDPR compliance for personal data",
            category="compliance",
            template={
                "priority": 90,
                "conditions": [
                    {
                        "type": "data",
                        "field": "contains_personal_data",
                        "operator": "equals",
                        "value": True
                    }
                ],
                "actions": [
                    {
                        "type": "log",
                        "parameters": {"compliance": "gdpr", "action": "data_access_logged"}
                    },
                    {
                        "type": "notify",
                        "parameters": {"compliance": "gdpr", "notification": "data_access_notification"}
                    }
                ]
            },
            parameters=["data_type", "retention_period"]
        ))
        
        # Performance templates
        self.add_template(PolicyTemplate(
            id="rate-limiting",
            name="Rate Limiting",
            description="Limit request frequency to prevent abuse",
            category="performance",
            template={
                "priority": 75,
                "conditions": [
                    {
                        "type": "context",
                        "field": "request_count",
                        "operator": "greater_than",
                        "value": "${max_requests}"
                    }
                ],
                "actions": [
                    {
                        "type": "modify",
                        "parameters": {"throttle": True, "delay": "${throttle_delay}"}
                    }
                ]
            },
            parameters=["max_requests", "time_window", "throttle_delay"]
        ))
        
        # Access control templates
        self.add_template(PolicyTemplate(
            id="time-based-access",
            name="Time-Based Access Control",
            description="Restrict access based on time of day",
            category="access",
            template={
                "priority": 80,
                "conditions": [
                    {
                        "type": "time",
                        "field": "hour",
                        "operator": "greater_than",
                        "value": "${end_hour}"
                    },
                    {
                        "type": "time",
                        "field": "hour",
                        "operator": "less_than",
                        "value": "${start_hour}",
                        "logical_operator": "or"
                    }
                ],
                "actions": [
                    {
                        "type": "deny",
                        "parameters": {"reason": "Access restricted during off-hours"}
                    }
                ]
            },
            parameters=["start_hour", "end_hour", "timezone"]
        ))
    
    def _setup_event_handlers(self):
        """Set up event handlers for policy engine."""
        if self.config.enable_audit_logging:
            self.engine.on_event("policy_violation", self._handle_violation)
            self.engine.on_event("policy_log", self._handle_log)
        
        if self.config.enable_real_time_monitoring:
            self.engine.on_event("policy_notification", self._handle_notification)
            self.engine.on_event("policy_escalation", self._handle_escalation)
    
    def _handle_violation(self, violation: PolicyViolation):
        """Handle policy violation event."""
        self.audit_log.append({
            "type": "violation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "violation": violation
        })
    
    def _handle_log(self, log_entry: Dict[str, Any]):
        """Handle policy log event."""
        self.audit_log.append({
            "type": "log",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "log_entry": log_entry
        })
    
    def _handle_notification(self, notification: Dict[str, Any]):
        """Handle policy notification event."""
        print(f"Policy Notification: {notification.get('parameters', {}).get('reason', 'Policy event')}")
    
    def _handle_escalation(self, escalation: Dict[str, Any]):
        """Handle policy escalation event."""
        print(f"Policy Escalation: {escalation.get('parameters', {}).get('reason', 'Critical policy violation')}")
    
    def add_template(self, template: PolicyTemplate):
        """Add a policy template."""
        self.templates[template.id] = template
    
    def create_policy_from_template(
        self, 
        template_id: str, 
        name: str, 
        parameters: Dict[str, Any]
    ) -> Optional[PolicyRule]:
        """Create a policy from template."""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Substitute parameters in template
        policy_data = self._substitute_parameters(template.template, parameters)
        
        # Create policy rule
        policy = PolicyRule(
            id=f"{template_id}-{int(datetime.now().timestamp())}",
            name=name,
            description=template.description,
            priority=policy_data.get("priority", 50),
            enabled=True,
            conditions=self._parse_conditions(policy_data.get("conditions", [])),
            actions=self._parse_actions(policy_data.get("actions", [])),
            metadata={"template_id": template_id, "parameters": parameters}
        )
        
        self.engine.add_policy(policy)
        return policy
    
    def _substitute_parameters(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute parameters in template."""
        import copy
        result = copy.deepcopy(template)
        
        def substitute_value(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                param_name = value[2:-1]
                return parameters.get(param_name, value)
            return value
        
        def substitute_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    obj[key] = substitute_recursive(value)
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    obj[i] = substitute_recursive(value)
            else:
                obj = substitute_value(obj)
            return obj
        
        return substitute_recursive(result)
    
    def _parse_conditions(self, conditions_data: List[Dict[str, Any]]) -> List[Any]:
        """Parse conditions from template data."""
        from .policy_engine import PolicyCondition, PolicyConditionType, PolicyOperator
        
        conditions = []
        for cond_data in conditions_data:
            condition = PolicyCondition(
                type=PolicyConditionType(cond_data["type"]),
                field=cond_data["field"],
                operator=PolicyOperator(cond_data["operator"]),
                value=cond_data["value"],
                logical_operator=cond_data.get("logical_operator")
            )
            conditions.append(condition)
        return conditions
    
    def _parse_actions(self, actions_data: List[Dict[str, Any]]) -> List[Any]:
        """Parse actions from template data."""
        from .policy_engine import PolicyAction, PolicyActionType
        
        actions = []
        for action_data in actions_data:
            action = PolicyAction(
                type=PolicyActionType(action_data["type"]),
                parameters=action_data.get("parameters"),
                metadata=action_data.get("metadata")
            )
            actions.append(action)
        return actions
    
    def evaluate_envelope(self, envelope: ATPEnvelope, operation: str) -> PolicyEvaluationResult:
        """Evaluate policies for an ATP envelope."""
        # Safely calculate envelope size
        try:
            envelope_size = len(str(envelope.__dict__))
        except:
            envelope_size = 0
        
        # Safely get trust score if method exists
        try:
            trust_score = envelope.get_trust_score()
        except AttributeError:
            trust_score = 0
        
        context = PolicyContext(
            agent_identity=envelope.agent_identity,
            trust_level=envelope.trust_level,
            data_sensitivity=getattr(envelope.policy_context, 'data_sensitivity', None) if envelope.policy_context else None,
            operation=operation,
            resource=operation,
            timestamp=envelope.timestamp,
            environment={
                "envelope_size": envelope_size,
                "has_signature": bool(envelope.signature),
                "trust_score": trust_score
            },
            session_data={}
        )
        
        return self.engine.evaluate_policies(context)
    
    def evaluate_context(self, context: PolicyContext) -> PolicyEvaluationResult:
        """Evaluate policies for a specific context."""
        return self.engine.evaluate_policies(context)
    
    def can_perform_operation(
        self,
        agent_identity: IAgentIdentity,
        trust_level: TrustLevel,
        operation: str,
        data_sensitivity: Optional[DataSensitivity] = None
    ) -> bool:
        """Check if an agent can perform an operation."""
        context = PolicyContext(
            agent_identity=agent_identity,
            trust_level=trust_level,
            data_sensitivity=data_sensitivity,
            operation=operation,
            resource=operation,
            timestamp=datetime.now(timezone.utc).isoformat(),
            environment={},
            session_data={}
        )
        
        result = self.engine.evaluate_policies(context)
        return result.allowed
    
    def get_templates(self) -> List[PolicyTemplate]:
        """Get all policy templates."""
        return list(self.templates.values())
    
    def get_templates_by_category(self, category: str) -> List[PolicyTemplate]:
        """Get templates by category."""
        return [t for t in self.templates.values() if t.category == category]
    
    def get_policies(self) -> List[PolicyRule]:
        """Get all policies."""
        return self.engine.get_policies()
    
    def get_policies_by_category(self, category: str) -> List[PolicyRule]:
        """Get policies by category."""
        return [p for p in self.engine.get_policies() if p.metadata and p.metadata.get("category") == category]
    
    def set_policy_enabled(self, policy_id: str, enabled: bool) -> bool:
        """Enable or disable a policy."""
        return self.engine.set_policy_enabled(policy_id, enabled)
    
    def remove_policy(self, policy_id: str) -> bool:
        """Remove a policy."""
        return self.engine.remove_policy(policy_id)
    
    def get_violation_history(self) -> List[PolicyViolation]:
        """Get violation history."""
        return self.engine.get_violation_history()
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log."""
        return self.audit_log.copy()
    
    def clear_audit_log(self):
        """Clear audit log."""
        self.audit_log.clear()
    
    def get_policy_stats(self) -> Dict[str, Any]:
        """Get policy statistics."""
        engine_stats = self.engine.get_policy_stats()
        template_stats = {
            "total_templates": len(self.templates),
            "templates_by_category": self._get_template_category_stats()
        }
        
        return {
            **engine_stats,
            **template_stats,
            "audit_log_size": len(self.audit_log)
        }
    
    def _get_template_category_stats(self) -> Dict[str, int]:
        """Get template statistics by category."""
        stats = {}
        for template in self.templates.values():
            stats[template.category] = stats.get(template.category, 0) + 1
        return stats
    
    def export_policies(self) -> str:
        """Export policies to JSON."""
        return json.dumps({
            "policies": [p.__dict__ for p in self.engine.get_policies()],
            "templates": [t.__dict__ for t in self.templates.values()],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, indent=2, default=str)
    
    def import_policies(self, json_data: str):
        """Import policies from JSON."""
        try:
            data = json.loads(json_data)
            
            if "policies" in data:
                for policy_data in data["policies"]:
                    # Reconstruct policy from data
                    policy = PolicyRule(**policy_data)
                    self.engine.add_policy(policy)
            
            if "templates" in data:
                for template_data in data["templates"]:
                    template = PolicyTemplate(**template_data)
                    self.add_template(template)
            
            print(f"✅ Imported {len(data.get('policies', []))} policies and {len(data.get('templates', []))} templates")
        except Exception as e:
            raise ValueError(f"Failed to import policies: {e}")
    
    def get_policy_recommendations(self) -> List[Dict[str, Any]]:
        """Get policy recommendations based on violations."""
        violations = self.engine.get_violation_history()
        recommendations = []
        
        # Analyze violation patterns
        violation_patterns = {}
        for violation in violations:
            pattern = f"{violation.rule_id}-{violation.severity.value}"
            violation_patterns[pattern] = violation_patterns.get(pattern, 0) + 1
        
        # Generate recommendations
        for pattern, count in violation_patterns.items():
            if count > 5:
                recommendations.append({
                    "type": "high_violations",
                    "pattern": pattern,
                    "count": count,
                    "recommendation": f"Consider reviewing policy {pattern} due to high violation count"
                })
        
        return recommendations


# Global instance
_policy_manager_instance: Optional[PolicyManager] = None


def get_policy_manager(config: Optional[PolicyManagerConfig] = None) -> PolicyManager:
    """Get the global policy manager instance."""
    global _policy_manager_instance
    if _policy_manager_instance is None:
        _policy_manager_instance = PolicyManager(config)
    return _policy_manager_instance 