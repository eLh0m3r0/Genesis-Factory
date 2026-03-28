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
6. Ask the user: "Tell me about this project — what is it, who is it for, what tech stack?"
7. Fill in VISION.md based on their answer.
8. Create CLAUDE.md with technical context based on the stack they described.
9. Create GitHub remote: `gh repo create {name} --private --source=. --push`
10. Create basic CI workflow: .github/workflows/ci.yml
11. Report to Telegram: "New project '{name}' created. Run /discover to generate stories."
