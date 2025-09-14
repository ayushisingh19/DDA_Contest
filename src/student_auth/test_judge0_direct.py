#!/usr/bin/env python3
"""
Test Judge0 directly to isolate the issue
"""
import requests
import time


def test_judge0_directly():
    print("🧪 Testing Judge0 API directly...")

    # Test the Two Sum problem code
    code = """
nums = list(map(int, input().split()))
target = int(input())

for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            print([i, j])
            break
"""

    # Test case input
    stdin = "[2,7,11,15]\n9"

    # Create submission
    submission_data = {
        "source_code": code,
        "language_id": 71,  # Python 3.8.1
        "stdin": stdin,
        "expected_output": "[0,1]",
    }

    try:
        print("📤 Creating Judge0 submission...")
        response = requests.post(
            "http://localhost:2358/submissions?base64_encoded=false&wait=false",
            json=submission_data,
        )

        if response.status_code != 201:
            print(f"❌ Failed to create submission: {response.status_code}")
            print(f"Response: {response.text}")
            return

        result = response.json()
        token = result["token"]
        print(f"✅ Submission created with token: {token}")

        # Poll for result
        print("⏳ Waiting for result...")
        for i in range(10):
            time.sleep(2)
            result_response = requests.get(
                f"http://localhost:2358/submissions/{token}?base64_encoded=false"
            )

            if result_response.status_code == 200:
                result_data = result_response.json()
                status = result_data.get("status", {}).get("description", "unknown")
                print(f"Status: {status}")

                if status in [
                    "Accepted",
                    "Wrong Answer",
                    "Runtime Error",
                    "Time Limit Exceeded",
                    "Memory Limit Exceeded",
                    "Compilation Error",
                    "Internal Error",
                ]:
                    print("\n📊 Final Result:")
                    print(f"Status: {status}")
                    print(f"Stdout: {result_data.get('stdout', 'None')}")
                    print(f"Stderr: {result_data.get('stderr', 'None')}")
                    print(f"Message: {result_data.get('message', 'None')}")
                    print(f"Exit Code: {result_data.get('exit_code', 'None')}")
                    return result_data
            else:
                print(f"❌ Error getting result: {result_response.status_code}")

        print("⏰ Timeout waiting for result")

    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")


if __name__ == "__main__":
    test_judge0_directly()
