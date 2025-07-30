# 🛠️ Makefile Guide - Cognify Python SDK

## 📋 **Overview**

This Makefile provides a comprehensive build system for the Cognify Python SDK with professional-grade automation for development, testing, building, and publishing.

## 🚀 **Quick Start**

```bash
# Show all available commands
make help

# Setup development environment
make dev-setup

# Run all quality checks
make check-all

# Build and publish to TestPyPI
make publish-test

# Build and publish to PyPI
make publish
```

---

## 📚 **Available Commands**

### **🔧 Development Setup**

| Command | Description |
|---------|-------------|
| `make install` | Install package in current environment |
| `make install-dev` | Install with development dependencies |
| `make dev-setup` | Complete development setup (install-dev + pre-commit) |
| `make update-deps` | Update all dependencies |

### **🧹 Cleaning**

| Command | Description |
|---------|-------------|
| `make clean` | Clean build artifacts (dist/, build/, __pycache__) |
| `make clean-all` | Deep clean including virtual environments |

### **🏗️ Building**

| Command | Description |
|---------|-------------|
| `make build` | Build package for distribution |
| `make check-build` | Build and validate package with twine |

### **🧪 Testing**

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-unit` | Run unit tests only |
| `make test-integration` | Run integration tests only |
| `make test-coverage` | Run tests with coverage report |
| `make test-api` | Quick test with real API |

### **✨ Code Quality**

| Command | Description |
|---------|-------------|
| `make format` | Format code with black and isort |
| `make format-check` | Check formatting without changes |
| `make lint` | Run linting (flake8, pylint) |
| `make type-check` | Run type checking with mypy |
| `make security-check` | Run security checks (bandit, safety) |
| `make check-all` | Run all quality checks |

### **📖 Documentation**

| Command | Description |
|---------|-------------|
| `make docs` | Build documentation |
| `make docs-serve` | Build and serve docs locally |

### **🚀 Publishing**

| Command | Description |
|---------|-------------|
| `make publish-test` | Publish to TestPyPI |
| `make publish` | Publish to PyPI (production) |
| `make release` | Create git tag and release |

### **🔧 Utilities**

| Command | Description |
|---------|-------------|
| `make pre-commit` | Setup pre-commit hooks |
| `make version` | Show current version |
| `make info` | Show package information |

---

## 🔄 **Common Workflows**

### **🆕 New Developer Setup**
```bash
# Clone repository
git clone <repository-url>
cd cognify-py-sdk

# Setup development environment
make dev-setup

# Verify everything works
make check-all
```

### **💻 Daily Development**
```bash
# Before starting work
make clean
make install-dev

# During development
make format          # Format code
make test           # Run tests
make lint           # Check code quality

# Before committing
make check-all      # Run all checks
```

### **🚀 Release Process**
```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md

# 3. Test release
make clean
make check-all
make publish-test

# 4. Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cognify-sdk

# 5. Production release
make publish

# 6. Create git release
make release
```

### **🔍 Quality Assurance**
```bash
# Full quality check pipeline
make clean
make install-dev
make format-check
make lint
make type-check
make security-check
make test-coverage
make build
```

---

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# Optional: Set custom Python interpreter
export PYTHON=python3.11

# Optional: Set custom pip
export PIP=pip3.11
```

### **Customization**
Edit the Makefile variables at the top:
```makefile
PYTHON := python3
PIP := pip3
PACKAGE_NAME := cognify-sdk
SOURCE_DIR := cognify_sdk
TESTS_DIR := tests
```

---

## 🔐 **Publishing Setup**

### **Prerequisites**
1. **PyPI Account**: Register at https://pypi.org/account/register/
2. **TestPyPI Account**: Register at https://test.pypi.org/account/register/
3. **API Tokens**: 
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

### **Credentials**
When publishing, use:
- **Username**: `__token__`
- **Password**: `[your-api-token]`

### **Optional: ~/.pypirc**
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = [your-pypi-api-token]

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = [your-testpypi-api-token]
```

---

## 🛡️ **Quality Standards**

### **Code Quality Checks**
- **Formatting**: Black (88 char line length)
- **Import Sorting**: isort (black profile)
- **Linting**: flake8 + pylint
- **Type Checking**: mypy (strict mode)
- **Security**: bandit + safety

### **Testing Standards**
- **Coverage**: Minimum 90% (target: 95%+)
- **Test Types**: Unit, integration, API tests
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`

### **Pre-commit Hooks**
Automatically run on every commit:
- Trailing whitespace removal
- End-of-file fixing
- YAML/TOML/JSON validation
- Code formatting (black, isort)
- Linting (flake8)
- Type checking (mypy)
- Security checks (bandit)

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Build Fails**
```bash
# Clean and retry
make clean-all
make install-dev
make build
```

#### **Tests Fail**
```bash
# Check test environment
make clean
make install-dev
make test-unit  # Run unit tests first
```

#### **Publishing Fails**
```bash
# Verify package first
make check-build

# Check credentials
cat ~/.pypirc

# Try TestPyPI first
make publish-test
```

#### **Pre-commit Issues**
```bash
# Reinstall hooks
make pre-commit

# Manual run
pre-commit run --all-files
```

---

## 📞 **Support**

For issues with the Makefile or build system:
1. Check this guide first
2. Run `make help` for available commands
3. Check individual tool documentation
4. Review error messages carefully

**Happy building! 🚀**
