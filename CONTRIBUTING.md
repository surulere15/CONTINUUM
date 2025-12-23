# Contributing to CONTINUUM

Thank you for your interest in contributing to CONTINUUM. This document outlines
contribution guidelines with special attention to kernel modification procedures.

## General Contribution Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/your-feature`)
3. **Make** your changes following code standards
4. **Test** your changes thoroughly
5. **Submit** a pull request

## Directory-Specific Guidelines

### 🔴 Kernel (`/kernel`) — ELEVATED REVIEW REQUIRED

> ⚠️ **The kernel is the most protected directory in CONTINUUM.**

Modifications to `/kernel` require:

- [ ] Two maintainer approvals minimum
- [ ] Explicit rationale documented in PR description
- [ ] No new imports from `execution/`, `agents/`, or `cognitive/`
- [ ] Backward compatibility analysis
- [ ] Threat model impact assessment
- [ ] Audit log entry

**Kernel modifications are human-written only. AI-generated code is not permitted.**

### 🟡 Cognitive, Memory, Instrumentation

Standard review process:
- [ ] One maintainer approval
- [ ] Tests pass
- [ ] Documentation updated

### 🟢 Execution, Interfaces, Infrastructure

These directories are safe zones for AI-assisted development (Antigravity):
- [ ] Standard code review
- [ ] Tests pass
- [ ] No kernel imports

### 🟢 Agents

Agent modifications follow standard review, but remember:
- Agents are disposable by design
- No agent may persist identity without kernel approval
- Lifecycle changes require governance review

## Code Standards

### Python

- Use type hints
- Follow PEP 8
- Docstrings for public functions
- No global mutable state

### YAML

- Use explicit typing where ambiguous
- Comments for non-obvious values
- Validate schema before commit

## Testing Requirements

| Directory | Test Coverage | Test Type |
|-----------|---------------|-----------|
| `/kernel` | 100% | Unit + Integration |
| `/cognitive` | 90% | Unit + Integration |
| `/execution` | 80% | Unit + Integration |
| `/agents` | 80% | Unit |

## Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Questions?

Open an issue with the `question` label.
