Onboarding

Goals
- Set up backend (Django + Postgres), frontend (React), and Judge0 locally.
- Learn the repository layout and contribution conventions.

High-level Steps
1. Create a Python virtualenv; install backend requirements from backend/requirements/dev.txt
2. Configure Postgres and environment (.env) using .env.example
3. Run migrations and start the backend server
4. Scaffold the React app under frontend/apps/web
5. Start the dev stack (compose/dev) once Docker files are added

Conventions
- Python: type hints, ruff + black, pytest
- JS/TS: eslint + prettier
- Commits: Conventional Commits
