#!/usr/bin/env python3
import json, os, time, warnings, sys, re, subprocess, sqlite3
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
warnings.filterwarnings("ignore")
try:
    import google.generativeai as genai
    import requests
except ImportError:
    sys.exit("Error: Install requirements: pip install google-generativeai requests")
console = Console(width=120)
class MultiToolAIAgent:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY', '')
        if not api_key:
            sys.exit("Error: Set GEMINI_API_KEY environment variable")
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash', generation_config={'temperature': 0.3, 'max_output_tokens': 4096})
        except Exception as e:
            sys.exit(f"Error initializing AI: {e}")
        self.context = {'files': [], 'history': [], 'db_path': 'agent.db'}
        self.stats = {'queries': 0, 'start_time': time.time(), 'ai_calls': 0, 'tool_calls': 0}
        self.tools = ['create_file', 'edit_file', 'read_file', 'list_files', 'analyze_code', 'web_search', 'web_fetch', 'db_query', 'db_create', 'git_init', 'git_status', 'git_commit', 'sys_exec', 'sys_info']
        self._load_session()
        self._init_db()
    def _load_session(self):
        try:
            self.context.update(json.load(open('session.json', 'r')))
        except: pass
    def _save_session(self):
        try:
            json.dump({k: v for k, v in self.context.items() if k != 'db_path'}, open('session.json', 'w'))
        except: pass
    def _init_db(self):
        try:
            conn = sqlite3.connect(self.context['db_path'])
            conn.execute('CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, timestamp TEXT, action TEXT, result TEXT)')
            conn.close()
        except: pass
    def _log_action(self, action, result):
        try:
            conn = sqlite3.connect(self.context['db_path'])
            conn.execute('INSERT INTO logs (timestamp, action, result) VALUES (?, ?, ?)', (time.strftime('%Y-%m-%d %H:%M:%S'), action, str(result)[:200]))
            conn.commit()
            conn.close()
        except: pass
    def _read_file(self, path):
        try:
            return open(path, 'r', encoding='utf-8').read()
        except: return ""
    def _write_file(self, path, content):
        try:
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            open(path, 'w', encoding='utf-8').write(content)
            return True
        except: return False
    def _call_ai(self, prompt, context=""):
        try:
            self.stats['ai_calls'] += 1
            full_prompt = f"CONTEXT:\n{context}\n\nTOOLS: {', '.join(self.tools)}\n\n{prompt}" if context else prompt
            result = self.model.generate_content(full_prompt).text.strip()
            return result if result else None
        except Exception as e:
            console.print(f"[yellow]AI error: {str(e)[:80]}[/yellow]")
            return None
    def _clean_code(self, code):
        return re.sub(r'```(python|bash|sql)?\s*|\s*```', '', code or '', flags=re.MULTILINE).strip()
    def _generate_code(self, description):
        prompt = f"Generate complete Python code for: {description}\nInclude imports, error handling, main block. Only code, no explanations:"
        code = self._call_ai(prompt)
        return self._clean_code(code) if code else 'print("Generation failed")'
    def _find_files(self, pattern=""):
        found = []
        for f in os.listdir('.'):
            if os.path.isfile(f) and (not pattern or pattern.lower() in f.lower()):
                found.append(f)
        return found[:20]
    def _web_search(self, query):
        try:
            search_term = self._call_ai(f"Generate a web search query for: {query}") or query
            return f"Search executed: {search_term[:100]}... (simulated web search)"
        except: return "Web search failed"
    def _web_fetch(self, url):
        try:
            response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            content = response.text[:1000]
            return f"Fetched {len(response.text)} chars from {url}\n{content}..."
        except Exception as e: return f"Failed to fetch {url}: {str(e)[:50]}"
    def _db_operation(self, operation, query=""):
        try:
            conn = sqlite3.connect(self.context['db_path'])
            if operation == "query":
                results = conn.execute(query or "SELECT * FROM logs ORDER BY id DESC LIMIT 5").fetchall()
                conn.close()
                return f"Query results: {results[:3]}"
            elif operation == "create":
                conn.execute(query or "CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, name TEXT, value TEXT)")
                conn.commit()
                conn.close()
                return "Table created successfully"
        except Exception as e: return f"DB error: {str(e)[:50]}"
    def _git_operation(self, operation):
        try:
            if operation == "init": result = subprocess.run(['git', 'init'], capture_output=True, text=True, timeout=5)
            elif operation == "status": result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True, timeout=5)
            elif operation == "commit":
                subprocess.run(['git', 'add', '.'], capture_output=True, timeout=5)
                result = subprocess.run(['git', 'commit', '-m', 'AI agent update'], capture_output=True, text=True, timeout=5)
            else: return f"Unknown git operation: {operation}"
            return f"Git {operation}: {result.stdout[:100] or result.stderr[:100] or 'completed'}"
        except Exception as e: return f"Git error: {str(e)[:50]}"
    def _system_operation(self, operation, command=""):
        try:
            if operation == "exec" and command:
                result = subprocess.run(command.split()[:3], capture_output=True, text=True, timeout=5)
                return f"Executed: {result.stdout[:200] or result.stderr[:200] or 'no output'}"
            elif operation == "info": return f"OS: {os.name}, CWD: {os.getcwd()}, Python: {sys.version[:20]}"
        except Exception as e: return f"System error: {str(e)[:50]}"
    def _execute_tool(self, tool, params):
        try:
            self.stats['tool_calls'] += 1
            result = ""
            if tool == "create_file":
                name = params.get('filename', 'script.py')
                desc = params.get('description', name)
                content = self._generate_code(desc)
                if self._write_file(name, content):
                    self.context['files'] = self.context.get('files', [])
                    if name not in self.context['files']: self.context['files'].append(name)
                    result = f"Created {name} ({len(content)} chars)"
            elif tool == "edit_file":
                name = params.get('filename')
                if not name or not os.path.exists(name): result = "File not found"
                else:
                    content = self._read_file(name)
                    prompt = f"Modify: {params.get('changes')}\nCODE:\n{content}\nReturn complete code:"
                    new_content = self._clean_code(self._call_ai(prompt))
                    result = f"Updated {name}" if new_content and self._write_file(name, new_content) else "Failed"
            elif tool == "read_file":
                name = params.get('filename')
                content = self._read_file(name)
                result = f"=== {name} ===\n{content[:600]}" if content else "File not found"
            elif tool == "list_files":
                files = self._find_files(params.get('pattern', ''))
                result = f"Files: {', '.join(files)}" if files else "No files"
            elif tool == "analyze_code":
                name = params.get('filename', self.context.get('files', [''])[0] if self.context.get('files') else '')
                content = self._read_file(name)
                if not content: result = "No file to analyze"
                else:
                    analysis = self._call_ai(f"Analyze this code briefly:\n{content[:800]}")
                    result = analysis or "Analysis failed"
            elif tool == "web_search":
                result = self._web_search(params.get('query', 'default search'))
            elif tool == "web_fetch":
                result = self._web_fetch(params.get('url', 'https://httpbin.org/json'))
            elif tool == "db_query":
                result = self._db_operation('query', params.get('sql', ''))
            elif tool == "db_create":
                result = self._db_operation('create', params.get('sql', ''))
            elif tool == "git_init":
                result = self._git_operation('init')
            elif tool == "git_status":
                result = self._git_operation('status')
            elif tool == "git_commit":
                result = self._git_operation('commit')
            elif tool == "sys_exec":
                result = self._system_operation('exec', params.get('command', ''))
            elif tool == "sys_info":
                result = self._system_operation('info')
            else:
                result = f"Unknown tool: {tool}"
            self._log_action(f"{tool}({params})", result)
            return result
        except Exception as e:
            return f"Tool error: {str(e)[:50]}"
    def _intelligent_parse(self, user_input):
        context = f"Files: {', '.join(self.context.get('files', []))}\nHistory: {len(self.context.get('history', []))} items"
        prompt = f"Parse this request and return JSON with tools to use:\nUser: {user_input}\nAvailable tools: {', '.join(self.tools)}\nContext: {context}\n\nReturn ONLY JSON format: {{\"tools\": [{{\"name\": \"tool_name\", \"params\": {{\"key\": \"value\"}}}}]}}"
        response = self._call_ai(prompt)
        if response:
            try:
                clean_response = self._clean_code(response)
                parsed = json.loads(clean_response)
                return parsed.get('tools', [])
            except: pass
        return self._fallback_parse(user_input)
    def _fallback_parse(self, user_input):
        actions, lower = [], user_input.lower()
        if 'create' in lower:
            if 'web scraper' in lower: actions.append({"name": "create_file", "params": {"filename": "web_scraper.py", "description": "web scraper with requests and beautifulsoup"}})
            elif 'api' in lower: actions.append({"name": "create_file", "params": {"filename": "api_client.py", "description": "REST API client with error handling"}})
            elif 'database' in lower: actions.append({"name": "create_file", "params": {"filename": "db_manager.py", "description": "database manager with SQLite operations"}})
            else: actions.append({"name": "create_file", "params": {"filename": "script.py", "description": user_input}})
        elif 'search' in lower and ('web' in lower or 'internet' in lower): actions.append({"name": "web_search", "params": {"query": user_input}})
        elif 'fetch' in lower or 'download' in lower: actions.append({"name": "web_fetch", "params": {"url": next((word for word in user_input.split() if 'http' in word), 'https://httpbin.org/json')}})
        elif 'git' in lower:
            if 'init' in lower: actions.append({"name": "git_init", "params": {}})
            elif 'status' in lower: actions.append({"name": "git_status", "params": {}})
            elif 'commit' in lower: actions.append({"name": "git_commit", "params": {}})
        elif 'database' in lower or 'db' in lower: actions.append({"name": "db_query" if 'query' in lower else "db_create", "params": {}})
        elif 'system' in lower or 'info' in lower: actions.append({"name": "sys_info", "params": {}})
        elif 'list' in lower and 'file' in lower: actions.append({"name": "list_files", "params": {}})
        elif 'analyze' in lower or 'explain' in lower: actions.append({"name": "analyze_code", "params": {}})
        return actions
    def _process_request(self, user_input):
        if user_input.lower().strip() in ['exit', 'quit', 'q']: return "exit"
        self.stats['queries'] += 1
        self.context['history'] = self.context.get('history', [])
        self.context['history'].append(user_input)
        if len(self.context['history']) > 20: self.context['history'] = self.context['history'][-20:]
        tools_to_use = self._intelligent_parse(user_input)
        if not tools_to_use: return "Could not parse request. Try: 'create web scraper', 'git status', 'search python tutorials'"
        results = []
        for tool_config in tools_to_use[:5]:
            tool_name = tool_config.get('name')
            tool_params = tool_config.get('params', {})
            if tool_name in self.tools:
                result = self._execute_tool(tool_name, tool_params)
                if result: results.append(f"[{tool_name}] {result}")
        return '\n\n'.join(results) if results else "Request processed"
    def _show_status(self):
        files = len(self.context.get('files', []))
        tools_used = self.stats.get('tool_calls', 0)
        console.print(f"{files} files | {self.stats['queries']} queries | AI: {self.stats['ai_calls']} | Tools: {tools_used}")
    def run(self):
        console.print(Panel(f"MULTI-TOOL AI AGENT v5.0\n{len(self.tools)} tools available\nIntelligent tool orchestration\n✓ AI & {len(self.tools)} tools ready", title="AI Agent Ready", style="bold magenta"))
        self._show_status()
        while True:
            try:
                user_input = Prompt.ask("\nCommand", default="").strip()
                if not user_input: continue
                if len(user_input) > 500:
                    console.print("[yellow]Input too long (max 500 chars)[/yellow]")
                    continue
                result = self._process_request(user_input)
                if result == "exit": break
                if result: console.print(f"\n{result}\n")
                self._show_status()
                self._save_session()
            except KeyboardInterrupt:
                console.print("\nGoodbye!")
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)[:100]}[/red]")
        self._save_session()
if __name__ == "__main__":
    MultiToolAIAgent().run()
