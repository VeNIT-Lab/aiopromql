.PHONY: format lint unit-test integration-test coverage-html docs docs-clean docs-serve docs-watch docker-integration-test docker-clean

help:
	@echo "Available commands:"
	@echo "  make format          - Format the code using ruff"
	@echo "  make lint            - Lint the code using ruff"
	@echo "  make unit-test       - Run unit tests"
	@echo "  make integration-test - Run integration tests"
	@echo "  make coverage-html   - Generate HTML coverage report"
	@echo "  make tree            - Display project directory structure"
	@echo "  make help            - Show this help message"
	@echo "  make build           - Build the package"
	@echo "  make install         - Install the package in editable mode with dev dependencies"
	@echo "  make docs            - Build HTML documentation with Sphinx"
	@echo "  make docs-clean      - Remove generated documentation"
	@echo "  make docs-serve      - Serve built documentation locally on port 8000"
	@echo "  make docs-watch      - Auto-rebuild and serve docs on changes (port 8000)"
	@echo "  make docker-integration-test - Run integration tests using Docker Compose"
	@echo "  make docker-clean    - Tear down Docker setup and clean volumes/data"

format:
	ruff format

lint:
	ruff check .

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

build:
	hatch build
install:	
	pip install --upgrade pip
	pip install -e .[dev,docs]

# Documentation
docs:
	sphinx-build -b html docs/source docs/build/html

docs-clean:
	rm -rf docs/build

docs-serve:
	python -m http.server -d docs/build/html 8000

# Docker-based integration testing
docker-integration-test:
	docker compose up --build --abort-on-container-exit --exit-code-from integration-tests

docker-clean:
	docker compose down