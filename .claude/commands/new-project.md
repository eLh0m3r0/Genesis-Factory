---
description: "Create a new project from template. Usage: /new-project <project-name>"
argument-hint: "<project-name>"
---

# Create New Project

Create a new project in ~/projects/ using the factory templates.

## Process

1. Parse the project name from the argument.
2. Create directory: `mkdir -p ~/projects/{name}`
3. Copy template files:
   - templates/VISION.template.md → VISION.md
   - templates/CLAUDE.template.md → CLAUDE.md
   - templates/BACKLOG.template.md → BACKLOG.md
   - Create empty RESEARCH.md and AGENTS.md
4. Replace {PROJECT_NAME} placeholders in templates.
5. Initialize git repo: `cd ~/projects/{name} && git init`
6. **Interactive Q&A** — ask one at a time:
   - "Tell me about this project — what does it do, who is it for?"
   - "What tech stack? (e.g., Python/Flask, Node/React, etc.)"
   - "Does it have a database? If so, what type?"
   - "Where will it be deployed? (e.g., Vercel, Railway, VPS, Docker)"
   - "Any specific requirements or constraints?"
   - "Which factory phases should I skip? All are ON by default:
     discovery, uat, security_review, auto_merge, auto_deploy, auto_docs, retro.
     For example, a CLI tool might skip uat and auto_deploy.
     Say 'all active' for defaults."
7. Fill in VISION.md based on answers (direction, priorities, constraints, skip_phases).
8. Create CLAUDE.md with technical context:
   - Stack section based on tech stack answer
   - Architecture section with sensible defaults for the stack
   - Critical Rules section with stack-appropriate rules
   - Test commands section
9. **Generate CI workflow** based on stack:
   - Python: pytest + ruff linting
   - Node: npm test + eslint
   - Go: go test + go vet
   - Other: basic build + test
   - Save to `.github/workflows/ci.yml`
10. **Create heartbeat_config.yaml** with sensible defaults:
    - url_health monitor for production URL (if deployment target is known)
    - Placeholder monitor to be configured later
11. Create GitHub remote: `gh repo create {name} --private --source=. --push`
12. Report to Telegram: "New project '{name}' created. Run /discover to generate stories."
13. **Auto-run /discover** for the new project to generate initial backlog.
