.PHONY: test test-01 test-02 test-03 test-04

# Package mappings
PKG_01 = events_definition
PKG_02 = appending_events_db
PKG_03 = getting_state_from_events
PKG_04 = getting_state_from_events_db

# System detection
OS := $(shell uname 2>/dev/null || echo Windows)
SHELL := $(shell if [ "$(OS)" = "Windows" ]; then echo "cmd"; else echo "bash"; fi)

# Default target to run all tests
test: test-01 test-02 test-03 test-04

# Define the test command based on OS
ifeq ($(OS), Windows)
    TEST_CMD = if exist $(PKG)/tests (cd $(PKG) & uv run pytest tests/) else (echo "No tests directory found in $(PKG)")
else
    TEST_CMD = if [ -d "$(PKG)/tests" ]; then cd $(PKG) && uv run pytest tests/; else echo "No tests directory found in $(PKG)"; fi
endif

# Individual package test targets
test-01:
	@echo "Running tests for $(PKG_01)..."
	@$(MAKE) run-test PKG=$(PKG_01)

test-02:
	@echo "Running tests for $(PKG_02)..."
	@$(MAKE) run-test PKG=$(PKG_02)

test-03:
	@echo "Running tests for $(PKG_03)..."
	@$(MAKE) run-test PKG=$(PKG_03)

test-04:
	@echo "Running tests for $(PKG_04)..."
	@$(MAKE) run-test PKG=$(PKG_04)

run-test:
	@$(TEST_CMD)

# Help target
help:
	@echo "Available targets:"
	@echo "  test     - Run all tests"
	@echo "  test-01  - Run tests for events_definition"
	@echo "  test-02  - Run tests for appending_events_db"
	@echo "  test-03  - Run tests for getting_state_from_events"
	@echo "  test-04  - Run tests for getting_state_from_events_db"

mypy:
	@echo "Running mypy..."
	@uv run mypy .