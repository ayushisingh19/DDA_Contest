# DDA Contest Platform - Development Guide

Welcome to the comprehensive development guide for the DDA Contest Platform. This guide will help you understand the architecture, set up your development environment, and contribute effectively to the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Architecture Overview](#architecture-overview)
3. [Development Environment Setup](#development-environment-setup)
4. [Code Style and Standards](#code-style-and-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [API Development](#api-development)
7. [Frontend Development](#frontend-development)
8. [Database Management](#database-management)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Git** (latest version)
- **Docker** (20.10+ and Docker Compose)
- **Python** 3.11+ (for local backend development)
- **Node.js** 18+ and npm (for frontend development)
- **VS Code** (recommended IDE with extensions)

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ddt-coding
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

3. **Start the development environment:**
   ```bash
   docker compose -f infra/compose/dev/docker-compose.yml up --build
   ```

4. **Verify installation:**
   - Backend: http://localhost/api/health/
   - Frontend: http://localhost:3000
   - Admin Panel: http://localhost/admin/

## Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Frontend    │────│      Nginx      │────│     Backend     │
│   (React/Vite)  │    │  (Load Balancer)│    │    (Django)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐             │
                       │     Judge0      │─────────────┤
                       │ (Code Execution)│             │
                       └─────────────────┘             │
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Redis       │────│     Celery      │────│   PostgreSQL    │
│    (Cache)      │    │   (Task Queue)  │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

**Backend:**
- **Django 5.2+** - Web framework
- **Django REST Framework** - API development
- **Celery** - Asynchronous task processing
- **PostgreSQL** - Primary database
- **Redis** - Caching and message broker

**Frontend:**
- **React 18+** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework

**Infrastructure:**
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and static file serving
- **Judge0** - Code execution engine

### Directory Structure

```
ddt-coding/
├── src/                    # Backend Django application
│   ├── config/            # Django settings and configuration
│   ├── student_auth/      # Authentication and user management
│   ├── contests/          # Contest management
│   ├── problems/          # Problem definitions and test cases
│   └── submissions/       # Code submission handling
├── frontend/              # React frontend application
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   └── dist/             # Build output
├── infra/                 # Infrastructure and deployment
│   ├── compose/          # Docker Compose configurations
│   ├── docker/           # Dockerfiles
│   └── kubernetes/       # K8s manifests (if used)
├── tests/                 # Test suites
├── tools/                 # Development tools and scripts
└── docs/                  # Documentation
```

## Development Environment Setup

### Docker Development (Recommended)

1. **Start all services:**
   ```bash
   docker compose -f infra/compose/dev/docker-compose.yml up -d
   ```

2. **View logs:**
   ```bash
   docker compose -f infra/compose/dev/docker-compose.yml logs -f [service-name]
   ```

3. **Execute commands in containers:**
   ```bash
   # Django commands
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py createsuperuser
   
   # Install frontend dependencies
   docker compose exec frontend npm install
   ```

### Local Development Setup

**Backend Setup:**
```bash
# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r backend/requirements/dev.txt

# Set up database
cd src
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

### VS Code Setup

Install recommended extensions:
- Python
- Django
- TypeScript and JavaScript
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Docker
- GitLens

## Code Style and Standards

### Backend (Python/Django)

**Code Formatting:**
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

**Coding Standards:**
- Use type hints for all function parameters and return values
- Follow Django naming conventions
- Write docstrings for all classes and functions
- Keep functions small and focused (max 20 lines)
- Use descriptive variable names

**Example:**
```python
from typing import Optional
from django.db import models
from django.contrib.auth.models import User

class Problem(models.Model):
    """
    Represents a coding problem in the contest platform.
    
    Attributes:
        title: Human-readable problem title
        description: Detailed problem statement
        difficulty: Problem difficulty level
        time_limit: Execution time limit in seconds
        memory_limit: Memory limit in MB
    """
    title: str = models.CharField(max_length=200)
    description: str = models.TextField()
    difficulty: str = models.CharField(
        max_length=20, 
        choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]
    )
    time_limit: int = models.PositiveIntegerField(default=5)
    memory_limit: int = models.PositiveIntegerField(default=128)
    
    def __str__(self) -> str:
        return f"{self.title} ({self.difficulty})"
    
    def get_test_cases(self) -> list['TestCase']:
        """Get all test cases for this problem."""
        return self.testcase_set.all()
```

### Frontend (TypeScript/React)

**Code Formatting:**
- **Prettier** for code formatting
- **ESLint** for linting

```bash
cd frontend

# Format code
npm run format

# Lint code
npm run lint

# Type checking
npm run type-check
```

**Coding Standards:**
- Use functional components with hooks
- Implement proper TypeScript interfaces
- Follow React best practices (key props, proper effect dependencies)
- Use meaningful component and variable names
- Keep components small and focused

**Example:**
```typescript
import React, { useState, useEffect } from 'react';
import { ProblemService } from '../services/api';

interface Problem {
  id: number;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  description: string;
}

interface ProblemListProps {
  difficulty?: string;
  onProblemSelect: (problem: Problem) => void;
}

export const ProblemList: React.FC<ProblemListProps> = ({ 
  difficulty, 
  onProblemSelect 
}) => {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProblems = async (): Promise<void> => {
      try {
        setLoading(true);
        const data = await ProblemService.getProblems({ difficulty });
        setProblems(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchProblems();
  }, [difficulty]);

  if (loading) return <div>Loading problems...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="problem-list">
      {problems.map((problem) => (
        <ProblemCard 
          key={problem.id} 
          problem={problem} 
          onClick={() => onProblemSelect(problem)}
        />
      ))}
    </div>
  );
};
```

## Testing Guidelines

### Backend Testing

**Testing Framework:** pytest with Django test client

**Test Structure:**
```
tests/
├── unit/                  # Unit tests
│   ├── test_models.py
│   ├── test_views.py
│   └── test_utils.py
├── integration/           # Integration tests
│   ├── test_api.py
│   └── test_workflows.py
└── fixtures/              # Test data
    └── sample_data.json
```

**Writing Tests:**
```python
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from student_auth.models import Problem, Submission

class ProblemModelTest(TestCase):
    """Test cases for Problem model."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.problem = Problem.objects.create(
            title="Test Problem",
            description="A test problem",
            difficulty="Easy",
            time_limit=5,
            memory_limit=128
        )
    
    def test_problem_creation(self) -> None:
        """Test problem creation and string representation."""
        self.assertEqual(str(self.problem), "Test Problem (Easy)")
        self.assertEqual(self.problem.time_limit, 5)
    
    def test_problem_validation(self) -> None:
        """Test problem field validation."""
        with self.assertRaises(ValidationError):
            Problem.objects.create(
                title="",  # Invalid: empty title
                description="Test",
                difficulty="Easy"
            )

@pytest.mark.django_db
class ProblemAPITest:
    """Test cases for Problem API endpoints."""
    
    def test_problem_list_api(self, client: Client) -> None:
        """Test problem list endpoint."""
        response = client.get('/api/problems/')
        assert response.status_code == 200
        assert 'results' in response.json()
```

**Running Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run with verbose output
pytest -v
```

### Frontend Testing

**Testing Framework:** Vitest with React Testing Library

**Test Structure:**
```
frontend/src/
├── components/
│   ├── ProblemList.tsx
│   └── __tests__/
│       └── ProblemList.test.tsx
├── services/
│   ├── api.ts
│   └── __tests__/
│       └── api.test.ts
└── utils/
    ├── helpers.ts
    └── __tests__/
        └── helpers.test.ts
```

**Writing Tests:**
```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ProblemList } from '../ProblemList';
import { ProblemService } from '../../services/api';

// Mock the API service
vi.mock('../../services/api');

describe('ProblemList Component', () => {
  it('renders loading state initially', () => {
    render(<ProblemList onProblemSelect={vi.fn()} />);
    expect(screen.getByText('Loading problems...')).toBeInTheDocument();
  });

  it('renders problems after loading', async () => {
    const mockProblems = [
      { id: 1, title: 'Test Problem', difficulty: 'Easy', description: 'Test' }
    ];
    
    vi.mocked(ProblemService.getProblems).mockResolvedValue(mockProblems);

    render(<ProblemList onProblemSelect={vi.fn()} />);
    
    expect(await screen.findByText('Test Problem')).toBeInTheDocument();
  });

  it('calls onProblemSelect when problem is clicked', async () => {
    const mockOnSelect = vi.fn();
    const mockProblems = [
      { id: 1, title: 'Test Problem', difficulty: 'Easy', description: 'Test' }
    ];
    
    vi.mocked(ProblemService.getProblems).mockResolvedValue(mockProblems);

    render(<ProblemList onProblemSelect={mockOnSelect} />);
    
    const problemElement = await screen.findByText('Test Problem');
    fireEvent.click(problemElement);
    
    expect(mockOnSelect).toHaveBeenCalledWith(mockProblems[0]);
  });
});
```

**Running Tests:**
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## API Development

### API Design Principles

1. **RESTful Design** - Follow REST conventions
2. **Consistent Naming** - Use consistent URL patterns and naming
3. **Proper HTTP Status Codes** - Use appropriate status codes
4. **Error Handling** - Provide clear error messages
5. **Documentation** - Document all endpoints

### API Endpoints

**Authentication:**
```
POST /api/auth/login/          # User login
POST /api/auth/logout/         # User logout
POST /api/auth/register/       # User registration
GET  /api/auth/user/           # Get current user info
```

**Problems:**
```
GET    /api/problems/          # List all problems
GET    /api/problems/{id}/     # Get specific problem
POST   /api/problems/          # Create new problem (admin)
PUT    /api/problems/{id}/     # Update problem (admin)
DELETE /api/problems/{id}/     # Delete problem (admin)
```

**Submissions:**
```
GET  /api/submissions/         # List user's submissions
POST /api/submissions/         # Submit code for evaluation
GET  /api/submissions/{id}/    # Get submission details
```

**Contests:**
```
GET  /api/contests/            # List active contests
GET  /api/contests/{id}/       # Get contest details
GET  /api/contests/{id}/leaderboard/  # Contest leaderboard
```

### API Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Two Sum",
    "difficulty": "Easy"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "title": ["This field is required"],
      "difficulty": ["Invalid choice"]
    }
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0"
  }
}
```

### Creating New API Endpoints

1. **Define the Model:**
```python
# src/problems/models.py
from django.db import models

class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
```

2. **Create Serializer:**
```python
# src/problems/serializers.py
from rest_framework import serializers
from .models import Problem

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'title', 'description', 'difficulty', 'created_at']
        read_only_fields = ['id', 'created_at']
```

3. **Implement ViewSet:**
```python
# src/problems/views.py
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Problem
from .serializers import ProblemSerializer

class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'meta': {'count': len(serializer.data)}
        })
```

4. **Add URL Configuration:**
```python
# src/problems/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProblemViewSet

router = DefaultRouter()
router.register(r'problems', ProblemViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## Database Management

### Migrations

**Creating Migrations:**
```bash
# Create migration for model changes
python manage.py makemigrations

# Create named migration
python manage.py makemigrations --name add_problem_tags

# Create empty migration for data migration
python manage.py makemigrations --empty problems
```

**Running Migrations:**
```bash
# Apply all migrations
python manage.py migrate

# Apply specific migration
python manage.py migrate problems 0002

# Reverse migration
python manage.py migrate problems 0001
```

**Data Migrations Example:**
```python
# Migration file: 0003_populate_sample_problems.py
from django.db import migrations

def create_sample_problems(apps, schema_editor):
    Problem = apps.get_model('problems', 'Problem')
    Problem.objects.create(
        title="Two Sum",
        description="Find two numbers that add up to target",
        difficulty="Easy"
    )

def reverse_sample_problems(apps, schema_editor):
    Problem = apps.get_model('problems', 'Problem')
    Problem.objects.filter(title="Two Sum").delete()

class Migration(migrations.Migration):
    dependencies = [
        ('problems', '0002_add_difficulty_field'),
    ]
    
    operations = [
        migrations.RunPython(
            create_sample_problems, 
            reverse_sample_problems
        ),
    ]
```

### Database Best Practices

1. **Always backup before migrations in production**
2. **Test migrations on staging environment first**
3. **Use database indexes for frequently queried fields**
4. **Avoid large data migrations in peak hours**
5. **Keep migration files in version control**

## Deployment Guide

### Production Deployment Checklist

**Environment Configuration:**
- [ ] Set `DEBUG=False`
- [ ] Configure strong `SECRET_KEY`
- [ ] Set up proper database credentials
- [ ] Configure Redis for production
- [ ] Set up proper `ALLOWED_HOSTS`
- [ ] Configure email backend
- [ ] Set up SSL certificates
- [ ] Configure static file serving

**Security Checklist:**
- [ ] Enable HTTPS redirect
- [ ] Set security headers
- [ ] Configure CORS properly
- [ ] Enable database connection encryption
- [ ] Set up proper firewall rules
- [ ] Configure rate limiting
- [ ] Enable logging and monitoring

**Infrastructure:**
- [ ] Set up load balancer
- [ ] Configure auto-scaling
- [ ] Set up database backups
- [ ] Configure log aggregation
- [ ] Set up monitoring and alerting
- [ ] Configure CI/CD pipelines

### Docker Production Deployment

1. **Build production images:**
```bash
# Build backend
docker build -f infra/docker/backend/Dockerfile -t dda-contest-backend:latest .

# Build frontend
docker build -f infra/docker/frontend/Dockerfile -t dda-contest-frontend:latest ./frontend
```

2. **Deploy with Docker Compose:**
```bash
docker compose -f infra/compose/prod/docker-compose.yml up -d
```

3. **Run database migrations:**
```bash
docker compose exec backend python manage.py migrate
```

4. **Collect static files:**
```bash
docker compose exec backend python manage.py collectstatic --noinput
```

### Kubernetes Deployment

Example Kubernetes manifests are available in `infra/kubernetes/`.

**Deploy to Kubernetes:**
```bash
# Apply all manifests
kubectl apply -f infra/kubernetes/

# Check deployment status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/backend
```

## Troubleshooting

### Common Issues

**Backend Issues:**

1. **Database Connection Error:**
   ```
   Error: could not connect to server
   ```
   **Solution:** Check database credentials and ensure PostgreSQL is running.

2. **Judge0 Connection Error:**
   ```
   Error: Judge0 service unavailable
   ```
   **Solution:** Verify Judge0 URL and ensure service is running.

3. **Celery Task Failures:**
   ```
   Error: Task timeout
   ```
   **Solution:** Check Redis connection and increase task timeout.

**Frontend Issues:**

1. **Build Failures:**
   ```
   Error: Module not found
   ```
   **Solution:** Run `npm install` and check import paths.

2. **API Connection Issues:**
   ```
   Error: Network request failed
   ```
   **Solution:** Check API URL configuration and CORS settings.

**Docker Issues:**

1. **Port Conflicts:**
   ```
   Error: Port already in use
   ```
   **Solution:** Stop conflicting services or change port mappings.

2. **Build Context Issues:**
   ```
   Error: Cannot find Dockerfile
   ```
   **Solution:** Check Dockerfile path and build context.

### Debug Mode

**Enable Debug Mode:**
```bash
# Set environment variable
DEBUG=True

# Django debug toolbar (development only)
pip install django-debug-toolbar
```

**Logging Configuration:**
```python
# settings/dev.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'student_auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Performance Monitoring

**Database Query Analysis:**
```python
# Enable query logging
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
}

# Use Django Debug Toolbar
# Install: pip install django-debug-toolbar
```

**Frontend Performance:**
```bash
# Build bundle analyzer
npm run build:analyze

# Lighthouse performance testing
npm install -g lighthouse
lighthouse http://localhost:3000
```

## Contributing

### Git Workflow

1. **Fork the repository**
2. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push and create pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(auth): add JWT token authentication
fix(api): handle null values in submission response
docs(readme): update installation instructions
test(problems): add unit tests for problem model
```

### Code Review Process

1. **Automated Checks:** All CI/CD checks must pass
2. **Code Review:** At least one maintainer review required
3. **Testing:** Ensure adequate test coverage
4. **Documentation:** Update relevant documentation

### Issue Reporting

When reporting issues, include:
- **Environment details** (OS, Docker version, etc.)
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Error messages and logs**
- **Screenshots** (if applicable)

---

## Getting Help

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and discussions
- **Documentation:** Check this guide and README.md
- **Code Comments:** Inline documentation in the codebase

Happy coding! 🚀