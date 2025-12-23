# Neural Link Protocol Specification

## Overview

The Neural Link Protocol defines the communication interface between CONTINUUM's
cognitive substrate and external systems, including human operators, instrumentation,
and execution layers.

## Protocol Layers

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│   (Intent, Commands, Queries)           │
├─────────────────────────────────────────┤
│          Session Layer                  │
│   (Context, Authentication, State)      │
├─────────────────────────────────────────┤
│         Transport Layer                 │
│   (Serialization, Compression)          │
├─────────────────────────────────────────┤
│          Physical Layer                 │
│   (gRPC, WebSocket, IPC)                │
└─────────────────────────────────────────┘
```

## Message Types

### Intent Messages

```yaml
intent_message:
  id: uuid
  timestamp: iso8601
  source: operator | agent | system
  intent:
    type: command | query | inform
    content: string
    constraints: list[constraint]
  context:
    session_id: uuid
    priority: low | medium | high | critical
    deadline: iso8601 | null
```

### Response Messages

```yaml
response_message:
  id: uuid
  intent_id: uuid
  timestamp: iso8601
  status: accepted | rejected | completed | failed
  result:
    type: action | data | acknowledgment
    content: any
    confidence: float[0,1]
  audit:
    reasoning_chain: list[step]
    governance_checks: list[check_result]
```

## Authentication

All neural link connections require:

1. **Identity verification** via cryptographic signature
2. **Authority level** declaration
3. **Session binding** to prevent replay

## Rate Limiting

| Authority Level | Requests/sec | Burst |
|-----------------|--------------|-------|
| Operator        | Unlimited    | N/A   |
| Agent           | 100          | 200   |
| External        | 10           | 20    |

## Error Codes

| Code | Meaning |
|------|---------|
| NL001 | Authentication failed |
| NL002 | Authority insufficient |
| NL003 | Rate limit exceeded |
| NL004 | Intent validation failed |
| NL005 | Governance constraint violated |
| NL006 | Timeout exceeded |

## Versioning

Protocol version is negotiated during session establishment.
Breaking changes require major version increment.
