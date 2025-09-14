# Judge0/Celery Integration Bug Fix

## Problem Description
When users submitted code, the UI showed: "An error occurred while processing your code. Please try again." This was caused by several issues in the Judge0/Celery integration.

## Root Causes Identified

1. **Missing Redis Package**: The `redis` Python package was not installed, causing Celery to fail when trying to connect to Redis broker
2. **Missing Environment Variables**: `JUDGE0_AUTH_TOKEN` was missing from worker and beat services in docker-compose.yml
3. **Poor Error Handling**: No proper exception handling in submission endpoints, leading to generic error messages
4. **No Connectivity Checks**: No validation that Judge0 service is accessible before attempting to queue tasks
5. **Inadequate Retry Logic**: Limited retry mechanisms and timeout handling

## Fixes Applied

### 1. Environment Configuration (`infra/compose/dev/docker-compose.yml`)
- ✅ Added `JUDGE0_AUTH_TOKEN: ${JUDGE0_AUTH_TOKEN:-}` to `worker`, `beat`, and `backend` services
- ✅ Ensures consistent environment variables across all services

### 2. Python Dependencies
- ✅ Installed missing packages: `redis`, `celery`, `python-json-logger`, `django-cors-headers`

### 3. Enhanced Error Handling (`accounts/views.py`)
- ✅ Added try-catch blocks around `evaluate_submission.delay()` calls
- ✅ Graceful fallback when Celery is unavailable (returns 503 with clear message)
- ✅ User-friendly error messages instead of generic exceptions
- ✅ Debug-aware error details (only shown when `DEBUG=True`)

### 4. Improved Task Reliability (`accounts/tasks.py`)
- ✅ Added Judge0 connectivity check before processing submissions
- ✅ Enhanced retry logic with exponential backoff
- ✅ Increased timeouts (30s for requests, 120s for polling)
- ✅ Better error logging with structured data
- ✅ Graceful handling of partial failures

### 5. Health Check Endpoint (`/healthz/`)
- ✅ Added comprehensive health check for database, Judge0, and Celery
- ✅ Returns detailed status for each service component
- ✅ Enables monitoring and alerting

## Usage Instructions

### Development Setup
```bash
# 1. Install dependencies
pip install redis celery python-json-logger django-cors-headers

# 2. Start services
docker compose -f infra/compose/dev/docker-compose.yml up -d

# 3. Start Django development server
cd src/student_auth
python manage.py runserver

# 4. Start Celery worker (in separate terminal)
celery -A student_auth worker -l info

# 5. Test the integration
python test_integration.py
```

### Health Check
```bash
# Check overall system health
curl http://localhost:8000/healthz/

# Example healthy response:
{
  "database": "ok",
  "judge0": "ok", 
  "celery": "ok",
  "overall": "ok"
}

# Example degraded response:
{
  "database": "ok",
  "judge0": "error",
  "judge0_error": "Connection refused",
  "celery": "ok", 
  "overall": "degraded"
}
```

### Testing Judge0 Direct Access
```bash
# Test Judge0 service directly
curl http://localhost:2358/about

# Expected response:
{
  "version": "1.13.0",
  "homepage": "https://judge0.com",
  "source_code": "https://github.com/judge0/judge0",
  "maintainer": "Herman Zvonimir Došilović <hermanz.dosilovic@gmail.com>"
}
```

### Testing Submission API
```bash
# Create submission
curl -X POST http://localhost:8000/api/submissions/ \
  -H "Content-Type: application/json" \
  -d '{"problem_id": 1, "code": "print(1+1)", "language": "python"}'

# Expected response:
{
  "submission_id": "uuid-here",
  "status": "PENDING"
}

# Check submission status
curl http://localhost:8000/api/submissions/{submission_id}/

# Expected response:
{
  "id": "uuid-here",
  "status": "DONE",
  "score": 1.0,
  "max_score": 1.0,
  "results": [...]
}
```

## Error Messages

### Before Fix
- Generic: "An error occurred while processing your code. Please try again."
- No indication of root cause
- Users left confused about what went wrong

### After Fix
- **Celery Unavailable**: "Code evaluation service is temporarily unavailable. Please try again later."
- **Judge0 Unreachable**: Task retries automatically with exponential backoff
- **Timeout Issues**: Increased timeouts and better polling logic
- **Debug Information**: Detailed error info available when `DEBUG=True`

## Monitoring and Alerts

### Health Check Integration
- Use `/healthz/` endpoint for monitoring systems
- Returns HTTP 503 when services are degraded
- Structured JSON response for automated parsing

### Logging
Enhanced logging with structured data:
```python
logger.info("judge0.evaluate.done", extra={
    "submission_id": str(sub.id),
    "status": sub.status,
    "score": sub.score,
    "duration_s": sub.judge0_raw.get("duration_s"),
})
```

### Retry Behavior
- **Max Retries**: 3 attempts for network issues
- **Backoff**: Exponential with jitter to prevent thundering herd
- **Timeout**: 30s for individual requests, 120s for polling
- **Circuit Breaker**: Connectivity check before processing

## Testing

Run the integration test suite:
```bash
python test_integration.py
```

This validates:
- ✅ Health check endpoint functionality
- ✅ Judge0 direct connectivity
- ✅ End-to-end submission workflow
- ✅ Error handling and fallback behavior

## Future Improvements

1. **Circuit Breaker Pattern**: Temporarily disable Judge0 calls when service is consistently failing
2. **Queue Monitoring**: Add Celery task monitoring and dead letter queues
3. **Rate Limiting**: Implement rate limiting on submission endpoints
4. **Metrics**: Add Prometheus metrics for submission processing times
5. **Async Frontend**: Update frontend to poll submission status instead of blocking

## Security Considerations

- `JUDGE0_AUTH_TOKEN` should be set in production environments
- Error details are only exposed when `DEBUG=True`
- Health check endpoint doesn't expose sensitive configuration
- Request timeouts prevent resource exhaustion

## Troubleshooting

### Common Issues

1. **"Task queue unavailable"**
   - Ensure Redis is running: `docker compose up redis`
   - Check Celery worker is started: `celery -A student_auth worker -l info`

2. **"Judge0 service is not accessible"**
   - Verify Judge0 is running: `docker compose up judge0`
   - Check Judge0 health: `curl http://localhost:2358/about`

3. **Submissions stuck in PENDING**
   - Check Celery worker logs for errors
   - Verify Judge0 connectivity from worker container
   - Check network configuration in docker-compose.yml

4. **High latency on submissions**
   - Monitor Judge0 performance: `curl http://localhost:2358/statistics`
   - Consider scaling worker processes
   - Check if Judge0 needs more resources