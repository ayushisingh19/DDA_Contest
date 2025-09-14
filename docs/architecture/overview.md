# Architecture Overview

Components
- Frontend: React SPA(s) for students (web) and staff (admin)
- Backend: Django API + admin; integrates with Judge0 for code execution
- Database: PostgreSQL
- Judge0: Self-hosted code execution engine
- Reverse Proxy: Nginx (local and production)

Key Flows
1. Student signs in, fetches contest & problems from Backend
2. Student submits code; Backend forwards to Judge0 and tracks execution
3. Backend computes IOI-style partial scores using testcase weights
4. Results are stored and surfaced to student and proctors

Non-Functional Goals
- Handle ~400 concurrent exam users
- Deterministic environments (requirements split, Docker/K8s manifests)
- Observability (logs, metrics) and auditability (submission verdicts)
