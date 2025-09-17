# Deploy on Apache (mod_wsgi) — Quick Start

This guide follows the GeekyShows-style Apache + mod_wsgi approach adapted to this repo.

## Prereqs
- Ubuntu 22.04/24.04 with Apache2
- Python 3.10+ and virtualenv
- A domain pointing to the server

## Paths used
- Project checkout: /var/www/DDA_Contest
- Virtualenv: /var/www/DDA_Contest/venv
- Django source: /var/www/DDA_Contest/src/student_auth
- WSGI entry: /var/www/DDA_Contest/src/student_auth/student_auth/wsgi.py
- Static root: /var/www/DDA_Contest/static
- Media root: /var/www/DDA_Contest/media

## Install system deps
```bash
sudo apt update
sudo apt install -y apache2 libapache2-mod-wsgi-py3 python3-venv python3-pip
sudo a2enmod headers rewrite wsgi deflate
```

## App setup
```bash
sudo mkdir -p /var/www/DDA_Contest
sudo chown -R $USER:$USER /var/www/DDA_Contest
cd /var/www/DDA_Contest

# Get code (replace with your method)
# git clone https://github.com/<owner>/<repo>.git .

python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r backend/requirements/prod.txt

# Environment (adjust domain)
export DJANGO_SETTINGS_MODULE=student_auth.settings
export ALLOWED_HOSTS=ddacontest.com,www.ddacontest.com,localhost,127.0.0.1
export DJANGO_STATIC_ROOT=/var/www/DDA_Contest/static
export DJANGO_MEDIA_ROOT=/var/www/DDA_Contest/media

# Database env if using Postgres
# export POSTGRES_DB=dda_contest
# export POSTGRES_USER=dda_user
# export POSTGRES_PASSWORD=strong_password

# Django admin tasks
python src/student_auth/manage.py collectstatic --noinput
python src/student_auth/manage.py migrate --noinput
# python src/student_auth/manage.py createsuperuser
```

## Apache vhost
Copy and edit `deploy_Query/ddacontest.conf`:
```bash
sudo cp deploy_Query/ddacontest.conf /etc/apache2/sites-available/ddacontest.conf
sudo $SHELL -lc "sed -i 's/ServerName .*/ServerName ddacontest.com/' /etc/apache2/sites-available/ddacontest.conf"
```
Make sure these lines exist (already included):
```
SetEnv DJANGO_SETTINGS_MODULE student_auth.settings
SetEnv ALLOWED_HOSTS ddacontest.com,www.ddacontest.com,localhost,127.0.0.1
SetEnv DJANGO_STATIC_ROOT /var/www/DDA_Contest/static
SetEnv DJANGO_MEDIA_ROOT /var/www/DDA_Contest/media
```
Enable site:
```bash
sudo a2ensite ddacontest
sudo systemctl reload apache2
```

## Verify
```bash
curl -I http://ddacontest.com/
curl -sS http://ddacontest.com/healthz || true
```

## HTTPS (optional)
Use the SSL vhost template in `deploy_Query/ddacontest-ssl.conf` and Certbot, or run:
```bash
sudo apt install -y certbot python3-certbot-apache
sudo certbot --apache -d ddacontest.com -d www.ddacontest.com
```

## Troubleshooting
- 500 errors: check `/var/log/apache2/dda_contest_error.log`
- 404 on SPA routes: ensure Rewrite rules are active and `a2enmod rewrite`
- Static missing: confirm collectstatic path matches `DJANGO_STATIC_ROOT` and Apache aliases
- ALLOWED_HOSTS includes your domain
