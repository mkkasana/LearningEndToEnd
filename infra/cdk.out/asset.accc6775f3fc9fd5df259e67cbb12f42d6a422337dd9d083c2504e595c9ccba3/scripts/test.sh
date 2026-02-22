#!/usr/bin/env bash

set -e
set -x

# Run all tests with coverage
# Usage: ./scripts/test.sh [pytest-args]
# Examples:
#   ./scripts/test.sh                    # Run all tests
#   ./scripts/test.sh -m unit            # Run only unit tests
#   ./scripts/test.sh -m integration     # Run only integration tests
#   ./scripts/test.sh -k "test_login"    # Run tests matching pattern

coverage run -m pytest tests/ "$@"
coverage report
coverage html --title "${@:-coverage}"
