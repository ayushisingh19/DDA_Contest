#!/usr/bin/env python3
import requests

def check_languages():
    try:
        resp = requests.get('http://judge0:2358/languages')
        print(f'Status: {resp.status_code}')
        langs = resp.json()
        print('Available languages:')
        for lang in langs[:10]:  # Show first 10
            print(f'  {lang["id"]}: {lang["name"]}')
        print('...')
        # Look for Python
        python_langs = [l for l in langs if 'python' in l['name'].lower()]
        if python_langs:
            print('Python languages:')
            for lang in python_langs:
                print(f'  {lang["id"]}: {lang["name"]}')
        else:
            print('No Python languages found')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    check_languages()