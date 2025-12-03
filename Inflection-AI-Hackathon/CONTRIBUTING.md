# 🤝 Contributing to Agri-Adapt AI

Thank you for your interest in contributing to Agri-Adapt AI! This document provides guidelines and information for contributors.

## 🎯 How Can I Contribute?

### 🐛 Reporting Bugs

- Use the GitHub issue tracker
- Include detailed reproduction steps
- Provide system information and error logs
- Check if the bug has already been reported

### 💡 Suggesting Enhancements

- Describe the feature in detail
- Explain why it would be useful
- Include mockups or examples if possible
- Consider the impact on existing functionality

### 🔧 Code Contributions

- Fix bugs or implement features
- Improve documentation
- Add tests
- Optimize performance
- Enhance security

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Git
- Basic knowledge of FastAPI, React, and machine learning

### Development Setup

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/agri-adapt-ai.git
   cd agri-adapt-ai
   ```
3. **Set up the development environment**

   ```bash
   # Backend setup
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt

   # Frontend setup
   cd frontend
   npm install
   cd ..
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 📝 Development Guidelines

### Code Style

#### Python (Backend)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for function parameters and return values
- Maximum line length: 88 characters (use Black formatter)
- Use descriptive variable and function names
- Add docstrings for all public functions and classes

```python
def calculate_resilience_score(
    rainfall: float,
    soil_ph: float,
    organic_carbon: float
) -> float:
    """
    Calculate maize drought resilience score.

    Args:
        rainfall: Annual rainfall in mm
        soil_ph: Soil pH value (0-14)
        organic_carbon: Organic carbon percentage

    Returns:
        Resilience score (0-100)

    Raises:
        ValueError: If inputs are out of valid range
    """
    if not (0 <= soil_ph <= 14):
        raise ValueError("Soil pH must be between 0 and 14")

    # Implementation here
    return score
```

#### TypeScript/React (Frontend)

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use TypeScript for all new components
- Use functional components with hooks
- Prefer named exports over default exports
- Use meaningful component and prop names

```typescript
interface ResilienceGaugeProps {
  score: number;
  county: string;
  onScoreChange?: (score: number) => void;
}

export const ResilienceGauge: React.FC<ResilienceGaugeProps> = ({
  score,
  county,
  onScoreChange,
}) => {
  // Component implementation
};
```

### Testing Requirements

#### Backend Testing

- Write unit tests for all new functions
- Maintain minimum 80% code coverage
- Use pytest for testing framework
- Mock external dependencies

```python
def test_calculate_resilience_score():
    """Test resilience score calculation."""
    score = calculate_resilience_score(800, 6.5, 2.1)
    assert 0 <= score <= 100
    assert isinstance(score, float)

def test_calculate_resilience_score_invalid_ph():
    """Test resilience score with invalid pH."""
    with pytest.raises(ValueError):
        calculate_resilience_score(800, 15, 2.1)
```

#### Frontend Testing

- Write component tests for new React components
- Test user interactions and state changes
- Use React Testing Library
- Mock API calls

```typescript
import { render, screen, fireEvent } from "@testing-library/react";
import { ResilienceGauge } from "./ResilienceGauge";

describe("ResilienceGauge", () => {
  it("displays the resilience score", () => {
    render(<ResilienceGauge score={75} county="Nakuru" />);
    expect(screen.getByText("75%")).toBeInTheDocument();
  });
});
```

### Documentation Standards

#### Code Documentation

- Add docstrings to all public functions and classes
- Include examples in docstrings
- Document complex algorithms and business logic
- Keep documentation up-to-date with code changes

#### API Documentation

- Update OpenAPI/Swagger documentation for new endpoints
- Include request/response examples
- Document error codes and messages
- Add parameter validation rules

---

## 🔄 Development Workflow

### 1. Planning

- Create or comment on an issue
- Discuss the approach with maintainers
- Break down large features into smaller tasks
- Estimate effort and timeline

### 2. Development

- Work on your feature branch
- Make small, focused commits
- Test your changes thoroughly
- Update documentation as needed

### 3. Testing

- Run all tests locally
- Ensure code coverage is maintained
- Test edge cases and error conditions
- Verify functionality in different environments

### 4. Code Review

- Create a pull request
- Request review from maintainers
- Address feedback and suggestions
- Ensure CI/CD checks pass

### 5. Merge

- Squash commits if requested
- Update documentation
- Close related issues
- Celebrate your contribution! 🎉

---

## 📋 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] No console.log or debug code
- [ ] No sensitive information in code

### Pull Request Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console.log or debug code

## Screenshots (if applicable)

Add screenshots for UI changes

## Additional Notes

Any additional information
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: Maintainers review code for quality and correctness
3. **Testing**: Verify functionality in staging environment
4. **Approval**: At least one maintainer must approve
5. **Merge**: Changes are merged to main branch

---

## 🏗️ Project Structure

### Backend Structure

```
src/
├── api/                    # FastAPI application
│   ├── fastapi_app.py     # Main app and routes
│   ├── data_service.py    # Data processing
│   └── weather_service.py # Weather integration
├── models/                 # ML models
│   └── maize_resilience_model.py
└── utils/                  # Utility functions
```

### Frontend Structure

```
frontend/
├── app/                   # Next.js app directory
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   └── feature/          # Feature-specific components
├── lib/                   # Utility functions
└── public/                # Static assets
```

---

## 🧪 Testing Guidelines

### Running Tests

#### Backend Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_ml_model.py

# Run tests in parallel
python -m pytest -n auto
```

#### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run tests in watch mode
npm test -- --watch

# Run E2E tests
npx playwright test
```

### Writing Good Tests

#### Test Principles

- **Arrange**: Set up test data and conditions
- **Act**: Execute the function being tested
- **Assert**: Verify the expected outcome

#### Test Naming

- Use descriptive test names
- Follow the pattern: `test_[function_name]_[scenario]`
- Include expected behavior in the name

```python
def test_calculate_resilience_score_high_rainfall():
    """Test resilience score with high rainfall conditions."""
    score = calculate_resilience_score(1200, 6.5, 2.1)
    assert score > 80  # High rainfall should result in high resilience

def test_calculate_resilience_score_low_ph():
    """Test resilience score with low soil pH."""
    score = calculate_resilience_score(800, 4.0, 2.1)
    assert score < 50  # Low pH should result in lower resilience
```

---

## 🔧 Development Tools

### Code Quality Tools

#### Backend

- **Black**: Code formatter
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit**: Git hooks

#### Frontend

- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **TypeScript**: Type checking
- **Husky**: Git hooks

### IDE Configuration

#### VS Code

- Install Python and TypeScript extensions
- Configure auto-formatting on save
- Set up debugging configurations
- Enable linting and error checking

#### PyCharm/IntelliJ

- Configure Python interpreter
- Set up code style settings
- Enable type checking
- Configure test runners

---

## 🚨 Common Issues and Solutions

### Backend Issues

#### Import Errors

```bash
# Ensure you're in the correct directory
cd /path/to/agri-adapt-ai

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Database Connection Issues

```bash
# Check if database file exists
ls -la agri_adapt_ai.db

# Remove corrupted database (will be recreated)
rm agri_adapt_ai.db
```

### Frontend Issues

#### Build Failures

```bash
# Clear cache and reinstall
rm -rf .next node_modules
npm install
npm run build
```

#### API Connection Issues

```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify CORS settings
# Check network tab in browser dev tools
```

---

## 📚 Learning Resources

### Backend Development

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Testing](https://docs.pytest.org/)
- [Polars Data Processing](https://pola.rs/)

### Frontend Development

- [Next.js Documentation](https://nextjs.org/docs)
- [React Hooks](https://reactjs.org/docs/hooks-intro.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### Machine Learning

- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Feature Engineering](https://www.feature-engineering-for-ml.com/)
- [Model Validation](https://scikit-learn.org/stable/modules/cross_validation.html)

---

## 🎉 Recognition

### Contributors Hall of Fame

We recognize and appreciate all contributors! Your name will be added to:

- Project README
- Release notes
- Contributor acknowledgments

### Contribution Levels

- **Bronze**: 1-5 contributions
- **Silver**: 6-15 contributions
- **Gold**: 16+ contributions
- **Platinum**: Major feature contributions

---

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and discussions
- **Email**: dev@agri-adapt-ai.com
- **Slack**: #agri-adapt-ai channel

### Mentorship

- New contributors can request mentorship
- Experienced contributors can volunteer as mentors
- Pair programming sessions available
- Code review guidance provided

---

## 📄 License

By contributing to Agri-Adapt AI, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Thank You!

Thank you for contributing to Agri-Adapt AI! Every contribution, no matter how small, helps make this project better and more impactful for farmers in Kenya and beyond.

**Together, we can build a more sustainable and resilient agricultural future! 🌾**

---

**Last Updated**: December 2024  
**Maintainer**: [Your Name]
