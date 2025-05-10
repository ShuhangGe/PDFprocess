.PHONY: setup run docker-db import-catalog clean help test

# Variables
PYTHON = python
VENV = venv
PIP = $(VENV)/bin/pip
PYTHON_VENV = $(VENV)/bin/python

help:
	@echo "Document Processing Application"
	@echo ""
	@echo "Usage: make <command>"
	@echo ""
	@echo "Commands:"
	@echo "  setup          Create virtual environment and install dependencies"
	@echo "  run            Run the application"
	@echo "  docker-db      Start PostgreSQL using Docker"
	@echo "  setup-db       Set up the database"
	@echo "  import-catalog Import product catalog"
	@echo "  clean          Remove virtual environment and cache files"
	@echo "  test           Run tests"

setup:
	@echo "Setting up virtual environment and installing dependencies..."
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Setup complete! Use 'make run' to start the application."

run:
	@echo "Running the application..."
	$(PYTHON_VENV) run.py

docker-db:
	@echo "Starting PostgreSQL with Docker..."
	docker-compose up -d

setup-db:
	@echo "Setting up the database..."
	$(PYTHON_VENV) setup_db.py

import-catalog:
	@echo "Importing product catalog..."
	@curl -X 'POST' \
	  'http://localhost:8000/api/catalog/import' \
	  -H 'accept: application/json' \
	  -d ''

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf app/*/__pycache__
	@echo "Clean complete!"

test:
	@echo "Running tests..."
	$(PYTHON_VENV) -m pytest 