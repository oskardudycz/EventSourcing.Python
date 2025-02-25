.PHONY: test test-01 test-02 test-03 test-04

# Package mappings
PKG_01 = events_definition
PKG_02 = appending_events_db
PKG_03 = getting_state_from_events
PKG_04 = getting_state_from_events_db

# Default target to run all tests
test: test-01 test-02 test-03 test-04
# Individual package test targets
test-01:
	@echo "Running tests for $(PKG_01)..."
	@if [ -d "$(PKG_01)/tests" ]; then \
		cd $(PKG_01) && uv run pytest tests/; \
	else \
		echo "No tests directory found in $(PKG_01)"; \
	fi

test-02:
	@echo "Running tests for $(PKG_02)..."
	@if [ -d "$(PKG_02)/tests" ]; then \
		cd $(PKG_02) && uv run pytest tests/; \
	else \
		echo "No tests directory found in $(PKG_02)"; \
	fi

test-03:
	@echo "Running tests for $(PKG_03)..."
	@if [ -d "$(PKG_03)/tests" ]; then \
		cd $(PKG_03) && uv run pytest tests/; \
	else \
		echo "No tests directory found in $(PKG_03)"; \
	fi

test-04:
	@echo "Running tests for $(PKG_04)..."
	@if [ -d "$(PKG_04)/tests" ]; then \
		cd $(PKG_04) && uv run pytest tests/; \
	else \
		echo "No tests directory found in $(PKG_04)"; \
	fi

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