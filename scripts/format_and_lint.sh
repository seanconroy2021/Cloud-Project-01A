#!/bin/bash
# This script is used to format and lint the Python code in the project.
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
