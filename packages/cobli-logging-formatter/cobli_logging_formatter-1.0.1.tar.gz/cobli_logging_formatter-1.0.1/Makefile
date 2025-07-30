# Cobli Logging Formatter - Development Makefile
# 
# This Makefile provides all necessary development tasks for the cobli-logging-formatter package.
# It uses uv for fast dependency management and virtual environment handling.

.PHONY: help install clean test test-cov lint format check build publish
.PHONY: dev-install dev-clean examples docs verify-install all

# Default target
.DEFAULT_GOAL := help

# Variables
PACKAGE_NAME := cobli-logging-formatter
SOURCE_DIR := cobli_logging
TESTS_DIR := tests
EXAMPLES_DIR := examples

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help: ## Show this help message
	@echo "Cobli Logging Formatter - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install         Install production dependencies only"
	@echo "  dev-install     Install all dependencies including development tools"
	@echo "  clean           Remove build artifacts and cache files"
	@echo "  dev-clean       Remove all build artifacts, cache, and uv environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  test            Run all tests"
	@echo "  test-cov        Run tests with coverage report"
	@echo "  lint            Run linting checks (flake8)"
	@echo "  lint-mypy       Run type checking with mypy"
	@echo "  format          Format code with black"
	@echo "  format-check    Check code formatting without making changes"
	@echo "  check           Run all quality checks (format, lint, test)"
	@echo ""
	@echo "Build & Distribution:"
	@echo "  build           Build the package"
	@echo "  verify-build    Build and verify the package"
	@echo "  publish-test    Publish to TestPyPI"
	@echo "  publish         Publish to PyPI (production)"
	@echo ""
	@echo "Convenience Commands:"
	@echo "  examples        Run usage examples"
	@echo "  verify-install  Verify package can be imported correctly"
	@echo "  docs            Generate documentation"
	@echo "  all             Run complete development workflow"
	@echo "  dev-setup       Complete development setup"

# ============================================================================
# Setup Commands
# ============================================================================

install: ## Install production dependencies only
	@echo "$(YELLOW)Installing production dependencies...$(RESET)"
	uv sync --no-dev

dev-install: ## Install all dependencies including development tools
	@echo "$(YELLOW)Installing development dependencies...$(RESET)"
	uv sync --dev

clean: ## Remove build artifacts and cache files
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

dev-clean: clean ## Remove all build artifacts, cache, and uv environment
	@echo "$(YELLOW)Cleaning development environment...$(RESET)"
	uv clean

# ============================================================================
# Development Commands
# ============================================================================

test: ## Run all tests
	@echo "$(YELLOW)Running tests...$(RESET)"
	uv run python -m pytest $(TESTS_DIR) -v

test-cov: ## Run tests with coverage report
	@echo "$(YELLOW)Running tests with coverage...$(RESET)"
	uv run python -m pytest $(TESTS_DIR) --cov=$(SOURCE_DIR) --cov-report=term-missing --cov-report=html -v

lint: ## Run linting checks (flake8)
	@echo "$(YELLOW)Running linting checks...$(RESET)"
	uv run python -m flake8 $(SOURCE_DIR) $(TESTS_DIR) --max-line-length=88 --extend-ignore=E203,W503

lint-mypy: ## Run type checking with mypy
	@echo "$(YELLOW)Running type checking...$(RESET)"
	uv run python -m mypy $(SOURCE_DIR) --ignore-missing-imports

format: ## Format code with black
	@echo "$(YELLOW)Formatting code...$(RESET)"
	uv run python -m black $(SOURCE_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)

format-check: ## Check code formatting without making changes
	@echo "$(YELLOW)Checking code formatting...$(RESET)"
	uv run python -m black --check $(SOURCE_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)

check: format-check lint test ## Run all quality checks (format, lint, test)
	@echo "$(GREEN)✅ All quality checks passed!$(RESET)"

# ============================================================================
# Build & Distribution
# ============================================================================

build: clean ## Build the package
	@echo "$(YELLOW)Building package...$(RESET)"
	uv build

build-verbose: clean ## Build the package with verbose output
	@echo "$(YELLOW)Building package (verbose)...$(RESET)"
	uv build --verbose

verify-build: build ## Build and verify the package
	@echo "$(YELLOW)Verifying build artifacts...$(RESET)"
	@if [ -d "dist" ]; then \
		echo "$(GREEN)✅ Build artifacts created:$(RESET)"; \
		ls -la dist/; \
	else \
		echo "$(RED)❌ No build artifacts found$(RESET)"; \
		exit 1; \
	fi

publish-test: build ## Publish to TestPyPI
	@echo "$(YELLOW)Publishing to TestPyPI...$(RESET)"
	uv run python -m twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI (production)
	@echo "$(YELLOW)Publishing to PyPI...$(RESET)"
	@echo "$(RED)⚠️  This will publish to production PyPI!$(RESET)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	uv run python -m twine upload dist/*

# ============================================================================
# Convenience Commands
# ============================================================================

examples: ## Run usage examples
	@echo "$(YELLOW)Running usage examples...$(RESET)"
	uv run python $(EXAMPLES_DIR)/usage_examples.py

verify-install: ## Verify package can be imported correctly
	@echo "$(YELLOW)Verifying package installation...$(RESET)"
	uv run python -c "import cobli_logging; print('✅ Package imports successfully')"
	uv run python -c "from cobli_logging import JsonFormatter, configure_logging, get_logger; print('✅ All components import successfully')"

docs: ## Generate documentation (placeholder)
	@echo "$(YELLOW)Documentation generation...$(RESET)"
	@echo "$(GREEN)📚 Documentation is available in:$(RESET)"
	@echo "  - README.md"
	@echo "  - DEPLOYMENT.md"
	@echo "  - docstrings in $(SOURCE_DIR)/"

# ============================================================================
# Development Workflow Commands
# ============================================================================

dev-setup: dev-install ## Complete development setup
	@echo "$(GREEN)🚀 Development environment ready!$(RESET)"
	@echo ""
	@echo "$(CYAN)Quick commands:$(RESET)"
	@echo "  make test      - Run tests"
	@echo "  make check     - Run all quality checks"
	@echo "  make build     - Build package"
	@echo "  make examples  - Run usage examples"

dev-test: format lint test ## Quick development test cycle
	@echo "$(GREEN)✅ Development test cycle completed!$(RESET)"

all: dev-install check build verify-install examples ## Run complete development workflow
	@echo "$(GREEN)🎉 All development tasks completed successfully!$(RESET)"

# ============================================================================
# Advanced Commands
# ============================================================================

benchmark: ## Run performance benchmarks (placeholder)
	@echo "$(YELLOW)Running benchmarks...$(RESET)"
	@echo "$(CYAN)ℹ️  Benchmark functionality not yet implemented$(RESET)"

security: ## Run security checks (placeholder)
	@echo "$(YELLOW)Running security checks...$(RESET)"
	@echo "$(CYAN)ℹ️  Consider adding: bandit, safety, or similar tools$(RESET)"

update-deps: ## Update all dependencies to latest versions
	@echo "$(YELLOW)Updating dependencies...$(RESET)"
	uv sync --upgrade

# ============================================================================
# Environment Information
# ============================================================================

info: ## Show environment information
	@echo "$(CYAN)Environment Information:$(RESET)"
	@echo "Package: $(PACKAGE_NAME)"
	@echo "Source: $(SOURCE_DIR)"
	@echo "Tests: $(TESTS_DIR)"
	@echo ""
	@echo "$(CYAN)Tool Versions:$(RESET)"
	@uv --version
	@echo "Python: $$(uv run python --version)"
	@echo ""
	@echo "$(CYAN)Package Structure:$(RESET)"
	@find $(SOURCE_DIR) -name "*.py" | head -10

# ============================================================================
# Legacy Support (for migration from dev_setup.py)
# ============================================================================

legacy-setup: dev-setup ## Legacy alias for dev_setup.py compatibility
	@echo "$(YELLOW)⚠️  Note: Use 'make dev-setup' instead of dev_setup.py$(RESET)"
