.PHONY: format lint test-unit test-integration coverage-html

help:
	@echo "Available commands:"
	@echo "  make format          - Format the code using ruff"
	@echo "  make lint            - Lint the code using ruff"
	@echo "  make unit-test       - Run unit tests"
	@echo "  make integration-test - Run integration tests"
	@echo "  make coverage-html   - Generate HTML coverage report"
	@echo "  make tree            - Display project directory structure"

format:
	ruff --fix .

lint:
	ruff .

unit-test:
	pytest -m unit

integration-test:
	pytest -m integration

coverage-html:
	pytest -m unit --cov=aiopromql --cov-report=term-missing -q
	coverage html --include="aiopromql/**/*.py"
	@echo "HTML report generated at htmlcov/index.html"

tree:
	tree -I '.git|node_modules|*.log|*.pyc|venv|htmlcov|__pycache__'