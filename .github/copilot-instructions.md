# Copilot Instructions for AI Coding Agents

This codebase is a monorepo for a college-focused coding competition platform. It uses Django (backend), React (frontend), Judge0 (code execution), and containerized infrastructure. Follow these guidelines to be immediately productive:

## Prerequisites
- Git
- Docker & Docker Compose
- Python 3.8+ (for local backend development)
- VS Code (recommended) or preferred IDE

## Architecture Overview
- **Monorepo layout:**
  - `backend/`: Django project (APIs, business logic, modular apps)
  - `frontend/`: React apps (student portal, admin console)
  - `infra/`: Docker/Kubernetes configs for local/dev/prod
  - `docs/`: Architecture, onboarding, ADRs
  - `scripts/`: Dev/ops utilities
  - `new app/`: Legacy code, migrate incrementally
- **Data flow:**
  - Frontend submits code via REST API to backend
  - Backend stores submissions, dispatches async grading via Celery
  - Judge0 executes code, results returned to backend
  - Leaderboard updates via Redis

## Developer Workflows
- **Dev stack:**
  ```bash
  # Copy and configure environment
  cp .env.example .env

  # Start all services
  docker compose -f infra/compose/dev/docker-compose.yml up --build

  # Verify services
  curl http://localhost/api/healthz  # Backend health
  curl http://localhost  # Frontend
  ```

  Required env vars:
  - `JUDGE0_URL`: Judge0 API endpoint
  - `POSTGRES_*`: Database credentials
  - `REDIS_URL`: Redis connection string
  - `DEBUG`: Enable development mode

- **Backend:**
  ```bash
  # Install dependencies
  python -m pip install -r backend/requirements/dev.txt

  # Setup database
  python manage.py migrate
  python manage.py createsuperuser

  # Run tests
  pytest
  ```

- **Frontend:**
  ```bash
  # Install dependencies
  cd frontend && npm install

  # Development
  npm run dev

  # Run tests
  npm test
  ```

- **Validation:**
  ```bash
  # Backend tests and linting
  docker compose exec backend pytest
  docker compose exec backend black . && ruff check .

  # Frontend tests and linting
  docker compose exec frontend npm test
  docker compose exec frontend npm run lint
  ```

- **Seed sample data:**
  ```bash
  python new\ app/student_auth/add_sample_data.py
  ```

## Project Conventions
- **Backend:**
  - Modular apps in `backend/apps/`
  - Layered settings in `backend/config/settings/`
  - Use type hints, `ruff`, `black`, `pytest`
  - Example endpoint:
    ```python
    @api_view(['POST'])
    def submit_code(request):
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            submission = serializer.save()
            grade_submission.delay(submission.id)
            return Response(status=202)
    ```

- **Frontend:**
  - TypeScript, functional components, hooks
  - API client in `frontend/src/api/client.ts`
  - State management via Redux Toolkit or Zustand
  - Example component:
    ```typescript
    const SubmissionForm: React.FC = () => {
      const submit = useSubmitCode();
      return <form onSubmit={submit}>...</form>;
    };
    ```

- **Infra:**
  - Use `.env` for local secrets only
  - Do not commit credentials
- **Commits:**
  - Use Conventional Commits
  - PRs require passing checks

## Integration Points
- **Judge0:**
  - Self-hosted via Docker, configured with `JUDGE0_URL` env var
  - Backend communicates via REST
  - Default endpoint: http://localhost:2358
- **Redis:**
  - Used for leaderboard and Celery broker
  - Default URL: redis://localhost:6379
- **PostgreSQL:**
  - Main data store
  - Default credentials in .env.example

## Common Issues
- Backend 500 errors: Check `JUDGE0_URL` and Redis connection
- Frontend build fails: Clear `node_modules` and reinstall
- Docker networking: Ensure ports 80, 2358, 6379 are available
- Permission errors: Run `chmod -R 777 new\ app/student_auth/media`

## References
- See `docs/onboarding.md` for setup and workflows
- See ADRs in `docs/decisions/` for architectural choices
- See `backend/README.md` and `frontend/README.md` for slice-specific details

---

**If any section is unclear or missing, please request clarification or provide feedback to improve these instructions.**
