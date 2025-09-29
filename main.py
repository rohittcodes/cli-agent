#!/usr/bin/env python3
import json, os, time, warnings, sys, re, subprocess, sqlite3, glob
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
        console.print("[dim]Starting MultiToolAIAgent...[/dim]")
        api_key = os.getenv('GEMINI_API_KEY', '')
        if not api_key:
            sys.exit("Error: Set GEMINI_API_KEY environment variable")
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash', generation_config={'temperature': 0.3, 'max_output_tokens': 4096})
            console.print("[dim]AI model ready: gemini-2.0-flash[/dim]")
        except Exception as e:
            sys.exit(f"Error initializing AI: {e}")
        self.context = {'files': [], 'history': [], 'db_path': 'agent.db'}
        self.stats = {'queries': 0, 'start_time': time.time(), 'ai_calls': 0, 'tool_calls': 0}
        self.tools = ['create_file', 'edit_file', 'read_file', 'list_files', 'analyze_code', 'web_search', 'web_fetch', 'db_query', 'db_create', 'git_init', 'git_status', 'git_commit', 'sys_exec', 'sys_info']
        self._load_session()
        console.print("[dim]Session loaded[/dim]")
        self._init_db()
        console.print("[dim]Database initialized[/dim]")
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
    def _find_file(self, filename):
        if os.path.exists(filename): return filename
        for pattern in [f"**/{filename}", f"*/{filename}", filename]:
            matches = glob.glob(pattern, recursive=True)
            if matches: return matches[0]
        return None
    def _call_ai(self, prompt, context=""):
        try:
            self.stats['ai_calls'] += 1
            if context:
                full_prompt = f"CONTEXT:\n{context}\n\nTOOLS: {', '.join(self.tools)}\n\n{prompt}"
            else:
                full_prompt = prompt
            response = self.model.generate_content(full_prompt)
            result = response.text.strip() if response.text else None
            return result if result else None
        except Exception as e:
            console.print(f"[yellow]AI error: {str(e)[:80]}[/yellow]")
            return None
    def _clean_code(self, code):
        if not code:
            return ''
        cleaned = re.sub(r'```(python|bash|sql)?\s*|\s*```', '', code, flags=re.MULTILINE)
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        return cleaned.strip()
    def _generate_code(self, description):
        prompt = f"Generate complete code for: {description}\nInclude imports, error handling, main block. Only code, no explanations:"
        code = self._call_ai(prompt)
        return self._clean_code(code) if code else 'print("Generation failed")'
    def _find_files(self, pattern=""):
        found = []
        for pattern_search in ["**/*", "*"]:
            for f in glob.glob(pattern_search, recursive=True):
                if os.path.isfile(f) and (not pattern or pattern.lower() in f.lower()):
                    found.append(f)
        return found[:20]
    def _web_search(self, query):
        try:
            response = self._call_ai(f"Provide comprehensive information about: {query}\nInclude key topics, resources, and detailed explanations.")
            return response or "No search results available"
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
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if operation == "query":
                cursor.execute(query or "SELECT * FROM logs ORDER BY id DESC LIMIT 5")
                results = [dict(row) for row in cursor.fetchall()]
                conn.close()
                return f"Query results ({len(results)} rows): {results[:3]}"
            elif operation == "create":
                cursor.execute(query or "CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, name TEXT, value TEXT)")
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
            console.print(f"[dim]Executing tool: {tool}[/dim]")
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
                found_file = self._find_file(name) if name else None
                if not found_file: result = f"File '{name}' not found"
                else:
                    content = self._read_file(found_file)
                    prompt = f"Modify: {params.get('changes')}\nCODE:\n{content}\nReturn complete modified code:"
                    new_content = self._clean_code(self._call_ai(prompt))
                    result = f"Updated {found_file}" if new_content and self._write_file(found_file, new_content) else "Failed to edit"
            elif tool == "read_file":
                name = params.get('filename')
                found_file = self._find_file(name) if name else None
                if found_file:
                    content = self._read_file(found_file)
                    result = f"=== {found_file} ===\n{content[:600]}" if content else "File empty"
                else:
                    result = f"File '{name}' not found"
            elif tool == "list_files":
                files = self._find_files(params.get('pattern', ''))
                result = f"Files: {', '.join(files)}" if files else "No files"
            elif tool == "analyze_code":
                name = params.get('filename', self.context.get('files', [''])[0] if self.context.get('files') else '')
                found_file = self._find_file(name) if name else None
                if found_file:
                    content = self._read_file(found_file)
                    analysis = self._call_ai(f"Analyze this code briefly:\n{content[:800]}")
                    result = analysis or "Analysis failed"
                else: result = "No file to analyze"
            elif tool == "web_search": result = self._web_search(params.get('query', 'default search'))
            elif tool == "web_fetch": result = self._web_fetch(params.get('url', 'https://httpbin.org/json'))
            elif tool == "db_query": result = self._db_operation('query', params.get('sql', ''))
            elif tool == "db_create": result = self._db_operation('create', params.get('sql', ''))
            elif tool == "git_init": result = self._git_operation('init')
            elif tool == "git_status": result = self._git_operation('status')
            elif tool == "git_commit": result = self._git_operation('commit')
            elif tool == "sys_exec": result = self._system_operation('exec', params.get('command', ''))
            elif tool == "sys_info": result = self._system_operation('info')
            else: result = f"Unknown tool: {tool}"
            self._log_action(f"{tool}({params})", result)
            return result
        except Exception as e:
            return f"Tool error: {str(e)[:50]}"
    def _intelligent_parse(self, user_input):
        context = f"Files: {', '.join(self.context.get('files', []))}\nHistory: {len(self.context.get('history', []))} items"
        prompt = f"Parse this request and return ONLY valid JSON:\nUser: {user_input}\nTools: {', '.join(self.tools)}\nContext: {context}\n\nReturn JSON: {{\"tools\": [{{\"name\": \"tool_name\", \"params\": {{\"key\": \"value\"}}}}]}}\n\nParameter names: edit_file uses 'filename' and 'changes', db_query uses 'sql', create_file uses 'filename' and 'description', read_file uses 'filename', web_search uses 'query', web_fetch uses 'url', sys_exec uses 'command'."
        response = self._call_ai(prompt)
        if response:
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                    parsed = json.loads(json_str)
                    return parsed.get('tools', [])
            except: pass
        return []
    def _process_request(self, user_input):
        if user_input.lower().strip() in ['exit', 'quit', 'q']: return "exit"
        self.stats['queries'] += 1
        self.context['history'] = self.context.get('history', [])
        self.context['history'].append(user_input)
        if len(self.context['history']) > 20: self.context['history'] = self.context['history'][-20:]
        tools_to_use = self._intelligent_parse(user_input)
        if not tools_to_use: return "AI could not parse request. Please rephrase or be more specific."
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
        console.print("[dim]Event loop started[/dim]")
        self._show_status()
        while True:
            try:
                user_input = Prompt.ask("\nCommand", default="").strip()
                if not user_input: continue
                if len(user_input) > 500: console.print("[yellow]Input too long (max 500 chars)[/yellow]"); continue
                result = self._process_request(user_input)
                if result == "exit": break
                if result: console.print(f"\n{result}\n")
                self._show_status()
                self._save_session()
            except KeyboardInterrupt: console.print("\nGoodbye!"); break
            except Exception as e:
                console.print(f"[red]Error: {str(e)[:100]}[/red]")
        self._save_session()
if __name__ == "__main__":
    MultiToolAIAgent().run()
