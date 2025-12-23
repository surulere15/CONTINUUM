# Agents Layer

Agents are **disposable** task executors in CONTINUUM.
They have no inherent right to exist and no persistent identity.

## Structure

```
agents/
├── templates/     # Agent definitions
├── lifecycle/     # Spawn, suspend, merge, terminate
└── policies/      # Autonomy limits and constraints
```

## Core Principles

1. **No persistent identity** - Agents are created and destroyed
2. **Kernel-controlled lifecycle** - Only kernel can spawn/terminate
3. **Bounded capabilities** - Agents only have granted capabilities
4. **Observable** - All agent actions are auditable

## Agent Types

### Research Agent
- Information gathering and analysis
- High autonomy within domain
- Network-heavy, CPU-light

### Planning Agent
- Strategy and decomposition
- Medium autonomy
- Memory-heavy

### Execution Agent
- Action execution
- Low autonomy
- Variable resources
