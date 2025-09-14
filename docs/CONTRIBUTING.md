# Contributing to DDA Contest Platform

Thank you for your interest in contributing to the DDA Contest Platform! This guide will help you understand our development process and how to contribute effectively.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Commit Guidelines](#commit-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Issue Reporting](#issue-reporting)
8. [Testing Requirements](#testing-requirements)
9. [Documentation](#documentation)
10. [Community and Communication](#community-and-communication)

## Code of Conduct

### Our Commitment

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, experience level, gender identity, sexual orientation, disability, personal appearance, race, ethnicity, age, religion, or nationality.

### Expected Behavior

- **Be Respectful**: Treat all community members with respect and kindness
- **Be Inclusive**: Welcome newcomers and help them get started
- **Be Collaborative**: Work together constructively and share knowledge
- **Be Professional**: Maintain professionalism in all interactions
- **Be Constructive**: Provide helpful feedback and focus on solutions

### Unacceptable Behavior

- Harassment, discrimination, or intimidation of any kind
- Offensive, derogatory, or inappropriate comments
- Personal attacks or insults
- Publishing private information without consent
- Spam or self-promotion unrelated to the project

### Enforcement

Community leaders are responsible for clarifying and enforcing standards. They may take appropriate action, including warning, temporary ban, or permanent ban for violations.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Git** installed and configured
- **Docker & Docker Compose** for development environment
- **Python 3.11+** for backend development
- **Node.js 18+** for frontend development
- **Basic knowledge** of Django, React, and TypeScript

### Setting Up Development Environment

1. **Fork the repository:**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/ddt-coding.git
   cd ddt-coding
   ```

2. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/ddt-coding.git
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

4. **Start development environment:**
   ```bash
   docker compose -f infra/compose/dev/docker-compose.yml up --build
   ```

5. **Verify setup:**
   - Backend: http://localhost/api/health/
   - Frontend: http://localhost:3000
   - Admin: http://localhost/admin/

### First-Time Contributors

If you're new to the project, look for issues labeled:
- `good first issue` - Simple tasks for beginners
- `help wanted` - Issues where help is needed
- `documentation` - Documentation improvements

## Development Workflow

### Branch Strategy

We use **GitFlow** with the following branches:

- **`main`** - Production-ready code
- **`develop`** - Integration branch for features
- **`feature/*`** - New features and enhancements
- **`bugfix/*`** - Bug fixes
- **`hotfix/*`** - Critical production fixes
- **`release/*`** - Release preparation

### Workflow Steps

1. **Sync with upstream:**
   ```bash
   git checkout develop
   git pull upstream develop
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Keep branch updated:**
   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

### Feature Development Process

**1. Planning Phase:**
- Review existing issues or create new one
- Discuss approach in issue comments
- Break down large features into smaller tasks
- Get approval from maintainers for significant changes

**2. Implementation Phase:**
- Follow coding standards and best practices
- Write tests for new functionality
- Update documentation as needed
- Ensure backward compatibility when possible

**3. Review Phase:**
- Create pull request with detailed description
- Address review feedback promptly
- Ensure all checks pass
- Update branch if needed

## Coding Standards

### Backend (Python/Django)

**Code Style:**
```python
# Use type hints
def calculate_score(submission: Submission) -> int:
    """Calculate score for a submission."""
    return submission.points if submission.is_correct else 0

# Follow Django conventions
class ProblemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing problems."""
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticated]

# Use descriptive variable names
user_submissions = Submission.objects.filter(user=request.user)
successful_submissions = user_submissions.filter(status='accepted')
```

**Code Quality Tools:**
```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/

# Sort imports
isort src/
```

**Best Practices:**
- Use type hints for all function parameters and return values
- Write docstrings for all classes and public methods
- Keep functions focused and under 20 lines when possible
- Use Django's built-in features (ORM, forms, etc.)
- Handle exceptions appropriately
- Use logging instead of print statements

### Frontend (TypeScript/React)

**Code Style:**
```typescript
// Use proper TypeScript interfaces
interface ProblemProps {
  id: number;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  onSelect: (problem: Problem) => void;
}

// Use functional components with hooks
export const ProblemCard: React.FC<ProblemProps> = ({ 
  id, 
  title, 
  difficulty, 
  onSelect 
}) => {
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleClick = useCallback(() => {
    onSelect({ id, title, difficulty });
  }, [id, title, difficulty, onSelect]);

  return (
    <div className="problem-card" onClick={handleClick}>
      <h3>{title}</h3>
      <span className={`difficulty-${difficulty.toLowerCase()}`}>
        {difficulty}
      </span>
    </div>
  );
};
```

**Code Quality Tools:**
```bash
# Format code
npm run format

# Lint code
npm run lint

# Type checking
npm run type-check

# Fix auto-fixable issues
npm run lint:fix
```

**Best Practices:**
- Use TypeScript strict mode
- Implement proper error boundaries
- Use meaningful component and prop names
- Keep components small and focused
- Use hooks appropriately
- Implement proper loading and error states
- Use Tailwind CSS for styling

## Commit Guidelines

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add JWT token authentication` |
| `fix` | Bug fix | `fix(api): handle null values in response` |
| `docs` | Documentation | `docs(readme): update installation guide` |
| `style` | Code style changes | `style(frontend): fix linting issues` |
| `refactor` | Code refactoring | `refactor(models): simplify problem model` |
| `test` | Adding tests | `test(auth): add login endpoint tests` |
| `chore` | Maintenance | `chore(deps): update dependencies` |
| `perf` | Performance improvements | `perf(api): optimize query performance` |
| `ci` | CI/CD changes | `ci(github): add automated testing` |

### Scope Examples

- `auth` - Authentication related
- `api` - API endpoints
- `frontend` - Frontend components
- `backend` - Backend logic
- `models` - Database models
- `tests` - Test files
- `docs` - Documentation
- `config` - Configuration files

### Commit Message Examples

**Good Commits:**
```bash
feat(problems): add difficulty filter to problem list
fix(submissions): resolve timeout issue in code evaluation
docs(api): add authentication endpoint documentation
test(auth): add unit tests for login functionality
refactor(frontend): extract reusable button component
```

**Bad Commits:**
```bash
fixed bug          # Too vague
Updated files      # Not descriptive
WIP               # Work in progress (avoid in main)
asdf              # Meaningless
```

### Commit Best Practices

1. **Keep commits atomic** - One logical change per commit
2. **Write descriptive messages** - Explain what and why, not how
3. **Use present tense** - "Add feature" not "Added feature"
4. **Reference issues** - Include issue numbers when relevant
5. **Limit line length** - 72 characters for subject line
6. **Add body for complex changes** - Explain context and reasoning

## Pull Request Process

### Before Creating a PR

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with develop

### PR Title and Description

**Title Format:**
```
<type>(<scope>): <description>
```

**Description Template:**
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Related Issues
Closes #123
Fixes #456
```

### Review Process

1. **Automated Checks:**
   - CI/CD pipeline must pass
   - Code coverage requirements met
   - Security scans pass
   - Style guidelines enforced

2. **Code Review:**
   - At least one maintainer approval required
   - Address all review comments
   - Resolve conversations before merge

3. **Final Steps:**
   - Squash commits if requested
   - Update branch if conflicts arise
   - Maintainer will merge when ready

### Review Guidelines

**For Reviewers:**
- Be constructive and respectful
- Explain the reasoning behind suggestions
- Approve changes that improve the codebase
- Focus on logic, security, and maintainability
- Check for test coverage and documentation

**For Authors:**
- Respond to feedback promptly
- Ask questions if feedback is unclear
- Make requested changes or explain why not
- Be open to suggestions and learning
- Update PR description if scope changes

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Browser [e.g. chrome, safari]
- Version [e.g. 1.0.0]

**Additional Context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

### Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Improvements or additions to docs |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention is needed |
| `question` | Further information is requested |
| `wontfix` | This will not be worked on |
| `duplicate` | This issue or pull request already exists |
| `priority:high` | High priority issue |
| `priority:low` | Low priority issue |

## Testing Requirements

### Backend Testing

**Required Tests:**
- Unit tests for models, views, and utilities
- Integration tests for API endpoints
- Authentication and permission tests
- Database migration tests

**Test Structure:**
```python
# tests/unit/test_models.py
class TestProblemModel(TestCase):
    def setUp(self):
        self.problem = Problem.objects.create(
            title="Test Problem",
            difficulty="Easy"
        )
    
    def test_string_representation(self):
        self.assertEqual(str(self.problem), "Test Problem (Easy)")
    
    def test_get_test_cases(self):
        test_case = TestCase.objects.create(
            problem=self.problem,
            input_data="test",
            expected_output="result"
        )
        self.assertIn(test_case, self.problem.get_test_cases())

# tests/integration/test_api.py
class TestProblemAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_problems(self):
        response = self.client.get('/api/problems/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
```

**Running Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/test_models.py::TestProblemModel::test_string_representation
```

### Frontend Testing

**Required Tests:**
- Component unit tests
- Integration tests for user flows
- API service tests
- Utility function tests

**Test Structure:**
```typescript
// src/components/__tests__/ProblemCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProblemCard } from '../ProblemCard';

describe('ProblemCard', () => {
  const mockProblem = {
    id: 1,
    title: 'Test Problem',
    difficulty: 'Easy' as const
  };

  it('renders problem information', () => {
    render(<ProblemCard {...mockProblem} onSelect={jest.fn()} />);
    
    expect(screen.getByText('Test Problem')).toBeInTheDocument();
    expect(screen.getByText('Easy')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', () => {
    const mockOnSelect = jest.fn();
    render(<ProblemCard {...mockProblem} onSelect={mockOnSelect} />);
    
    fireEvent.click(screen.getByText('Test Problem'));
    expect(mockOnSelect).toHaveBeenCalledWith(mockProblem);
  });
});
```

**Running Tests:**
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific tests
npm test -- ProblemCard.test.tsx
```

### Test Coverage Requirements

- **Minimum coverage:** 80% for all new code
- **Critical paths:** 100% coverage required
- **Integration tests:** Required for all API endpoints
- **E2E tests:** Required for major user workflows

## Documentation

### Documentation Types

1. **Code Documentation:**
   - Inline comments for complex logic
   - Docstrings for all public functions and classes
   - README files for each major component

2. **API Documentation:**
   - OpenAPI/Swagger specifications
   - Example requests and responses
   - Error code documentation

3. **User Documentation:**
   - Installation and setup guides
   - User guides and tutorials
   - FAQ and troubleshooting

4. **Developer Documentation:**
   - Architecture overview
   - Development workflow
   - Contributing guidelines

### Documentation Standards

**Python Docstrings:**
```python
def calculate_submission_score(submission: Submission, test_results: list) -> int:
    """
    Calculate the final score for a submission based on test results.
    
    Args:
        submission: The submission object containing problem and user info
        test_results: List of test case results with status and execution time
        
    Returns:
        int: Final score between 0 and 100
        
    Raises:
        ValueError: If test_results is empty or contains invalid data
        
    Example:
        >>> submission = Submission(problem=problem, user=user)
        >>> results = [{'status': 'passed', 'time': 100}]
        >>> score = calculate_submission_score(submission, results)
        >>> print(score)
        100
    """
```

**TypeScript Documentation:**
```typescript
/**
 * Represents a coding problem in the contest platform.
 * 
 * @interface Problem
 * @property {number} id - Unique identifier for the problem
 * @property {string} title - Human-readable problem title
 * @property {string} description - Detailed problem statement
 * @property {'Easy' | 'Medium' | 'Hard'} difficulty - Problem difficulty level
 * @property {number} timeLimit - Execution time limit in seconds
 * @property {number} memoryLimit - Memory limit in MB
 * 
 * @example
 * ```typescript
 * const problem: Problem = {
 *   id: 1,
 *   title: "Two Sum",
 *   description: "Find two numbers that add up to target",
 *   difficulty: "Easy",
 *   timeLimit: 5,
 *   memoryLimit: 128
 * };
 * ```
 */
interface Problem {
  id: number;
  title: string;
  description: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  timeLimit: number;
  memoryLimit: number;
}
```

### Updating Documentation

When making changes:
- Update relevant documentation files
- Add new API endpoints to API reference
- Update development guide for workflow changes
- Include examples and code snippets
- Review documentation for accuracy and clarity

## Community and Communication

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests, questions
- **GitHub Discussions:** General discussions, ideas, help
- **Pull Requests:** Code review and collaboration
- **Email:** Security issues (security@your-domain.com)

### Getting Help

1. **Search existing issues** - Your question might already be answered
2. **Read the documentation** - Check development guide and API reference
3. **Ask in discussions** - For general questions and help
4. **Create an issue** - For specific problems or feature requests

### Contributing Beyond Code

- **Documentation improvements**
- **Bug reports and testing**
- **Feature suggestions and feedback**
- **Code review and mentoring**
- **Community support and help**

### Recognition

We recognize contributors through:
- **Contributors file** in the repository
- **Release notes** mentioning significant contributions
- **GitHub badges** for different types of contributions
- **Maintainer nominations** for consistent contributors

---

## Additional Resources

- [Development Guide](development-guide.md) - Detailed development information
- [API Reference](api-reference.md) - Complete API documentation
- [Architecture Overview](architecture/overview.md) - System design and structure
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines

Thank you for contributing to the DDA Contest Platform! Your contributions help make coding education better for everyone. 🚀