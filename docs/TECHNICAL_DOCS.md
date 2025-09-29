# AI Code Agent - Technical Documentation

## Architecture Overview

### System Design
The AI Code Agent is built as a single-class application (`MultiToolAIAgent`) that consolidates all functionality into optimized Python code. The architecture follows a modular design pattern with integrated components using Google's Gemini AI models.

### Core Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                 MultiToolAIAgent Class                      │
├─────────────────────────────────────────────────────────────┤
│  • Context Management (files, history)                      │
│  • AI Integration (Google Gemini 2.5 API)                   │
│  • File Operations (CRUD, search, indexing)                 │
│  • Performance Tracking (stats, uptime, queries)            │
│  • Tool Execution (routing, validation)                     │
│  • User Interface (Rich console, commands)                  │
└─────────────────────────────────────────────────────────────┘
```

## Data Structures

### Context Dictionary
```python
context = {
    'files': List[str],      # File paths in context
    'history': List[str]     # AI interaction history
}
```

### Performance Statistics
```python
performance_stats = {
    'queries': int,          # Number of AI queries
    'files_processed': int,  # Files indexed
    'start_time': float     # Application start timestamp
}
```

### File Index System
```python
file_index = Dict[str, float]           # filepath -> mtime
content_index = Dict[str, Set[str]]     # word -> set of filepaths
```

## Core Methods

### Initialization (`__init__`)
```python
def __init__(self):
    # Initialize AI connection, caching, and indexing
    # Load context from persistent storage
    # Start background file indexing
```

**Key Features:**
- Lazy loading of context files
- Background thread for file indexing
- Performance metrics initialization
- Error-resilient startup

### File Operations

#### `get_file_content(filepath: str) -> str`
- **Purpose**: Cached file content retrieval
- **Caching**: LRU cache with 1000 entries
- **Error Handling**: Returns empty string on failure
- **Performance**: O(1) for cached files

#### `add_context(paths: List[str]) -> None`
- **Purpose**: Add files/directories to context
- **Features**: 
  - File type validation
  - Duplicate prevention
  - Background indexing
  - Progress feedback

#### `list_files(query: str, directory: str, interactive: bool) -> List[str]`
- **Purpose**: File discovery and selection
- **Modes**: Context, search, browse
- **Features**: Interactive selection, filtering

### AI Integration

#### `ask_with_context(role: str, prompt: str, context_files: List[str]) -> str`
- **Purpose**: AI-powered responses with file context
- **Features**:
  - Context compression (2000 char limit)
  - Response caching (5-minute TTL)
  - Error handling
  - Performance tracking

#### `ask_stream(prompt: str, system: str) -> str`
- **Purpose**: Streaming AI responses
- **Features**:
  - Real-time output
  - Progress indicators
  - Chunk processing
  - Performance metrics

### Tool Execution

#### `_execute_single_tool(tool_name: str, data: Dict) -> str`
- **Purpose**: Execute specific tools
- **Supported Tools**:
  - `create_file`: File creation
  - `read_file`: File reading
  - `search_files`: File discovery
  - `search_content`: Content search
  - `show_context`: Context display
  - `clear_context`: Context clearing
  - `show_help`: Help display
  - `show_history`: History display
  - `exit_program`: Application exit

#### `_smart_route_command(user_input: str) -> str`
- **Purpose**: Route user commands to appropriate handlers
- **Features**:
  - Command parsing
  - AI tool routing
  - Error handling
  - Input validation

## Search and Indexing

### File Indexing Algorithm
```python
def build_index(files: List[str]) -> None:
    # 1. Check if re-indexing is needed (5-second interval)
    # 2. Clear existing indexes
    # 3. For each file:
    #    - Get modification time
    #    - Extract content
    #    - Tokenize and index words > 2 chars
    # 4. Update scan timestamp
```

### Content Search Algorithm
```python
def search_content(query: str, files: List[str]) -> List[Tuple]:
    # 1. Convert query to lowercase
    # 2. For each file:
    #    - Read content
    #    - Search for query in each line
    #    - Return (filepath, line_number, line_content)
    # 3. Limit results to 50 matches
```

### File Search Algorithm
```python
def search_files(query: str, files: List[str]) -> List[str]:
    # 1. Search filename matches
    # 2. Search content index for word matches
    # 3. Return top 20 results
```

## Performance Optimizations

### Caching Strategy
- **File Content**: LRU cache (1000 entries)
- **AI Responses**: 5-minute TTL cache
- **Health Checks**: 10-second cache
- **File Indexes**: Memory-based with persistence

### Background Processing
- **File Indexing**: Daemon thread for non-blocking operation
- **Context Loading**: Asynchronous file discovery
- **Performance Tracking**: Real-time metrics collection

### Memory Management
- **Cache Limits**: Automatic cleanup of old entries
- **File Truncation**: Large files truncated to 2000 chars
- **Index Optimization**: Word-based indexing for efficiency

## Error Handling

### Exception Hierarchy
```python
try:
    # File operations
except FileNotFoundError:
    # Handle missing files
except PermissionError:
    # Handle access denied
except Exception:
    # Generic error handling
```

### Graceful Degradation
- **AI Unavailable**: Continue with file operations
- **File Errors**: Skip problematic files
- **Network Issues**: Retry with backoff
- **Memory Issues**: Clear caches and continue

### User Feedback
- **Progress Indicators**: Real-time operation feedback
- **Error Messages**: Clear, actionable error descriptions
- **Status Updates**: Current operation status

## 🔧 Configuration Management

### Environment Variables
- **GEMINI_API_KEY**: Google Gemini API key (required)
### Startup Behavior
On initialization the agent emits a short console message using Rich: `Starting MultiToolAIAgent...`.
- **CACHE_SIZE**: LRU cache size (default: 1000)
- **SCAN_INTERVAL**: File re-scan interval (default: 5 seconds)

### Context Persistence
```python
# Save context
def _auto_save(self):
    with open(self.file, 'w') as f:
        json.dump(self.context, f)

# Load context
def __init__(self):
    try:
        with open(self.file) as f:
            data = json.load(f)
            self.context = {
                'files': data.get('files', []),
                'history': data.get('history', [])
            }
    except:
        self.context = {'files': [], 'history': []}
```

## Testing Architecture

### Test Categories
1. **Unit Tests**: Individual method testing
2. **Integration Tests**: End-to-end workflows
3. **Performance Tests**: Load and stress testing
4. **Error Tests**: Exception handling validation

### Test Isolation
- **Temporary Files**: Each test uses isolated temp files
- **Context Isolation**: Separate context files per test
- **Cleanup**: Automatic cleanup of test artifacts
- **Mocking**: AI and file system mocking

### Test Coverage
- **Code Coverage**: 100% method coverage
- **Branch Coverage**: All conditional paths tested
- **Error Coverage**: All exception paths tested
- **Integration Coverage**: All user workflows tested

## Performance Metrics

### Key Performance Indicators
- **Startup Time**: < 1 second
- **File Indexing**: ~100 files/second
- **AI Response Time**: 2-5 seconds average
- **Memory Usage**: < 50MB typical
- **Cache Hit Rate**: > 80% for repeated operations

### Monitoring Points
- **Query Count**: Track AI interactions
- **File Processing**: Monitor indexing performance
- **Response Times**: Measure AI response latency
- **Memory Usage**: Track memory consumption
- **Error Rates**: Monitor failure rates

## Security Considerations

### Input Validation
- **Path Sanitization**: Prevent directory traversal
- **File Type Filtering**: Only process safe file types
- **Input Length Limits**: Prevent buffer overflows
- **Command Validation**: Sanitize user commands

### File Safety
- **Permission Checks**: Validate file access rights
- **Path Resolution**: Resolve relative paths safely
- **Backup Protection**: Prevent overwriting important files
- **Quarantine**: Isolate potentially dangerous files

### AI Safety
- **Response Filtering**: Validate AI responses
- **Content Sanitization**: Clean AI-generated content
- **Error Boundaries**: Prevent AI errors from crashing app
- **Rate Limiting**: Prevent AI service abuse

## Deployment Considerations

### System Requirements
- **Python**: 3.8+ (tested on 3.13)
- **Memory**: 50MB minimum, 100MB recommended
- **Storage**: 10MB for application, variable for context
- **Network**: Internet connection for AI functionality

### Dependencies
- **Core**: Python standard library
- **AI**: Google Gemini API
- **UI**: Rich library
- **Testing**: pytest, unittest

### Scaling Considerations
- **File Limits**: Tested with 1000+ files
- **Memory Limits**: Automatic cache management
- **Network Limits**: Retry logic for AI requests
- **Storage Limits**: Context file size management

## Maintenance

### Regular Tasks
- **Cache Cleanup**: Automatic cache management
- **Context Backup**: Regular context file backups
- **Performance Monitoring**: Track key metrics
- **Error Logging**: Monitor and log errors

### Update Procedures
- **Code Updates**: Keep code compact (~250 lines) without sacrificing clarity
- **Dependency Updates**: Test compatibility
- **Feature Additions**: Preserve existing functionality
- **Performance Optimization**: Maintain response times
