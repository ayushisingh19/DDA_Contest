# DDA Contest Platform - API Reference

This document provides comprehensive API documentation for the DDA Contest Platform. All endpoints follow RESTful conventions and return JSON responses.

## Table of Contents

1. [Base Information](#base-information)
2. [Authentication](#authentication)
3. [Problems API](#problems-api)
4. [Submissions API](#submissions-api)
5. [Contests API](#contests-api)
6. [Users API](#users-api)
7. [Judge0 Integration](#judge0-integration)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)
10. [Webhooks](#webhooks)

## Base Information

**Base URL:** `http://localhost/api/` (development)  
**API Version:** v1  
**Content-Type:** `application/json`  
**Authentication:** JWT Token or Session-based

### Standard Response Format

All API responses follow a consistent format:

**Success Response:**
```json
{
  "success": true,
  "data": { /* response data */ },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0",
    "request_id": "req_123456789"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* additional error details */ }
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0",
    "request_id": "req_123456789"
  }
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request successful, no content to return |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

## Authentication

The API supports both JWT token authentication and session-based authentication.

### Login

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "username": "student123",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "student123",
      "email": "student@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_staff": false
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "expires_in": 3600
    }
  }
}
```

### Register

**Endpoint:** `POST /api/auth/register/`

**Request:**
```json
{
  "username": "newstudent",
  "email": "newstudent@example.com",
  "password": "securepassword",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 2,
      "username": "newstudent",
      "email": "newstudent@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "is_staff": false
    },
    "message": "Registration successful. Please verify your email."
  }
}
```

### Token Refresh

**Endpoint:** `POST /api/auth/token/refresh/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

### Logout

**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Successfully logged out"
  }
}
```

### Current User Info

**Endpoint:** `GET /api/auth/user/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "student123",
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": false,
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-15T10:30:00Z"
  }
}
```

## Problems API

### List Problems

**Endpoint:** `GET /api/problems/`

**Query Parameters:**
- `difficulty` (optional): Filter by difficulty (Easy, Medium, Hard)
- `search` (optional): Search in title and description
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 20)

**Example:** `GET /api/problems/?difficulty=Easy&search=array&page=1`

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 25,
    "next": "http://localhost/api/problems/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "Two Sum",
        "description": "Given an array of integers and a target sum...",
        "difficulty": "Easy",
        "time_limit": 5,
        "memory_limit": 128,
        "acceptance_rate": 0.85,
        "total_submissions": 1250,
        "successful_submissions": 1062,
        "tags": ["array", "hash-table"],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-10T15:30:00Z"
      }
    ]
  },
  "meta": {
    "pagination": {
      "current_page": 1,
      "total_pages": 2,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

### Get Problem Details

**Endpoint:** `GET /api/problems/{id}/`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Two Sum",
    "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
    "difficulty": "Easy",
    "time_limit": 5,
    "memory_limit": 128,
    "acceptance_rate": 0.85,
    "total_submissions": 1250,
    "successful_submissions": 1062,
    "tags": ["array", "hash-table"],
    "constraints": [
      "2 <= nums.length <= 10^4",
      "-10^9 <= nums[i] <= 10^9",
      "-10^9 <= target <= 10^9"
    ],
    "examples": [
      {
        "input": "nums = [2,7,11,15], target = 9",
        "output": "[0,1]",
        "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
      }
    ],
    "starter_code": {
      "python": "def two_sum(nums, target):\n    pass",
      "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        \n    }\n};",
      "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        \n    }\n}",
      "javascript": "var twoSum = function(nums, target) {\n    \n};"
    },
    "test_cases": [
      {
        "id": 1,
        "input": "[2,7,11,15]\n9",
        "expected_output": "[0,1]",
        "is_sample": true
      },
      {
        "id": 2,
        "input": "[3,2,4]\n6",
        "expected_output": "[1,2]",
        "is_sample": true
      }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-10T15:30:00Z"
  }
}
```

### Create Problem (Admin Only)

**Endpoint:** `POST /api/problems/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

**Request:**
```json
{
  "title": "Three Sum",
  "description": "Given an integer array nums, return all the triplets...",
  "difficulty": "Medium",
  "time_limit": 10,
  "memory_limit": 256,
  "tags": ["array", "two-pointers", "sorting"],
  "constraints": [
    "3 <= nums.length <= 3000",
    "-10^5 <= nums[i] <= 10^5"
  ],
  "starter_code": {
    "python": "def three_sum(nums):\n    pass"
  },
  "test_cases": [
    {
      "input": "[-1,0,1,2,-1,-4]",
      "expected_output": "[[-1,-1,2],[-1,0,1]]",
      "is_sample": true
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 25,
    "title": "Three Sum",
    "difficulty": "Medium",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Update Problem (Admin Only)

**Endpoint:** `PUT /api/problems/{id}/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

**Request:** Same format as create problem

### Delete Problem (Admin Only)

**Endpoint:** `DELETE /api/problems/{id}/`

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Problem deleted successfully"
  }
}
```

## Submissions API

### Submit Code

**Endpoint:** `POST /api/submissions/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

**Request:**
```json
{
  "problem_id": 1,
  "language": "python",
  "source_code": "def two_sum(nums, target):\n    hash_map = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in hash_map:\n            return [hash_map[complement], i]\n        hash_map[num] = i\n    return []"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "submission_id": "sub_12345",
    "status": "queued",
    "message": "Code submitted successfully. Evaluation in progress.",
    "estimated_time": "30 seconds"
  }
}
```

### Get Submission Status

**Endpoint:** `GET /api/submissions/{submission_id}/`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "sub_12345",
    "problem": {
      "id": 1,
      "title": "Two Sum",
      "difficulty": "Easy"
    },
    "user": {
      "id": 1,
      "username": "student123"
    },
    "language": "python",
    "source_code": "def two_sum(nums, target):...",
    "status": "completed",
    "verdict": "accepted",
    "score": 100,
    "execution_time": "45ms",
    "memory_usage": "14.2MB",
    "test_results": [
      {
        "test_case_id": 1,
        "status": "passed",
        "execution_time": "12ms",
        "memory_usage": "13.8MB",
        "input": "[2,7,11,15], 9",
        "expected_output": "[0,1]",
        "actual_output": "[0,1]"
      },
      {
        "test_case_id": 2,
        "status": "passed",
        "execution_time": "15ms",
        "memory_usage": "14.2MB",
        "input": "[3,2,4], 6",
        "expected_output": "[1,2]",
        "actual_output": "[1,2]"
      }
    ],
    "error_message": null,
    "submitted_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:30:45Z"
  }
}
```

### List User Submissions

**Endpoint:** `GET /api/submissions/`

**Query Parameters:**
- `problem_id` (optional): Filter by problem
- `status` (optional): Filter by status (queued, running, completed, error)
- `verdict` (optional): Filter by verdict (accepted, wrong_answer, time_limit_exceeded, etc.)
- `page` (optional): Page number
- `page_size` (optional): Items per page

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 45,
    "next": "http://localhost/api/submissions/?page=2",
    "previous": null,
    "results": [
      {
        "id": "sub_12345",
        "problem": {
          "id": 1,
          "title": "Two Sum",
          "difficulty": "Easy"
        },
        "language": "python",
        "status": "completed",
        "verdict": "accepted",
        "score": 100,
        "execution_time": "45ms",
        "submitted_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### Get Submission Code

**Endpoint:** `GET /api/submissions/{submission_id}/code/`

**Response:**
```json
{
  "success": true,
  "data": {
    "source_code": "def two_sum(nums, target):\n    hash_map = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in hash_map:\n            return [hash_map[complement], i]\n        hash_map[num] = i\n    return []",
    "language": "python",
    "language_version": "3.11.0"
  }
}
```

## Contests API

### List Contests

**Endpoint:** `GET /api/contests/`

**Query Parameters:**
- `status` (optional): Filter by status (upcoming, active, completed)
- `search` (optional): Search in title and description

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 12,
    "results": [
      {
        "id": 1,
        "title": "Weekly Contest 123",
        "description": "Weekly programming contest featuring algorithmic problems",
        "status": "active",
        "start_time": "2024-01-15T09:00:00Z",
        "end_time": "2024-01-15T11:00:00Z",
        "duration": 120,
        "max_participants": 1000,
        "current_participants": 245,
        "problems": [
          {
            "id": 1,
            "title": "Two Sum",
            "difficulty": "Easy",
            "points": 100
          },
          {
            "id": 2,
            "title": "Add Two Numbers",
            "difficulty": "Medium",
            "points": 200
          }
        ],
        "created_at": "2024-01-10T00:00:00Z"
      }
    ]
  }
}
```

### Get Contest Details

**Endpoint:** `GET /api/contests/{id}/`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Weekly Contest 123",
    "description": "Weekly programming contest featuring algorithmic problems of varying difficulty levels.",
    "status": "active",
    "start_time": "2024-01-15T09:00:00Z",
    "end_time": "2024-01-15T11:00:00Z",
    "duration": 120,
    "max_participants": 1000,
    "current_participants": 245,
    "rules": [
      "Each problem has a specific point value",
      "Penalty for wrong submissions: 20 minutes",
      "Final ranking based on total score and time"
    ],
    "problems": [
      {
        "id": 1,
        "title": "Two Sum",
        "difficulty": "Easy",
        "points": 100,
        "solved_count": 180,
        "total_submissions": 320
      }
    ],
    "user_participation": {
      "is_registered": true,
      "registration_time": "2024-01-14T15:30:00Z",
      "current_rank": 42,
      "total_score": 300,
      "problems_solved": 2
    },
    "created_at": "2024-01-10T00:00:00Z"
  }
}
```

### Register for Contest

**Endpoint:** `POST /api/contests/{id}/register/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Successfully registered for Weekly Contest 123",
    "registration_time": "2024-01-15T08:45:00Z"
  }
}
```

### Contest Leaderboard

**Endpoint:** `GET /api/contests/{id}/leaderboard/`

**Query Parameters:**
- `page` (optional): Page number
- `page_size` (optional): Items per page (default: 50)

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 245,
    "results": [
      {
        "rank": 1,
        "user": {
          "id": 15,
          "username": "codemaster",
          "first_name": "Alice",
          "last_name": "Johnson"
        },
        "total_score": 800,
        "problems_solved": 4,
        "total_time": 85,
        "last_submission_time": "2024-01-15T10:25:00Z",
        "problem_scores": [
          {
            "problem_id": 1,
            "score": 100,
            "attempts": 1,
            "solve_time": 15
          },
          {
            "problem_id": 2,
            "score": 200,
            "attempts": 2,
            "solve_time": 35
          }
        ]
      }
    ]
  }
}
```

## Users API

### Get User Profile

**Endpoint:** `GET /api/users/{user_id}/`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "student123",
    "first_name": "John",
    "last_name": "Doe",
    "email": "student@example.com",
    "profile": {
      "bio": "Passionate about algorithms and data structures",
      "location": "New York, USA",
      "github_username": "johndoe",
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "website": "https://johndoe.dev"
    },
    "statistics": {
      "problems_solved": 45,
      "total_submissions": 128,
      "acceptance_rate": 0.72,
      "ranking": 156,
      "contests_participated": 12,
      "best_contest_rank": 8
    },
    "badges": [
      {
        "id": "first_solve",
        "name": "First Blood",
        "description": "First to solve a problem",
        "earned_at": "2024-01-10T14:30:00Z"
      }
    ],
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

### Update User Profile

**Endpoint:** `PUT /api/users/{user_id}/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "bio": "Updated bio",
    "location": "San Francisco, USA",
    "github_username": "johndoe_sf"
  }
}
```

### User Submission History

**Endpoint:** `GET /api/users/{user_id}/submissions/`

**Query Parameters:**
- `problem_id` (optional): Filter by problem
- `verdict` (optional): Filter by verdict
- `limit` (optional): Number of recent submissions (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "submissions": [
      {
        "id": "sub_12345",
        "problem": {
          "id": 1,
          "title": "Two Sum",
          "difficulty": "Easy"
        },
        "language": "python",
        "verdict": "accepted",
        "score": 100,
        "submitted_at": "2024-01-15T10:30:00Z"
      }
    ],
    "statistics": {
      "total_submissions": 128,
      "accepted_submissions": 92,
      "acceptance_rate": 0.72
    }
  }
}
```

## Judge0 Integration

### Get Judge0 Status

**Endpoint:** `GET /api/judge0/health/`

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.13.0",
    "available_languages": [
      {
        "id": 71,
        "name": "Python (3.8.1)"
      },
      {
        "id": 54,
        "name": "C++ (GCC 9.2.0)"
      },
      {
        "id": 62,
        "name": "Java (OpenJDK 13.0.1)"
      },
      {
        "id": 63,
        "name": "JavaScript (Node.js 12.14.0)"
      }
    ],
    "queue_status": {
      "pending": 3,
      "processing": 2
    }
  }
}
```

### Get Supported Languages

**Endpoint:** `GET /api/judge0/languages/`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 71,
      "name": "Python (3.8.1)",
      "compile_cmd": null,
      "run_cmd": "/usr/local/python3/bin/python3 \\\"main.py\\\"",
      "source_file": "main.py"
    },
    {
      "id": 54,
      "name": "C++ (GCC 9.2.0)",
      "compile_cmd": "/usr/local/gcc-9.2.0/bin/g++ {source_file} -o main",
      "run_cmd": "./main",
      "source_file": "main.cpp"
    }
  ]
}
```

## Error Handling

### Common Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | Request validation failed | 400 |
| `AUTHENTICATION_FAILED` | Invalid credentials | 401 |
| `TOKEN_EXPIRED` | JWT token has expired | 401 |
| `PERMISSION_DENIED` | Insufficient permissions | 403 |
| `RESOURCE_NOT_FOUND` | Requested resource not found | 404 |
| `DUPLICATE_ENTRY` | Resource already exists | 409 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `JUDGE0_UNAVAILABLE` | Judge0 service unavailable | 503 |
| `INTERNAL_ERROR` | Server internal error | 500 |

### Validation Error Example

**Request:** `POST /api/problems/` with invalid data

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "title": ["This field is required"],
      "difficulty": ["Select a valid choice. 'Expert' is not one of the available choices."],
      "time_limit": ["Ensure this value is greater than 0"]
    }
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### Judge0 Error Example

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "JUDGE0_UNAVAILABLE",
    "message": "Code execution service is temporarily unavailable",
    "details": {
      "service": "judge0",
      "retry_after": 30,
      "status": "maintenance"
    }
  }
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

### Rate Limits

| Endpoint Category | Rate Limit | Window |
|------------------|------------|---------|
| Authentication | 5 requests | 1 minute |
| Code Submission | 10 requests | 1 minute |
| Problem Listing | 100 requests | 1 minute |
| General API | 1000 requests | 1 hour |

### Rate Limit Headers

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642252800
```

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "limit": 10,
      "window": 60,
      "retry_after": 45
    }
  }
}
```

## Webhooks

### Contest Events

You can register webhooks to receive real-time notifications about contest events.

**Available Events:**
- `contest.started`
- `contest.ended`
- `submission.completed`
- `leaderboard.updated`

### Webhook Payload Example

```json
{
  "event": "submission.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "submission_id": "sub_12345",
    "user_id": 1,
    "problem_id": 1,
    "contest_id": 1,
    "verdict": "accepted",
    "score": 100,
    "execution_time": "45ms"
  }
}
```

### Webhook Registration

**Endpoint:** `POST /api/webhooks/`

**Request:**
```json
{
  "url": "https://your-app.com/webhooks/contest",
  "events": ["submission.completed", "contest.ended"],
  "secret": "your-webhook-secret"
}
```

---

## SDK and Libraries

### Python SDK Example

```python
import requests

class DDAContestAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def get_problems(self, difficulty=None):
        params = {'difficulty': difficulty} if difficulty else {}
        response = requests.get(
            f'{self.base_url}/problems/',
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def submit_code(self, problem_id, language, source_code):
        data = {
            'problem_id': problem_id,
            'language': language,
            'source_code': source_code
        }
        response = requests.post(
            f'{self.base_url}/submissions/',
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage
api = DDAContestAPI('http://localhost/api', 'your-jwt-token')
problems = api.get_problems(difficulty='Easy')
```

### JavaScript SDK Example

```javascript
class DDAContestAPI {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  async getProblems(difficulty) {
    const params = new URLSearchParams();
    if (difficulty) params.append('difficulty', difficulty);
    
    const response = await fetch(`${this.baseUrl}/problems/?${params}`, {
      headers: this.headers
    });
    return response.json();
  }

  async submitCode(problemId, language, sourceCode) {
    const response = await fetch(`${this.baseUrl}/submissions/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        problem_id: problemId,
        language: language,
        source_code: sourceCode
      })
    });
    return response.json();
  }
}

// Usage
const api = new DDAContestAPI('http://localhost/api', 'your-jwt-token');
const problems = await api.getProblems('Easy');
```

---

For more information and support, please refer to the [Development Guide](development-guide.md) or create an issue in the GitHub repository.