#!/usr/bin/env bash

set -e
set -x

# Run only integration tests (end-to-end tests with real database)
# Usage: ./scripts/test-integration.sh [pytest-args]
# Examples:
#   ./scripts/test-integration.sh                     # Run all integration tests
#   ./scripts/test-integration.sh -k "test_auth"      # Run integration tests matching pattern
#   ./scripts/test-integration.sh -v                  # Run with verbose output

coverage run -m pytest tests/ -m integration "$@"
coverage report
coverage html --title "integration-coverage"
