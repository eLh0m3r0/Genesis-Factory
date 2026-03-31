# {PROJECT_NAME}

## What
<!-- One paragraph: what is this project? What does it do? -->

## Why
<!-- One paragraph: why does it exist? Who is it for? What problem does it solve? -->

## Direction
<!-- List priorities in order. Be specific — this is how the factory decides what to build. -->
- Priority 1: ...
- Priority 2: ...
- Avoid: ...

## Constraints
- Tech stack: ...
- Compliance: ...

## Competition (optional)
<!-- List competitors so the factory can research them during discovery cycles. -->
- Competitor A: https://...

## project_weight: 3
<!-- Scale 1-5: 1=low priority, 3=default, 5=critical.
     Used to rank stories across projects when deciding what to build next.
     5 = this project gets attention every nightly cycle
     3 = normal rotation with other projects
     1 = only when nothing else is ready -->

## skip_phases: []
<!-- Phases the factory will skip for this project.
     Valid: discovery, uat, security_review, auto_merge, auto_deploy, auto_docs, retro
     Default: [] (all phases active)
     Examples:
       skip_phases: [uat, auto_deploy]         — CLI tool, no web UI, manual deploy
       skip_phases: [discovery]                 — backlog managed manually
       skip_phases: [auto_merge, security_review] — human reviews all PRs -->

<!--
EXAMPLE (delete this block when filling in):

# CzechAttend
## What
A modern attendance tracking SaaS for small Czech companies (5-50 employees).
Web app + mobile-friendly. Czech-first, EU-compliant.

## Why
Czech small businesses use paper sheets or generic HR tools that don't handle
Czech labor law (sick leave, vacation accrual, public holidays). We fill this gap.

## Direction
- Priority 1: Core attendance tracking (clock in/out, breaks, overtime)
- Priority 2: Czech labor law compliance (vacation calculation, sick leave)
- Priority 3: Manager dashboard with team overview
- Avoid: Payroll (too regulated), enterprise features (not our market)

## Constraints
- Tech stack: Next.js, PostgreSQL, Tailwind CSS
- Compliance: GDPR, Czech labor code
- Deploy: Vercel + Supabase

## Competition
- Sloneek: https://sloneek.com — HR platform, too complex for small companies
- Attendance Cloud: https://attendancecloud.com — generic, no Czech law support

## project_weight: 4
## skip_phases: []
-->
