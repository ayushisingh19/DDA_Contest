# decode_test

> This project is about building a code evalueation platform with a realtime leaderboard.

## Table of contents
- [About](#about)
- [Repo structure](#repo-structure)
- [Quick start (dev)](#quick-start-dev)
- [Running services individually](#running-services-individually)
- [Environment variables](#environment-variables)
- [Tests](#tests)
- [Branching & workflow](#branching--workflow)
- [Issues & PRs](#issues--prs)
- [Code owners & teams](#code-owners--teams)
- [License](#license)
- [Contacts / Onboarding](#contacts--onboarding)

## About
This repository is a monorepo designed for collaborative development by multiple teams:
- `frontend/` — UI (React / Vue / Next)
- `backend/` — API (Django / Node / FastAPI)
- `ai/` — model code, adapters, training scripts
- `infra/` — Docker / compose / k8s manifests / deployment scripts
- `judge0-integration/` — Judge0 wrappers and tests
- `docs/` — architecture, runbooks, onboarding
The goal is to enable frontend, backend and AI teams to work concurrently with clear boundaries and fast CI feedback.

## Repo structure