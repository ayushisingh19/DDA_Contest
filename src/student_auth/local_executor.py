#!/usr/bin/env python3
"""
Local code execution fallback for development when Judge0 fails
"""
import subprocess
import tempfile
import os
import sys


class LocalCodeExecutor:
    def __init__(self):
        self.timeout = 5  # 5 second timeout

    def execute_python_code(self, code, test_cases):
        """
        Execute Python code locally with test cases
        """
        results = []

        for i, test_case in enumerate(test_cases):
            stdin_data = test_case.get("stdin", "")
            expected_output = test_case.get("expected_output", "")

            try:
                # Create a temporary file for the code
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as f:
                    f.write(code)
                    temp_file = f.name

                # Execute the code with stdin
                process = subprocess.Popen(
                    [sys.executable, temp_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                try:
                    stdout, stderr = process.communicate(
                        input=stdin_data, timeout=self.timeout
                    )
                except subprocess.TimeoutExpired:
                    process.kill()
                    os.unlink(temp_file)
                    results.append(
                        {
                            "index": i,
                            "group": "visible",
                            "weight": 1.0,
                            "status": "Time Limit Exceeded",
                            "passed": False,
                            "time_ms": self.timeout * 1000,
                            "memory_kb": 0,
                            "output": "",
                            "expected_output": expected_output,
                            "stderr": "Time limit exceeded",
                            "exit_code": -1,
                        }
                    )
                    continue

                # Clean up
                os.unlink(temp_file)

                # Determine if the output matches
                actual_output = stdout.strip()
                expected_clean = expected_output.strip()
                passed = actual_output == expected_clean

                result = {
                    "index": i,
                    "group": "visible",
                    "weight": 1.0,
                    "status": "Accepted" if passed else "Wrong Answer",
                    "passed": passed,
                    "time_ms": 100,  # Placeholder
                    "memory_kb": 1024,  # Placeholder
                    "output": actual_output,
                    "expected_output": expected_output,
                    "stderr": stderr,
                    "exit_code": process.returncode,
                }

                if process.returncode != 0:
                    result["status"] = "Runtime Error"
                    result["passed"] = False

                results.append(result)

            except Exception as e:
                if "temp_file" in locals():
                    os.unlink(temp_file)
                results.append(
                    {
                        "index": i,
                        "group": "visible",
                        "weight": 1.0,
                        "status": "Internal Error",
                        "passed": False,
                        "time_ms": 0,
                        "memory_kb": 0,
                        "output": "",
                        "expected_output": expected_output,
                        "stderr": str(e),
                        "exit_code": -1,
                    }
                )

        return results


def test_local_executor():
    """Test the local executor with Two Sum problem"""
    executor = LocalCodeExecutor()

    # Two Sum solution code
    code = """
import json
line1 = input().strip()
line2 = input().strip()

# Parse the array from JSON format
nums = json.loads(line1)
target = int(line2)

for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        if nums[i] + nums[j] == target:
            print([i, j])
            break
"""

    # Test cases
    test_cases = [
        {"stdin": "[2,7,11,15]\n9", "expected_output": "[0, 1]"},
        {"stdin": "[3,2,4]\n6", "expected_output": "[1, 2]"},
        {"stdin": "[3,3]\n6", "expected_output": "[0, 1]"},
    ]

    print("🧪 Testing Local Code Executor...")
    results = executor.execute_python_code(code, test_cases)

    for result in results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} Test {result['index'] + 1}: {result['status']}")
        print(f"  Expected: {result['expected_output']}")
        print(f"  Got:      {result['output']}")
        if result["stderr"]:
            print(f"  Error:    {result['stderr']}")
        print()

    passed_tests = sum(1 for r in results if r["passed"])
    total_tests = len(results)
    print(f"📊 Summary: {passed_tests}/{total_tests} tests passed")

    return results


if __name__ == "__main__":
    test_local_executor()
