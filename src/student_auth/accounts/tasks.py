import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Submission, SubmissionTestCaseResult, TestCase, UserSolution
from .wrapping import maybe_wrap_code
import json
import requests
import time
import subprocess
import tempfile
import os
import sys


@shared_task
def ping() -> str:
    return "pong"


@shared_task
def add(x, y):
    """Simple test task for connectivity testing"""
    return x + y


def _judge0_headers():
    token = getattr(settings, "JUDGE0_AUTH_TOKEN", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Auth-Token"] = token
    return headers


def _check_judge0_connectivity():
    """Check if Judge0 service is accessible"""
    try:
        base_url = getattr(settings, "JUDGE0_URL", "http://localhost:2358").rstrip("/")
        resp = requests.get(f"{base_url}/about", headers=_judge0_headers(), timeout=10)
        resp.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)


logger = logging.getLogger(__name__)


class LocalCodeExecutor:
    """Fallback local code executor for when Judge0 fails"""

    def __init__(self):
        self.timeout = 5  # 5 second timeout

    def execute_python_code(self, code, test_cases):
        """Execute Python code locally with test cases"""
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


def _post_evaluation_update(sub: Submission) -> None:
    """After a submission is evaluated, mark the problem as solved for the student
    if and only if all tests passed (full score). Safe to call multiple times.
    """
    try:
        # Only for logged-in students
        if not sub.student_id:
            return
        # Update per-track shadow tables for easier evaluation exports
        try:
            cname = (sub.problem.contest.name or "").lower() if sub.problem and sub.problem.contest_id else ""
        except Exception:
            cname = ""
        if "junior" in cname:
            from .models import JuniorSubmission
            try:
                js = JuniorSubmission.objects.filter(orig_submission=sub.id).first()
                if js:
                    js.status = sub.status
                    js.score = sub.score
                    js.max_score = sub.max_score
                    js.judge0_tokens = sub.judge0_tokens
                    js.judge0_raw = sub.judge0_raw
                    js.save(update_fields=["status", "score", "max_score", "judge0_tokens", "judge0_raw", "updated_at"])
            except Exception:
                logger.exception("mirror.junior.update_failed", extra={"submission_id": str(sub.id)})
        elif "senior" in cname:
            from .models import SeniorSubmission
            try:
                ss = SeniorSubmission.objects.filter(orig_submission=sub.id).first()
                if ss:
                    ss.status = sub.status
                    ss.score = sub.score
                    ss.max_score = sub.max_score
                    ss.judge0_tokens = sub.judge0_tokens
                    ss.judge0_raw = sub.judge0_raw
                    ss.save(update_fields=["status", "score", "max_score", "judge0_tokens", "judge0_raw", "updated_at"])
            except Exception:
                logger.exception("mirror.senior.update_failed", extra={"submission_id": str(sub.id)})

        # Only count as solved when evaluation is DONE and perfect
        if (
            sub.status == Submission.Status.DONE
            and sub.max_score > 0
            and float(sub.score) >= float(sub.max_score)
        ):
            us, _ = UserSolution.objects.get_or_create(
                student=sub.student, problem=sub.problem
            )
            # Compute cumulative time across testcases if available
            try:
                total_time_ms = 0.0
                # Prefer saved per-testcase times; fallback to judge0_raw duration if present
                res = list(sub.results.all())
                if res:
                    for r in res:
                        try:
                            total_time_ms += float(r.time_ms or 0)
                        except Exception:
                            pass
                else:
                    # Convert seconds to ms
                    dur_s = float(sub.judge0_raw.get("duration_s", 0)) if isinstance(sub.judge0_raw, dict) else 0.0
                    total_time_ms = max(0.0, dur_s * 1000.0)
            except Exception:
                total_time_ms = None

            # Preserve first AC time
            updates = []
            if not us.is_solved:
                us.is_solved = True
                us.solved_at = sub.updated_at or timezone.now()
                updates += ["is_solved", "solved_at"]

            # Update best code/language on first AC or when we have a faster submission
            is_faster = False
            if total_time_ms is not None:
                if us.best_time_ms is None or total_time_ms < float(us.best_time_ms):
                    us.best_time_ms = total_time_ms
                    us.best_submission_id = sub.id
                    is_faster = True
                    updates += ["best_time_ms", "best_submission_id"]

            if not us.best_code or is_faster:
                us.best_code = sub.code
                us.language = sub.language
                updates += ["best_code", "language"]

            if updates:
                us.save(update_fields=updates)
    except Exception:
        # Never break evaluation flow due to leaderboard updates
        logger.exception(
            "leaderboard.post_update_failed",
            extra={"submission_id": str(sub.id)},
        )


@shared_task(
    bind=True,
    autoretry_for=(
        requests.RequestException,
        requests.ConnectionError,
        requests.Timeout,
    ),
    retry_backoff=2,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def evaluate_submission(self, submission_id: str):
    """
    Evaluate a submission using Judge0 API with proper error handling and retry logic
    """
    try:
        sub = Submission.objects.select_related("problem").get(id=submission_id)
    except Submission.DoesNotExist:
        logger.error(
            "evaluate_submission.submission_not_found",
            extra={"submission_id": submission_id},
        )
        return submission_id

    # Idempotency: don't re-evaluate if already DONE
    if sub.status == Submission.Status.DONE:
        logger.info("judge0.evaluate.skip_done", extra={"submission_id": str(sub.id)})
        return str(sub.id)

    # Prepare source code (attempt to wrap with template if available)
    try:
        wrapped_code = maybe_wrap_code(sub.problem, sub.language, sub.code)
    except Exception:
        wrapped_code = sub.code

    # Check Judge0 connectivity before proceeding
    is_connected, connectivity_error = _check_judge0_connectivity()
    if not is_connected:
        logger.error(
            "judge0.connectivity_check.failed",
            extra={"submission_id": str(sub.id), "error": connectivity_error},
        )

        # Attempt local fallback execution instead of failing immediately
        try:
            testcases_qs = TestCase.objects.filter(
                problem=sub.problem, language=sub.language
            )
            testcase_count = testcases_qs.count()

            if testcase_count == 0:
                sub.status = Submission.Status.ERROR
                sub.judge0_raw = {
                    "error": "No test cases available for this problem",
                    "details": f"No TestCase records found for problem {sub.problem.id} with language '{sub.language}'",
                    "connectivity_error": connectivity_error,
                }
                sub.save(update_fields=["status", "judge0_raw", "updated_at"])
                return str(sub.id)

            tests = []
            file_errors = []
            for tc in testcases_qs:
                if not tc.file or not tc.file.path.endswith(".json"):
                    file_errors.append(
                        f"TestCase {tc.id}: Invalid file path or extension"
                    )
                    continue
                try:
                    with open(tc.file.path, "r") as f:
                        data = json.load(f)
                        test_cases_in_file = data.get("test_cases", [])
                        if not test_cases_in_file:
                            file_errors.append(
                                f"TestCase {tc.id}: No 'test_cases' array found in JSON"
                            )
                            continue
                        for case in test_cases_in_file:
                            tests.append(
                                {
                                    "stdin": case.get("stdin", ""),
                                    "expected_output": case.get("expected_output", ""),
                                    "group": case.get("group", "default"),
                                    "weight": float(case.get("weight", 1.0)),
                                }
                            )
                except Exception as e:
                    file_errors.append(f"TestCase {tc.id} ({tc.file.path}): {str(e)}")

            if not tests:
                sub.status = Submission.Status.ERROR
                sub.judge0_raw = {
                    "error": "No valid test cases could be loaded",
                    "details": f"Found {testcase_count} TestCase records but couldn't load any valid test cases",
                    "file_errors": file_errors,
                    "connectivity_error": connectivity_error,
                }
                sub.save(update_fields=["status", "judge0_raw", "updated_at"])
                return str(sub.id)

            local_executor = LocalCodeExecutor()
            local_test_cases = [
                {"stdin": t["stdin"], "expected_output": t["expected_output"]}
                for t in tests
            ]

            local_results = local_executor.execute_python_code(
                wrapped_code, local_test_cases
            )

            total_weight = 0.0
            gained = 0.0
            for i, result in enumerate(local_results):
                SubmissionTestCaseResult.objects.update_or_create(
                    submission=sub,
                    index=i,
                    defaults={
                        "group": tests[i]["group"],
                        "weight": tests[i]["weight"],
                        "stdin": tests[i]["stdin"],
                        "expected_output": tests[i]["expected_output"],
                        "output": result.get("output", ""),
                        "passed": result.get("passed", False),
                        "status": result.get("status", "Unknown"),
                        "time_ms": float(result.get("time_ms", 0)),
                        "memory_kb": int(result.get("memory_kb", 0)),
                        "judge0_raw": {"local_fallback": True},
                    },
                )
                total_weight += float(tests[i]["weight"])
                if result.get("passed"):
                    gained += float(tests[i]["weight"])

            sub.max_score = total_weight
            sub.score = gained
            sub.status = Submission.Status.DONE
            sub.judge0_raw = {
                "local_execution": True,
                "fallback_reason": "Judge0 service is not accessible",
                "connectivity_error": connectivity_error,
                "timestamp": time.time(),
            }
            sub.save(
                update_fields=[
                    "max_score",
                    "score",
                    "status",
                    "judge0_raw",
                    "updated_at",
                ]
            )
            logger.info(
                "judge0.fallback.no_connectivity_success",
                extra={
                    "submission_id": str(sub.id),
                    "score": f"{gained}/{total_weight}",
                },
            )
            _post_evaluation_update(sub)
            return str(sub.id)

        except Exception as fb_error:
            sub.status = Submission.Status.ERROR
            sub.judge0_raw = {
                "error": "Judge0 service is not accessible and local fallback failed",
                "connectivity_error": connectivity_error,
                "fallback_error": str(fb_error),
                "timestamp": time.time(),
            }
            sub.save(update_fields=["status", "judge0_raw", "updated_at"])
            return str(sub.id)

    sub.status = Submission.Status.RUNNING
    sub.save(update_fields=["status", "updated_at"])

    try:
        # Load all testcases for the problem/language
        testcases_qs = TestCase.objects.filter(
            problem=sub.problem, language=sub.language
        )
        testcase_count = testcases_qs.count()

        logger.info(
            "judge0.testcase.loading",
            extra={
                "submission_id": str(sub.id),
                "problem_id": sub.problem.id,
                "language": sub.language,
                "testcase_records_found": testcase_count,
            },
        )

        if testcase_count == 0:
            sub.status = Submission.Status.ERROR
            sub.judge0_raw = {
                "error": "No test cases available for this problem",
                "details": f"No TestCase records found for problem {sub.problem.id} with language '{sub.language}'",
            }
            sub.save(update_fields=["status", "judge0_raw", "updated_at"])
            logger.error(
                "judge0.testcase.no_records",
                extra={
                    "submission_id": str(sub.id),
                    "problem_id": sub.problem.id,
                    "language": sub.language,
                },
            )
            return str(sub.id)

        tests = []
        file_errors = []

        for tc in testcases_qs:
            if not tc.file or not tc.file.path.endswith(".json"):
                file_errors.append(f"TestCase {tc.id}: Invalid file path or extension")
                continue

            try:
                with open(tc.file.path, "r") as f:
                    data = json.load(f)
                    test_cases_in_file = data.get("test_cases", [])

                    if not test_cases_in_file:
                        file_errors.append(
                            f"TestCase {tc.id}: No 'test_cases' array found in JSON"
                        )
                        continue

                    for case in test_cases_in_file:
                        tests.append(
                            {
                                "stdin": case.get("stdin", ""),
                                "expected_output": case.get("expected_output", ""),
                                "group": case.get("group", "default"),
                                "weight": float(case.get("weight", 1.0)),
                            }
                        )

                    logger.info(
                        "judge0.testcase.loaded",
                        extra={
                            "submission_id": str(sub.id),
                            "testcase_id": tc.id,
                            "file_path": tc.file.path,
                            "test_cases_loaded": len(test_cases_in_file),
                        },
                    )

            except Exception as e:
                error_msg = f"TestCase {tc.id} ({tc.file.path}): {str(e)}"
                file_errors.append(error_msg)
                logger.warning(
                    "judge0.testcase.parse_error",
                    extra={
                        "submission_id": str(sub.id),
                        "testcase_id": tc.id,
                        "testcase_file": tc.file.path,
                        "error": str(e),
                    },
                )

        if not tests:
            sub.status = Submission.Status.ERROR
            sub.judge0_raw = {
                "error": "No valid test cases could be loaded",
                "details": f"Found {testcase_count} TestCase records but couldn't load any valid test cases",
                "file_errors": file_errors,
            }
            sub.save(update_fields=["status", "judge0_raw", "updated_at"])
            logger.error(
                "judge0.testcase.no_valid_tests",
                extra={
                    "submission_id": str(sub.id),
                    "testcase_records": testcase_count,
                    "file_errors": file_errors,
                },
            )
            return str(sub.id)

        logger.info(
            "judge0.testcase.ready",
            extra={
                "submission_id": str(sub.id),
                "total_test_cases": len(tests),
                "testcase_records": testcase_count,
            },
        )

        # Build batch submissions
        LANGUAGE_MAP = {
            "python": 71,
            "cpp": 54,
            "c": 50,
            "java": 62,
            "javascript": 63,
        }
        lang_id = LANGUAGE_MAP.get(sub.language)
        if not lang_id:
            sub.status = Submission.Status.ERROR
            sub.judge0_raw = {"error": f"Unsupported language {sub.language}"}
            sub.save(update_fields=["status", "judge0_raw", "updated_at"])
            return str(sub.id)

        submissions_payload = [
            {
                "source_code": wrapped_code,
                "language_id": lang_id,
                "stdin": t["stdin"],
                "expected_output": t["expected_output"],
            }
            for t in tests
        ]

        base_url = getattr(settings, "JUDGE0_URL", "http://localhost:2358").rstrip("/")
        payload = {"submissions": submissions_payload}

        logger.info(
            "judge0.create_batch.start",
            extra={
                "submission_id": str(sub.id),
                "base_url": base_url,
                "tests": len(submissions_payload),
                "language": sub.language,
                "payload_sample": (
                    payload["submissions"][0] if payload["submissions"] else None
                ),
            },
        )

        # Create individual submissions instead of batch
        logger.info(
            "judge0.create_individual.start",
            extra={
                "submission_id": str(sub.id),
                "base_url": base_url,
                "tests": len(submissions_payload),
                "language": sub.language,
            },
        )

        tokens = []
        for i, test_payload in enumerate(submissions_payload):
            try:
                create_resp = requests.post(
                    f"{base_url}/submissions?base64_encoded=false&wait=false",
                    headers=_judge0_headers(),
                    json=test_payload,
                    timeout=30,
                )
                create_resp.raise_for_status()

                create_data = create_resp.json()
                token = create_data.get("token")
                if token:
                    tokens.append(token)
                else:
                    logger.error(
                        "judge0.create_individual.no_token",
                        extra={
                            "submission_id": str(sub.id),
                            "test_index": i,
                            "response": create_data,
                        },
                    )

            except requests.RequestException as e:
                error_response = None
                if hasattr(e, "response") and e.response is not None:
                    try:
                        error_response = e.response.text
                    except Exception:
                        error_response = "Could not parse response"

                logger.error(
                    "judge0.create_individual.request_failed",
                    extra={
                        "submission_id": str(sub.id),
                        "test_index": i,
                        "error": str(e),
                        "status_code": (
                            getattr(e.response, "status_code", None)
                            if hasattr(e, "response")
                            else None
                        ),
                        "response_text": error_response,
                        "payload": test_payload,
                    },
                )
                # Continue with other tests instead of failing completely
                continue

        if not tokens:
            logger.warning(
                "judge0.fallback.local_execution",
                extra={
                    "submission_id": str(sub.id),
                    "reason": "No successful Judge0 submissions",
                },
            )

            # Use local executor as fallback
            try:
                local_executor = LocalCodeExecutor()

                # Convert test cases to local executor format
                local_test_cases = []
                for tc in tests:
                    local_test_cases.append(
                        {"stdin": tc["stdin"], "expected_output": tc["expected_output"]}
                    )

                # Execute locally
                local_results = local_executor.execute_python_code(
                    wrapped_code, local_test_cases
                )

                # Create SubmissionTestCaseResult objects
                for result in local_results:
                    SubmissionTestCaseResult.objects.create(
                        submission=sub,
                        index=result["index"],
                        group=result["group"],
                        weight=result["weight"],
                        status=result["status"],
                        passed=result["passed"],
                        time_ms=result["time_ms"],
                        memory_kb=result["memory_kb"],
                        output=result["output"],
                        expected_output=result["expected_output"],
                    )

                # Calculate score
                passed_tests = sum(1 for r in local_results if r["passed"])
                total_weight = sum(r["weight"] for r in local_results)
                score = (
                    (passed_tests / len(local_results)) * total_weight
                    if local_results
                    else 0
                )

                sub.status = Submission.Status.DONE
                sub.score = score
                sub.max_score = total_weight
                sub.judge0_raw = {
                    "local_execution": True,
                    "results": local_results,
                    "timestamp": time.time(),
                }
                sub.save(
                    update_fields=[
                        "status",
                        "score",
                        "max_score",
                        "judge0_raw",
                        "updated_at",
                    ]
                )

                logger.info(
                    "judge0.fallback.success",
                    extra={
                        "submission_id": str(sub.id),
                        "score": f"{score}/{total_weight}",
                        "passed_tests": f"{passed_tests}/{len(local_results)}",
                    },
                )
                _post_evaluation_update(sub)
                return str(sub.id)

            except Exception as local_error:
                logger.error(
                    "judge0.fallback.failed",
                    extra={"submission_id": str(sub.id), "error": str(local_error)},
                )
                # Fall back to original error handling
                sub.status = Submission.Status.ERROR
                sub.judge0_raw = {
                    "error": "No successful submissions to Judge0 and local fallback failed",
                    "local_error": str(local_error),
                    "total_tests": len(tests),
                    "timestamp": time.time(),
                }
                sub.save(update_fields=["status", "judge0_raw", "updated_at"])
                return str(sub.id)

        sub.judge0_tokens = tokens
        sub.save(update_fields=["judge0_tokens", "updated_at"])
        logger.info(
            "judge0.create_batch.ok",
            extra={
                "submission_id": str(sub.id),
                "token_count": len(tokens),
            },
        )

        # Poll results in batches with improved timeout handling
        results = [None] * len(tokens)
        start = time.time()
        poll_timeout = 120  # Increased to 2 minutes

        while any(r is None for r in results):
            try:
                poll = requests.get(
                    f"{base_url}/submissions/batch?tokens={','.join(tokens)}&base64_encoded=false",
                    headers=_judge0_headers(),
                    timeout=30,
                )
                poll.raise_for_status()
            except requests.RequestException as e:
                logger.warning(
                    "judge0.poll.request_failed",
                    extra={
                        "submission_id": str(sub.id),
                        "error": str(e),
                        "elapsed_s": round(time.time() - start, 2),
                    },
                )
                time.sleep(2)  # Brief pause before retry
                continue

            poll_data = poll.json()
            # poll_data might be {"submissions": [ ... ]}
            items = poll_data.get("submissions", poll_data)
            for i, item in enumerate(items):
                if i >= len(results):  # Safety check
                    continue
                status_id = (item.get("status") or {}).get("id")
                if status_id in (1, 2):  # In Queue / Processing
                    continue
                results[i] = item

            if time.time() - start > poll_timeout:
                logger.warning(
                    "judge0.poll.timeout",
                    extra={
                        "submission_id": str(sub.id),
                        "waited_s": round(time.time() - start, 2),
                        "completed_results": sum(1 for r in results if r is not None),
                        "total_results": len(results),
                    },
                )
                break
            time.sleep(1)

        # Persist per-test results
        total_weight = 0.0
        gained = 0.0
        internal_error_count = 0

        for i, (test, item) in enumerate(zip(tests, results)):
            status = (item or {}).get("status", {})
            status_desc = status.get("description", "Unknown")
            stdout = (item or {}).get("stdout") or ""
            stderr = (item or {}).get("stderr") or ""
            out = (stdout or stderr or "").strip()
            passed = out.strip() == str(test["expected_output"]).strip()
            time_ms = (item or {}).get("time") or 0
            mem_kb = (item or {}).get("memory") or 0

            # Count internal errors for fallback detection
            if status_desc == "Internal Error":
                internal_error_count += 1

            SubmissionTestCaseResult.objects.update_or_create(
                submission=sub,
                index=i,
                defaults={
                    "group": test["group"],
                    "weight": test["weight"],
                    "stdin": test["stdin"],
                    "expected_output": test["expected_output"],
                    "output": out,
                    "passed": passed,
                    "status": status_desc,
                    "time_ms": float(time_ms) if time_ms else 0.0,
                    "memory_kb": int(mem_kb) if mem_kb else 0,
                    "judge0_raw": item or {},
                },
            )
            total_weight += float(test["weight"])
            if passed:
                gained += float(test["weight"])

        # Check if all submissions failed with Internal Error - trigger local fallback
        if internal_error_count == len(results) and internal_error_count > 0:
            logger.warning(
                "judge0.fallback.all_internal_errors",
                extra={
                    "submission_id": str(sub.id),
                    "failed_tests": internal_error_count,
                    "total_tests": len(results),
                },
            )

            try:
                # Clear existing failed results
                sub.results.all().delete()

                local_executor = LocalCodeExecutor()

                # Convert test cases to local executor format
                local_test_cases = []
                for tc in tests:
                    local_test_cases.append(
                        {"stdin": tc["stdin"], "expected_output": tc["expected_output"]}
                    )

                # Execute locally
                local_results = local_executor.execute_python_code(
                    wrapped_code, local_test_cases
                )

                # Create new SubmissionTestCaseResult objects
                total_weight = 0.0
                gained = 0.0
                for result in local_results:
                    SubmissionTestCaseResult.objects.create(
                        submission=sub,
                        index=result["index"],
                        group=result["group"],
                        weight=result["weight"],
                        stdin=local_test_cases[result["index"]]["stdin"],
                        expected_output=result["expected_output"],
                        output=result["output"],
                        passed=result["passed"],
                        status=result["status"],
                        time_ms=result["time_ms"],
                        memory_kb=result["memory_kb"],
                    )
                    total_weight += float(result["weight"])
                    if result["passed"]:
                        gained += float(result["weight"])

                # Update submission with local execution results
                sub.max_score = total_weight
                sub.score = gained
                sub.status = Submission.Status.DONE
                sub.judge0_raw = {
                    "local_execution": True,
                    "fallback_reason": "All Judge0 submissions returned Internal Error",
                    "original_duration_s": round(time.time() - start, 2),
                    "results": local_results,
                    "timestamp": time.time(),
                }
                sub.save(
                    update_fields=[
                        "max_score",
                        "score",
                        "status",
                        "judge0_raw",
                        "updated_at",
                    ]
                )

                logger.info(
                    "judge0.fallback.internal_error_success",
                    extra={
                        "submission_id": str(sub.id),
                        "score": f"{gained}/{total_weight}",
                        "passed_tests": f"{sum(1 for r in local_results if r['passed'])}/{len(local_results)}",
                    },
                )
                _post_evaluation_update(sub)
                return str(sub.id)

            except Exception as local_error:
                logger.error(
                    "judge0.fallback.internal_error_failed",
                    extra={"submission_id": str(sub.id), "error": str(local_error)},
                )
                # Continue with original Judge0 error results

        # Original Judge0 result processing
        sub.max_score = total_weight
        sub.score = gained
        sub.status = (
            Submission.Status.DONE if None not in results else Submission.Status.ERROR
        )
        sub.judge0_raw = {"duration_s": round(time.time() - start, 2)}
        sub.save(
            update_fields=["score", "max_score", "status", "judge0_raw", "updated_at"]
        )
        _post_evaluation_update(sub)

        logger.info(
            "judge0.evaluate.done",
            extra={
                "submission_id": str(sub.id),
                "status": sub.status,
                "score": sub.score,
                "max_score": sub.max_score,
                "duration_s": sub.judge0_raw.get("duration_s"),
            },
        )
        return str(sub.id)

    except Exception as e:
        logger.error(
            "judge0.evaluate.unexpected_error",
            extra={
                "submission_id": str(sub.id),
                "error": str(e),
                "retry": self.request.retries,
            },
        )

        # Update submission with error status
        sub.status = Submission.Status.ERROR
        sub.judge0_raw = {
            "error": "Unexpected error during evaluation",
            "details": str(e),
            "timestamp": time.time(),
            "retry_count": self.request.retries,
        }
        sub.save(update_fields=["status", "judge0_raw", "updated_at"])

        # Re-raise for potential retry
        raise
