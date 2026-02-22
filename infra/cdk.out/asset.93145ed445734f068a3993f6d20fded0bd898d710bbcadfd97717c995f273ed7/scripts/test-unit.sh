#!/usr/bin/env bash

set -e
set -x

# Run only unit tests (fast, isolated tests with mocked dependencies)
# Usage: ./scripts/test-unit.sh [pytest-args]
# Examples:
#   ./scripts/test-unit.sh                        # Run all unit tests
#   ./scripts/test-unit.sh -k "test_person"       # Run unit tests matching pattern
#   ./scripts/test-unit.sh -v                     # Run with verbose output

coverage run -m pytest tests/ -m unit "$@"
coverage report
coverage html --title "unit-coverage"
