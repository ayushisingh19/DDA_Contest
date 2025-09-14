import requests
import json

try:
    r = requests.get('http://127.0.0.1:8000/healthz/')
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')
except Exception as e:
    print(f'Error: {e}')