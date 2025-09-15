# DDA_Contest – Production Deployment (Ubuntu 22.04)

This guide explains how to run the full stack (Postgres, Redis, Judge0, Django, Celery, Nginx) on a VPS using Docker Compose.

## 1) Prerequisites
- Ubuntu 22.04 VPS with sudo
- DNS A/AAAA records pointing your domain to the VPS (optional but recommended)
- Docker Engine and Compose plugin

Install Docker and Compose:

```bash
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

Open firewall (if using ufw):

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 2) Get the code on the server

```bash
cd /var/www
sudo git clone https://github.com/ayushisingh19/DDA_Contest.git
sudo chown -R $USER:$USER DDA_Contest
cd DDA_Contest
```

## 3) Configure the environment

Copy the example env and edit values:

```bash
cp infra/compose/prod/.env.example infra/compose/prod/.env
nano infra/compose/prod/.env
```

- SECRET_KEY: generate a long random string
- ALLOWED_HOSTS: comma-separated domain(s)/IP(s), no spaces
- POSTGRES_*: set strong password
- VITE_API_BASE_URL: recommended to keep as `/api` when Nginx serves API and frontend on same domain

## 4) Choose how to listen on HTTP

- Option A: Let the Dockerized Nginx listen on public port 80 (simplest).
- Option B: Keep Apache on the host and reverse-proxy to Docker Nginx on 127.0.0.1:8080.

To use Option B, copy the sample override:

```bash
cp infra/compose/prod/docker-compose.override.sample.yml infra/compose/prod/docker-compose.override.yml
```

Then configure Apache with `infra/compose/prod/apache-vhost.conf.example` as a starting point.

## 5) Build and start

```bash
# From repository root
docker compose -f infra/compose/prod/docker-compose.yml up -d --build
```

Check containers:

```bash
docker compose -f infra/compose/prod/docker-compose.yml ps
docker compose -f infra/compose/prod/docker-compose.yml logs -f web
```

## 6) Initialize the database

```bash
docker compose -f infra/compose/prod/docker-compose.yml exec backend python src/student_auth/manage.py migrate --noinput
```

Create an admin user:

```bash
docker compose -f infra/compose/prod/docker-compose.yml exec backend python src/student_auth/manage.py createsuperuser
```

## 7) Verify

- http://YOUR_DOMAIN/ should serve the frontend
- http://YOUR_DOMAIN/api/healthz should return a health response

## 8) HTTPS (optional)

If using Apache as front proxy:

```bash
sudo apt-get install -y certbot python3-certbot-apache
sudo certbot --apache -d yourdomain.com -d www.yourdomain.com
```

If exposing Docker Nginx directly, consider placing a host-level reverse proxy (nginx/apache/caddy) with TLS, or use a companion like `nginx-proxy` + `acme-companion`.

## 9) Routine operations

Pull updates and redeploy:

```bash
cd /var/www/DDA_Contest
git pull
# Rebuild images if Dockerfiles or frontend changed
docker compose -f infra/compose/prod/docker-compose.yml build
# Apply DB migrations
docker compose -f infra/compose/prod/docker-compose.yml exec backend python src/student_auth/manage.py migrate --noinput
# Restart services (if needed)
docker compose -f infra/compose/prod/docker-compose.yml up -d
```

Check logs:

```bash
docker compose -f infra/compose/prod/docker-compose.yml logs -f backend
```

Backups: snapshot Postgres volume `db_data` and media volume `media_data` regularly.

---
Troubleshooting:
- Port 80 busy: stop Apache (`sudo systemctl stop apache2`) or use the override to bind Docker to 127.0.0.1:8080 and proxy via Apache.
- Judge0 not starting: ensure DB and Redis are healthy; we run Judge0 without isolate for simplicity.
- 500 errors: confirm `JUDGE0_URL` is `http://judge0:2358` inside containers and Redis is reachable.
