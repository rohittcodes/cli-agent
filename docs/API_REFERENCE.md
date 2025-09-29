# AI Code Agent - API Reference

## MultiToolAIAgent Class

The main class that provides all functionality for the AI Code Agent.

### Constructor
```python
MultiToolAIAgent()
```
**Description**: Initializes the AI Code Agent with default configuration.

**Attributes**:
- `context`: Dictionary containing files and history
- `stats`: Dictionary with performance metrics
- `tools`: List of supported tool names

### Supported Tools
- `create_file`, `edit_file`, `read_file`, `list_files`
- `analyze_code`
- `web_search`, `web_fetch`
- `db_query`, `db_create`
- `git_init`, `git_status`, `git_commit`
- `sys_exec`, `sys_info`

---

## Core Methods

### File Operations

#### `get_file_content(filepath: str) -> str`
**Description**: Retrieves file content with LRU caching.

**Parameters**:
- `filepath` (str): Path to the file to read

**Returns**:
- `str`: File content or empty string if error

**Example**:
```python
content = agent.get_file_content("main.py")
```

#### `add_context(paths: List[str]) -> None`
**Description**: Adds files or directories to the context.

**Parameters**:
- `paths` (List[str]): List of file or directory paths

**Example**:
```python
agent.add_context(["src/", "main.py"])
```

#### `list_files(query: str = "", directory: str = ".", interactive: bool = True, title: str = "Files") -> List[str]`
**Description**: Lists files with optional filtering and interactive selection.

**Parameters**:
- `query` (str): Search query for filtering files
- `directory` (str): Directory to search (default: current directory)
- `interactive` (bool): Enable interactive file selection
- `title` (str): Title for the file list display

**Returns**:
- `List[str]`: List of file paths

**Example**:
```python
files = agent.list_files("*.py", interactive=False)
```

### Search Operations

#### `search_files(query: str, files: List[str]) -> List[str]`
**Description**: Searches for files by name or content.

**Parameters**:
- `query` (str): Search query
- `files` (List[str]): List of files to search

**Returns**:
- `List[str]`: List of matching file paths (max 20)

**Example**:
```python
matches = agent.search_files("test", all_files)
```

#### `search_content(query: str, files: List[str]) -> List[Tuple]`
**Description**: Searches for content within files.

**Parameters**:
- `query` (str): Content to search for
- `files` (List[str]): List of files to search

**Returns**:
- `List[Tuple]`: List of (filepath, line_number, line_content) tuples (max 50)

**Example**:
```python
results = agent.search_content("def main", context_files)
```

### AI Integration

#### `ask_stream(prompt: str, system: str = "") -> str`
**Description**: Sends a prompt to the AI with streaming response.

**Parameters**:
- `prompt` (str): User prompt
- `system` (str): System prompt for AI context

**Returns**:
- `str`: AI response or "Failed" if error

**Example**:
```python
response = agent.ask_stream("Analyze this code", "You are a code reviewer")
```

#### `ask_with_context(role: str, prompt: str, context_files: List[str] = None) -> str`
**Description**: AI response with file context and caching.

**Parameters**:
- `role` (str): AI role (e.g., "analyzer", "developer")
- `prompt` (str): User prompt
- `context_files` (List[str]): Files to include as context

**Returns**:
- `str`: AI response with context

**Example**:
```python
response = agent.ask_with_context("analyzer", "Review this code", ["main.py"])
```

### Performance and Statistics

#### `available() -> bool`
**Description**: Checks if AI service is available.

**Returns**:
- `bool`: True if AI service is reachable

**Example**:
```python
if agent.available():
    response = agent.ask_stream("Hello")
```

#### `_get_stats() -> str`
**Description**: Returns formatted performance statistics.

**Returns**:
- `str`: Formatted statistics string

**Example**:
```python
stats = agent._get_stats()
print(stats)  # "Stats: 15 files, 1250 lines, 8 history, 12 queries, 45.2s uptime"
```

### Context Management
### Startup Message
On initialization, the agent prints a brief console message: `Starting MultiToolAIAgent...` to indicate startup.

#### `_auto_save() -> None`
**Description**: Saves current context to persistent storage.

**Example**:
```python
agent._auto_save()
```

#### `_status() -> str`
**Description**: Displays current context status.

**Returns**:
- `str`: Status message

**Example**:
```python
status = agent._status()
```

---

## Tool Execution Methods

### `_execute_single_tool(tool_name: str, data: Dict = None) -> str`
**Description**: Executes a specific tool with given data.

**Parameters**:
- `tool_name` (str): Name of the tool to execute
- `data` (Dict): Tool-specific data

**Supported Tools**:

#### `create_file`
**Data**: `{"filename": str, "content": str}`
**Description**: Creates a new file with specified content.

#### `read_file`
**Data**: `{"filename": str}`
**Description**: Reads and returns file content.

#### `search_files`
**Data**: `{"query": str}`
**Description**: Searches for files matching query.

#### `search_content`
**Data**: `{"query": str}`
**Description**: Searches for content within context files.

#### `show_context`
**Data**: `{}`
**Description**: Displays current context files.

#### `clear_context`
**Data**: `{}`
**Description**: Clears all files from context.

#### `show_help`
**Data**: `{}`
**Description**: Displays help information.

#### `show_history`
**Data**: `{}`
**Description**: Displays AI interaction history.

#### `exit_program`
**Data**: `{}`
**Description**: Exits the application.

---

## Command Routing

### `_smart_route_command(user_input: str) -> str`
**Description**: Routes user commands to appropriate handlers.

**Parameters**:
- `user_input` (str): User command input

**Supported Commands**:
- `help`, `h` → Show help
- `context`, `files` → List context files
- `clear` → Clear context
- `history`, `hist` → Show history
- `stats` → Show statistics
- `save` → Manual save
- `export` → Export history
- `exit`, `quit`, `q` → Exit application
- `cls`, `clear screen` → Clear screen
- `chat "..."` → AI tool routing

**Example**:
```python
result = agent._smart_route_command("help")
result = agent._smart_route_command('chat "create a new file"')
```

---

## Internal Methods

### File System Operations

#### `_walk_files(directory: str = ".", include_hidden: bool = False) -> Generator[str]`
**Description**: Walks directory tree and yields file paths.

#### `_walk_dir(directory: str) -> Generator[str]`
**Description**: Walks directory and yields valid file paths.

### Indexing Operations

#### `build_index(files: List[str]) -> None`
**Description**: Builds file and content indexes.

#### `_quick_actions() -> Dict[str, Callable]`
**Description**: Returns dictionary of quick action functions.

---

## Data Structures

### Context Dictionary
```python
context = {
    'files': List[str],      # File paths in context
    'history': List[str]    # AI interaction history
}
```

### Performance Statistics
```python
performance_stats = {
    'queries': int,          # Number of AI queries
    'files_processed': int, # Files indexed
    'start_time': float     # Application start timestamp
}
```

### File Indexes
```python
file_index = Dict[str, float]           # filepath -> modification_time
content_index = Dict[str, Set[str]]     # word -> set of filepaths
```

---

## Usage Examples

### Basic File Operations
```python
from main import CodeAgent

# Initialize agent
agent = CodeAgent()

# Add files to context
agent.add_context(["src/", "main.py"])

# Search for files
files = agent.search_files("test", agent.context['files'])

# Search for content
results = agent.search_content("def main", agent.context['files'])

# Get file content
content = agent.get_file_content("main.py")
```

### AI Integration
```python
# Check if AI is available
if agent.available():
    # Simple AI query
    response = agent.ask_stream("What does this code do?")
    
    # AI query with context
    response = agent.ask_with_context(
        "analyzer", 
        "Review this code for issues", 
        ["main.py", "utils.py"]
    )
```

### Tool Execution
```python
# Create a file
result = agent._execute_single_tool("create_file", {
    "filename": "test.py",
    "content": "print('Hello, World!')"
})

# Read a file
result = agent._execute_single_tool("read_file", {
    "filename": "test.py"
})

# Search for content
result = agent._execute_single_tool("search_content", {
    "query": "print"
})
```

### Command Processing
```python
# Process user commands
result = agent._smart_route_command("help")
result = agent._smart_route_command("context")
result = agent._smart_route_command('chat "create a new file"')
```

---

## Configuration

### Environment Variables
- `OLLAMA_URL`: AI service endpoint (default: "http://localhost:11434")
- `CACHE_SIZE`: LRU cache size (default: 1000)
- `SCAN_INTERVAL`: File re-scan interval (default: 5 seconds)

### Context File
- **Location**: `agent_context.json`
- **Format**: JSON
- **Content**: Context files and history

---

## Error Handling

### Common Exceptions
- `FileNotFoundError`: File not found
- `PermissionError`: Access denied
- `ConnectionError`: AI service unavailable
- `JSONDecodeError`: Invalid context file

### Error Recovery
- **File Errors**: Skip problematic files, continue processing
- **AI Errors**: Fall back to file operations only
- **Network Errors**: Retry with exponential backoff
- **Context Errors**: Reset to default context
