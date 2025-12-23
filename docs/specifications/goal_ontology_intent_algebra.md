# Goal Ontology & Intent Algebra

## Overview

This specification defines the formal system for representing goals, intents,
and their algebraic relationships within CONTINUUM.

## Goal Ontology

### Hierarchy

```
Civilization Objectives (Canon)
        │
        ├── Strategic Goals
        │       │
        │       ├── Tactical Objectives
        │       │       │
        │       │       └── Operational Tasks
        │       │
        │       └── Tactical Objectives
        │
        └── Strategic Goals
```

### Goal Schema

```yaml
goal:
  id: uuid
  type: civilization | strategic | tactical | operational
  parent: goal_id | null
  name: string
  description: string
  priority:
    absolute: integer
    relative_to_siblings: float
  constraints:
    - axiom_ref: string
  success_criteria:
    - metric: string
      target: expression
  time_horizon: duration | indefinite
  decomposition_strategy: sequential | parallel | conditional
```

## Intent Algebra

### Primitives

| Symbol | Meaning |
|--------|---------|
| I | Intent |
| G | Goal |
| A | Action |
| C | Constraint |
| ⊢ | Satisfies |
| ∧ | Conjunction (AND) |
| ∨ | Disjunction (OR) |
| → | Implication |
| ⊥ | Contradiction/Failure |

### Operations

**Composition**:
```
I₁ ∘ I₂ = Intent that achieves both I₁ and I₂
```

**Derivation**:
```
G → I : Goal G derives intent I
I → A : Intent I produces action A
```

**Constraint Application**:
```
I ∧ C = Constrained intent
If (I ∧ C) = ⊥, intent is rejected
```

### Conflict Resolution

When intents conflict:

```
resolve(I₁, I₂) =
    if priority(I₁) > priority(I₂): I₁
    elif priority(I₂) > priority(I₁): I₂
    else: escalate_to_governance()
```

## Validation Rules

1. **Completeness**: Every intent must trace to a goal
2. **Consistency**: No intent may violate axioms
3. **Grounding**: Operational intents must map to actions
4. **Explainability**: Derivation chain must be recordable

## Examples

### Valid Intent Chain

```
Civilization: Maximize human flourishing
    → Strategic: Improve access to education
        → Tactical: Develop learning platform
            → Operational: Implement user authentication
                → Action: Create login endpoint
```

### Invalid Intent (Constraint Violation)

```
Operational: Collect user data without consent
    ∧ Constraint: Privacy preservation (from canon)
    = ⊥ (Contradiction - Rejected)
```

## Implementation

Intent algebra is implemented in:
- `kernel/governance/intent_validator.py`
- `cognitive/orchestration/planner.py`
