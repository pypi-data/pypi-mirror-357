# Contributing to Flask-BunnyStream

Thank you for your interest in contributing to Flask-BunnyStream! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. Please be respectful and professional in all interactions.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When creating a bug report, please include:

- A clear and descriptive title
- Steps to reproduce the behavior
- Expected vs actual behavior
- Environment details (OS, Python version, Flask version, etc.)
- Code samples and error logs if applicable

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml) when creating bug reports.

### Suggesting Features

Feature suggestions are welcome! Please use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.yml) and include:

- Clear description of the feature
- Use case and motivation
- Implementation ideas (if any)
- Examples of how it would be used

### Asking Questions

If you have questions about usage, please:

1. Check the [documentation](README.md) and [examples](examples/)
2. Search existing [issues](../../issues) and [discussions](../../discussions)
3. Create a new issue using the [Question template](.github/ISSUE_TEMPLATE/question.yml)

## Development Setup

### Prerequisites

- Python 3.8+ (we test on 3.8, 3.9, 3.10, 3.11, 3.12)
- RabbitMQ server (for integration testing)
- Git

### Setting Up Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/flask-bunnystream.git
   cd flask-bunnystream
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks (optional but recommended):**
   ```bash
   pre-commit install
   ```

5. **Start RabbitMQ for testing:**
   ```bash
   # Using Docker (recommended)
   docker run -d --name rabbitmq-dev \
     -p 5672:5672 -p 15672:15672 \
     rabbitmq:3.12-management
   
   # Or install locally following RabbitMQ documentation
   ```

### Project Structure

```
flask-bunnystream/
├── src/flask_bunnystream/     # Main package code
│   ├── __init__.py
│   ├── extension.py           # Flask extension
│   └── decorators.py          # Event handler decorators
├── tests/                     # Test suite
├── examples/                  # Usage examples
├── docs/                      # Additional documentation
├── .github/                   # GitHub templates and workflows
└── pyproject.toml            # Project configuration
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=flask_bunnystream

# Run specific test file
pytest tests/test_extension.py -v

# Run tests for specific Python version (if using tox)
tox -e py311
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names that explain what is being tested
- Follow the existing test patterns and structure
- Ensure tests are isolated and don't depend on external state
- Mock external dependencies when appropriate

Example test structure:
```python
class TestNewFeature:
    """Test suite for new feature."""
    
    def test_feature_basic_functionality(self):
        """Test that the feature works in basic scenarios."""
        # Arrange
        # Act
        # Assert
        
    def test_feature_error_handling(self):
        """Test that the feature handles errors gracefully."""
        # Test error conditions
```

### Integration Testing

For features that interact with RabbitMQ:
- Ensure RabbitMQ is running before tests
- Clean up queues and connections after tests
- Use unique queue/exchange names to avoid conflicts

## Code Style

We maintain high code quality standards:

### Formatting and Linting

- **Black** for code formatting
- **Pylint** for linting
- **MyPy** for type checking
- **Ruff** for additional linting

```bash
# Format code
black src/ tests/ examples/

# Check formatting
black --check src/ tests/ examples/

# Lint code
pylint src/flask_bunnystream/

# Type check
mypy src/flask_bunnystream/

# Additional linting
ruff check src/ tests/ examples/
```

### Code Guidelines

1. **Follow PEP 8** style guide
2. **Use type hints** for all function signatures
3. **Write docstrings** for all public functions and classes
4. **Keep functions focused** and single-purpose
5. **Use descriptive variable names**
6. **Comment complex logic**
7. **Handle errors gracefully**

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """Brief description of what the function does.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.
        
    Returns:
        Description of the return value.
        
    Raises:
        ValueError: When param1 is empty.
        RuntimeError: When operation fails.
        
    Example:
        >>> result = example_function("test", 5)
        >>> print(result)
        True
    """
```

## Documentation

### Updating Documentation

When making changes that affect users:

1. **Update README.md** if the change affects basic usage
2. **Update relevant documentation** in `docs/` directory
3. **Update examples** if the change affects example code
4. **Update docstrings** for any modified functions/classes

### Documentation Standards

- Use clear, concise language
- Provide code examples for complex features
- Include both basic and advanced usage patterns
- Keep examples up-to-date with current API
- Use proper Markdown formatting

## Submitting Changes

### Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-description
   ```

2. **Make your changes:**
   - Write code following the style guidelines
   - Add or update tests
   - Update documentation if needed

3. **Test your changes:**
   ```bash
   pytest
   black --check src/ tests/ examples/
   pylint src/flask_bunnystream/
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   # or
   git commit -m "fix: resolve issue with specific component"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request:**
   - Use the PR template
   - Provide clear description of changes
   - Link related issues
   - Ensure CI passes

### Commit Message Guidelines

Use conventional commits format:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `style:` for formatting changes
- `chore:` for maintenance tasks

Examples:
```
feat: add event handler retry mechanism
fix: resolve memory leak in extension cleanup
docs: update installation instructions
test: add integration tests for decorators
```

### Pull Request Guidelines

- **Fill out the PR template** completely
- **Link related issues** using "Fixes #123" or "Closes #123"
- **Ensure all CI checks pass**
- **Request review** from maintainers
- **Be responsive** to feedback and questions
- **Keep PRs focused** on a single feature or fix

## Release Process

For maintainers, the release process involves:

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create and push a tag:**
   ```bash
   git tag -a v1.2.3 -m "Release version 1.2.3"
   git push origin v1.2.3
   ```
4. **GitHub Actions** will automatically:
   - Run all tests
   - Build the package
   - Publish to PyPI
   - Create a GitHub release

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

## Getting Help

If you need help with contributing:

- Check existing [documentation](README.md) and [examples](examples/)
- Search [existing issues](../../issues)
- Ask questions in [discussions](../../discussions)
- Reach out to maintainers in issues or PRs

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Special recognition for major features or improvements

Thank you for contributing to Flask-BunnyStream! 🎉
