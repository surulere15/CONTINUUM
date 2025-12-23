# Kernel

> ⚠️ **MOST PROTECTED DIRECTORY**

This directory contains the foundational governance layer of CONTINUUM.
Modifications here require elevated review procedures.

## Structure

```
kernel/
├── axioms/         # Immutable foundational constraints
├── canon/          # Civilization objectives and priorities
├── governance/     # Enforcement logic
├── state/          # Kernel state management
└── kernel_entrypoint.py
```

## Isolation Rules

The kernel **MUST NOT** import from:
- `execution/`
- `agents/`
- `cognitive/`

This isolation is enforced by CI and is non-negotiable.

## Modification Procedure

### Axioms

Axiom modifications require:
1. RFC with full rationale
2. Ethical review board assessment
3. 60-day public comment period
4. 5 maintainer approvals
5. Governance board approval
6. Immutable commit with audit trail

### Canon

Canon modifications require:
1. RFC with rationale
2. 7-day review period
3. 2 maintainer approvals
4. Governance audit entry

### Governance Logic

Standard PR process with:
1. 2 maintainer approvals
2. Full test coverage
3. No new external imports

## Human-Written Only

**AI-generated code is not permitted in this directory.**

All kernel code must be:
- Written by humans
- Reviewed by humans
- Approved by humans

## Testing

Kernel code requires 100% test coverage.

See `/tests/kernel/` for test suite.
