#!/usr/bin/env python3
import json, os, time, logging, warnings, sys
from functools import lru_cache
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Suppress warnings and logs
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)
os.environ.update({'GRPC_VERBOSITY': 'NONE', 'GLOG_minloglevel': '3', 'TF_CPP_MIN_LOG_LEVEL': '3'})
sys.stderr = open(os.devnull, 'w') if os.name != 'nt' else sys.stderr

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except:
    GENAI_AVAILABLE = False

console = Console(force_terminal=True, width=120)

class AICodeAgent:
    def __init__(self):
        self.model = None
        if GENAI_AVAILABLE:
            api_key = os.getenv('GEMINI_API_KEY', '')
            if api_key and api_key != 'your-api-key-here':
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-1.5-flash', generation_config={'temperature': 0.1, 'max_output_tokens': 1024})
                except: pass
        self.context = {'files': [], 'history': []}
        self.stats = {'queries': 0, 'start_time': time.time()}
        self._load_session()
        
    def _load_session(self):
        try: data = json.load(open('session.json', 'r')); self.context.update(data); self.context['files'] = self.context.get('files') or []
        except: pass
        
    def _save_session(self):
        try: json.dump(self.context, open('session.json', 'w'))
        except: pass
        
    def _read_file(self, path):
        try: return open(path, 'r', encoding='utf-8').read()
        except: return ""
    def _write_file(self, path, content):
        try:
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            open(path, 'w', encoding='utf-8').write(content)
            return True
        except Exception as e:
            console.print(f"[red]File write error: {e}[/red]")
            return False
        
    @lru_cache(maxsize=1)
    def _ai_available(self): return self.model is not None
    def _stream_ai(self, prompt):
        if not self._ai_available(): return None
        try: return self.model.generate_content(prompt).text.strip() or None
        except: return None
    def _find_files(self, pattern=""):
        found = []
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'__pycache__', 'node_modules', '.git', 'venv'}]
            for f in files:
                if not f.startswith('.') and not f.endswith(('.pyc', '.log')):
                    path = os.path.join(root, f).replace('\\', '/')
                    if not pattern or pattern.lower() in f.lower() or pattern.lower() in path.lower(): 
                        found.append(path)
                        if len(found) >= 20: return found
        return found
        
    def _search_in_files(self, query):
        results = []
        for fpath in self.context['files'][:10]:
            try:
                content = self._read_file(fpath)
                for i, line in enumerate(content.split('\n')[:50], 1):
                    if query.lower() in line.lower(): 
                        results.append((fpath, i, line.strip()[:80]))
                        if len(results) >= 15: return results
            except: continue
        return results
    
    def _get_code_templates(self, name):
        templates = {
            'downloader': 'import requests\nimport os\nfrom urllib.parse import urlparse\n\ndef download_file(url, folder="downloads"):\n    """Download a file from URL to specified folder"""\n    try:\n        os.makedirs(folder, exist_ok=True)\n        response = requests.get(url, stream=True, timeout=30)\n        response.raise_for_status()\n        \n        # Get filename from URL or use default\n        filename = os.path.basename(urlparse(url).path) or "downloaded_file"\n        filepath = os.path.join(folder, filename)\n        \n        with open(filepath, "wb") as f:\n            for chunk in response.iter_content(chunk_size=8192):\n                f.write(chunk)\n        \n        print(f"Downloaded: {filepath} ({os.path.getsize(filepath)} bytes)")\n        return filepath\n    except Exception as e:\n        print(f"Error downloading {url}: {e}")\n        return None\n\ndef download_multiple(urls, folder="downloads"):\n    """Download multiple files from URLs"""\n    results = []\n    for url in urls:\n        result = download_file(url, folder)\n        if result: results.append(result)\n    return results\n\nif __name__ == "__main__":\n    # Example usage\n    url = input("Enter URL to download: ")\n    if url:\n        download_file(url)\n    else:\n        # Example URLs for testing\n        test_urls = [\n            "https://httpbin.org/json",\n            "https://jsonplaceholder.typicode.com/posts/1"\n        ]\n        download_multiple(test_urls)',
            'scraper': 'import requests\nfrom bs4 import BeautifulSoup\nimport csv\n\ndef scrape_page(url):\n    """Scrape content from a webpage"""\n    try:\n        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}\n        response = requests.get(url, headers=headers, timeout=10)\n        response.raise_for_status()\n        soup = BeautifulSoup(response.content, "html.parser")\n        \n        # Extract common elements\n        data = {\n            "title": soup.title.text.strip() if soup.title else "No title",\n            "headings": [h.text.strip() for h in soup.find_all(["h1", "h2", "h3"])[:10]],\n            "links": [a.get("href") for a in soup.find_all("a", href=True)[:20]],\n            "text": soup.get_text(strip=True)[:1000]\n        }\n        return data\n    except Exception as e:\n        return {"error": str(e)}\n\ndef save_to_csv(data_list, filename="scraped_data.csv"):\n    """Save scraped data to CSV file"""\n    if not data_list: return\n    with open(filename, "w", newline="", encoding="utf-8") as f:\n        writer = csv.DictWriter(f, fieldnames=data_list[0].keys())\n        writer.writeheader()\n        writer.writerows(data_list)\n    print(f"Data saved to {filename}")\n\nif __name__ == "__main__":\n    url = input("Enter URL to scrape: ")\n    result = scrape_page(url)\n    print(f"Scraped data: {result}")',
            'calculator': 'import math\nimport re\n\ndef safe_calculate(expression):\n    """Safely evaluate mathematical expressions"""\n    # Remove spaces and validate characters\n    expr = re.sub(r"\\s+", "", expression)\n    allowed = set("0123456789+-*/().sincostan")\n    \n    if not all(c in allowed for c in expr.lower()):\n        return "Error: Invalid characters in expression"\n    \n    # Replace math functions\n    expr = expr.replace("sin", "math.sin")\n    expr = expr.replace("cos", "math.cos") \n    expr = expr.replace("tan", "math.tan")\n    \n    try:\n        result = eval(expr, {"__builtins__": {}, "math": math})\n        return f"{result:.6g}"\n    except Exception as e:\n        return f"Error: {str(e)}"\n\ndef calculator_interface():\n    """Interactive calculator interface"""\n    print("Advanced Calculator - Enter expressions or \'quit\' to exit")\n    print("Supports: +, -, *, /, (), sin, cos, tan, pi, e")\n    print("Examples: 2+2*3, sin(3.14159/2), sqrt(16)")\n    \n    while True:\n        try:\n            expr = input("\\n> ").strip()\n            if expr.lower() in ["quit", "exit", "q"]: break\n            if not expr: continue\n            \n            result = safe_calculate(expr)\n            print(f"Result: {result}")\n            \n        except KeyboardInterrupt:\n            print("\\nCalculator stopped.")\n            break\n\nif __name__ == "__main__":\n    calculator_interface()',
            'hello': 'print("Hello, World!")\nprint("Welcome to Python programming!")',
            'api': 'import requests\nimport json\nfrom datetime import datetime\n\ndef make_api_request(url, method="GET", headers=None, params=None, data=None):\n    """Make API request with error handling"""\n    try:\n        response = requests.request(\n            method=method,\n            url=url,\n            headers=headers or {"Content-Type": "application/json"},\n            params=params,\n            json=data,\n            timeout=10\n        )\n        response.raise_for_status()\n        return {\n            "success": True,\n            "status_code": response.status_code,\n            "data": response.json() if response.content else {},\n            "timestamp": datetime.now().isoformat()\n        }\n    except Exception as e:\n        return {\n            "success": False,\n            "error": str(e),\n            "timestamp": datetime.now().isoformat()\n        }\n\ndef test_api_endpoints():\n    """Test common API endpoints"""\n    endpoints = [\n        "https://httpbin.org/json",\n        "https://jsonplaceholder.typicode.com/posts/1",\n        "https://api.github.com/users/octocat"\n    ]\n    \n    for url in endpoints:\n        print(f"\\nTesting: {url}")\n        result = make_api_request(url)\n        print(json.dumps(result, indent=2))\n\nif __name__ == "__main__":\n    choice = input("Enter API URL or press Enter for tests: ").strip()\n    if choice:\n        result = make_api_request(choice)\n        print(json.dumps(result, indent=2))\n    else:\n        test_api_endpoints()',
            'server': 'from http.server import HTTPServer, BaseHTTPRequestHandler\nimport json\nimport urllib.parse as urlparse\n\nclass APIHandler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        """Handle GET requests"""\n        path = self.path\n        if path == "/":\n            self.send_response(200)\n            self.send_header("Content-type", "text/html")\n            self.end_headers()\n            self.wfile.write(b"<h1>Python HTTP Server</h1><p>Server is running!</p>")\n        elif path == "/api/status":\n            self.send_json_response({"status": "running", "message": "Server is healthy"})\n        elif path.startswith("/api/echo"):\n            query = urlparse.urlparse(path).query\n            params = urlparse.parse_qs(query)\n            self.send_json_response({"echo": params})\n        else:\n            self.send_error(404, "Not Found")\n    \n    def do_POST(self):\n        """Handle POST requests"""\n        content_length = int(self.headers.get("Content-Length", 0))\n        post_data = self.rfile.read(content_length).decode("utf-8")\n        try:\n            data = json.loads(post_data) if post_data else {}\n            self.send_json_response({"received": data, "method": "POST"})\n        except:\n            self.send_error(400, "Invalid JSON")\n    \n    def send_json_response(self, data):\n        """Send JSON response"""\n        self.send_response(200)\n        self.send_header("Content-type", "application/json")\n        self.send_header("Access-Control-Allow-Origin", "*")\n        self.end_headers()\n        self.wfile.write(json.dumps(data).encode())\n    \n    def log_message(self, format, *args):\n        """Suppress default logging"""\n        pass\n\ndef start_server(port=8000):\n    """Start the HTTP server"""\n    try:\n        server = HTTPServer(("localhost", port), APIHandler)\n        print(f"Server running at http://localhost:{port}")\n        print("Available endpoints:")\n        print(f"  GET  http://localhost:{port}/")\n        print(f"  GET  http://localhost:{port}/api/status")\n        print(f"  GET  http://localhost:{port}/api/echo?param=value")\n        print(f"  POST http://localhost:{port}/api/data")\n        print("Press Ctrl+C to stop")\n        server.serve_forever()\n    except KeyboardInterrupt:\n        print("\\nServer stopped")\n    except Exception as e:\n        print(f"Server error: {e}")\n\nif __name__ == "__main__":\n    start_server()'
        }
        
        for key, template in templates.items():
            if key in name.lower(): return template
        if name.endswith('.py'):
            return f'#!/usr/bin/env python3\n# {name}\n\ndef main():\n    print("Hello from {name}!")\n    pass\n\nif __name__ == "__main__":\n    main()'
        return f'# {name.title()}\nprint("File created successfully!")'
        
    def _execute_tool(self, tool, params):
        try:
            if tool == "create_file":
                name = params.get('filename') or params.get('name') or params.get('file') or 'script.py'
                content = params.get('content') or self._get_code_templates(name)
                
                if content.startswith('{"') and content.endswith('}'):
                    content = self._get_code_templates(name)
                
                if self._write_file(name, content):
                    if name not in self.context['files']: self.context['files'].append(name)
                    console.print(f"[green]✓ Created {name} ({len(content)} chars)[/green]")
                    return f"Successfully created {name} with {len(content)} characters"
                return "Failed to create file"
                
            elif tool == "read_file":
                name = params.get('filename') or params.get('name') or params.get('file', '')
                content = self._read_file(name)
                if content: return f"=== {name} ({len(content)} chars) ===\n{content[:800]}{'...' if len(content) > 800 else ''}"
                return "File not found"
                
            elif tool == "search_files":
                query = params.get('query', '')
                if not query: return "No search query provided"
                if 'python' in query.lower(): query = '.py'
                elif 'javascript' in query.lower(): query = '.js'
                elif 'html' in query.lower(): query = '.html'
                
                files = self._find_files(query)
                if files:
                    for f in files[:5]:
                        if f not in self.context['files']: self.context['files'].append(f)
                    result = f"Found {len(files)} files:\n" + '\n'.join(f"  • {f}" for f in files[:10])
                    if len(files) > 10: result += f"\n  ... and {len(files) - 10} more"
                    return result
                return f"No files found: {query}"
                
            elif tool == "search_content":
                query = params.get('query', '')
                matches = self._search_in_files(query)
                if matches: return f"Found {len(matches)} matches:\n" + '\n'.join(f"  {os.path.basename(path)}:{line} - {content}" for path, line, content in matches[:8])
                return "No matches found"
                
            elif tool == "show_context":
                if not self.context['files']: return "No files in context"
                return f"Context files ({len(self.context['files'])}):\n" + '\n'.join(f"  {i}. {os.path.basename(f)}" for i, f in enumerate(self.context['files'], 1))
                
            elif tool == "analyze_code":
                files = params.get('files', self.context['files'][:2])
                if isinstance(files, str): files = [files]
                content = ""
                for f in files[:2]:
                    file_content = self._read_file(f)
                    if file_content: content += f"\n=== {f} ===\n{file_content[:500]}\n"
                if not content: return "No files to analyze"
                
                if self._ai_available():
                    analysis = self._stream_ai(f"Analyze this code:\n\n{content}")
                    return analysis or "Code analysis completed"
                return f"Found {len(files)} files with {len(content)} characters"
                
            elif tool == "list_directory":
                directory = params.get('directory', '.')
                try:
                    items = [i for i in os.listdir(directory) if not i.startswith('.')]
                    dirs = [i for i in items if os.path.isdir(os.path.join(directory, i))][:8]
                    files = [i for i in items if os.path.isfile(os.path.join(directory, i))][:12]
                    result = f"Directory: {os.path.abspath(directory)}\n"
                    if dirs: result += f"Folders: {', '.join(dirs)}\n"
                    if files: result += f"Files: {', '.join(files)}"
                    return result
                except: return "Cannot access directory"
                
            elif tool == "add_context":
                files = params.get('files', [])
                if isinstance(files, str): files = [files]
                added = 0
                for f in files:
                    if os.path.exists(f) and f not in self.context['files']: self.context['files'].append(f); added += 1
                return f"Added {added} files to context"
                
            elif tool == "clear_context":
                count = len(self.context['files'])
                self.context['files'] = []
                return f"Cleared {count} files from context"
                
            elif tool == "show_stats":
                uptime = int(time.time() - self.stats['start_time'])
                return f"Agent Stats:\n• Files: {len(self.context['files'])}\n• Queries: {self.stats['queries']}\n• Uptime: {uptime}s\n• AI: {'Yes' if self._ai_available() else 'No'}"
                
            else: return f"Unknown tool: {tool}"
        except Exception as e: return f"Tool execution error: {str(e)}"
    def _simple_parse_request(self, user_input):
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['create', 'make', 'build', 'generate']):
            if 'download' in input_lower or 'url' in input_lower: return {"response": "Creating file downloader", "actions": [{"tool": "create_file", "params": {"filename": "file_downloader.py", "content": ""}}]}
            elif 'scraper' in input_lower or 'scrape' in input_lower:
                return {"response": "Creating web scraper", "actions": [{"tool": "create_file", "params": {"filename": "web_scraper.py", "content": ""}}]}
            elif 'calculator' in input_lower or 'calc' in input_lower:
                return {"response": "Creating calculator", "actions": [{"tool": "create_file", "params": {"filename": "calculator.py", "content": ""}}]}
            elif 'server' in input_lower or 'api' in input_lower:
                return {"response": "Creating HTTP server", "actions": [{"tool": "create_file", "params": {"filename": "http_server.py", "content": ""}}]}
            else:
                return {"response": "Creating Python script", "actions": [{"tool": "create_file", "params": {"filename": "script.py", "content": ""}}]}
        
        elif 'read' in input_lower or 'show' in input_lower:
            if 'context' in input_lower: return {"response": "Showing context", "actions": [{"tool": "show_context", "params": {}}]}
            elif 'stats' in input_lower: return {"response": "Showing statistics", "actions": [{"tool": "show_stats", "params": {}}]}
            elif 'directory' in input_lower or 'folder' in input_lower: return {"response": "Listing directory", "actions": [{"tool": "list_directory", "params": {}}]}
        
        elif 'find' in input_lower or 'search' in input_lower:
            if 'python' in input_lower: return {"response": "Finding Python files", "actions": [{"tool": "search_files", "params": {"query": ".py"}}]}
            elif 'javascript' in input_lower: return {"response": "Finding JavaScript files", "actions": [{"tool": "search_files", "params": {"query": ".js"}}]}
            elif 'files' in input_lower: return {"response": "Finding files", "actions": [{"tool": "search_files", "params": {"query": ""}}]}
        
        elif 'analyze' in input_lower or 'review' in input_lower:
            return {"response": "Analyzing code", "actions": [{"tool": "analyze_code", "params": {}}]}
        
        return {"response": "Processing request", "actions": [{"tool": "list_directory", "params": {}}]}
            
    def _process_request(self, user_input):
        if user_input.lower().strip() in ['exit', 'quit', 'q']: return "exit"
        self.stats['queries'] += 1
        
        if self._ai_available():
            prompt = f'Parse this request into JSON format with response message and tool actions. ONLY return valid JSON, no extra text or markdown:\n\nUSER: "{user_input}"\n\nTOOLS: create_file, read_file, search_files, search_content, analyze_code, show_context, list_directory, add_context, clear_context, show_stats\n\nJSON FORMAT:\n{{"response": "brief message", "actions": [{{"tool": "tool_name", "params": {{"key": "value"}}}}]}}\n\nUSER REQUEST: {user_input}'
            
            ai_response = self._stream_ai(prompt)
            if ai_response:
                try:
                    cleaned = ai_response.strip()
                    if cleaned.startswith('```json'): cleaned = cleaned[7:]
                    if cleaned.endswith('```'): cleaned = cleaned[:-3]
                    cleaned = cleaned.strip()
                    
                    start = cleaned.find('{')
                    end = cleaned.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = cleaned[start:end]
                        data = json.loads(json_str)
                        if not isinstance(data.get('actions'), list):
                            data = self._simple_parse_request(user_input)
                    else:
                        data = self._simple_parse_request(user_input)
                except:
                    data = self._simple_parse_request(user_input)
            else:
                data = self._simple_parse_request(user_input)
        else:
            data = self._simple_parse_request(user_input)
        
        message = data.get('response', 'Processing request...')
        console.print(f"[dim blue]{message}[/dim blue]")
        
        actions = data.get('actions', [])
        results = []
        for action in actions[:3]:
            tool = action.get('tool')
            params = action.get('params', {})
            if tool:
                result = self._execute_tool(tool, params)
                if result: results.append(result)
        
        if results: self.context['history'].append(f"{user_input[:50]} -> {len(actions)} actions")
        return '\n\n'.join(results) if results else "Request processed"
        
    def _show_status(self):
        ctx = f"[green]{len(self.context['files'])} files[/green]" if self.context['files'] else "[dim]No files[/dim]"
        if self.stats['queries'] > 0: ctx += f" [dim]| 🔍 {self.stats['queries']} queries[/dim]"
        console.print(ctx)
        
    def run(self):
        console.print(Panel("AI CODE AGENT v2.1\nIntelligent coding assistant with natural language interface\nFixed warnings and improved file creation", title="Welcome", style="bold cyan"))
        console.print("[dim]Examples: 'create file downloader', 'make web scraper', 'build calculator', 'show files'[/dim]")
        if not self._ai_available(): console.print("[yellow]AI mode unavailable - using rule-based parsing (set GEMINI_API_KEY for full features)[/yellow]")
        self._show_status()
        
        while True:
            try:
                user_input = Prompt.ask("Assistant", default="").strip()
                if not user_input: console.print("[yellow]Try: 'create downloader', 'find python files', 'show directory', 'make calculator'[/yellow]"); continue
                if len(user_input) > 200: console.print("[red]Input too long - keep under 200 characters[/red]"); continue
                
                result = self._process_request(user_input)
                if result == "exit": break
                if result: console.print(f"\n{result}\n")
                self._show_status()
                self._save_session()
                
            except KeyboardInterrupt: console.print("\n[yellow]Goodbye![/yellow]"); break
            except Exception as e: console.print(f"[red]Unexpected error: {str(e)}[/red]")
        self._save_session()

if __name__ == "__main__": AICodeAgent().run()