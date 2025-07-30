# Makefile for the epa-syllabicate project

.PHONY: help install install-dev test test-verbose test-coverage clean format lint all venv activate

# Variables
VENV_DIR := .venv
PYTHON := python3
PIP := pip3
PYTEST := pytest

# Check if we're in a virtual environment, if not use venv if it exists
ifdef VIRTUAL_ENV
    VENV_PYTHON := python
    VENV_PIP := pip
else ifneq (,$(wildcard $(VENV_DIR)/bin/python))
    VENV_PYTHON := $(VENV_DIR)/bin/python
    VENV_PIP := $(VENV_DIR)/bin/pip
else
    VENV_PYTHON := $(PYTHON)
    VENV_PIP := $(PIP)
endif

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default command
help: ## Show this help
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

venv: ## Create a virtual environment
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)Virtual environment created in $(VENV_DIR)$(NC)"
	@echo "$(YELLOW)To activate the virtual environment, run:$(NC)"
	@echo "  $(BLUE)source $(VENV_DIR)/bin/activate$(NC)"
	@echo "$(YELLOW)Or use:$(NC)"
	@echo "  $(BLUE)make activate$(NC)"

activate: ## Show command to activate virtual environment
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(GREEN)To activate the virtual environment, run:$(NC)"; \
		echo "  $(BLUE)source $(VENV_DIR)/bin/activate$(NC)"; \
		echo "$(YELLOW)Or run commands in the activated environment with:$(NC)"; \
		echo "  $(BLUE)$(VENV_DIR)/bin/python your_script.py$(NC)"; \
	else \
		echo "$(YELLOW)Virtual environment not found. Create it first with:$(NC)"; \
		echo "  $(BLUE)make venv$(NC)"; \
	fi

# Target to ensure venv exists
ensure-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(YELLOW)Virtual environment not found. Creating it...$(NC)"; \
		make venv; \
	fi

install: ensure-venv ## Install basic project dependencies
	@echo "$(GREEN)Installing basic dependencies...$(NC)"
	$(VENV_PIP) install -e .
	@echo "$(YELLOW)Using virtual environment: $(VENV_DIR)$(NC)"

install-dev: ensure-venv ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(VENV_PIP) install -e ".[dev]"
	@echo "$(YELLOW)Using virtual environment: $(VENV_DIR)$(NC)"

test: install-dev ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)Using virtual environment: $(VENV_DIR)$(NC)"; \
		$(VENV_PYTHON) -m pytest tests/; \
	else \
		echo "$(YELLOW)No virtual environment found, using system Python$(NC)"; \
		$(PYTHON) -m pytest tests/; \
	fi

test-verbose: install-dev ## Run tests with detailed output
	@echo "$(GREEN)Running tests with detailed output...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)Using virtual environment: $(VENV_DIR)$(NC)"; \
		$(VENV_PYTHON) -m pytest -v tests/; \
	else \
		echo "$(YELLOW)No virtual environment found, using system Python$(NC)"; \
		$(PYTHON) -m pytest -v tests/; \
	fi

test-coverage: install-dev ## Run tests with code coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)Using virtual environment: $(VENV_DIR)$(NC)"; \
		$(VENV_PYTHON) -m pytest --cov=epa_syllabicate --cov-report=html --cov-report=term tests/; \
	else \
		echo "$(YELLOW)No virtual environment found, using system Python$(NC)"; \
		$(PYTHON) -m pytest --cov=epa_syllabicate --cov-report=html --cov-report=term tests/; \
	fi

test-watch: install-dev ## Run tests in watch mode (requires pytest-watch)
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)Using virtual environment: $(VENV_DIR)$(NC)"; \
		$(VENV_PYTHON) -m pytest --watch tests/; \
	else \
		echo "$(YELLOW)No virtual environment found, using system Python$(NC)"; \
		$(PYTHON) -m pytest --watch tests/; \
	fi

format: ## Format code with black
	@echo "$(GREEN)Formatting code...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)Using virtual environment: $(VENV_DIR)$(NC)"; \
		$(VENV_PYTHON) -m black epa_syllabicate/ tests/; \
	else \
		echo "$(YELLOW)No virtual environment found, using system Python$(NC)"; \
		$(PYTHON) -m black epa_syllabicate/ tests/; \
	fi

lint: ## Check code format
	@echo "$(GREEN)Checking code format...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)Using virtual environment: $(VENV_DIR)$(NC)"; \
		$(VENV_PYTHON) -m black --check epa_syllabicate/ tests/; \
	else \
		echo "$(YELLOW)No virtual environment found, using system Python$(NC)"; \
		$(PYTHON) -m black --check epa_syllabicate/ tests/; \
	fi

clean: ## Clean temporary files
	@echo "$(GREEN)Cleaning temporary files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

clean-venv: ## Remove virtual environment
	@echo "$(GREEN)Removing virtual environment...$(NC)"
	rm -rf $(VENV_DIR)

build: ## Build the package
	@echo "$(GREEN)Building package...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)Using virtual environment: $(VENV_DIR)$(NC)"; \
		$(VENV_PYTHON) -m build; \
	else \
		echo "$(YELLOW)No virtual environment found, using system Python$(NC)"; \
		$(PYTHON) -m build; \
	fi

all: clean install-dev test ## Run cleanup, installation and tests

# Quick development commands
dev-setup: venv install-dev ## Quick setup for development (create venv and install dev dependencies)
	@echo "$(GREEN)Development setup completed$(NC)"
	@echo "$(YELLOW)To activate the virtual environment, run:$(NC)"
	@echo "  $(BLUE)source $(VENV_DIR)/bin/activate$(NC)"
	@echo "$(YELLOW)Or use:$(NC)"
	@echo "  $(BLUE)make activate$(NC)"

quick-test: ## Quick test without detailed output
	@if [ -d "$(VENV_DIR)" ]; then \
		$(VENV_PYTHON) -m pytest tests/ -q; \
	else \
		$(PYTHON) -m pytest tests/ -q; \
	fi

# Command to run a specific test
# Usage: make test-file FILE=test_syllabicate.py
test-file: install-dev ## Run a specific test file (use FILE=filename)
	@echo "$(GREEN)Running $(FILE)...$(NC)"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)Using virtual environment: $(VENV_DIR)$(NC)"; \
		$(VENV_PYTHON) -m pytest tests/$(FILE) -v; \
	else \
		echo "$(YELLOW)No virtual environment found, using system Python$(NC)"; \
		$(PYTHON) -m pytest tests/$(FILE) -v; \
	fi 