# Contributing

We welcome contributions to Coval External Skills.

## Adding a Skill

1. Fork the repository
2. Create a branch for your skill
3. Add your skill to the appropriate category under `skills/`
4. Include a `SKILL.md` with clear instructions
5. Add examples demonstrating usage
6. Submit a pull request

## Skill Structure

```
skills/<category>/<skill-name>/
├── SKILL.md          # Main instructions (required)
├── examples/         # Usage examples (optional)
└── scripts/          # Utility scripts (optional)
```

## SKILL.md Format

Every skill needs YAML frontmatter:

```yaml
---
name: skill-name
description: What this skill does and when to use it
argument-hint: "[expected-arguments]"
---

# Skill instructions here...
```

- `name`: lowercase letters, numbers, hyphens (max 64 chars)
- `description`: helps Claude decide when to use the skill
- `argument-hint`: shown during autocomplete
- Keep SKILL.md under 500 lines; use supporting files for details

## Guidelines

- Keep skills focused on a single responsibility
- Include clear documentation and examples
- Test with the Coval API before submitting
- Follow existing naming conventions

## Questions

Open an issue for questions or suggestions.
