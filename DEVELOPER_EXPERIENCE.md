**Quick Start**
- Install deps: `cd frontend` then `npm install`
- One command dev: `powershell -ExecutionPolicy Bypass -File scripts/dev.ps1`

**Frontend**
- Source HTML: `frontend/templates/accounts/`
- Source TS: `frontend/src/pages/`
- Build JS: `cd frontend; npm run build`
- Copy HTML: `cd frontend; npm run copy:html`
- Full build: `cd frontend; npm run build:all`
- Watch: `cd frontend; npm run watch:all`

**Django**
- Run server: `cd src/student_auth; ..\..\env\Scripts\python.exe manage.py runserver`
- Static bundles path: `src/student_auth/static/build/*.js`
- Templates destination: `src/student_auth/accounts/templates/accounts/*.html`

**Combined Dev**
- Start both (frontend watch + Django):
  `powershell -ExecutionPolicy Bypass -File scripts/dev.ps1`
  - Use `Get-Job` to view the frontend background job.

**CI/Build**
- Frontend build only: `cd frontend; npm ci && npm run build:all`
- Backend tests: `cd src/student_auth; ..\..\env\Scripts\python.exe -m pytest`

This setup keeps frontend assets in one place while producing Django-ready outputs with minimal steps.
