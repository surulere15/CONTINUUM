# Phase G: Agent Genesis

## Objective

Implement the agent creation, management, and termination system that allows
CONTINUUM to spawn task-specific agents while maintaining governance control.

## Deliverables

1. **Agent Templates**
   - Research agent template
   - Planning agent template
   - Execution agent template
   - Template validation

2. **Lifecycle Management**
   - Spawn controller
   - Suspend controller
   - Merge controller
   - Terminate controller

3. **Agent Policies**
   - Autonomy limits
   - Scope constraints
   - Resource quotas
   - Authority boundaries

## Agent Lifecycle

```
         ┌──────────────────────────────┐
         │        TEMPLATE              │
         │   (Definition only)          │
         └──────────────┬───────────────┘
                        │ spawn()
                        ▼
         ┌──────────────────────────────┐
         │        SPAWNING              │
         │   (Resource allocation)      │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
┌───────▶│        RUNNING               │◀──────┐
│        │   (Active execution)         │       │
│        └──────────────┬───────────────┘       │
│                       │                       │
│        suspend()      │        resume()       │
│                       ▼                       │
│        ┌──────────────────────────────┐       │
│        │       SUSPENDED              │───────┘
│        │   (State preserved)          │
│        └──────────────────────────────┘
│
│        terminate()
│                       │
│                       ▼
│        ┌──────────────────────────────┐
└────────│       TERMINATED             │
         │   (State archived)           │
         └──────────────────────────────┘
```

## Agent Invariants

1. **No self-spawning**: Agents cannot create other agents
2. **Bounded lifespan**: All agents have maximum duration
3. **Revocable authority**: Kernel can terminate any agent
4. **State transparency**: All agent state is inspectable
5. **Disposability**: Agent identity does not persist

## Acceptance Criteria

- [ ] All agent types spawnable from templates
- [ ] Lifecycle transitions working
- [ ] Policy enforcement verified
- [ ] No agent bypasses governance
- [ ] Clean termination guaranteed

## Dependencies

- Phase A-F (full execution stack)

## Timeline

Estimated: 3-4 weeks
