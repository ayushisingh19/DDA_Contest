#!/usr/bin/env python3
"""
Test the complete Judge0 + Celery + Worker pipeline
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
PROBLEM_ID = 1

# Two Sum solution in Python
SOLUTION_CODE = '''
nums = list(map(int, input().split()))
target = int(input())

for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            print([i, j])
            break
    else:
        continue
    break
'''

def test_submission():
    """Test submitting code and polling for results"""
    
    print("🚀 Testing Judge0 + Celery Pipeline")
    print("=" * 50)
    
    # Create a session to handle cookies and CSRF
    session = requests.Session()
    
    # Test 1: Check backend health
    try:
        response = session.get(f"{BACKEND_URL}/", timeout=10)
        print(f"✅ Backend Health: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return
    
    # Test 2: Get CSRF token
    try:
        csrf_response = session.get(f"{BACKEND_URL}/problems/1/", timeout=10)
        csrf_token = None
        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']
            print(f"✅ Got CSRF token: {csrf_token[:10]}...")
        else:
            print("⚠️ No CSRF token found, trying without it")
    except Exception as e:
        print(f"⚠️ Could not get CSRF token: {e}")
        csrf_token = None
    
    # Test 3: Submit code via API endpoint
    submission_data = {
        'code': SOLUTION_CODE,
        'language': 'python',
        'problem_id': PROBLEM_ID
    }
    
    headers = {}
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token
        submission_data['csrfmiddlewaretoken'] = csrf_token
    
    try:
        print(f"\n📝 Submitting code to problem {PROBLEM_ID}...")
        response = session.post(
            f"{BACKEND_URL}/api/submissions/",
            json=submission_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        print(f"Submission response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Submission successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # If submission ID is returned, poll for results
            if 'submission_id' in result:
                submission_id = result['submission_id']
                print(f"\n🔄 Polling for results (ID: {submission_id})...")
                
                for attempt in range(30):  # Poll for up to 60 seconds
                    try:
                        status_response = session.get(
                            f"{BACKEND_URL}/api/submissions/{submission_id}/",
                            timeout=10
                        )
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            print(f"Status check {attempt + 1}: {status_data.get('status', 'unknown')}")
                            
                            if status_data.get('status') == 'completed':
                                print(f"✅ Execution completed!")
                                print(f"Results: {json.dumps(status_data, indent=2)}")
                                break
                        else:
                            print(f"Status check failed: {status_response.status_code}")
                    except Exception as e:
                        print(f"Polling error: {e}")
                    
                    time.sleep(2)
                else:
                    print("⏰ Polling timeout - submission may still be processing")
        else:
            print(f"❌ Submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Submission error: {e}")

if __name__ == "__main__":
    test_submission()