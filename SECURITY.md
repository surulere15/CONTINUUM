# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

### Standard Vulnerabilities

For standard security vulnerabilities, please email:

**security@continuum.dev**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a detailed response
within 7 days.

### Kernel/Governance Vulnerabilities

> ⚠️ **Critical: Governance bypass or kernel vulnerabilities require elevated handling.**

For vulnerabilities affecting:
- Kernel axioms or canon
- Governance mechanisms
- Intent validation
- Objective persistence
- Rollback controllers

Please use our encrypted channel:

**kernel-security@continuum.dev** (PGP key available in `/security/pgp-key.asc`)

These reports are escalated immediately to the governance review board.

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────┐
│          Human Authority Layer          │
│        (Final override capability)      │
├─────────────────────────────────────────┤
│           Governance Layer              │
│   (Intent validation, conflict res.)    │
├─────────────────────────────────────────┤
│             Kernel Layer                │
│    (Axioms, canon, state management)    │
├─────────────────────────────────────────┤
│           Execution Layer               │
│         (Sandboxed, monitored)          │
└─────────────────────────────────────────┘
```

### Threat Models

See `/docs/threat_models/` for detailed analysis of:
- Misalignment risks
- Runaway optimization
- Governance bypass
- Human failure modes

## Security Invariants

The following invariants must never be violated:

1. **Kernel isolation**: No execution-layer code may modify kernel state directly
2. **Audit completeness**: All state changes must be logged
3. **Rollback capability**: Any action must be reversible within defined bounds
4. **Human override**: Human authority supersedes all automated decisions

## Bug Bounty

We offer bounties for verified security vulnerabilities:

| Severity | Bounty |
|----------|--------|
| Critical (Kernel/Governance) | $10,000+ |
| High | $5,000 |
| Medium | $1,000 |
| Low | $250 |

## Disclosure Policy

We follow responsible disclosure:
- 90 days for standard vulnerabilities
- 30 days for critical kernel vulnerabilities
- Coordinated disclosure with reporter
