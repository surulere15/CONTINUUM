# Cognitive Layer

The cognitive layer provides reasoning, planning, and decision-making capabilities
for CONTINUUM, always operating within kernel governance constraints.

## Structure

```
cognitive/
├── orchestration/     # High-level task coordination
├── substrate/         # Model interfaces and reasoning
└── evaluation/        # Quality and coherence checking
```

## Governance Relationship

The cognitive layer **cannot**:
- Modify kernel axioms or canon
- Bypass governance validation
- Execute actions directly (must go through execution layer)

The cognitive layer **must**:
- Submit all intents to kernel for validation
- Trace reasoning to canon objectives
- Maintain explainability

## Components

### Orchestration

- **Planner**: Decomposes goals into tasks
- **Scenario Simulator**: Evaluates potential outcomes
- **Reasoning Router**: Directs queries to appropriate reasoners
- **Context Compressor**: Manages context window efficiently

### Substrate

- **Model Registry**: Tracks available models and capabilities
- **Inference Gateway**: Routes inference requests
- **Symbolic Reasoner**: Formal logic and constraint solving

### Evaluation

- **Coherence Checks**: Verifies reasoning consistency
- **Outcome Scoring**: Assesses predicted outcomes
- **Regression Tests**: Catches reasoning regressions
