#!/usr/bin/env bash
# Idempotent deployment script for Hostinger KVM / Ubuntu 24.04
# Runs app stack bound to 127.0.0.1:8080 without touching system Apache.
# Safe to re-run; will install Docker if missing, build images, run migrations, verify health.

set -Eeuo pipefail

COMPOSE_FILE="infra/compose/prod/docker-compose.yml"
OVERRIDE_FILE="infra/compose/prod/docker-compose.override.yml"
ENV_FILE="infra/compose/prod/.env"
BRANCH="chore/deploy-8080"
REPO_URL="https://github.com/ayushisingh19/DDA_Contest.git"
REPO_DIR="/var/www/DDA_Contest"

log() { echo -e "[deploy] $*"; }
err() { echo -e "[deploy][ERROR] $*" >&2; }

trap 'err "Deployment failed (line $LINENO). See logs above."; dump_state' ERR

dump_state() {
  log "Container state:" || true
  docker compose -f "$COMPOSE_FILE" ps || true
  log "Recent logs (tail=120):" || true
  docker compose -f "$COMPOSE_FILE" logs --tail=120 || true
}

ensure_docker() {
  if command -v docker >/dev/null 2>&1; then
    log "Docker already installed: $(docker --version)"; return
  fi
  log "Installing Docker Engine + Compose plugin..."
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg lsb-release
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin git
  log "Docker installed."
}

fetch_repo() {
  mkdir -p /var/www
  cd /var/www
  if [ ! -d "$REPO_DIR/.git" ]; then
    log "Cloning repository..."
    git clone "$REPO_URL" "$REPO_DIR"
  else
    log "Repository exists. Pulling latest..."
  fi
  cd "$REPO_DIR"
  git fetch origin
  if git rev-parse --verify origin/$BRANCH >/dev/null 2>&1; then
    git checkout -B "$BRANCH" "origin/$BRANCH" || git checkout "$BRANCH"
  fi
  git pull --ff-only || true
}

prepare_env() {
  cd "$REPO_DIR"
  if [ ! -f "$ENV_FILE" ]; then
    cp infra/compose/prod/.env.example "$ENV_FILE" || true
  fi
  # Ensure required keys exist
  grep -q '^SECRET_KEY=' "$ENV_FILE" || echo "SECRET_KEY=$(tr -dc 'A-Za-z0-9!@#$%^&*()_+-=' </dev/urandom | head -c 48)" >> "$ENV_FILE"
  grep -q '^ALLOWED_HOSTS=' "$ENV_FILE" || echo 'ALLOWED_HOSTS=localhost,127.0.0.1' >> "$ENV_FILE"
  # Force relative API path for same-origin calls
  if grep -q '^VITE_API_BASE_URL=' "$ENV_FILE"; then
    sed -i 's|^VITE_API_BASE_URL=.*$|VITE_API_BASE_URL=/api|g' "$ENV_FILE"
  else
    echo 'VITE_API_BASE_URL=/api' >> "$ENV_FILE"
  fi
  log "Using env values:"; grep -E '^(ALLOWED_HOSTS|VITE_API_BASE_URL|POSTGRES_DB|POSTGRES_USER)=' "$ENV_FILE" || true
}

prepare_override() {
  cd "$REPO_DIR"
  cp infra/compose/prod/docker-compose.override.8080.yml "$OVERRIDE_FILE"
}

start_stack() {
  cd "$REPO_DIR"
  log "Building and starting containers..."
  docker compose -f "$COMPOSE_FILE" up -d --build
  docker compose -f "$COMPOSE_FILE" ps
}

wait_health() {
  log "Waiting for backend health endpoint..."
  for i in $(seq 1 60); do
    if curl -fsS http://127.0.0.1:8080/api/healthz >/dev/null 2>&1; then
      log "Health endpoint OK."; return
    fi
    sleep 2
  done
  err "Backend health check did not become ready in time."; exit 1
}

migrate_db() {
  log "Running migrations..."
  docker compose -f "$COMPOSE_FILE" exec backend python src/student_auth/manage.py migrate --noinput
}

verify_http() {
  log "Verifying HTTP responses..."
  curl -I http://127.0.0.1:8080/ || true
  curl -sS http://127.0.0.1:8080/api/healthz || true
}

# ==== Main ====
ensure_docker
fetch_repo
prepare_env
prepare_override
start_stack
wait_health
migrate_db
verify_http

log "Deployment complete. To create admin:"
log "docker compose -f $COMPOSE_FILE exec backend python src/student_auth/manage.py createsuperuser"
log "Logs: docker compose -f $COMPOSE_FILE logs -f --tail=200"
