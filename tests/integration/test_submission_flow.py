import requests
import json

# Test the submission flow
def test_submission():
    base_url = "http://127.0.0.1:8002"
    
    # First, test health check
    print("🔍 Testing health check...")
    try:
        health_resp = requests.get(f"{base_url}/healthz/")
        print(f"Health check status: {health_resp.status_code}")
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            print(f"✅ Health check passed: {health_data}")
        else:
            print(f"❌ Health check failed: {health_resp.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print("\n" + "="*50)
    
    # Test visible test cases endpoint
    print("🔍 Testing visible test cases...")
    try:
        testcases_resp = requests.get(f"{base_url}/get_visible_testcases/1/")
        print(f"Test cases status: {testcases_resp.status_code}")
        if testcases_resp.status_code == 200:
            testcases_data = testcases_resp.json()
            print(f"✅ Test cases found: {len(testcases_data.get('testcases', []))} visible test cases")
            for i, tc in enumerate(testcases_data.get('testcases', [])[:3]):  # Show first 3
                print(f"   Test case {i+1}: {tc.get('stdin', '')[:30]}...")
        else:
            print(f"❌ Test cases failed: {testcases_resp.text}")
    except Exception as e:
        print(f"❌ Test cases error: {e}")
    
    print("\n" + "="*50)
    print("🧪 End-to-end test completed!")

if __name__ == "__main__":
    test_submission()