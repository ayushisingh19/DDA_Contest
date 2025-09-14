Infrastructure

Purpose
- Local development and deployment tooling for backend, frontend, Postgres, Judge0, and reverse proxy.

Subfolders
- compose/dev: docker-compose for local dev with hot-reload
- compose/prod: compose for single-host production
- docker/: Dockerfiles and config for each service (backend, frontend, judge0, nginx)
- k8s/: Kubernetes manifests (base + overlays)

Notes
- Prefer .env files for local; use secret stores for prod.
- Do not commit credentials or tokens.
