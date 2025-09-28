#!/usr/bin/env python3
import json, requests, os, time, threading, re
from functools import lru_cache
from collections import defaultdict
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console(force_terminal=True, width=120)

class CodeAgent:
    def __init__(self):
        self.url, self.response_cache, self.last_health_check, self.is_available = "http://localhost:11434", {}, 0, False
        self.file_index, self.content_index, self.last_scan, self.scan_interval = {}, defaultdict(set), 0, 5
        self.file, self.context = 'agent_context.json', {'files': [], 'history': []}
        self.performance_stats = {'queries': 0, 'files_processed': 0, 'start_time': time.time()}
        try: self.context = {'files': json.load(open(self.file, 'r')).get('files', []), 'history': json.load(open(self.file, 'r')).get('history', [])}
        except: pass
        if self.context['files']: threading.Thread(target=lambda: self.build_index(self.context['files']), daemon=True).start() if not os.environ.get('PYTEST_CURRENT_TEST') else self.build_index(self.context['files'])
    
    def get_file_content(self, filepath: str) -> str:
        try: return open(filepath, 'r', encoding='utf-8').read()
        except: return ""
    
    def build_index(self, files: List[str]) -> None:
        if time.time() - self.last_scan <= self.scan_interval and self.file_index: return
        self.file_index.clear(); self.content_index.clear()
        for filepath in files:
            try: self.file_index[filepath] = os.stat(filepath).st_mtime; [self.content_index[word].add(filepath) for word in set(self.get_file_content(filepath).lower().split()) if len(word) > 2]
            except: continue
        self.last_scan = time.time()
    
    def search_files(self, query: str, files: List[str]) -> List[str]:
        return files if not query else [filepath for filepath in files if query.lower() in os.path.basename(filepath).lower() or any(word in self.content_index and filepath in self.content_index[word] for word in query.lower().split() if len(word) > 2)][:20]
    def search_content(self, query: str, files: List[str]) -> List[tuple]:
        if not query: return []
        query_lower, results = query.lower(), []
        for filepath in files:
            try: results.extend([(filepath, i, line.strip()) for i, line in enumerate(self.get_file_content(filepath).split('\n'), 1) if query_lower in line.lower()][:50-len(results)])
            except: continue
            if len(results) >= 50: break
        return results
    
    @lru_cache(maxsize=100)
    def available(self): 
        if time.time() - self.last_health_check < 10: return self.is_available
        try: self.is_available = requests.get(f"{self.url}/api/tags", timeout=2).status_code == 200; self.last_health_check = time.time(); return self.is_available
        except: self.is_available = False; self.last_health_check = time.time(); return False
    
    def ask_stream(self, prompt, system=""):
        r = requests.post(f"{self.url}/api/generate", json={'model': 'llama2:latest', 'prompt': prompt, 'system': system, 'stream': True})
        if r.status_code != 200: return "Failed"
        response, chunk_count, thinking_chars, thinking_idx, start_time = "", 0, ["🤖", "⚡", "🧠", "💭"], 0, time.time()
        for line in r.iter_lines():
            if not line: continue
            data = json.loads(line.decode('utf-8'))
            if 'response' in data:
                chunk = data['response']; response += chunk; chunk_count += 1
                if chunk_count == 1: console.print("\r" + " " * 50 + "\r", end="")
                print(chunk, end="", flush=True)
                if chunk_count % 3 == 0: time.sleep(0.02)
            elif not data.get('done', False) and chunk_count == 0:
                thinking_idx = (thinking_idx + 1) % len(thinking_chars)
                print(f"\r[dim]{thinking_chars[thinking_idx]} AI is thinking...[/dim]", end="", flush=True); time.sleep(0.1)
            if data.get('done', False): break
        if chunk_count > 0: console.print(f"\n[dim]✨ Generated {len(response)} chars in {chunk_count} chunks ({time.time() - start_time:.1f}s)[/dim]")
        return response
    
    def ask_with_context(self, role, prompt, context_files=None):
        context_tuple = tuple(sorted(context_files or []))
        cache_key = (role, hash(prompt), hash(context_tuple))
        if cache_key in self.response_cache and time.time() - self.response_cache[cache_key][1] < 300:
            console.print("[dim]Using cached response[/dim]"); return self.response_cache[cache_key][0]
        
        context = ""
        if context_files:
            for file_path in context_files[:5]:
                try: content = self.get_file_content(file_path); context += f"\n=== {os.path.basename(file_path)} ===\n{(content[:2000] + '\\n... [truncated]') if len(content) > 2000 else content}\n"
                except Exception as e: context += f"\n=== {os.path.basename(file_path)} ===\n[Error reading file: {e}]\n"
        
        system_prompt = f"You are an expert {role}. Analyze the provided files and give specific, actionable responses. Be precise and technical. When users ask you to create files, provide the EXACT content they requested. When users ask for code changes, provide the SPECIFIC changes needed. Always be helpful and solve the actual problem."
        full_prompt = f"{prompt}\n\nCodebase Context:\n{context}" if context else prompt
        response = self.ask_stream(full_prompt, system_prompt)
        
        if response != "Failed":
            self.response_cache[cache_key] = (response, time.time())
            if len(self.response_cache) > 50: del self.response_cache[min(self.response_cache.keys(), key=lambda k: self.response_cache[k][1])]
        return response
    
    def _walk_files(self, directory=".", include_hidden=False):
        ignore_dirs = {'__pycache__', 'node_modules', '.git', 'venv', 'env', '.venv', '.pytest_cache'}
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if include_hidden or (not d.startswith('.') and d not in ignore_dirs)]
            for f in files:
                if include_hidden or not f.startswith('.') and not f.endswith(('.pyc', '.pyo')): yield os.path.join(root, f)
    def list_files(self, query="", directory=".", interactive=True, title="Files"):
        files = self.context['files'] if query == "" and title == "Context Files" else (self.search_files(query, list(self._walk_files(directory))) if query else list(self._walk_files(directory)))
        if query: self.build_index(files)
        if not files: console.print("[yellow]No files found[/yellow]"); return []
        if interactive:
            console.print(f"[bold]{title} in {os.path.abspath(directory)}:[/bold]")
            [console.print(f"[{i}] {f}") for i, f in enumerate(files)]
            try: idx = input("Pick file # (or 'q' to quit): ").strip(); return [] if idx.lower() in ['q', 'quit', 'exit'] else [files[int(idx)]] if idx.isdigit() and (f := files[int(idx)]) else (console.print("[red]Invalid selection[/red]"), [])[1]
            except (ValueError, IndexError): console.print("[red]Invalid selection[/red]"); return []
        else: [console.print(f"[{i+1}] {file}") for i, file in enumerate(files)]; console.print(f"\n[dim]Total files: {len(files)}[/dim]"); return files
    
    def _walk_dir(self, directory):
        VALID_EXTS = ('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.sh', '.bat', '.ps1', '.sql', '.html', '.css', '.scss', '.less', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.md', '.txt')
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if not file.startswith('.') and file.endswith(VALID_EXTS): yield os.path.join(root, file)
    def add_context(self, paths):
        VALID_EXTS = ('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.sh', '.bat', '.ps1', '.sql', '.html', '.css', '.scss', '.less', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.md', '.txt')
        added_files = []
        for path in paths:
            if os.path.isfile(path):
                if path.endswith(VALID_EXTS) and path not in self.context['files']: self.context['files'].append(path); added_files.append(path)
            else: [self.context['files'].append(file_path) or added_files.append(file_path) for file_path in self._walk_dir(path) if file_path not in self.context['files']]
        if added_files:
            console.print(f"[green]Added {len(added_files)} files[/green]")
            [console.print(f"[dim]  - {os.path.basename(file)}[/dim]") for file in added_files[:3]]
            if len(added_files) > 3: console.print(f"[dim]  - ... and {len(added_files) - 3} more files[/dim]")
            threading.Thread(target=lambda: self.build_index(self.context['files']), daemon=True).start() if not os.environ.get('PYTEST_CURRENT_TEST') else self.build_index(self.context['files'])
    
    def _status(self): 
        status = f"[green]{len(self.context['files'])} files in context[/green]" if self.context['files'] else "[dim]No files in context[/dim]"
        if self.file_index: status += f" [dim](indexed: {len(self.file_index)})[/dim]"
        console.print(status); return status
    def _add_files_command(self):
        try: paths = input("Enter file/directory paths (comma-separated): ").strip().split(','); self.add_context([p.strip() for p in paths if p.strip()]); return "Files added to context"
        except: return "Error adding files"
    
    def _remove_files_command(self):
        try: 
            if not self.context['files']: return "No files in context to remove"
            console.print(f"[yellow]Current files in context:[/yellow]"); [console.print(f"[dim]{i}. {file}[/dim]") for i, file in enumerate(self.context['files'], 1)]
            indices = input("Enter file numbers to remove (comma-separated, e.g., 1,3,5): ").strip().split(',')
            removed = [self.context['files'].pop(idx) for idx in sorted([int(i.strip()) - 1 for i in indices if i.strip().isdigit()], reverse=True) if 0 <= idx < len(self.context['files'])]
            return f"Removed {len(removed)} files: {', '.join(removed)}" if removed else "No valid files to remove"
        except: return "Error removing files"
    def _auto_save(self): 
        with open(self.file, 'w') as f: json.dump(self.context, f)
    def _quick_actions(self): return {"create": lambda: self._add_files_command(), "search": lambda: self.list_files("", interactive=False), "analyze": lambda: self._ai_tool_route_command("analyze"), "help": lambda: self.show_help(), "context": lambda: self.list_files("", interactive=False, title="Context Files"), "history": lambda: self._show_history_tool(), "stats": lambda: console.print(self._get_stats()), "save": lambda: self._auto_save(), "export": lambda: (open('export.txt', 'w').write('\n'.join(self.context['history'])), console.print("[green]Exported to export.txt[/green]"), "Exported")[2], "clear": lambda: (self.context['files'].clear(), "Context cleared")[1], "exit": lambda: "exit"}
    def _get_stats(self):
        total_lines = sum(len(self.get_file_content(f).split('\n')) for f in self.context['files']); uptime = time.time() - self.performance_stats['start_time']
        return f"[dim]Stats: {len(self.context['files'])} files, {total_lines} lines, {len(self.context['history'])} history, {self.performance_stats['queries']} queries, {uptime:.1f}s uptime[/dim]"
    def _smart_route_command(self, user_input):
        if (user_input.startswith('chat "') and user_input.endswith('"')) or (user_input.startswith("chat '") and user_input.endswith("'")):
            return self._ai_tool_route_command(user_input[6:-1])
        commands = {
            'help': lambda: (self.show_help(), "Help displayed")[1], 'h': lambda: (self.show_help(), "Help displayed")[1],
            'context': lambda: self.list_files("", interactive=False, title="Context Files"), 'files': lambda: self.list_files("", interactive=False, title="Context Files"),
            'add': lambda: self._add_files_command(), 'add files': lambda: self._add_files_command(),
            'remove': lambda: self._remove_files_command(), 'remove files': lambda: self._remove_files_command(),
            'clear': lambda: (self.context['files'].clear(), "Context cleared")[1], 'clear context': lambda: (self.context['files'].clear(), "Context cleared")[1],
            'history': lambda: self._show_history_tool(), 'hist': lambda: self._show_history_tool(),
            'stats': lambda: (console.print(self._get_stats()), "Stats displayed")[1], 'save': lambda: (self._auto_save(), console.print("[green]Auto-saved![/green]"), "Saved")[2], 'export': lambda: (open('export.txt', 'w').write('\n'.join(self.context['history'])), console.print("[green]Exported to export.txt[/green]"), "Exported")[2],
            'exit': lambda: "exit", 'quit': lambda: "exit", 'q': lambda: "exit",
            'cls': lambda: (os.system('cls' if os.name == 'nt' else 'clear'), "Screen cleared")[1], 'clear screen': lambda: (os.system('cls' if os.name == 'nt' else 'clear'), "Screen cleared")[1]
        }
        result = commands.get(user_input.lower())
        return result() if result else (console.print("[yellow]Unknown command. Use 'help' for commands or 'chat \"your request\"' for AI assistance.[/yellow]"), "Unknown command")[1]
    def _ai_tool_route_command(self, user_input):
        self.performance_stats['queries'] += 1
        tools_description = """TOOLS: 1. create_file(filename, content) 2. read_file(filename) 3. edit_file(filename, content) 4. delete_file(filename) 5. search_files(query) 6. search_content(query) 7. list_directory(path) 8. add_to_context(files) 9. remove_from_context(files) 10. clear_context() 11. show_context() 12. analyze_code(files) 13. show_help() 14. show_history() 15. exit_program()"""
        routing_prompt = f"""Execute user requests using tools. TOOLS: {tools_description} REQUEST: "{user_input}" RULES: 1. Search CONTENT → search_content 2. Find FILES → search_files 3. Create file → create_file 4. Read file → read_file 5. Show help → show_help RESPOND WITH JSON: {{ "response": "I'll execute your request", "actions": [ {{ "tool": "tool_name", "data": {{"param1": "value1"}} }} ] }}"""
        ai_response = self.ask_with_context("tool router", routing_prompt, [])
        return self._execute_ai_tool_calls(ai_response, user_input)
    
    def _execute_ai_tool_calls(self, ai_response, user_input):
        try:
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if not json_match: return self._handle_direct_request(user_input, ai_response)
            try: response_data = json.loads(json_match.group(0))
            except json.JSONDecodeError as e: console.print(f"[red]Invalid JSON response: {e}[/red]"); return self._handle_direct_request(user_input, ai_response)
            user_response = response_data.get('response', '')
            if user_response: console.print(f"[dim]{user_response}[/dim]")
            actions = response_data.get('actions', [])
            results = [self._execute_single_tool(action.get('tool'), action.get('data', {})) for action in actions]
            if any(r == "exit" for r in results): return "exit"
            return "\n".join([r for r in results if r and r != "exit"]) if results else user_response
        except Exception as e: return f"Error executing tool calls: {e}. AI response: {ai_response}"
    
    def _handle_direct_request(self, user_input, ai_response):
        if any(word in user_input.lower() for word in ['create', 'make', 'new']) and any(ext in user_input.lower() for ext in ['.txt', '.py', '.js']):
            filename_match = re.search(r'(\w+\.\w+)', user_input)
            if filename_match:
                filename = filename_match.group(1)
                content = re.search(r'write\s+(.+?)(?:\s+in\s+it|$)', user_input, re.IGNORECASE)
                content = content.group(1).strip() if content else "Hello World"
                try:
                    with open(filename, 'w', encoding='utf-8') as f: f.write(content)
                    console.print(f"[green]Created {filename}[/green]")
                    self.add_context([filename])
                    return f"Created {filename} with content: {content}"
                except Exception as e: return f"Failed to create {filename}: {e}"
        return ai_response
    
    def _execute_single_tool(self, tool_name, data=None):
        try:
            if tool_name == "create_file":
                if not data: return "Error: create_file requires data (filename, content)"
                open(data.get('filename'), 'w', encoding='utf-8').write(data.get('content'))
                console.print(f"[green]Created {data.get('filename')}[/green]")
                self.add_context([data.get('filename')])
                return f"Created {data.get('filename')} with content: {data.get('content')}"
            elif tool_name == "read_file":
                if not data: return "Error: read_file requires data (filename)"
                return f"Contents of {data.get('filename')}:\n{open(data.get('filename'), 'r', encoding='utf-8').read()}"
            elif tool_name == "search_files":
                if not data: return "Error: search_files requires data (query)"
                query = data.get('query', '').lower()
                target_ext = '.py' if 'python' in query or 'py' in query else '.js' if 'javascript' in query or 'js' in query else None
                ignore_dirs = {'.venv', '__pycache__', '.git', 'node_modules', 'venv', 'env', '.pytest_cache'}
                found_files = [os.path.join(root, file) for root, dirs, files in os.walk(".") for file in files if not file.startswith('.') and not any(ignore in root for ignore in ignore_dirs) and (target_ext and file.endswith(target_ext) or not target_ext and query in file.lower())][:20]
                if found_files: self.add_context(found_files); return f"Found {len(found_files)} files matching '{data.get('query')}'"
                return f"No files found matching '{data.get('query')}'"
            elif tool_name == "search_content":
                if not data: return "Error: search_content requires data (query)"
                if not self.context['files']: return "No files in context to search"
                self.build_index(self.context['files']); matches = self.search_content(data.get('query'), self.context['files'])
                if matches: [console.print(f"[dim]{file_path}:{line_num}: {line_content}[/dim]") for file_path, line_num, line_content in matches[:5]]; console.print(f"[dim]... and {len(matches) - 5} more matches[/dim]") if len(matches) > 5 else None; return f"Found {len(matches)} matches for '{data.get('query')}' in context files"
                return f"No matches found for '{data.get('query')}' in context files"
            elif tool_name == "add_to_context":
                if not data: return "Error: add_to_context requires data (files)"
                files_list = data.get('files') if isinstance(data.get('files'), list) else [data.get('files')]
                self.add_context(files_list); return f"Added {len(files_list)} files to context"
            elif tool_name == "remove_from_context":
                if not data: return "Error: remove_from_context requires data (files)"
                files_list = data.get('files') if isinstance(data.get('files'), list) else [data.get('files')]
                removed = [f for f in files_list if f in self.context['files'] and self.context['files'].remove(f)]
                return f"Removed {len(removed)} files from context" if removed else "No matching files found in context"
            elif tool_name == "show_context": return self.list_files("", interactive=False, title="Context Files")
            elif tool_name == "clear_context": self.context['files'].clear(); return "Context cleared"
            elif tool_name == "show_help": self.show_help(); return "Help displayed"
            elif tool_name == "show_history":
                if self.context['history']: [console.print(f"[{i+1}] {h}") for i, h in enumerate(self.context['history'])]; return "History displayed"
                else: console.print("[yellow]No history[/yellow]"); return "No history available"
            elif tool_name == "exit_program": return "exit"
            else: return f"Unknown tool: {tool_name}"
        except Exception as e: return f"Error executing {tool_name}: {e}"
    
    def show_help(self):
        console.print("\n[bold cyan]AI Code Agent - Help Guide[/bold cyan]\n")
        [console.print(item) for item in ["chat \"request\" - AI tool routing", "context - List files", "add - Add files", "remove - Remove files", "clear - Clear context", "history - Show responses", "help - Show guide", "exit/quit - Quit", "\n[bold]Features:[/bold]", "Fast indexing, cached responses, smart compression", "\n[bold]Examples:[/bold]", 'chat "create test.py"', 'chat "search Python files"', 'chat "analyze main.py"']]
    
    def main_menu(self):
        console.print("[dim]Type 'help' for commands, or just start typing what you want to do[/dim]"); self._status()
        while True:
            try:
                user_input = Prompt.ask("AI", default="").strip()
                validations = [(not user_input, "[yellow]Type something or 'help' for commands. Try 'analyze' or 'chat'[/yellow]"), (any(pattern in user_input.lower() for pattern in ['rm ', 'del ', 'format ', 'fdisk ', 'mkfs']), "[red]Invalid input: Potentially dangerous command detected[/red]"), (len(user_input) > 1000, "[red]Invalid input: Input too long (max 1000 characters)[/red]")]
                for condition, message in validations:
                    if condition: console.print(message); break
                else:
                    result = self._smart_route_command(user_input)
                    if result == "exit": break
                    self._status()
            except KeyboardInterrupt: console.print("\n[yellow]Interrupted by user[/yellow]"); break
            except Exception as e: console.print(f"[red]Unexpected error: {e}[/red]"); continue
        self._auto_save()
    
    def run(self):
        console.print(Panel("AI CODE AGENT\nIntelligent Coding Assistant with Context Management", title="Welcome to Code Agent", style="bold cyan"))
        if not self.available() and not Confirm.ask("AI not detected. Install Ollama: https://ollama.ai\nContinue anyway?"): return
        try: self.main_menu()
        except KeyboardInterrupt: console.print("\n[yellow]Interrupted.[/yellow]")
        console.print("\nThanks for using Code Agent!")

if __name__ == "__main__": 
    CodeAgent().run()