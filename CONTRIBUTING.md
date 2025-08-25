# Contributing to Building Energy Optimizer

Thank you for your interest in contributing to Building Energy Optimizer! This document provides guidelines and instructions for contributing to the project.

## 🚀 Quick Start for Contributors

### 1. Fork and Clone
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/your-username/building-energy-optimizer.git
cd building-energy-optimizer

# Add upstream remote
git remote add upstream https://github.com/original-username/building-energy-optimizer.git
```

### 2. Development Setup
```bash
# Setup development environment
make setup
make install-dev

# Install pre-commit hooks
pre-commit install

# Verify setup
make health
make quick-test
```

### 3. Create Feature Branch
```bash
# Create and switch to feature branch
git checkout -b feature/your-amazing-feature

# Or for bug fixes
git checkout -b fix/issue-123-description
```

## 📋 Types of Contributions

We welcome various types of contributions:

### 🐛 Bug Reports
- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include minimal reproduction steps
- Provide system information and logs
- Test with the latest version first

### ✨ Feature Requests
- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Explain the use case and business value
- Consider implementation complexity
- Discuss with maintainers before large features

### 🔧 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test improvements

### 📚 Documentation
- API documentation
- User guides
- Examples and tutorials
- Code comments
- README improvements

### 🧪 Testing
- Unit tests
- Integration tests
- Performance tests
- End-to-end tests

## 🛠 Development Workflow

### 1. Development Environment
```bash
# Check Python version (3.8+ required)
python --version

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
make setup
```

### 2. Code Standards

#### Python Code Style
- **Formatter**: Black with 100 character line length
- **Import Sorting**: isort with Black profile
- **Linting**: flake8 with project-specific configuration
- **Type Hints**: mypy for static type checking

```bash
# Format code
make format

# Check code quality
make lint

# Fix common issues
make lint-fix
```

#### Code Quality Standards
- **Test Coverage**: Maintain >85% test coverage
- **Documentation**: All public functions must have docstrings
- **Type Hints**: Use type hints for all function signatures
- **Error Handling**: Proper exception handling with meaningful messages
- **Logging**: Use structured logging with appropriate levels

### 3. Testing Requirements

All contributions must include appropriate tests:

#### Test Categories
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **API Tests**: Test REST API endpoints
- **Performance Tests**: Ensure performance requirements

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test categories
make test-core      # Core optimizer tests
make test-api       # API tests
make test-plugins   # Plugin tests

# Run performance benchmarks
make benchmark
```

#### Test Guidelines
- Tests should be fast (<1s per test typically)
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Mock external dependencies
- Test edge cases and error conditions

### 4. Documentation Requirements

#### Code Documentation
```python
def optimize_energy_consumption(data: pd.DataFrame, algorithm: str = "xgboost") -> Dict[str, Any]:
    """
    Optimize building energy consumption using machine learning.
    
    Args:
        data: DataFrame with energy consumption data including timestamps,
              consumption values, and environmental factors
        algorithm: ML algorithm to use ('xgboost', 'lightgbm', 'random_forest')
    
    Returns:
        Dictionary containing optimization results with keys:
        - 'predictions': Array of predicted consumption values
        - 'suggestions': List of optimization suggestions
        - 'report': Comprehensive analysis report
        - 'training_metrics': Model performance metrics
    
    Raises:
        ValueError: If data is invalid or algorithm not supported
        RuntimeError: If optimization fails
    
    Example:
        >>> data = create_enhanced_example_data('2024-01-01', '2024-01-07')
        >>> result = optimize_energy_consumption(data, 'xgboost')
        >>> print(f"Potential savings: {result['report']['summary']['potential_savings_percent']:.1f}%")
    """
```

#### API Documentation
- All endpoints must have proper OpenAPI documentation
- Include request/response examples
- Document error responses
- Provide code examples in multiple languages

### 5. Commit Standards

#### Commit Message Format
Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Build process or auxiliary tool changes

#### Examples
```bash
feat(optimizer): add LightGBM algorithm support

Add LightGBM as an alternative to XGBoost for energy optimization.
Includes parameter tuning and performance comparisons.

Closes #123

fix(api): handle missing weather data gracefully

When weather API is unavailable, fall back to synthetic weather data
instead of failing the optimization request.

Fixes #456

docs(readme): update installation instructions

Add Docker installation option and troubleshooting section.
```

## 🔍 Pull Request Process

### 1. Pre-submission Checklist
- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated for user-facing changes
- [ ] No merge conflicts with main branch
- [ ] Pre-commit hooks pass

### 2. Pull Request Template
Use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) and provide:

- **Description**: Clear description of changes
- **Motivation**: Why this change is needed
- **Testing**: How the changes were tested
- **Screenshots**: For UI changes
- **Breaking Changes**: Any breaking changes
- **Checklist**: Completed pre-submission checklist

### 3. Review Process
1. **Automated Checks**: CI/CD pipeline must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Changes tested in multiple environments
4. **Documentation**: Documentation review if applicable
5. **Security**: Security review for sensitive changes

### 4. Merge Requirements
- All CI checks pass
- At least one approved review from maintainer
- No conflicts with target branch
- All review comments addressed

## 🧩 Plugin Development

Building Energy Optimizer supports custom plugins. See our [Plugin Development Guide](docs/plugin-development.md) for details.

### Plugin Structure
```python
from building_energy_optimizer.plugins.base import AnalyticsPlugin

class MyCustomPlugin(AnalyticsPlugin):
    @property
    def name(self) -> str:
        return "My Custom Plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: dict) -> bool:
        # Plugin initialization
        return True
    
    def analyze(self, data: dict) -> dict:
        # Plugin functionality
        return {"result": "analysis complete"}
```

### Plugin Guidelines
- Follow the base plugin interface
- Include comprehensive tests
- Provide clear documentation
- Handle errors gracefully
- Follow semantic versioning

## 🔒 Security Guidelines

### Reporting Security Issues
- **DO NOT** open public issues for security vulnerabilities
- Email security@energy-optimizer.com with details
- Include steps to reproduce the issue
- Allow time for investigation before public disclosure

### Security Best Practices
- Never commit API keys, passwords, or sensitive data
- Use environment variables for configuration
- Follow OWASP security guidelines
- Regular dependency updates
- Input validation and sanitization

## 📝 Documentation Guidelines

### Documentation Types
- **API Documentation**: OpenAPI/Swagger specifications
- **User Documentation**: How-to guides and tutorials  
- **Developer Documentation**: Architecture and implementation details
- **Examples**: Working code examples

### Writing Style
- **Clear and Concise**: Use simple, direct language
- **Code Examples**: Include working code examples
- **Screenshots**: Visual aids for UI features
- **Cross-references**: Link related documentation
- **Up-to-date**: Keep documentation current with code

### Documentation Tools
- **Sphinx**: For comprehensive documentation
- **Docstrings**: Google-style docstrings
- **Markdown**: For GitHub documentation
- **OpenAPI**: For API documentation

## 🚀 Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps
1. **Update Version**: Update version in `src/building_energy_optimizer/__init__.py`
2. **Update Changelog**: Add release notes to CHANGELOG.md
3. **Create Tag**: `git tag -a v2.1.0 -m "Release v2.1.0"`
4. **Push Tag**: `git push origin v2.1.0`
5. **GitHub Release**: Create release on GitHub
6. **PyPI Release**: Automated via GitHub Actions

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/                 # Unit tests
│   ├── test_optimizer.py
│   ├── test_database.py
│   └── test_plugins.py
├── integration/          # Integration tests
│   ├── test_api_integration.py
│   └── test_database_integration.py
├── performance/          # Performance tests
│   └── test_performance.py
└── fixtures/             # Test data and fixtures
    ├── sample_data.csv
    └── test_config.json
```

### Writing Tests
```python
import pytest
from building_energy_optimizer import BuildingEnergyOptimizer

class TestEnergyOptimizer:
    """Test suite for energy optimizer."""
    
    @pytest.fixture
    def sample_data(self):
        """Provide sample data for tests."""
        from building_energy_optimizer import create_enhanced_example_data
        return create_enhanced_example_data('2024-01-01', '2024-01-03')
    
    @pytest.fixture
    def optimizer(self):
        """Provide configured optimizer."""
        return BuildingEnergyOptimizer(algorithm='random_forest')
    
    def test_basic_optimization(self, optimizer, sample_data):
        """Test basic optimization functionality."""
        # Test preprocessing
        X, y = optimizer.preprocess_data(sample_data)
        assert len(X) == len(sample_data)
        assert len(y) == len(sample_data)
        
        # Test training
        metrics = optimizer.train(X, y)
        assert metrics['val_r2'] > 0.5  # Minimum acceptable accuracy
        
        # Test prediction
        predictions, suggestions = optimizer.predict(X[:24])  # First day
        assert len(predictions) == 24
        assert len(suggestions) > 0
    
    def test_error_handling(self, optimizer):
        """Test error handling with invalid data."""
        import pandas as pd
        
        # Empty DataFrame should raise ValueError
        with pytest.raises(ValueError):
            optimizer.preprocess_data(pd.DataFrame())
        
        # Invalid algorithm should raise ValueError
        with pytest.raises(ValueError):
            BuildingEnergyOptimizer(algorithm='invalid_algorithm')
```

### Test Data Management
- Use fixtures for test data
- Create realistic but synthetic test data
- Keep test data small for fast tests
- Use factories for generating test objects

## 📊 Performance Guidelines

### Performance Requirements
- **Training Time**: <2 minutes for typical datasets (1000-10000 points)
- **Prediction Time**: <100ms for single predictions
- **Memory Usage**: <1GB for typical operations
- **API Response Time**: <5s for optimization endpoints

### Performance Testing
```python
import time
import pytest

def test_optimization_performance():
    """Test optimization performance requirements."""
    from building_energy_optimizer import quick_optimize, create_enhanced_example_data
    
    # Generate test data
    data = create_enhanced_example_data('2024-01-01', '2024-01-31')  # 1 month
    
    # Measure optimization time
    start_time = time.time()
    result = quick_optimize(data, algorithm='xgboost')
    duration = time.time() - start_time
    
    # Assert performance requirements
    assert duration < 120  # Less than 2 minutes
    assert result['training_metrics']['val_r2'] > 0.7  # Minimum accuracy
```

## 🐛 Debugging Guidelines

### Debugging Tools
- **IDE Debugger**: Use your IDE's debugging capabilities
- **Print Debugging**: Use logging instead of print statements
- **Memory Profiling**: Use memory_profiler for memory issues
- **Performance Profiling**: Use cProfile for performance analysis

### Common Issues
1. **Import Errors**: Check virtual environment activation
2. **Database Errors**: Verify database initialization
3. **API Errors**: Check port availability and configuration
4. **Memory Issues**: Use data sampling for large datasets

### Debugging Example
```python
import logging
from building_energy_optimizer.utils.logging import log_info, log_error

def debug_optimization_issue():
    """Debug optimization performance issues."""
    try:
        log_info("Starting optimization debug session")
        
        # Add detailed logging
        optimizer = BuildingEnergyOptimizer(algorithm='xgboost')
        
        # Enable detailed logging
        logging.getLogger('building_energy_optimizer').setLevel(logging.DEBUG)
        
        # Your debug code here
        
    except Exception as e:
        log_error(f"Debug session failed: {e}")
        raise
```

## 📚 Documentation Standards

### Docstring Format
Use Google-style docstrings:

```python
def process_energy_data(data: pd.DataFrame, building_type: str) -> pd.DataFrame:
    """
    Process energy consumption data for optimization.
    
    This function cleans and preprocesses energy consumption data,
    including feature engineering and validation.
    
    Args:
        data: Raw energy consumption data with timestamps
        building_type: Type of building ('residential', 'commercial', 'industrial')
    
    Returns:
        Processed DataFrame ready for ML algorithms
    
    Raises:
        ValueError: If data is invalid or building_type not supported
        DataProcessingError: If preprocessing fails
    
    Example:
        >>> data = pd.read_csv('energy_data.csv')
        >>> processed = process_energy_data(data, 'commercial')
        >>> print(f"Processed {len(processed)} records")
    
    Note:
        This function modifies the input DataFrame. Make a copy if you need
        to preserve the original data.
    """
```

### API Documentation
All API endpoints must include:
- Clear description
- Request/response schemas
- Example requests/responses
- Error codes and messages
- Authentication requirements

## 🔄 Review Process

### Maintainer Review
- **Code Quality**: Adherence to coding standards
- **Functionality**: Feature works as intended
- **Testing**: Adequate test coverage
- **Documentation**: Proper documentation
- **Performance**: Meets performance requirements
- **Security**: No security vulnerabilities

### Automated Checks
- **CI Pipeline**: All GitHub Actions checks must pass
- **Code Coverage**: Test coverage must not decrease
- **Security Scan**: No critical security issues
- **Performance**: Performance benchmarks must pass

### Review Feedback
- Address all review comments
- Ask questions if feedback is unclear
- Make additional commits to address issues
- Request re-review after changes

## 🏷️ Labeling System

We use labels to categorize issues and pull requests:

### Priority Labels
- **🔥 priority/critical**: Critical issues requiring immediate attention
- **🚨 priority/high**: High priority issues
- **📋 priority/medium**: Medium priority issues
- **📝 priority/low**: Low priority issues

### Type Labels
- **🐛 type/bug**: Bug reports and fixes
- **✨ type/enhancement**: New features and improvements
- **📚 type/documentation**: Documentation changes
- **🧪 type/testing**: Testing improvements
- **🔧 type/maintenance**: Maintenance and refactoring

### Status Labels
- **👀 status/needs-review**: Waiting for review
- **🔄 status/in-progress**: Work in progress
- **⏸️ status/blocked**: Blocked by other issues
- **✅ status/ready**: Ready for merge

### Component Labels
- **🤖 component/ml**: Machine learning components
- **📡 component/api**: API server
- **📊 component/dashboard**: Dashboard interface
- **🔌 component/iot**: IoT integration
- **🗄️ component/database**: Database operations

## 🎯 Contribution Ideas

### Good First Issues
Perfect for new contributors:
- Documentation improvements
- Test coverage improvements
- Minor bug fixes
- Example code additions
- Error message improvements

### Medium Complexity
- New plugin development
- Performance optimizations
- Additional ML algorithms
- API endpoint additions
- Dashboard feature enhancements

### Advanced Contributions
- Architecture improvements
- New IoT protocol support
- Advanced analytics features
- Cloud deployment options
- Security enhancements

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: Real-time chat at [discord.gg/energy-optimizer](https://discord.gg/energy-optimizer)
- **Email**: maintainers@energy-optimizer.com

### Before Asking for Help
1. Check existing issues and documentation
2. Search GitHub discussions
3. Try the troubleshooting guide
4. Provide detailed information about your setup

### When Asking for Help
Include:
- Operating system and Python version
- Installation method and dependencies
- Complete error messages and stack traces
- Steps to reproduce the issue
- Expected vs actual behavior

## 🎉 Recognition

### Contributors
All contributors are recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

### Types of Recognition
- **Code Contributors**: Direct code contributions
- **Documentation Contributors**: Documentation improvements
- **Bug Reporters**: Quality bug reports
- **Community Contributors**: Helping others, discussions

## 📋 Code of Conduct

### Our Standards
- **Respectful**: Treat everyone with respect
- **Inclusive**: Welcome people of all backgrounds
- **Collaborative**: Work together constructively
- **Professional**: Maintain professional communication
- **Helpful**: Help others learn and contribute

### Unacceptable Behavior
- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing private information
- Spamming or off-topic discussions

### Enforcement
Violations of the code of conduct may result in:
1. Warning from maintainers
2. Temporary ban from project
3. Permanent ban from project

Report violations to: conduct@energy-optimizer.com

## 📈 Project Roadmap

See our [Project Roadmap](docs/roadmap.md) for planned features and improvements.

### Current Focus Areas
- **🧠 Deep Learning**: TensorFlow/PyTorch integration
- **🌍 Internationalization**: Multi-language support
- **📱 Mobile Support**: Mobile app development
- **☁️ Cloud Platform**: Managed service platform

### How to Contribute to Roadmap Items
1. Check the roadmap for planned features
2. Comment on roadmap issues to express interest
3. Propose implementation approaches
4. Submit pull requests for approved features

## 🔧 Advanced Development

### Custom Algorithm Development
To add a new ML algorithm:

1. **Create Algorithm Class**:
```python
from building_energy_optimizer.algorithms.base import BaseAlgorithm

class MyCustomAlgorithm(BaseAlgorithm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = None
    
    def train(self, X, y):
        # Implement training
        pass
    
    def predict(self, X):
        # Implement prediction
        pass
```

2. **Register Algorithm**:
```python
# In optimizer.py
AVAILABLE_ALGORITHMS['my_custom'] = MyCustomAlgorithm
```

3. **Add Tests**:
```python
def test_my_custom_algorithm():
    optimizer = BuildingEnergyOptimizer(algorithm='my_custom')
    # Test implementation
```

### Database Schema Changes
For database schema changes:

1. **Create Migration**:
```bash
alembic revision -m "Add new feature table"
```

2. **Implement Migration**:
```python
def upgrade():
    op.create_table(
        'new_feature',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False)
    )

def downgrade():
    op.drop_table('new_feature')
```

3. **Test Migration**:
```bash
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

## 🎖️ Maintainer Guidelines

### For Project Maintainers

#### Release Management
1. **Version Planning**: Plan releases with community input
2. **Quality Assurance**: Ensure thorough testing
3. **Documentation**: Maintain comprehensive documentation
4. **Communication**: Regular updates to community

#### Review Standards
- **Code Quality**: Maintain high standards
- **Backward Compatibility**: Preserve compatibility when possible
- **Performance**: Monitor performance impact
- **Security**: Review security implications

#### Community Management
- **Responsive**: Respond to issues and PRs promptly
- **Helpful**: Provide constructive feedback
- **Inclusive**: Welcome new contributors
- **Transparent**: Communicate decisions clearly

## 🙏 Acknowledgments

Thank you to all contributors who have helped make Building Energy Optimizer better:

- **Core Team**: Development and maintenance
- **Contributors**: Feature development and bug fixes
- **Community**: Bug reports, suggestions, and feedback
- **Beta Testers**: Early testing and validation

## 📄 License

By contributing to Building Energy Optimizer, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

**Happy Contributing! 🎉**

For questions about contributing, reach out to us at: contribute@energy-optimizer.com
