# AI Code Agent

A powerful, intelligent CLI developer tool that provides AI-powered code assistance with context management, file operations, and performance tracking. Built with Python and designed for maximum productivity in just 250 lines of code.

## Features

### Core Functionality
- **AI-Powered Code Assistance**: Intelligent tool routing for complex development tasks
- **Context Management**: Smart file indexing and content search
- **File Operations**: Create, read, edit, delete, and search files
- **Interactive CLI**: Rich console interface with command routing
- **Performance Tracking**: Query monitoring and uptime statistics

### New Enhanced Features
- **Auto-Save**: Automatic context persistence across sessions
- **Export Functionality**: Export conversation history to files
- **Performance Statistics**: Real-time metrics and uptime tracking
- **Quick Actions**: Fast access to stats, save, and export commands

## Requirements

- Python 3.8+
- Ollama (for AI functionality)
- Rich library for console output

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd py-game
   ```

2. **Install dependencies:**
   ```bash
   uv install
   ```

3. **Install Ollama:**
   - Visit [https://ollama.ai](https://ollama.ai)
   - Download and install Ollama
   - Pull the required model:
     ```bash
     ollama pull llama2:latest
     ```

## Usage

### Basic Usage
```bash
uv run python main.py
```

### Available Commands

#### Core Commands
- `help` or `h` - Show help information
- `context` or `files` - List files in context
- `clear` - Clear context
- `history` or `hist` - Show AI interaction history
- `exit`, `quit`, or `q` - Exit the application
- `cls` or `clear screen` - Clear the screen

#### Enhanced Commands
- `stats` - Display performance statistics
- `save` - Manual save with confirmation
- `export` - Export conversation history to `export.txt`

#### AI Commands
- `chat "your request"` - AI-powered tool routing for complex requests

### Examples

#### File Operations
```bash
# Create a new file
chat "create a new file test.py with print('hello world')"

# Search for Python files
chat "find Python files"

# Search for content
chat "search for 'def main'"

# Analyze code
chat "analyze the main.py file"
```

#### Context Management
```bash
# Add files to context
context

# Clear context
clear

# View statistics
stats

# Export history
export
```

## Architecture

### Core Components

#### CodeAgent Class
The main class that handles all functionality:
- **Context Management**: File indexing and content search
- **AI Integration**: Tool routing and response handling
- **Performance Tracking**: Query monitoring and statistics
- **File Operations**: Create, read, search, and manage files

#### Key Methods
- `_smart_route_command()` - Routes user commands to appropriate handlers
- `_execute_single_tool()` - Executes specific tools (create, read, search, etc.)
- `ask_with_context()` - AI-powered responses with file context
- `add_context()` - Manages file context and indexing
- `_auto_save()` - Automatic context persistence

### Data Structures
- **Context**: Dictionary with `files` and `history` lists
- **Performance Stats**: Query count, uptime, and file processing metrics
- **File Index**: Fast content search with word indexing

## Testing

### Test Suite
The application includes comprehensive test coverage:

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test categories
uv run python -m pytest tests/test_new_features.py -v
uv run python -m pytest tests/test_integration.py -v
```

### Test Categories
1. **AI Functionality** (`test_ai.py`) - AI operations and performance
2. **CodeAgent Core** (`test_codeagent.py`) - Core functionality and file operations
3. **Context Management** (`test_context.py`) - Context persistence and commands
4. **New Features** (`test_new_features.py`) - Enhanced functionality
5. **Tool Execution** (`test_orchestrator.py`) - Tool routing and execution
6. **Integration** (`test_integration.py`) - End-to-end workflows

### Test Cleanup
All tests include proper cleanup to prevent file leaks:
- Temporary files are automatically cleaned up
- Context files are isolated per test
- Export files are removed after testing

## Performance Features

### Intelligent Caching
- **Response Cache**: Cached AI responses for repeated queries
- **File Indexing**: Background file content indexing
- **Smart Compression**: Context truncation for large files

### Performance Monitoring
- **Query Tracking**: Monitor AI interactions and response times
- **Uptime Statistics**: Track application runtime
- **File Processing**: Monitor indexed files and content

### Statistics Display
```bash
stats
# Output: Stats: 15 files, 1250 lines, 8 history, 12 queries, 45.2s uptime
```

## Configuration

### Context File
The application uses `agent_context.json` to persist:
- File context and indexing
- Conversation history
- Performance statistics

### AI Configuration
- **Model**: llama2:latest (configurable)
- **URL**: http://localhost:11434 (Ollama default)
- **Timeout**: 2 seconds for health checks

## Error Handling

### Graceful Degradation
- **AI Unavailable**: Continue with file operations only
- **File Errors**: Skip problematic files, continue processing
- **Network Issues**: Retry with exponential backoff

### User-Friendly Messages
- Clear error messages for common issues
- Helpful suggestions for troubleshooting
- Progress indicators for long operations

## Use Cases

### Development Workflows
1. **Code Analysis**: Analyze existing codebases
2. **File Management**: Organize and search project files
3. **Content Search**: Find specific code patterns or functions
4. **Documentation**: Generate and export project documentation

### AI-Assisted Development
1. **Code Generation**: Create new files with AI assistance
2. **Code Review**: Analyze and improve existing code
3. **Debugging**: Get AI insights on code issues
4. **Refactoring**: Intelligent code restructuring suggestions

## Advanced Features

### Smart File Indexing
- **Content Search**: Full-text search across all files
- **File Type Detection**: Automatic file type recognition
- **Incremental Updates**: Only re-index changed files

### AI Tool Routing
- **Intelligent Parsing**: Understands natural language requests
- **Tool Selection**: Automatically chooses appropriate tools
- **Context Integration**: Uses file context for better responses

### Export Capabilities
- **History Export**: Save conversation history to files
- **Statistics Export**: Export performance metrics
- **Context Backup**: Save current file context

## Security Considerations

### File Safety
- **Path Validation**: Prevents directory traversal attacks
- **File Type Filtering**: Only processes safe file types
- **Permission Checks**: Validates file access permissions

### AI Safety
- **Input Validation**: Sanitizes user inputs
- **Response Filtering**: Validates AI responses
- **Error Boundaries**: Prevents AI errors from crashing the app

## Performance Metrics

### Benchmarks
- **Startup Time**: < 1 second
- **File Indexing**: ~100 files/second
- **AI Response**: 2-5 seconds average
- **Memory Usage**: < 50MB typical

### Optimization Features
- **Lazy Loading**: Load files only when needed
- **Background Processing**: Non-blocking file operations
- **Smart Caching**: Reduce redundant operations

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for new functions
- Maintain the 273-line constraint

## License

This project is licensed under the MIT License - see the LICENSE file for details.
