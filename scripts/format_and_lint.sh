#!/bin/bash
cd "$(dirname "$0")/.."
# Format all Python files with Black
echo "Formatting with Black..."
black ./src

# Sort imports with isort
echo "Sorting imports with isort..."
isort ./src

# Lint with Flake8
echo "Linting with Flake8..."
flake8 ./src

echo "Formatting and linting complete."
