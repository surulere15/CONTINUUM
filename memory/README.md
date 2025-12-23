# Memory Layer

The memory layer provides structured storage and retrieval for
different types of information in CONTINUUM.

## Structure

```
memory/
├── working_memory/    # Current session context
├── episodic_memory/   # Past experiences
├── semantic_memory/   # Facts and knowledge
├── value_memory/      # Objective weights
└── memory_router.py   # Routes queries to stores
```

## Memory Types

### Working Memory
- Short-term, session-scoped
- Current task context
- Pending actions queue

### Episodic Memory
- Long-term experience storage
- Timestamped episodes
- Outcome tracking

### Semantic Memory
- Knowledge graph
- Facts with confidence scores
- Source attribution

### Value Memory
- Objective weights
- Preference rankings
- Requires kernel approval for changes

## Governance

Memory modifications affecting value weights require kernel approval.
All memory access is logged for audit purposes.
