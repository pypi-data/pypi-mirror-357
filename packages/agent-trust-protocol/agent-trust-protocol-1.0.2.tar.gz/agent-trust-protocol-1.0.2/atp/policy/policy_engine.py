"""
Policy Engine - Core policy enforcement for Agent Trust Protocol.

This module provides the PolicyEngine class which handles rule-based policy
evaluation, violation tracking, and event emission for ATP.
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock

from ..types import IAgentIdentity, TrustLevel, DataSensitivity


class PolicyActionType(str, Enum):
    """Types of policy actions."""
    ALLOW = "allow"
    DENY = "deny"
    MODIFY = "modify"
    LOG = "log"
    NOTIFY = "notify"
    QUARANTINE = "quarantine"
    ESCALATE = "escalate"


class PolicyConditionType(str, Enum):
    """Types of policy conditions."""
    AGENT = "agent"
    DATA = "data"
    TIME = "time"
    RESOURCE = "resource"
    CONTEXT = "context"
    CUSTOM = "custom"


class PolicyOperator(str, Enum):
    """Policy condition operators."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


class ViolationSeverity(str, Enum):
    """Violation severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PolicyCondition:
    """A policy condition."""
    type: PolicyConditionType
    field: str
    operator: PolicyOperator
    value: Any
    logical_operator: Optional[str] = None  # 'and' or 'or'


@dataclass
class PolicyAction:
    """A policy action."""
    type: PolicyActionType
    parameters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PolicyRule:
    """A policy rule."""
    id: str
    name: str
    description: str
    priority: int  # Higher number = higher priority
    enabled: bool = True
    conditions: List[PolicyCondition] = field(default_factory=list)
    actions: List[PolicyAction] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PolicyContext:
    """Context for policy evaluation."""
    agent_identity: IAgentIdentity
    trust_level: TrustLevel
    data_sensitivity: Optional[DataSensitivity] = None
    operation: str = ""
    resource: Optional[str] = None
    timestamp: str = ""
    environment: Optional[Dict[str, Any]] = None
    session_data: Optional[Dict[str, Any]] = None


@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation."""
    allowed: bool = True
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    actions: List[PolicyAction] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    trust_score_impact: int = 0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PolicyViolation:
    """A policy violation record."""
    rule_id: str
    rule_name: str
    severity: ViolationSeverity
    description: str
    timestamp: str
    context: PolicyContext
    actions: List[PolicyAction]


class PolicyEngine:
    """
    Core policy engine for ATP.
    
    Handles rule-based policy evaluation, violation tracking,
    and event emission for policy-related activities.
    """
    
    def __init__(self):
        self._policies: Dict[str, PolicyRule] = {}
        self._violation_history: List[PolicyViolation] = []
        self._custom_evaluators: Dict[str, Callable] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._lock = Lock()
        
        # Initialize default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default security policies."""
        
        # Trust level access control
        self.add_policy(PolicyRule(
            id="trust-level-access",
            name="Trust Level Access Control",
            description="Enforce access control based on trust levels",
            priority=100,
            conditions=[
                PolicyCondition(
                    type=PolicyConditionType.AGENT,
                    field="trust_level",
                    operator=PolicyOperator.IN,
                    value=["certified", "verified", "unverified", "sandboxed"]
                )
            ],
            actions=[
                PolicyAction(
                    type=PolicyActionType.ALLOW,
                    parameters={"reason": "Valid trust level"}
                )
            ]
        ))
        
        # Data sensitivity control
        self.add_policy(PolicyRule(
            id="data-sensitivity-control",
            name="Data Sensitivity Control",
            description="Control access based on data sensitivity levels",
            priority=90,
            conditions=[
                PolicyCondition(
                    type=PolicyConditionType.DATA,
                    field="sensitivity",
                    operator=PolicyOperator.EQUALS,
                    value="restricted"
                )
            ],
            actions=[
                PolicyAction(
                    type=PolicyActionType.DENY,
                    parameters={"reason": "Restricted data access requires certified trust level"}
                )
            ]
        ))
        
        # Business hours restriction
        self.add_policy(PolicyRule(
            id="business-hours-only",
            name="Business Hours Restriction",
            description="Restrict operations to business hours",
            priority=80,
            enabled=False,  # Disabled by default
            conditions=[
                PolicyCondition(
                    type=PolicyConditionType.TIME,
                    field="hour",
                    operator=PolicyOperator.GREATER_THAN,
                    value=17
                ),
                PolicyCondition(
                    type=PolicyConditionType.TIME,
                    field="hour",
                    operator=PolicyOperator.LESS_THAN,
                    value=9,
                    logical_operator="or"
                )
            ],
            actions=[
                PolicyAction(
                    type=PolicyActionType.DENY,
                    parameters={"reason": "Operation outside business hours"}
                )
            ]
        ))
        
        # Resource usage limits
        self.add_policy(PolicyRule(
            id="resource-usage-limits",
            name="Resource Usage Limits",
            description="Limit resource consumption",
            priority=70,
            conditions=[
                PolicyCondition(
                    type=PolicyConditionType.RESOURCE,
                    field="cpu_usage",
                    operator=PolicyOperator.GREATER_THAN,
                    value=80
                )
            ],
            actions=[
                PolicyAction(
                    type=PolicyActionType.MODIFY,
                    parameters={"throttle": True, "reason": "High CPU usage detected"}
                )
            ]
        ))
        
        # Capability validation
        self.add_policy(PolicyRule(
            id="capability-validation",
            name="Capability Validation",
            description="Validate agent capabilities for operations",
            priority=85,
            conditions=[
                PolicyCondition(
                    type=PolicyConditionType.AGENT,
                    field="capabilities",
                    operator=PolicyOperator.CONTAINS,
                    value="required_capability"
                )
            ],
            actions=[
                PolicyAction(
                    type=PolicyActionType.ALLOW,
                    parameters={"reason": "Agent has required capabilities"}
                )
            ]
        ))
    
    def add_policy(self, policy: PolicyRule) -> None:
        """Add a new policy rule."""
        with self._lock:
            self._policies[policy.id] = policy
            self._emit_event("policy_added", policy)
            print(f"Policy added: {policy.name} (ID: {policy.id})")
    
    def remove_policy(self, policy_id: str) -> bool:
        """Remove a policy rule."""
        with self._lock:
            if policy_id in self._policies:
                del self._policies[policy_id]
                self._emit_event("policy_removed", policy_id)
                print(f"Policy removed: {policy_id}")
                return True
            return False
    
    def set_policy_enabled(self, policy_id: str, enabled: bool) -> bool:
        """Enable or disable a policy."""
        with self._lock:
            if policy_id in self._policies:
                self._policies[policy_id].enabled = enabled
                self._emit_event("policy_updated", self._policies[policy_id])
                print(f"Policy {policy_id} {'enabled' if enabled else 'disabled'}")
                return True
            return False
    
    def evaluate_policies(self, context: PolicyContext) -> PolicyEvaluationResult:
        """Evaluate policies for a given context."""
        result = PolicyEvaluationResult()
        
        # Sort policies by priority (highest first)
        sorted_policies = sorted(
            [p for p in self._policies.values() if p.enabled],
            key=lambda p: p.priority,
            reverse=True
        )
        
        for policy in sorted_policies:
            evaluation = self._evaluate_policy(policy, context)
            
            if evaluation["matched"]:
                result.rule_id = policy.id
                result.rule_name = policy.name
                result.actions.extend(evaluation["actions"])
                
                # Check for deny actions
                deny_action = next((a for a in evaluation["actions"] if a.type == PolicyActionType.DENY), None)
                if deny_action:
                    result.allowed = False
                    result.violations.append(
                        f"Policy violation: {policy.name} - {deny_action.parameters.get('reason', 'Access denied')}"
                    )
                    result.trust_score_impact -= 20
                
                # Check for allow actions
                allow_action = next((a for a in evaluation["actions"] if a.type == PolicyActionType.ALLOW), None)
                if allow_action:
                    result.allowed = True
                    result.trust_score_impact += 5
                
                # Handle other action types
                for action in evaluation["actions"]:
                    self._execute_action(action, context)
                
                # Record violation if denied
                if not result.allowed:
                    self._record_violation(policy, context, evaluation["actions"])
                
                # Stop evaluation if a high-priority rule denies access
                if not result.allowed and policy.priority >= 90:
                    break
        
        return result
    
    def _evaluate_policy(self, policy: PolicyRule, context: PolicyContext) -> Dict[str, Any]:
        """Evaluate a single policy rule."""
        conditions_met = True
        logical_operator = "and"
        
        for i, condition in enumerate(policy.conditions):
            condition_met = self._evaluate_condition(condition, context)
            
            if i == 0:
                conditions_met = condition_met
            else:
                if logical_operator == "and":
                    conditions_met = conditions_met and condition_met
                else:
                    conditions_met = conditions_met or condition_met
            
            logical_operator = condition.logical_operator or "and"
        
        return {
            "matched": conditions_met,
            "actions": policy.actions if conditions_met else []
        }
    
    def _evaluate_condition(self, condition: PolicyCondition, context: PolicyContext) -> bool:
        """Evaluate a single condition."""
        value = self._extract_field_value(condition.field, context)
        
        if condition.operator == PolicyOperator.EQUALS:
            return value == condition.value
        elif condition.operator == PolicyOperator.NOT_EQUALS:
            return value != condition.value
        elif condition.operator == PolicyOperator.CONTAINS:
            if isinstance(value, list):
                return condition.value in value
            else:
                return str(condition.value) in str(value)
        elif condition.operator == PolicyOperator.NOT_CONTAINS:
            if isinstance(value, list):
                return condition.value not in value
            else:
                return str(condition.value) not in str(value)
        elif condition.operator == PolicyOperator.GREATER_THAN:
            if value is None or condition.value is None:
                return False
            try:
                return float(value) > float(condition.value)
            except (TypeError, ValueError):
                return False
        elif condition.operator == PolicyOperator.LESS_THAN:
            if value is None or condition.value is None:
                return False
            try:
                return float(value) < float(condition.value)
            except (TypeError, ValueError):
                return False
        elif condition.operator == PolicyOperator.IN:
            return value in condition.value if isinstance(condition.value, list) else False
        elif condition.operator == PolicyOperator.NOT_IN:
            return value not in condition.value if isinstance(condition.value, list) else True
        elif condition.operator == PolicyOperator.REGEX:
            return bool(re.search(condition.value, str(value)))
        elif condition.operator == PolicyOperator.EXISTS:
            return value is not None
        elif condition.operator == PolicyOperator.NOT_EXISTS:
            return value is None
        else:
            return False
    
    def _extract_field_value(self, field: str, context: PolicyContext) -> Any:
        """Extract field value from context."""
        field_parts = field.split('.')
        value = context
        
        for part in field_parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def _execute_action(self, action: PolicyAction, context: PolicyContext) -> None:
        """Execute a policy action."""
        if action.type == PolicyActionType.LOG:
            self._emit_event("policy_log", {
                "action": action.type.value,
                "context": context,
                "parameters": action.parameters,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        elif action.type == PolicyActionType.NOTIFY:
            self._emit_event("policy_notification", {
                "action": action.type.value,
                "context": context,
                "parameters": action.parameters,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        elif action.type == PolicyActionType.QUARANTINE:
            self._emit_event("policy_quarantine", {
                "action": action.type.value,
                "context": context,
                "parameters": action.parameters,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        elif action.type == PolicyActionType.ESCALATE:
            self._emit_event("policy_escalation", {
                "action": action.type.value,
                "context": context,
                "parameters": action.parameters,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        elif action.type == PolicyActionType.MODIFY:
            self._emit_event("policy_modification", {
                "action": action.type.value,
                "context": context,
                "parameters": action.parameters,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
    
    def _record_violation(self, policy: PolicyRule, context: PolicyContext, actions: List[PolicyAction]) -> None:
        """Record a policy violation."""
        violation = PolicyViolation(
            rule_id=policy.id,
            rule_name=policy.name,
            severity=self._determine_severity(policy.priority),
            description=f"Policy violation: {policy.name}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            context=context,
            actions=actions
        )
        
        with self._lock:
            self._violation_history.append(violation)
            self._emit_event("policy_violation", violation)
            
            # Keep only last 1000 violations
            if len(self._violation_history) > 1000:
                self._violation_history = self._violation_history[-1000:]
    
    def _determine_severity(self, priority: int) -> ViolationSeverity:
        """Determine violation severity based on policy priority."""
        if priority >= 90:
            return ViolationSeverity.CRITICAL
        elif priority >= 70:
            return ViolationSeverity.HIGH
        elif priority >= 50:
            return ViolationSeverity.MEDIUM
        else:
            return ViolationSeverity.LOW
    
    def add_custom_evaluator(self, condition_type: str, evaluator: Callable) -> None:
        """Add custom condition evaluator."""
        self._custom_evaluators[condition_type] = evaluator
    
    def get_policies(self) -> List[PolicyRule]:
        """Get all policies."""
        return list(self._policies.values())
    
    def get_policy(self, policy_id: str) -> Optional[PolicyRule]:
        """Get policy by ID."""
        return self._policies.get(policy_id)
    
    def get_violation_history(self) -> List[PolicyViolation]:
        """Get violation history."""
        return self._violation_history.copy()
    
    def clear_violation_history(self) -> None:
        """Clear violation history."""
        with self._lock:
            self._violation_history.clear()
    
    def get_policy_stats(self) -> Dict[str, Any]:
        """Get policy statistics."""
        enabled_policies = sum(1 for p in self._policies.values() if p.enabled)
        
        # Count recent violations (last hour)
        one_hour_ago = datetime.now(timezone.utc).replace(microsecond=0)
        recent_violations = sum(
            1 for v in self._violation_history
            if datetime.fromisoformat(v.timestamp.replace('Z', '+00:00')) > one_hour_ago
        )
        
        return {
            "total_policies": len(self._policies),
            "enabled_policies": enabled_policies,
            "violations": len(self._violation_history),
            "recent_violations": recent_violations
        }
    
    def on_event(self, event_type: str, handler: Callable) -> None:
        """Register event handler."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def _emit_event(self, event_type: str, data: Any) -> None:
        """Emit an event to registered handlers."""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")


# Global instance
_policy_engine_instance: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get the global policy engine instance."""
    global _policy_engine_instance
    if _policy_engine_instance is None:
        _policy_engine_instance = PolicyEngine()
    return _policy_engine_instance 