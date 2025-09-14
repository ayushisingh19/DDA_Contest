#!/usr/bin/env python3
"""
Test script to validate Judge0/Celery integration fixes

This script tests:
1. Health check endpoint
2. Judge0 connectivity
3. Submission creation and status checking
"""

import requests
import json
import time
import sys


def test_health_check(base_url="http://localhost:8000"):
    """Test the health check endpoint"""
    print("🏥 Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/healthz/", timeout=10)
        print(f"Health check status: {response.status_code}")
        health_data = response.json()
        print(f"Health check response: {json.dumps(health_data, indent=2)}")
        
        if health_data.get("overall") == "ok":
            print("✅ All services are healthy!")
            return True
        else:
            print("⚠️  Some services are degraded")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_judge0_direct(judge0_url="http://localhost:2358"):
    """Test Judge0 service directly"""
    print(f"\n⚖️  Testing Judge0 directly at {judge0_url}...")
    try:
        response = requests.get(f"{judge0_url}/about", timeout=10)
        print(f"Judge0 /about status: {response.status_code}")
        if response.status_code == 200:
            about_data = response.json()
            print(f"Judge0 version: {about_data.get('version', 'unknown')}")
            print("✅ Judge0 is accessible!")
            return True
        else:
            print(f"❌ Judge0 returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Judge0 direct test failed: {e}")
        return False


def test_submission_api(base_url="http://localhost:8000"):
    """Test the submission API"""
    print(f"\n📝 Testing submission API at {base_url}...")
    
    # Test data
    test_submission = {
        "problem_id": 1,
        "code": "print(1+1)",
        "language": "python"
    }
    
    try:
        # Create submission
        response = requests.post(
            f"{base_url}/api/submissions/",
            json=test_submission,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Submission creation status: {response.status_code}")
        
        if response.status_code == 200:
            submission_data = response.json()
            submission_id = submission_data.get("submission_id")
            print(f"✅ Submission created: {submission_id}")
            print(f"Initial status: {submission_data.get('status')}")
            
            # Poll for status
            if submission_id:
                print("⏳ Polling submission status...")
                for i in range(10):  # Poll for up to 10 seconds
                    time.sleep(1)
                    status_response = requests.get(
                        f"{base_url}/api/submissions/{submission_id}/",
                        timeout=5
                    )
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_status = status_data.get("status")
                        print(f"Status check {i+1}: {current_status}")
                        
                        if current_status in ["DONE", "ERROR"]:
                            print(f"✅ Final status: {current_status}")
                            if current_status == "DONE":
                                print(f"Score: {status_data.get('score')}/{status_data.get('max_score')}")
                            return True
                            
                print("⏰ Timeout waiting for completion")
                return False
            else:
                print("❌ No submission ID returned")
                return False
                
        elif response.status_code == 503:
            print("⚠️  Service temporarily unavailable (expected if Celery/Judge0 is down)")
            print(f"Response: {response.json()}")
            return False
        else:
            print(f"❌ Submission failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Submission API test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Judge0/Celery integration tests...\n")
    
    results = {
        "health_check": test_health_check(),
        "judge0_direct": test_judge0_direct(),
        "submission_api": test_submission_api()
    }
    
    print(f"\n📊 Test Results:")
    print(f"Health Check: {'✅' if results['health_check'] else '❌'}")
    print(f"Judge0 Direct: {'✅' if results['judge0_direct'] else '❌'}")
    print(f"Submission API: {'✅' if results['submission_api'] else '❌'}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ All tests passed!' if all_passed else '❌ Some tests failed'}")
    
    if not all_passed:
        print("\n💡 Troubleshooting tips:")
        if not results['judge0_direct']:
            print("- Start Judge0: docker compose -f infra/compose/dev/docker-compose.yml up -d judge0")
        if not results['health_check']:
            print("- Check Django server is running: python manage.py runserver")
        if not results['submission_api']:
            print("- Start Celery worker: celery -A student_auth worker -l info")
            
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())