Backend (Django)

Purpose
- Django project for APIs, admin, auth, grading, and orchestration.

Layout
- apps/: modular domain apps (problems, submissions, contests, accounts, grading, common)
- config/: Django project (ASGI/WSGI, urls, settings)
- config/settings/: layered settings (base.py, dev.py, prod.py, test.py)
- requirements/: dependency pins (base.txt, dev.txt, prod.txt, test.txt)
- scripts/: backend maintenance scripts
- tests/: test suite root

Getting started (dev)
- Create .env based on repo .env.example
- Install dependencies from requirements/dev.txt
- Run migrations, create superuser, runserver

Notes
- Keep business logic inside domain apps.
- Keep settings minimal; push env-specific config to environment variables.
- Use typing, ruff, black, pytest.
