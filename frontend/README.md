Frontend (React)

Purpose

- Student exam portal and admin console.

Suggested layout

- apps/: multiple SPAs if needed (web/, admin/)
- public/: static assets
- src/: shared libs (components, pages, hooks, services, store, utils, styles)

Conventions

- Use TypeScript when possible; lint with eslint + prettier.
- API access via a typed client in src/services.
- Keep UI state in a store (Redux Toolkit or Zustand), avoid prop drilling.
