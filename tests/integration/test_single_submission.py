#!/usr/bin/env python3
import requests
import json

def test_single_submission():
    """Test single Judge0 submission"""
    payload = {
        'source_code': 'print("Hello World")',
        'language_id': 71,
        'stdin': '',
        'expected_output': 'Hello World'
    }

    try:
        response = requests.post(
            'http://judge0:2358/submissions?base64_encoded=false&wait=false',
            json=payload,
            timeout=10
        )
        print(f'Status: {response.status_code}')
        print('Response:', response.text[:500])
        
        if response.status_code == 201:
            data = response.json()
            print(f"Submission ID: {data.get('token')}")
            return data.get('token')
        else:
            print(f"FAILED: {response.status_code}")
            return None
            
    except Exception as e:
        print(f'Error: {e}')
        return None

if __name__ == "__main__":
    test_single_submission()