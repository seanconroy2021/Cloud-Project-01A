#!/bin/bash
# This script is used to format and lint the Python code in the project.
# I used this script to automate the process of formatting and linting the code.

# Format all Python files with Black
echo "Formatting with Black..."
black ./src

# Sort imports with isort
echo "Sorting imports with isort..."
isort ./src

# Lint with Flake8
echo "Linting with Flake8..."
flake8 --ignore=E501 ./src # Ignore line length errors this is due to long userdata

echo "Formatting and linting complete."
