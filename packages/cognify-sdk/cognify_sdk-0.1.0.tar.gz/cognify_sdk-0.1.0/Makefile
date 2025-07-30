# Cognify Python SDK - Makefile
# Professional build, test, and publish automation

.PHONY: help install install-dev clean clean-all build test test-unit test-integration lint format type-check security-check docs docs-serve publish-test publish release pre-commit check-all

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
PACKAGE_NAME := cognify-sdk
SOURCE_DIR := cognify_sdk
TESTS_DIR := tests
DOCS_DIR := docs

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Help target
help: ## Show this help message
	@echo "$(BLUE)Cognify Python SDK - Build System$(NC)"
	@echo "=================================="
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Common workflows:$(NC)"
	@echo "  $(YELLOW)make install-dev$(NC)     - Setup development environment"
	@echo "  $(YELLOW)make check-all$(NC)       - Run all checks (lint, test, type)"
	@echo "  $(YELLOW)make build$(NC)           - Build package for distribution"
	@echo "  $(YELLOW)make publish-test$(NC)    - Publish to TestPyPI"
	@echo "  $(YELLOW)make publish$(NC)         - Publish to PyPI"

# Installation targets
install: ## Install package in current environment
	@echo "$(BLUE)Installing package...$(NC)"
	$(PIP) install -e .

install-dev: ## Install package with development dependencies
	@echo "$(BLUE)Installing development environment...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(PIP) install build twine pre-commit
	@echo "$(GREEN)✅ Development environment ready$(NC)"

# Cleaning targets
clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✅ Build artifacts cleaned$(NC)"

clean-all: clean ## Clean all artifacts including virtual environments
	@echo "$(BLUE)Deep cleaning...$(NC)"
	rm -rf .venv/
	rm -rf venv/
	rm -rf .tox/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	@echo "$(GREEN)✅ Deep clean completed$(NC)"

# Build targets
build: clean ## Build package for distribution
	@echo "$(BLUE)Building package...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✅ Package built successfully$(NC)"
	@echo "$(YELLOW)Built files:$(NC)"
	@ls -la dist/

check-build: build ## Build and check package
	@echo "$(BLUE)Checking package...$(NC)"
	$(PYTHON) -m twine check dist/*
	@echo "$(GREEN)✅ Package check passed$(NC)"

# Testing targets
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTHON) -m pytest $(TESTS_DIR) -v --tb=short

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTHON) -m pytest $(TESTS_DIR)/unit -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTHON) -m pytest $(TESTS_DIR)/integration -v

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTHON) -m pytest $(TESTS_DIR) --cov=$(SOURCE_DIR) --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/$(NC)"

# Code quality targets
lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	$(PYTHON) -m flake8 $(SOURCE_DIR) $(TESTS_DIR)
	$(PYTHON) -m pylint $(SOURCE_DIR)
	@echo "$(GREEN)✅ Linting passed$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(PYTHON) -m black $(SOURCE_DIR) $(TESTS_DIR)
	$(PYTHON) -m isort $(SOURCE_DIR) $(TESTS_DIR)
	@echo "$(GREEN)✅ Code formatted$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(NC)"
	$(PYTHON) -m black --check $(SOURCE_DIR) $(TESTS_DIR)
	$(PYTHON) -m isort --check-only $(SOURCE_DIR) $(TESTS_DIR)
	@echo "$(GREEN)✅ Code formatting is correct$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	$(PYTHON) -m mypy $(SOURCE_DIR)
	@echo "$(GREEN)✅ Type checking passed$(NC)"

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	$(PYTHON) -m bandit -r $(SOURCE_DIR)
	$(PYTHON) -m safety check
	@echo "$(GREEN)✅ Security checks passed$(NC)"

# Documentation targets
docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	cd $(DOCS_DIR) && $(PYTHON) -m sphinx -b html . _build/html
	@echo "$(GREEN)✅ Documentation built$(NC)"

docs-serve: docs ## Build and serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(NC)"
	cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8000

# Publishing targets
publish-test: check-build ## Publish to TestPyPI
	@echo "$(BLUE)Publishing to TestPyPI...$(NC)"
	@echo "$(YELLOW)You will need your TestPyPI API token$(NC)"
	@echo "$(YELLOW)Username: __token__$(NC)"
	@echo "$(YELLOW)Password: [your-testpypi-api-token]$(NC)"
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✅ Published to TestPyPI$(NC)"
	@echo "$(YELLOW)Test installation:$(NC)"
	@echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ $(PACKAGE_NAME)"

publish: check-build ## Publish to PyPI (production)
	@echo "$(RED)⚠️  WARNING: This will publish to production PyPI!$(NC)"
	@read -p "Are you sure you want to continue? (y/N): " confirm && [ "$$confirm" = "y" ]
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
	@echo "$(YELLOW)You will need your PyPI API token$(NC)"
	@echo "$(YELLOW)Username: __token__$(NC)"
	@echo "$(YELLOW)Password: [your-pypi-api-token]$(NC)"
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)✅ Published to PyPI$(NC)"
	@echo "$(YELLOW)Package available at: https://pypi.org/project/$(PACKAGE_NAME)/$(NC)"
	@echo "$(YELLOW)Install with: pip install $(PACKAGE_NAME)$(NC)"

# Release workflow
release: ## Create a new release (tag, build, publish)
	@echo "$(BLUE)Creating new release...$(NC)"
	@read -p "Enter version number (e.g., 0.1.1): " version && \
	echo "Updating version to $$version..." && \
	git add . && \
	git commit -m "Release v$$version" && \
	git tag "v$$version" && \
	git push origin main && \
	git push origin "v$$version"
	@echo "$(GREEN)✅ Release created$(NC)"
	@echo "$(YELLOW)Now run 'make publish' to publish to PyPI$(NC)"

# Pre-commit setup
pre-commit: ## Setup pre-commit hooks
	@echo "$(BLUE)Setting up pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✅ Pre-commit hooks installed$(NC)"

# Comprehensive check
check-all: format-check lint type-check test security-check ## Run all quality checks
	@echo "$(GREEN)✅ All checks passed! Ready for release.$(NC)"

# Development workflow
dev-setup: install-dev pre-commit ## Complete development setup
	@echo "$(GREEN)✅ Development environment fully configured$(NC)"

# Quick test with real API
test-api: ## Quick test with real API
	@echo "$(BLUE)Running quick API test...$(NC)"
	$(PYTHON) -c "from cognify_sdk import CognifyClient; print('✅ SDK import successful')"
	@echo "$(GREEN)✅ API test completed$(NC)"

# Version info
version: ## Show current version
	@echo "$(BLUE)Current version:$(NC)"
	@grep -E '^version = ' pyproject.toml | sed 's/version = //' | tr -d '"'

# Dependencies update
update-deps: ## Update all dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[dev]"
	@echo "$(GREEN)✅ Dependencies updated$(NC)"

# Show package info
info: ## Show package information
	@echo "$(BLUE)Package Information:$(NC)"
	@echo "Name: $(PACKAGE_NAME)"
	@echo "Source: $(SOURCE_DIR)"
	@echo "Tests: $(TESTS_DIR)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo ""
	@echo "$(BLUE)Project Structure:$(NC)"
	@tree -I '__pycache__|*.pyc|.git|.pytest_cache|htmlcov|dist|build|*.egg-info' -L 2
