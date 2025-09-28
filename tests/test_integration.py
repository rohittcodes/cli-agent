#!/usr/bin/env python3
"""
Integration tests for the complete CLI application
"""
import unittest
import tempfile
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CodeAgent

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Create temporary context file
        self.temp_context = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({"files": [], "history": []}, self.temp_context)
        self.temp_context.close()
        
        self.agent = CodeAgent()
        self.agent.file = self.temp_context.name
    
    def tearDown(self):
        os.unlink(self.temp_context.name)
    
    def test_full_workflow_file_operations(self):
        """Test complete workflow: add files, create, delete"""
        # Create a separate context file for this test
        temp_context = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({"files": [], "history": []}, temp_context)
        temp_context.close()
        
        # Create a separate agent for this test
        test_agent = CodeAgent()
        test_agent.file = temp_context.name
        # Clear the context to start fresh
        test_agent.context = {'files': [], 'history': []}
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create test files
                test_file1 = os.path.join(temp_dir, "test1.py")
                test_file2 = os.path.join(temp_dir, "test2.py")
                
                with open(test_file1, 'w') as f: f.write("print('hello')")
                with open(test_file2, 'w') as f: f.write("print('world')")
                
                # Add files to context
                test_agent.add_context([test_file1, test_file2])
                self.assertEqual(len(test_agent.context['files']), 2)
            
                # Test file operations through tool execution
                result = test_agent._execute_single_tool("create_file", {"filename": "new_file.py", "content": "print('hello')"})
                self.assertIn("Created", result)
                
                # Clean up created file
                if os.path.exists("new_file.py"):
                    os.unlink("new_file.py")
                
                # Test search functionality
                result = test_agent._execute_single_tool("search_content", {"query": "print"})
                self.assertIsNotNone(result)
        finally:
            os.unlink(temp_context.name)
    
    def test_ai_task_workflow(self):
        """Test AI task execution workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f: f.write("def hello(): pass")
            
            self.agent.add_context([test_file])
            
            # Test AI tool routing
            with patch.object(self.agent, 'ask_with_context', return_value="AI response"):
                result = self.agent._ai_tool_route_command("analyze the code")
                self.assertIsNotNone(result)
            
            # Check context was updated
            self.assertGreater(len(self.agent.context['files']), 0)
    
    def test_file_gathering_workflow(self):
        """Test complete file gathering workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create various file types
            files_to_create = [
                "main.py",
                "test.py", 
                "config.json",
                "README.md"
            ]
            
            for filename in files_to_create:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f: f.write(f"# {filename}")
            
            # Test different file operations
            context_files = self.agent.list_files("", interactive=False, title="Context Files")
            search_files = self.agent.list_files("main", directory=temp_dir, interactive=False)
            browse_files = self.agent.list_files("", directory=temp_dir, interactive=False)
            
            # Verify results
            self.assertIsInstance(context_files, list)
            self.assertIsInstance(search_files, list)
            self.assertIsInstance(browse_files, list)
    
    def test_error_handling_workflow(self):
        """Test error handling in various scenarios"""
        # Test with non-existent files
        self.agent.add_context(["/nonexistent/file.py"])
        
        # Test search with empty context
        result = self.agent._execute_single_tool("search_content", {"query": "test"})
        self.assertIsNotNone(result)
        
        # Test file operations with invalid paths
        result1 = self.agent._execute_single_tool("delete_file", {"filename": "/nonexistent/file.py"})
        result2 = self.agent._execute_single_tool("create_file", {"filename": "/invalid/path/file.py", "content": "test"})
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)

if __name__ == '__main__':
    unittest.main()


