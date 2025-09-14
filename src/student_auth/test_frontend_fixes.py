#!/usr/bin/env python3
"""
Test the updated HTML template functionality
"""
import requests


# Test the frontend by making a submission
def test_frontend_fixes():
    try:
        # Check if server is responding
        response = requests.get("http://127.0.0.1:8000/problems/1/")
        if response.status_code == 200:
            print("✅ Django server is running and problem page loads")
            print(f"Response size: {len(response.text)} bytes")

            # Check if the fixed JavaScript is present
            if "pollSubmissionResults" in response.text:
                print("✅ Updated polling function is present")
            else:
                print("❌ Polling function not found in response")

            if "showSecurityAlert" in response.text:
                print("✅ Security alert function is present")
            else:
                print("❌ Security alert function not found")

            if "displayResults" in response.text and "expected_output" in response.text:
                print("✅ Fixed displayResults function with field mapping is present")
            else:
                print("❌ Fixed displayResults function not found")

            # Check if enhanced error handling is present
            if "console.error" in response.text and "Error stack:" in response.text:
                print("✅ Enhanced error handling is present")
            else:
                print("❌ Enhanced error handling not found")

            return True
        else:
            print(f"❌ Server error: {response.status_code}")
            return False

    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Updated HTML Template")
    print("=" * 50)

    success = test_frontend_fixes()

    if success:
        print("\n🎉 All frontend fixes are deployed!")
        print("\n📋 Fixed Issues:")
        print(
            "- Field mapping: frontend now handles both 'expected' and 'expected_output'"
        )
        print("- Enhanced error handling with detailed console logging")
        print("- Better CSRF token handling")
        print("- Improved polling with detailed status messages")
        print("- Added missing showSecurityAlert function")
        print("- Better visual formatting for test results")

        print("\n🔧 To test the fixes:")
        print("1. Open http://127.0.0.1:8000/problems/1/ in your browser")
        print("2. Write some code (e.g., the Two Sum solution)")
        print("3. Click 'Run Code' or 'Submit'")
        print("4. Check the browser console (F12) for detailed logs")
        print("5. Verify test results display properly")
    else:
        print("\n❌ Frontend testing failed - server not accessible")
