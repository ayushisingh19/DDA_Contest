# Repository Setup & CI/CD Configuration

## Repository Settings Configuration

### 1. Branch Protection Rules

Navigate to **Settings > Branches** and add protection for `main` branch:

```yaml
Branch Protection Rules:
  - Require pull request reviews before merging: ✅
  - Dismiss stale reviews when new commits are pushed: ✅  
  - Require status checks to pass before merging: ✅
    Required checks:
      - backend-ci
      - frontend-ci
      - integration
  - Require branches to be up to date before merging: ✅
  - Restrict pushes that create files larger than 100MB: ✅
  - Do not allow bypassing the above settings: ✅
```

### 2. Required Secrets

Navigate to **Settings > Secrets and variables > Actions**:

#### Repository Secrets:
```env
# Docker Registry (for image builds/pushes)
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-token

# Security Scanning
SNYK_TOKEN=your-snyk-api-token

# Code Coverage (optional)
CODECOV_TOKEN=your-codecov-token

# Deployment (when ready for production)
STAGING_SSH_KEY=ssh-private-key-for-staging
PRODUCTION_SSH_KEY=ssh-private-key-for-production
```

#### Environment Variables (public):
```env
# Build Configuration
NODE_VERSION=20
PYTHON_VERSION=3.12
```

### 3. Webhook Configuration (Optional)

For deployment automation:
- **Settings > Webhooks**
- Add webhook URL for your deployment system
- Events: `push`, `release`

### 4. Repository Topics

Add relevant topics for discoverability:
- `coding-platform`
- `contest-programming` 
- `judge0`
- `django`
- `react`
- `docker`
- `education`

### 5. Security Settings

**Settings > Security > Code security and analysis**:
- ✅ Dependency graph
- ✅ Dependabot alerts  
- ✅ Dependabot security updates
- ✅ Secret scanning
- ✅ Push protection for secrets

## CI/CD Workflow Status

### ✅ Working Workflows:
- **backend-ci.yml**: Tests, linting, security scanning
- **frontend-ci.yml**: Type checking, linting, building
- **integration.yml**: Full-stack testing
- **deploy.yml**: Deployment pipeline (needs secrets)

### 🔧 Setup Requirements:

1. **Snyk Token** (for security scanning):
   ```bash
   # Sign up at https://snyk.io
   # Get API token from Account Settings
   # Add as SNYK_TOKEN secret
   ```

2. **Docker Registry** (for image storage):
   ```bash
   # Create Docker Hub account
   # Generate access token
   # Add DOCKER_USERNAME and DOCKER_PASSWORD secrets
   ```

3. **Codecov Token** (for coverage reports):
   ```bash
   # Link repository at https://codecov.io
   # Get upload token
   # Add as CODECOV_TOKEN secret
   ```

## Local Development Commands

### Quick Start:
```bash
# Start all services
docker compose -f infra/compose/dev/docker-compose.yml up -d

# Check health
curl http://localhost:8000/healthz/
curl http://localhost/

# Run tests
docker exec dev-backend-1 python -m pytest
```

### Development Workflow:
```bash
# Backend changes
docker compose -f infra/compose/dev/docker-compose.yml restart backend

# Frontend changes (auto-reloads)
# Just edit files - Vite handles hot reload

# Database changes
docker exec dev-backend-1 python src/student_auth/manage.py migrate

# Sample data
docker exec dev-backend-1 python src/student_auth/add_sample_data.py
```

## Production Deployment Checklist

### Security:
- [ ] Change all default passwords/keys
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Set up monitoring alerts

### Performance:
- [ ] Configure Redis persistence
- [ ] Set up database backups
- [ ] Configure CDN for static assets
- [ ] Set up load balancing (if needed)

### Monitoring:
- [ ] Application logs (structured JSON)
- [ ] Database performance metrics  
- [ ] Judge0 service health
- [ ] User submission patterns

## Troubleshooting

### Common Issues:

1. **CI failing on secrets**:
   - Check if required secrets are set
   - Verify secret names match workflow files

2. **Docker build failures**:
   - Ensure .dockerignore excludes node_modules
   - Check Dockerfile paths are correct

3. **Tests failing**:
   - Run tests locally first
   - Check database/redis connectivity in CI

### Support Resources:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)