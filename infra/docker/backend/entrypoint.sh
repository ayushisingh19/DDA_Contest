#!/bin/sh
set -e

cd /workspace

# Ensure we're using the new src/ layout; legacy paths removed

# Wait for DB
python - <<'PY'
import os, time, psycopg2
host=os.getenv('POSTGRES_HOST','db')
port=os.getenv('POSTGRES_PORT','5432')
user=os.getenv('POSTGRES_USER','postgres')
pw=os.getenv('POSTGRES_PASSWORD','postgres')
db=os.getenv('POSTGRES_DB','coding')
for i in range(30):
  try:
    psycopg2.connect(host=host, port=port, user=user, password=pw, dbname=db).close()
    print('DB ready')
    break
  except Exception as e:
    print('Waiting for DB...', e)
    time.sleep(2)
PY

# Wait for Redis
python - <<'PY'
import os, time, redis
broker_url=os.getenv('CELERY_BROKER_URL','redis://redis:6379/0')
result_url=os.getenv('CELERY_RESULT_BACKEND','redis://redis:6379/1')

# Parse Redis URLs to get connection details
def parse_redis_url(url):
    import re
    match = re.match(r'redis://([^:]+):(\d+)/(\d+)', url)
    if match:
        return match.group(1), int(match.group(2)), int(match.group(3))
    return 'redis', 6379, 0

broker_host, broker_port, broker_db = parse_redis_url(broker_url)
result_host, result_port, result_db = parse_redis_url(result_url)

# Test both broker and result backend connections
for name, host, port, db in [('broker', broker_host, broker_port, broker_db), ('result', result_host, result_port, result_db)]:
    for i in range(30):
        try:
            r = redis.Redis(host=host, port=port, db=db, socket_timeout=2)
            r.ping()
            print(f'Redis {name} ready at {host}:{port}/{db}')
            break
        except Exception as e:
            print(f'Waiting for Redis {name} at {host}:{port}/{db}...', e)
            time.sleep(2)
    else:
        print(f'WARNING: Could not connect to Redis {name} after 60 seconds')
PY

# Wait for Judge0
python - <<'PY'
import os, time, urllib.request
judge0_url = os.getenv('JUDGE0_URL', 'http://judge0:2358')
print(f'Waiting for Judge0 at {judge0_url}...')
for i in range(60):  # Wait up to 2 minutes
    try:
        response = urllib.request.urlopen(f'{judge0_url}/about', timeout=5)
        if response.getcode() == 200:
            print('Judge0 ready!')
            break
    except Exception as e:
        print(f'Waiting for Judge0... ({i+1}/60)', str(e)[:50])
        time.sleep(2)
else:
    print('WARNING: Judge0 not ready after 2 minutes, continuing anyway...')
PY

# Migrations and static
python "src/student_auth/manage.py" migrate --noinput
python "src/student_auth/manage.py" collectstatic --noinput || true

if [ "${DEBUG}" = "1" ]; then
  exec python "src/student_auth/manage.py" runserver 0.0.0.0:8000
else
  # Run gunicorn in prod-like mode
  pip install gunicorn
  exec gunicorn student_auth.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-60}
fi