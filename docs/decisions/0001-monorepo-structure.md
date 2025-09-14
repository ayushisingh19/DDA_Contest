# ADR 0001: Monorepo Structure

Status: Accepted
Date: 2025-09-12

Context
- The platform spans multiple services (Django API, React apps, infra, scripts).
- Student contributors benefit from a single entry point and consistent tooling.

Decision
- Use a single repository (monorepo) with top-level slices: backend/, frontend/, infra/, docs/, scripts/.
- Provide thorough README breadcrumbs and .env.example to bootstrap quickly.

Consequences
- Easier onboarding and cross-cutting changes
- Requires clear code ownership and CI to keep slices healthy
