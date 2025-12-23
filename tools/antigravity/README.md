# Antigravity Tools

Safe AI codegen zone for CONTINUUM development.

## Structure

```
antigravity/
├── prompts/           # Codegen prompts and templates
├── generated_code/    # AI-generated code (for review)
└── review_checklists.md
```

## Safe Zones

Antigravity may generate code for:
- `execution/`
- `interfaces/`
- `infra/`

Antigravity may **NOT** generate code for:
- `kernel/` (human-only)
- `docs/specifications/` (human-authored)

## Review Requirements

All AI-generated code requires human review before merge.
