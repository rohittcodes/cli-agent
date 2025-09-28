# AI Code Agent - User Guide

## Getting Started

### Quick Start
1. **Get Gemini API Key**: Visit [Google AI Studio](https://aistudio.google.com/) and get your API key
2. **Set Environment Variable**: `export GEMINI_API_KEY=your-api-key-here`
3. **Start the Agent**: Run `uv run python main.py`
4. **Start Coding**: Type `help` to see available commands

### First Steps
```bash
# Start the agent
uv run python main.py

# See available commands
help

# Add your project to context
context

# Ask AI for help
analyze my code structure
```

---

## Basic Commands

### Essential Commands

#### `help` or `h`
Shows all available commands and their descriptions.

**Example**:
```bash
AI> help
```

#### `context` or `files`
Lists all files currently in your context.

**Example**:
```bash
AI> context
```

#### `clear`
Removes all files from your context.

**Example**:
```bash
AI> clear
```

#### `exit`, `quit`, or `q`
Exits the application.

**Example**:
```bash
AI> exit
```

---

## AI Commands

### Chat with AI
Use natural language to interact with the AI assistant.

**Examples**:
```bash
# Analyze code
AI> analyze the main.py file

# Create new files
AI> create a new file test.py with a hello world function

# Search for content
AI> search for all functions that start with 'def'

# Get help with debugging
AI> help me debug this error in my code
```

### AI Capabilities
- **Code Analysis**: Understand and explain code
- **File Creation**: Generate new files with content
- **Code Search**: Find specific patterns or functions
- **Debugging**: Help identify and fix issues
- **Refactoring**: Suggest code improvements
- **Documentation**: Generate code documentation

---

## File Management

### Adding Files to Context

#### Add Individual Files
```bash
# The agent will automatically add files when you reference them
AI> analyze main.py
```

#### Add Directories
```bash
# Add entire directories to context
AI> add all Python files in src/ directory
```

### File Operations

#### Create Files
```bash
AI> create a new file utils.py with helper functions
AI> create a config.json file with database settings
```

#### Read Files
```bash
AI> show me the content of main.py
AI> read the README.md file
```

#### Search Files
```bash
AI> find all Python files
AI> search for files containing 'database'
```

#### Search Content
```bash
AI> search for all functions named 'main'
AI> find all imports in the codebase
```

---

## Advanced Features

### Performance Monitoring

#### View Statistics
```bash
AI> stats
# Output: Stats: 15 files, 1250 lines, 8 history, 12 queries, 45.2s uptime
```

#### Manual Save
```bash
AI> save
# Saves current context and shows confirmation
```

#### Export History
```bash
AI> export
# Exports conversation history to export.txt
```

### Context Management

#### View Context Status
The agent automatically shows context status:
```
[green]15 files in context[/green] [dim](indexed: 12)[/dim]
```

#### Clear Context
```bash
AI> clear
# Removes all files from context
```

#### View History
```bash
AI> history
# Shows last 5 AI interactions
```

---

## Common Workflows

### 1. Project Analysis
```bash
# Start with your project
AI> analyze the structure of my project

# Get specific insights
AI> find all the main functions in my code
AI> identify potential issues in my code
```

### 2. Code Generation
```bash
# Create new files
AI> create a new API endpoint for user authentication
AI> generate a test file for my main functions
AI> create a configuration file for my application
```

### 3. Debugging
```bash
# Get help with errors
AI> help me fix this error: 'NameError: name 'x' is not defined'
AI> debug this function that's not working correctly
```

### 4. Code Review
```bash
# Review your code
AI> review this code for best practices
AI> suggest improvements for this function
AI> check for security issues in my code
```

### 5. Documentation
```bash
# Generate documentation
AI> create documentation for my API
AI> generate comments for this complex function
AI> create a README for my project
```

---

## Tips and Best Practices

### Effective AI Interactions

#### Be Specific
```bash
# Good: Specific request
AI> create a function that calculates fibonacci numbers with memoization

# Less effective: Vague request
AI> help me with math
```

#### Provide Context
```bash
# Good: With context
AI> analyze the authentication system in my Flask app

# Less effective: Without context
AI> analyze authentication
```

#### Use Follow-up Questions
```bash
AI> create a user model
AI> now add validation to that model
AI> create tests for the validation
```

### File Management Tips

#### Keep Context Focused
- Add only relevant files to context
- Clear context when switching projects
- Use specific file references

#### Use Descriptive Names
- Name files clearly
- Use consistent naming conventions
- Organize files in logical directories

### Performance Tips

#### Monitor Usage
- Check stats regularly with `stats`
- Export history periodically with `export`
- Clear context when not needed

#### Optimize Queries
- Be specific in AI requests
- Use targeted searches
- Avoid overly broad queries

---

## Troubleshooting

### Common Issues

#### AI Not Responding
```bash
# Check if Gemini API key is set
AI> stats
# If no AI available, check your GEMINI_API_KEY environment variable
```

#### Files Not Found
```bash
# Check your context
AI> show context

# Add files to context
AI> add main.py to context
```

#### Slow Performance
```bash
# Check statistics
AI> stats

# Clear context if too many files
AI> clear
```

### Error Messages

#### "AI not detected"
- Get Gemini API key: [Google AI Studio](https://aistudio.google.com/)
- Set environment variable: `export GEMINI_API_KEY=your-api-key-here`
- Restart the agent

#### "No files in context"
- Add files: `AI> add my project files`
- Check context: `AI> show context`

#### "Invalid selection"
- Use valid file numbers
- Check available files with `context`

---

## Advanced Usage

### Custom Workflows

#### Project Setup
```bash
# 1. Add project to context
AI> add all files in my project directory

# 2. Analyze structure
AI> analyze my project structure and suggest improvements

# 3. Generate missing files
AI> create any missing configuration files
```

#### Code Review Process
```bash
# 1. Add code to context
AI> add the files I want reviewed

# 2. Get comprehensive review
AI> review this code for bugs, performance, and best practices

# 3. Address issues
AI> help me fix the issues you found
```

#### Documentation Generation
```bash
# 1. Add source files
AI> add my source code files

# 2. Generate documentation
AI> create comprehensive documentation for my API

# 3. Export results
AI> export conversation history
```

### Integration with Development Tools

#### Git Integration
```bash
# Analyze changes
AI> analyze the changes in my git diff

# Generate commit messages
AI> generate a commit message for my changes
```

#### Testing
```bash
# Generate tests
AI> create unit tests for my functions

# Analyze test coverage
AI> analyze my test coverage and suggest improvements
```

---

## Examples

### Example 1: Web Application
```bash
# Start with project analysis
AI> analyze my Flask web application

# Get specific insights
AI> find all the routes in my application
AI> identify security issues in my code

# Generate improvements
AI> create a better error handling system
AI> add input validation to my forms
```

### Example 2: Data Analysis
```bash
# Analyze data processing code
AI> review my data analysis pipeline

# Optimize performance
AI> suggest optimizations for my data processing

# Generate visualizations
AI> create code for data visualization
```

### Example 3: API Development
```bash
# Design API structure
AI> design a REST API for my application

# Implement endpoints
AI> create the user authentication endpoints

# Add documentation
AI> generate API documentation
```

---

## Conclusion

The AI Code Agent is a powerful tool that can significantly enhance your development workflow. By following this guide and practicing with the examples, you'll be able to:

- **Analyze** your codebase effectively
- **Generate** new code and files
- **Debug** issues quickly
- **Document** your projects
- **Optimize** your development process

Remember to experiment with different commands and workflows to find what works best for your specific needs. The AI is designed to be helpful and responsive, so don't hesitate to ask questions or request assistance with your coding tasks.

Happy coding!
