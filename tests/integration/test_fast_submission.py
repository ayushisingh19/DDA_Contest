#!/usr/bin/env python3
import requests
import json
import time

def test_simple_fast_submission():
    """Test with minimal code that should execute quickly"""
    print("🚀 Testing Fast Submission")
    print("=" * 40)
    
    # Very simple Python code that should execute instantly
    submission_data = {
        'problem_id': 1,
        'language': 'python',
        'code': 'print(7)'  # Simple output, should be fast
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/submissions/",
            json=submission_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            submission_id = result.get('submission_id')
            print(f"✅ Fast submission created: {submission_id}")
            
            # Monitor status more frequently
            print("🔄 Monitoring status...")
            start_time = time.time()
            
            for i in range(60):  # Check for 1 minute
                time.sleep(2)
                status_response = requests.get(f"http://localhost:8000/api/submissions/{submission_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    current_status = status.get('status')
                    elapsed = time.time() - start_time
                    print(f"  {i*2:3d}s: {current_status}")
                    
                    if current_status not in ['QUEUED', 'RUNNING']:
                        print(f"✅ Completed in {elapsed:.1f}s")
                        print(f"📊 Final Status: {current_status}")
                        print(f"🏆 Score: {status.get('score', 0)}/{status.get('max_score', 0)}")
                        return True
                        
            print(f"⏰ Still processing after 2 minutes")
            return False
        else:
            print(f"❌ Submission failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_fast_submission()
    if success:
        print("\n🎉 Fast submission completed!")
    else:
        print("\n❌ Submission timeout issue confirmed")