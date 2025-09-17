# Apache Deployment Options

This project originally ships with an Nginx-based `web` container. This guide explains two Apache-focused alternatives:

1. Containerized Apache (drop-in replacement for Nginx)
2. Host Apache (system Apache serves frontend/static and proxies API to backend container)

---
## 1. Containerized Apache (recommended if you want everything in Compose)

Add the Apache override when bringing up the stack:

```bash
docker compose \
  -f infra/compose/prod/docker-compose.yml \
  -f infra/compose/prod/docker-compose.apache.yml \
  up -d --build
```

What the override does:
- Rebuilds `web` using `infra/docker/apache/Dockerfile.prod`.
- Apache serves the built frontend (Vite dist) and static/media via mounted volumes.
- Proxies `/api/` to `backend:8000`.
- Provides SPA fallback to `index.html`.

Environment variable `VITE_API_BASE_URL` should remain `/api` (recommended) so the frontend uses relative requests.

### Verify
```bash
curl -I http://YOUR_HOST/
curl -sS http://YOUR_HOST/api/healthz
```

### Rolling back to Nginx
Just omit the Apache override file on the next `up -d` run.

---
## 2. Host Apache (system Apache outside Docker)

If you prefer to keep Apache on the host and remove the web container entirely:

1. Expose backend on a loopback port and remove/disable the `web` container.
   - Create an override (example):
   ```yaml
   # infra/compose/prod/docker-compose.host-apache.yml
   services:
     backend:
       ports:
         - "127.0.0.1:9000:8000"
     web:
       profiles: ["disabled"]
   ```
   Then run with that override.

2. Build frontend assets locally (inside repo):
   ```bash
   cd frontend
   npm install
   npm run build
   # Dist output in frontend/dist/
   ```
3. Collect Django static files (already done automatically by entrypoint): static files end up in the `static_data` volume. Copy them to a host path if you want Apache to serve them directly.
4. Configure a host Apache vhost:
   ```apache
   <VirtualHost *:80>
       ServerName yourdomain.com
       DocumentRoot /var/www/DDA_Contest/frontend/dist

       ProxyPreserveHost On
       ProxyPass /api/ http://127.0.0.1:9000/api/
       ProxyPassReverse /api/ http://127.0.0.1:9000/api/

       Alias /static/ /var/www/DDA_Contest/staticfiles/
       <Directory /var/www/DDA_Contest/staticfiles/>
           Require all granted
           Header set Cache-Control "public, max-age=31536000, immutable"
       </Directory>

       Alias /media/ /var/www/DDA_Contest/media/
       <Directory /var/www/DDA_Contest/media/>
           Require all granted
       </Directory>

       RewriteEngine On
       RewriteCond %{REQUEST_FILENAME} !-f
       RewriteCond %{REQUEST_URI} !^/api/
       RewriteCond %{REQUEST_URI} !^/static/
       RewriteCond %{REQUEST_URI} !^/media/
       RewriteRule ^ /index.html [L]
   </VirtualHost>
   ```

5. Ensure required Apache modules are enabled:
   ```bash
   sudo a2enmod proxy proxy_http headers rewrite
   sudo systemctl reload apache2
   ```

6. Optional: serve HTTPS via Let's Encrypt:
   ```bash
   sudo certbot --apache -d yourdomain.com -d www.yourdomain.com
   ```

### Keeping static/media in sync
If static/media are written by Django inside containers (volume), you can mount the Docker volume to the host or run a periodic `docker cp` / rsync job. For most contest uploads, proxying `/media/` through the backend via Django is also acceptable (adjust vhost if desired).

---
## Notes
- Containerized Apache path is the simplest migration: no changes to DB/Redis/Judge0 services.
- Performance differences between Nginx and Apache for this use case are negligible compared to Judge0 execution time.
- Ensure `ALLOWED_HOSTS` includes your domain regardless of which reverse proxy is used.

---
## Troubleshooting
| Symptom | Check |
|---------|-------|
| 404 on SPA routes | Rewrite conditions missing or Apache modules not enabled |
| 502 / API failure | Backend container running? Port mapping correct? ProxyPass path ends with trailing slash? |
| Stale frontend | Rebuild images (`--build`) to regenerate assets |
| Missing static assets | Volume mounts present? `collectstatic` executed? |

---
## Quick Commands

Switch to Apache web service:
```bash
docker compose -f infra/compose/prod/docker-compose.yml -f infra/compose/prod/docker-compose.apache.yml up -d --build
```

Back to Nginx:
```bash
docker compose -f infra/compose/prod/docker-compose.yml up -d --build
```

View logs:
```bash
docker compose -f infra/compose/prod/docker-compose.yml logs -f web
```

Enjoy your Apache-based deployment.
