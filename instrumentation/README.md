# Instrumentation Layer

Civilization-scale signal observation for CONTINUUM.

> ⚠️ **Signals are facts, not feedback.**

## Structure

```
instrumentation/
├── schema/           # Signal data structures
├── ingestion/        # Data adapters and registry
├── normalization/    # Unit and temporal alignment
├── storage/          # Append-only persistence
├── access/           # Read-only API
└── tests/            # Rejection path tests
```

## Hard Law

Phase C is allowed to:
- Define signal schemas
- Ingest signals from trusted sources
- Normalize and timestamp signals
- Persist signals immutably
- Expose read-only queries

Phase C is **NOT** allowed to:
- Interpret signals
- Optimize against signals
- Trigger alerts or actions
- Modify objectives
- Influence planning or execution
- Aggregate into scores or utilities

## Isolation

**No imports from**: `kernel/`, `cognitive/`, `execution/`, `agents/`

Kernel cannot command instrumentation.
