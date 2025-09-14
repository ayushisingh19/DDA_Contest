#!/usr/bin/env python3
import requests
import json

def test_judge0_direct():
    """Test Judge0 batch submission directly"""
    payload = {
        'submissions': [
            {
                'source_code': 'print("Hello World")',
                'language_id': 71,
                'stdin': ''
            }
        ]
    }

    try:
        response = requests.post(
            'http://judge0:2358/submissions/batch?base64_encoded=false&wait=false',
            json=payload,
            timeout=10
        )
        print(f'Status: {response.status_code}')
        print(f'Response: {response.text[:500]}')
        
        if response.status_code == 201:
            print("SUCCESS: Judge0 accepted batch submission")
            return response.json()
        else:
            print(f"FAILED: Judge0 rejected with {response.status_code}")
            return None
            
    except Exception as e:
        print(f'Error: {e}')
        return None

if __name__ == "__main__":
    test_judge0_direct()