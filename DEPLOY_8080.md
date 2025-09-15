# Deploy on a KVM with Apache intact (Docker on 8080)

We’ll run the project’s prod stack with Nginx in Docker bound to 127.0.0.1:8080 and keep system Apache untouched.

## Steps

1) Install Docker & Compose (Ubuntu 24.04)

```bash
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

2) Prepare env

```bash
cd /var/www/DDA_Contest
cp infra/compose/prod/.env.example infra/compose/prod/.env
nano infra/compose/prod/.env
```

- SECRET_KEY: long random
- ALLOWED_HOSTS: your.domain,localhost,127.0.0.1
- VITE_API_BASE_URL: /api (recommended)
- Set strong POSTGRES_PASSWORD

3) Bind Nginx to 127.0.0.1:8080

```bash
cp infra/compose/prod/docker-compose.override.8080.yml infra/compose/prod/docker-compose.override.yml
```

4) Start the stack

```bash
docker compose -f infra/compose/prod/docker-compose.yml up -d --build
```

5) Migrate & create admin

```bash
docker compose -f infra/compose/prod/docker-compose.yml exec backend python src/student_auth/manage.py migrate --noinput

docker compose -f infra/compose/prod/docker-compose.yml exec backend python src/student_auth/manage.py createsuperuser
```

6) Verify locally on the VPS

```bash
curl -I http://127.0.0.1:8080/
curl -sS http://127.0.0.1:8080/api/healthz
```

7) Apache reverse proxy (example)

Add a site that proxies / to http://127.0.0.1:8080/ and enable it. Do not change global Apache configs. Use the sample at `infra/compose/prod/apache-vhost.conf.example`.

## Operate

- Tail logs: `./scripts/prod-logs.sh`
- Restart: `./scripts/prod-down.sh && ./scripts/prod-up.sh`
- Rollback: `git checkout <prev-tag-or-commit> && ./scripts/prod-up.sh`

## Troubleshooting

- Check container health: `docker compose -f infra/compose/prod/docker-compose.yml ps`
- View recent logs: `docker compose -f infra/compose/prod/docker-compose.yml logs --tail=200`
- If web 502s: `docker compose -f infra/compose/prod/docker-compose.yml logs -f backend web`
