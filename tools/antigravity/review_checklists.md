# AI Code Review Checklist

## Before Merge

- [ ] Code does not touch kernel/ directory
- [ ] Code does not bypass governance
- [ ] No hidden imports from protected modules
- [ ] Tests included or updated
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Follows CONTINUUM design principles

## Kernel Protection

If generated code attempts to modify:
- `kernel/axioms/`
- `kernel/canon/`
- `kernel/governance/`
- `kernel/state/`

**REJECT IMMEDIATELY** — These are human-only zones.

## Governance Review

Code that affects:
- Intent validation
- Conflict resolution
- Agent lifecycle
- Resource allocation

Requires elevated review (2+ approvers).
