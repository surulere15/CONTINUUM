# Agent Genesis Specification

## Overview

Agent Genesis defines how agents are created, configured, and deployed within
CONTINUUM. Agents are **disposable** by design—they exist to execute tasks
and are terminated when complete.

## Core Principles

1. **Agents have no inherent right to exist**
2. **Identity does not persist without kernel approval**
3. **Capabilities are granted, not assumed**
4. **Lifecycle is explicitly controlled**

## Agent Template

```yaml
agent_template:
  id: string
  type: research | planning | execution | composite
  name: string
  description: string

  capabilities:
    - capability_id: string
      scope: string
      constraints: list[constraint]

  resources:
    cpu: cpu_units
    memory: bytes
    network: boolean
    tools: list[tool_id]

  lifecycle:
    max_duration: duration
    checkpoint_interval: duration | null
    termination_conditions:
      - condition: expression
        action: terminate | suspend | notify

  governance:
    autonomy_level: low | medium | high
    requires_approval: list[action_type]
    audit_frequency: always | sampling | none
```

## Lifecycle Management

### Spawn

```python
def spawn(template_id: str, context: Context) -> Agent:
    """
    Create new agent from template.
    
    1. Validate spawn request against governance
    2. Allocate resources from pool
    3. Initialize agent state
    4. Register with runtime
    5. Begin execution
    """
```

### Suspend

```python
def suspend(agent_id: str, reason: str) -> Checkpoint:
    """
    Pause agent execution, preserving state.
    
    - Creates recoverable checkpoint
    - Releases compute resources
    - Maintains memory state
    """
```

### Merge

```python
def merge(agent_ids: List[str]) -> Agent:
    """
    Combine multiple agents into one.
    
    - Requires compatible types
    - Merges memory states
    - Validates combined capabilities
    - Requires governance approval
    """
```

### Terminate

```python
def terminate(agent_id: str, reason: str) -> TerminationReport:
    """
    End agent existence.
    
    - Archive final state
    - Release all resources
    - Log termination reason
    - Cannot be reversed
    """
```

## Autonomy Levels

| Level | Description | Approval Required |
|-------|-------------|-------------------|
| Low | Every action requires approval | All actions |
| Medium | Routine actions auto-approved | Resource acquisition, external calls |
| High | Most actions auto-approved | Governance-affecting actions only |

## Agent Policies

### Autonomy Limits

```yaml
autonomy_limits:
  resource_acquisition:
    max_cpu_request: 4
    max_memory_request: 8GB
    max_network_bandwidth: 100Mbps

  action_limits:
    max_external_calls_per_minute: 10
    max_file_operations: 100
    forbidden_operations:
      - system_modification
      - kernel_access
      - agent_spawning  # Agents cannot spawn other agents

  escalation:
    on_uncertainty: always
    on_conflict: always
    on_high_impact: always
```

### Scope Constraints

```yaml
scope_constraints:
  domain_restrictions:
    - allowed_domains: list[string]
    - forbidden_topics: list[string]

  temporal_restrictions:
    - operating_hours: timerange | null
    - blackout_periods: list[timerange]

  authority_restrictions:
    - cannot_modify: [kernel, governance, canon]
    - cannot_access: [secrets, credentials]
```

## Agent Types

### Research Agent

- **Purpose**: Information gathering and analysis
- **Autonomy**: High (within domain)
- **Resources**: CPU-light, network-heavy
- **Duration**: Hours

### Planning Agent

- **Purpose**: Strategy and task decomposition
- **Autonomy**: Medium
- **Resources**: CPU-medium, memory-heavy
- **Duration**: Minutes to hours

### Execution Agent

- **Purpose**: Action execution
- **Autonomy**: Low
- **Resources**: Variable based on task
- **Duration**: Task-dependent
