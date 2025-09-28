# AI Code Agent Test Suite

This directory contains comprehensive unit tests for the AI Code Agent CLI tool.

## Test Structure

- `test_ai.py` - Tests for the AI class (Ollama integration, file operations)
- `test_orchestrator.py` - Tests for the Orchestrator class (tool management, file operations)
- `test_codeagent.py` - Tests for the CodeAgent class (main application logic)
- `test_context.py` - Tests for the Context dataclass (data management)
- `test_integration.py` - Integration tests for complete workflows
- `test_runner.py` - Test runner script

## Running Tests

### Run All Tests
```bash
python tests/test_runner.py
```

### Run Individual Test Files
```bash
python tests/test_ai.py
python tests/test_orchestrator.py
python tests/test_codeagent.py
python tests/test_context.py
python tests/test_integration.py
```

### Run with Verbose Output
```bash
python -m unittest tests.test_ai -v
```

## Test Coverage

### AI Class Tests
- ✅ AI initialization
- ✅ Server availability checking
- ✅ File editing operations
- ✅ Error handling

### Orchestrator Tests
- ✅ Tool registry initialization
- ✅ File creation/deletion/editing
- ✅ File searching functionality
- ✅ Request routing logic

### CodeAgent Tests
- ✅ Context management
- ✅ File gathering (search/browse/context modes)
- ✅ File filtering and directory walking
- ✅ Status reporting

### Context Tests
- ✅ Data structure initialization
- ✅ File list management
- ✅ History management with size limits

### Integration Tests
- ✅ Complete workflow testing
- ✅ AI task execution
- ✅ File operation workflows
- ✅ Error handling scenarios

## Mocking Strategy

Tests use `unittest.mock` to:
- Mock AI server responses
- Mock file system operations
- Mock user input/output
- Isolate components for unit testing

## Requirements

- Python 3.7+
- unittest (built-in)
- tempfile (built-in)
- os, sys (built-in)

## Notes

- Tests create temporary files and directories that are cleaned up automatically
- Mock objects prevent actual network calls to Ollama server
- File operations are tested with temporary files to avoid affecting the main codebase


