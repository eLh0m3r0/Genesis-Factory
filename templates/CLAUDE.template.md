# {PROJECT_NAME} — Technical Context

## Stack
<!-- Language, framework, database, frontend, deployment target -->

## Architecture
<!-- How is the code organized? Key patterns, directory structure. -->

## Critical Rules
<!-- Rules the factory MUST follow. Breaking these = broken production. -->
1. ...

## Staging
- URL: ...
- Test credentials: ...

## UAT Critical Flows
<!-- Playwright browser tests will exercise these flows after every change. -->
1. ...
2. ...

<!--
EXAMPLE (delete this block when filling in):

# CzechAttend — Technical Context

## Stack
- Frontend: Next.js 15 (App Router), TypeScript, Tailwind CSS
- Backend: Next.js API routes + Prisma ORM
- Database: PostgreSQL 16 (Supabase)
- Auth: NextAuth.js with email/password + Google OAuth
- Deploy: Vercel (frontend) + Supabase (database)
- Testing: Vitest (unit), Playwright (E2E)

## Architecture
- `src/app/` — Next.js App Router pages and layouts
- `src/components/` — React components (shadcn/ui)
- `src/lib/` — Shared utilities, Prisma client, auth config
- `prisma/` — Schema and migrations
- `tests/` — Vitest unit tests
- `e2e/` — Playwright E2E tests

## Critical Rules
1. All database changes MUST go through Prisma migrations (never raw SQL in prod)
2. Czech public holidays are hardcoded in `src/lib/holidays.ts` — update yearly
3. Vacation calculation uses Czech labor code formula — do NOT simplify
4. All user-facing text must be in Czech (i18n keys in `src/lib/i18n/cs.ts`)

## Staging
- URL: https://staging.czechattend.cz
- Test credentials: test@example.com / TestPass123!

## UAT Critical Flows
1. Login → Dashboard loads → Shows today's attendance status
2. Clock in → Timer starts → Clock out → Record saved correctly
3. Manager view → See team attendance → Export to CSV
4. Request vacation → Manager approves → Balance updated
-->
