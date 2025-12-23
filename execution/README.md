# Execution Layer

The execution layer provides sandboxed, monitored runtime for all
CONTINUUM actions. It translates cognitive decisions into real-world effects
within governance constraints.

## Structure

```
execution/
├── fabric/           # Core execution infrastructure
├── tools/            # Adapters for external systems
└── sandboxes/        # Isolated execution environments
```

## Governance

All execution must:
1. Pass governance validation before starting
2. Run in sandboxed environment
3. Respect resource limits
4. Log all actions for audit

## AI Codegen Safe Zone

This directory is safe for AI-assisted development (Antigravity).
However, the following rules apply:

- No kernel imports
- No governance bypassing
- All tool integrations require security review
