.PHONY: help install install-dev install-ai test test-unit test-integration coverage lint format type-check docs clean build upload

# Default target
help: ## Show this help message
	@echo "🔥 Farm Content - Вирусная Контент-Машина 2025"
	@echo "================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation commands
install: ## Install the package in development mode
	@echo "📦 Installing Farm Content..."
	pip install -e .

install-dev: ## Install with development dependencies
	@echo "🛠️ Installing development dependencies..."
	pip install -e ".[dev]"
	pre-commit install

install-ai: ## Install with AI dependencies
	@echo "🤖 Installing AI dependencies..."
	pip install -e ".[ai]"

install-all: ## Install all dependencies
	@echo "🚀 Installing all dependencies..."
	pip install -e ".[dev,ai,docs]"

# Development commands
run: ## Run the main application
	@echo "🚀 Starting Farm Content..."
	python -m farm_content

run-web: ## Run web interface
	@echo "🌐 Starting web interface..."
	python -m farm_content.interfaces.web

run-gui: ## Run GUI interface
	@echo "🖥️ Starting GUI interface..."
	python -m farm_content.interfaces.gui

run-cli: ## Run CLI interface
	@echo "💻 Starting CLI interface..."
	python -m farm_content.interfaces.cli

# Testing commands
test: ## Run all tests
	@echo "🧪 Running all tests..."
	pytest

test-unit: ## Run unit tests only
	@echo "🔬 Running unit tests..."
	pytest -m "not integration and not slow"

test-integration: ## Run integration tests only
	@echo "🔗 Running integration tests..."
	pytest -m integration

test-slow: ## Run slow tests
	@echo "⏳ Running slow tests..."
	pytest -m slow

coverage: ## Generate coverage report
	@echo "📊 Generating coverage report..."
	pytest --cov-report=html --cov-report=term
	@echo "📈 Coverage report generated in htmlcov/"

# Code quality commands
lint: ## Run linting
	@echo "🔍 Running linters..."
	flake8 src/ tests/
	mypy src/

format: ## Format code
	@echo "✨ Formatting code..."
	black src/ tests/
	isort src/ tests/

format-check: ## Check code formatting
	@echo "🔍 Checking code formatting..."
	black --check src/ tests/
	isort --check-only src/ tests/

type-check: ## Run type checking
	@echo "🔎 Running type checks..."
	mypy src/

pre-commit: ## Run pre-commit hooks
	@echo "🪝 Running pre-commit hooks..."
	pre-commit run --all-files

# Documentation commands
docs: ## Build documentation
	@echo "📚 Building documentation..."
	cd docs && make html

docs-serve: ## Serve documentation locally
	@echo "🌐 Serving documentation..."
	cd docs/_build/html && python -m http.server 8000

docs-clean: ## Clean documentation build
	@echo "🧹 Cleaning documentation..."
	cd docs && make clean

# Build and release commands
clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	@echo "🏗️ Building package..."
	python -m build

upload-test: ## Upload to TestPyPI
	@echo "🚀 Uploading to TestPyPI..."
	python -m twine upload --repository testpypi dist/*

upload: ## Upload to PyPI
	@echo "🚀 Uploading to PyPI..."
	python -m twine upload dist/*

# Docker commands
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t farm-content:latest .

docker-run: ## Run in Docker container
	@echo "🐳 Running in Docker..."
	docker run -p 5000:5000 -it farm-content:latest

# Environment commands
env-create: ## Create virtual environment
	@echo "🏠 Creating virtual environment..."
	python -m venv venv

env-activate: ## Show activation command
	@echo "To activate the virtual environment, run:"
	@echo "source venv/bin/activate  # On Unix/macOS"
	@echo "venv\\Scripts\\activate     # On Windows"

# System info
info: ## Show system information
	@echo "📋 System Information"
	@echo "===================="
	@echo "Python: $$(python --version)"
	@echo "Pip: $$(pip --version)"
	@echo "OS: $$(uname -s)"
	@echo "Working directory: $$(pwd)"
	@echo ""
	@echo "📦 Package Information"
	@echo "==================="
	@python -c "import pkg_resources; print('Farm Content:', pkg_resources.get_distribution('farm-content').version)" 2>/dev/null || echo "Farm Content: Not installed"
