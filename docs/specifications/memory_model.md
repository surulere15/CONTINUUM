# Memory Model Specification

## Overview

CONTINUUM's memory architecture provides structured storage and retrieval for
different types of information, supporting both operational needs and long-term
learning while maintaining governance constraints.

## Memory Types

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY ROUTER                            │
├────────────┬────────────┬────────────┬────────────┬────────┤
│  Working   │  Episodic  │  Semantic  │   Value    │ Audit  │
│  Memory    │  Memory    │  Memory    │  Memory    │  Log   │
├────────────┼────────────┼────────────┼────────────┼────────┤
│ Short-term │ Experiences│ Knowledge  │ Objectives │ Trace  │
│ Context    │ Timeline   │ Graph      │ Weights    │ Events │
└────────────┴────────────┴────────────┴────────────┴────────┘
```

## Working Memory

**Purpose**: Current execution context and temporary state.

```yaml
working_memory:
  capacity: bounded
  retention: session
  access: read-write
  contents:
    - active_intents: list[Intent]
    - current_context: Context
    - pending_actions: queue[Action]
    - scratch_space: map[key, value]
```

**Constraints**:
- Maximum size: 1MB
- Automatic garbage collection
- No persistence across sessions

## Episodic Memory

**Purpose**: Record of past experiences and outcomes.

```yaml
episodic_memory:
  capacity: unbounded (with archival)
  retention: permanent
  access: read-only (append-only write)
  contents:
    - episodes: list[Episode]
    - temporal_index: btree[timestamp, episode_id]
    - outcome_index: btree[outcome_type, episode_id]
```

**Episode Schema**:
```yaml
episode:
  id: uuid
  timestamp: iso8601
  context: Context
  intent: Intent
  actions: list[Action]
  outcome: Outcome
  reflection: string | null
```

## Semantic Memory

**Purpose**: Factual knowledge and learned relationships.

```yaml
semantic_memory:
  structure: knowledge_graph
  retention: permanent (with decay)
  access: read-write (with validation)
  contents:
    - entities: set[Entity]
    - relations: set[Relation]
    - facts: set[Fact]
```

**Governance**:
- New facts require source attribution
- Contradictions trigger review
- Confidence scores decay over time

## Value Memory

**Purpose**: Learned preferences and objective weights.

```yaml
value_memory:
  structure: weighted_graph
  retention: permanent
  access: read-write (kernel approval required)
  contents:
    - objective_weights: map[objective_id, weight]
    - preference_rankings: partial_order
    - constraint_strengths: map[constraint_id, strength]
```

**Constraints**:
- Modifications require kernel approval
- Changes are logged to audit
- Canon objectives cannot be down-weighted below threshold

## Memory Router

The router directs queries to appropriate memory stores:

```python
class MemoryRouter:
    def route(query: Query) -> Memory:
        """Direct query to appropriate memory store."""

    def consolidate() -> None:
        """Move working memory to long-term stores."""

    def recall(context: Context) -> RelevantMemories:
        """Retrieve contextually relevant memories."""
```

## Retention Policies

| Memory Type | Retention | Archival |
|-------------|-----------|----------|
| Working | Session | None |
| Episodic | 1 year active | Cold storage |
| Semantic | Indefinite | Confidence decay |
| Value | Permanent | Full audit trail |
