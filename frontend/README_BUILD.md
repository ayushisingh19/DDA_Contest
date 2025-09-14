# Frontend Build & Template Workflow

## Source-of-Truth

- All HTML templates live in `frontend/templates/accounts/`.
- All TypeScript entrypoints live in `frontend/src/pages/`.

## Build Steps

1. **Build JS Bundles:**
   ```powershell
   cd frontend
   npm run build
   ```
   - Output: `../src/student_auth/static/build/*.js` (for Django static)
2. **Copy HTML Templates to Django:**
   ```powershell
   cd frontend
   npm run copy:html
   ```
   - Copies all HTML from `frontend/templates/accounts/` to `src/student_auth/accounts/templates/accounts/`.
3. **Full Build (JS + HTML):**
   ```powershell
   cd frontend
   npm run build:all
   ```
   - Runs both steps above.

## Development Experience

- **Watch JS & Copy HTML on change:**
  ```powershell
  cd frontend
  npm run watch:all
  ```
  - Rebuilds JS and copies HTML automatically.

## Django Integration

- In Django templates, use:
  ```django
  {% load static %}
  <script type="module" src="{% static 'build/start.js' %}"></script>
  ```
- All template changes should be made in `frontend/templates/accounts/` and copied over.

## Adding New Pages

- Add new HTML to `frontend/templates/accounts/`.
- Add new TS entry to `frontend/src/pages/` and update `vite.config.ts`.

---

This workflow keeps frontend assets and templates in one place for easy editing and reliable builds.
