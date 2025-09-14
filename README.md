# DDA Contest Platform

A comprehensive college-focused coding competition platform featuring real-time code execution, automated judging, and contest management capabilities.

## 🏗️ Architecture

- **Backend**: Django 5.2.6 with REST Framework
- **Frontend**: React 18 with TypeScript and Vite
- **Code Execution**: Judge0 API v1.13.1
- **Database**: PostgreSQL with Redis caching
- **Task Processing**: Celery with Redis broker
- **Infrastructure**: Docker Compose for orchestration

## 🚀 Quick Start

### Prerequisites

- Git
- Docker & Docker Compose
- Python 3.8+ (for local development)
- Node.js 16+ (for frontend development)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ayushisingh19/DDA_Contest.git
   cd DDA_Contest
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the development environment**
   ```bash
   docker-compose -f infra/compose/dev/docker-compose.yml up --build
   ```

4. **Verify services**
   ```bash
   curl http://localhost/api/healthz  # Backend health check
   curl http://localhost              # Frontend application
   ```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
POSTGRES_DB=dda_contest
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_URL=redis://localhost:6379

# Judge0
JUDGE0_URL=http://localhost:2358

# Django
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📁 Project Structure

```
DDA_Contest/
├── src/                          # Main application code
│   └── student_auth/            # Django application
│       ├── accounts/            # User management & contests
│       ├── student_auth/        # Django project settings
│       └── manage.py           # Django management script
├── frontend/                    # React application
│   ├── src/                    # Source code
│   ├── package.json           # Dependencies
│   └── vite.config.ts         # Build configuration
├── backend/                     # Django backend configuration
│   ├── config/                 # Settings modules
│   └── requirements/           # Python dependencies
├── infra/                      # Infrastructure & deployment
│   ├── compose/               # Docker Compose configurations
│   └── docker/                # Docker build files
├── tests/                      # Test suites
│   └── integration/           # Integration tests
├── tools/                      # Utility scripts
│   └── scripts/              # Maintenance and setup scripts
└── docs/                       # Documentation
```

## 🔧 Development

This repository is set up to be easy to develop on and hard to break. We use formatters and linters across backend and frontend, plus tests. The same checks run locally and in CI.

### Tooling overview

- Backend (Python/Django)
   - Formatter: black
   - Linter: ruff
   - Tests: pytest (pytest-django)

- Frontend (React/TypeScript)
   - Formatter: prettier
   - Linter: eslint (@typescript-eslint)
   - Tests: npm test (placeholder; add tests as pages/components evolve)

### Backend Development

```bash
# Install dependencies
cd src/student_auth
python -m pip install -r ../../backend/requirements/dev.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Quality checks (backend):

```bash
# Format and lint (auto-fix) the backend codebase
black src/
ruff check src/ --fix

# Run tests
pytest -q
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

Quality checks (frontend):

```bash
# Format and lint the frontend
npm run format:check
npm run lint

# Auto-format
npm run format:write

# Run tests (if configured)
npm test
```

### Testing

```bash
# Backend tests
cd src/student_auth
python manage.py test

# Integration tests
python -m pytest tests/integration/

# Frontend tests
cd frontend
npm test
```

## 🏃‍♂️ Usage

### Admin Interface

1. Access Django admin at `http://localhost:8000/admin`
2. Login with superuser credentials
3. Manage contests, problems, and participants

### Creating Contests

1. Navigate to admin interface
2. Add new Contest with start/end times
3. Create Problems with test cases
4. Add Participants to contest

### Submitting Solutions

1. Students access contest at `http://localhost`
2. Register and login
3. Select problem and submit code
4. View real-time results and leaderboard

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout

### Contests
- `GET /api/contests/` - List active contests
- `GET /api/contests/{id}/` - Contest details
- `GET /api/contests/{id}/problems/` - Contest problems

### Submissions
- `POST /api/submissions/` - Submit solution
- `GET /api/submissions/{id}/` - Submission status
- `GET /api/leaderboard/{contest_id}/` - Contest leaderboard

### Health Checks
- `GET /api/healthz` - Backend health
- `GET /api/judge0/health` - Judge0 connectivity

## 🐳 Docker Services

The platform runs 9 services in development:

1. **backend** - Django application server
2. **frontend** - React development server
3. **nginx** - Reverse proxy and static files
4. **postgres** - Primary database
5. **redis** - Cache and task broker
6. **celery** - Background task worker
7. **celery-beat** - Scheduled task scheduler
8. **judge0-server** - Code execution engine
9. **judge0-worker** - Code execution worker

## 📊 Monitoring

### Service Health
```bash
# Check all containers
docker-compose -f infra/compose/dev/docker-compose.yml ps

# View logs
docker-compose -f infra/compose/dev/docker-compose.yml logs backend
```

### Performance Metrics
- Backend response times via Django admin
- Judge0 execution metrics at `http://localhost:2358`
- Redis monitoring via redis-cli

## 🛠️ Troubleshooting

### Common Issues

**Backend 500 errors**
- Check `JUDGE0_URL` configuration
- Verify Redis connectivity
- Check Docker network status

**Frontend build failures**
- Clear `node_modules`: `rm -rf frontend/node_modules`
- Reinstall dependencies: `cd frontend && npm install`

**Docker networking issues**
- Ensure ports 80, 2358, 6379 are available
- Check firewall settings
- Restart Docker daemon

**Permission errors**
- Ensure proper file permissions: `chmod -R 755 src/`
- Check Docker volume mounts

### Debug Mode

Enable debug logging:
```bash
# Set in .env
DEBUG=True
DJANGO_LOG_LEVEL=DEBUG

# Restart services
docker-compose -f infra/compose/dev/docker-compose.yml restart
```

## 🚀 Function Stub (Starter Code) Feature

The DDA Contest Platform includes an intelligent starter code generation system that provides language-specific templates for programming problems.

### For Students

- **Never start with a blank editor** - automatic starter code based on problem requirements
- **Language switching** - get appropriate templates for Python, Java, C++, C#, JavaScript, TypeScript
- **Smart templates** - includes function signatures, parameter hints, and return types
- **Toggle control** - enable/disable starter code or reset to original template

### For Maintainers

Set function metadata when creating problems:

```python
problem = Problem.objects.create(
    title="Two Sum",
    function_name="two_sum",
    function_params=["nums", "target"],
    return_type="List[int]"
)
```

Or provide custom starter code:

```python
problem.default_stub = {
    "python": "def two_sum(nums, target):\n    # Your solution here\n    pass",
    "java": "public class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Your solution here\n        return new int[]{};\n    }\n}"
}
```

### Bulk Population

Populate existing problems with starter code metadata:

```bash
cd src/student_auth
python populate_function_stubs.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Code Style

- Python: Follow PEP 8, use `black` and `ruff`
- TypeScript: Follow project ESLint configuration
- Commits: Use [Conventional Commits](https://conventionalcommits.org/)

### Local pre-flight checks

Before pushing a branch or opening a PR, run:

```bash
# Backend
black src/
ruff check src/
pytest -q

# Frontend
cd frontend
npm run format:check
npm run lint
npm test
```

### Testing Requirements

- All new features require tests
- Maintain minimum 80% code coverage
- Integration tests for API endpoints
- Frontend component tests

## 📋 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Judge0](https://judge0.com/) for code execution infrastructure
- [Django REST Framework](https://www.django-rest-framework.org/) for API development
- [React](https://reactjs.org/) for frontend framework
- [Docker](https://www.docker.com/) for containerization

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ayushisingh19/DDA_Contest/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ayushisingh19/DDA_Contest/discussions)
- **Wiki**: [Project Wiki](https://github.com/ayushisingh19/DDA_Contest/wiki)

---

**Built with ❤️ for coding education and competitive programming**