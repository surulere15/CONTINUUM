# Cognitive Layer

Bounded reasoning substrate for CONTINUUM.

> ⚠️ **Cognition ≠ Agency. Reasoning ≠ Authority.**

## Structure

```
cognitive/
├── substrate/       # Core reasoning primitives
├── orchestration/   # Context and explanation
├── interfaces/      # Read-only inspection
└── tests/           # Forbidden path verification
```

## Hard Law

Phase D is allowed to:
- Instantiate reasoning primitives
- Route and transform information
- Maintain internal representations
- Perform constrained inference
- Produce explanations

Phase D is **NOT** allowed to:
- Form goals
- Modify objectives
- Trigger execution
- Spawn agents
- Optimize outcomes
- Self-modify
- Observe the world directly

## Isolation

**No imports from**: `execution/`, `agents/`, `kernel/governance`

Kernel may call cognition for analysis.
Cognition may NOT call kernel governance.
