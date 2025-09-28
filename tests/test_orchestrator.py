#!/usr/bin/env python3
"""
Unit tests for tool execution functionality within CodeAgent
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

class TestToolExecution(unittest.TestCase):
    def setUp(self):
        # Create temporary context file
        self.temp_context = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({"files": [], "history": []}, self.temp_context)
        self.temp_context.close()
        
        self.agent = CodeAgent()
        self.agent.file = self.temp_context.name
    
    def tearDown(self):
        os.unlink(self.temp_context.name)
    
    def test_tool_execution_create_file(self):
        """Test create_file tool execution"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_file = f.name
        
        try:
            result = self.agent._execute_single_tool("create_file", {"filename": test_file, "content": "test content"})
            self.assertIn("Created", result)
            with open(test_file, 'r') as f:
                self.assertEqual(f.read(), "test content")
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def test_tool_execution_read_file(self):
        """Test read_file tool execution"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            test_file = f.name
        
        try:
            result = self.agent._execute_single_tool("read_file", {"filename": test_file})
            self.assertIn("Contents of", result)
            self.assertIn("test content", result)
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def test_tool_execution_search_files(self):
        """Test search_files tool execution"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("test content")
            
            result = self.agent._execute_single_tool("search_files", {"query": "test"})
            self.assertIn("Found", result)
    
    def test_tool_execution_search_content(self):
        """Test search_content tool execution"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test line\nother line")
            test_file = f.name
        
        try:
            self.agent.context['files'] = [test_file]
            result = self.agent._execute_single_tool("search_content", {"query": "test"})
            self.assertIn("Found", result)
        finally:
            os.unlink(test_file)
    
    def test_tool_execution_show_context(self):
        """Test show_context tool execution"""
        self.agent.context['files'] = ["test1.py", "test2.py"]
        result = self.agent._execute_single_tool("show_context", {})
        self.assertIsNotNone(result)
    
    def test_tool_execution_clear_context(self):
        """Test clear_context tool execution"""
        self.agent.context['files'] = ["test1.py", "test2.py"]
        result = self.agent._execute_single_tool("clear_context", {})
        self.assertEqual(result, "Context cleared")
        self.assertEqual(self.agent.context['files'], [])
    
    def test_tool_execution_show_help(self):
        """Test show_help tool execution"""
        with patch('rich.console.Console.print') as mock_print:
            result = self.agent._execute_single_tool("show_help", {})
            self.assertEqual(result, "Help displayed")
            mock_print.assert_called()
    
    def test_tool_execution_show_history(self):
        """Test show_history tool execution"""
        self.agent.context['history'] = ["AI: test response"]
        with patch('rich.console.Console.print') as mock_print:
            result = self.agent._execute_single_tool("show_history", {})
            self.assertEqual(result, "History displayed")
            mock_print.assert_called()
    
    def test_tool_execution_unknown_tool(self):
        """Test execution of unknown tool"""
        result = self.agent._execute_single_tool("unknown_tool", {})
        self.assertIn("Unknown tool", result)
    
    def test_tool_execution_error_handling(self):
        """Test tool execution error handling"""
        # Test with invalid data
        result = self.agent._execute_single_tool("create_file", {})
        self.assertIn("Error", result)
    
    def test_smart_route_command_basic_commands(self):
        """Test smart routing for basic commands"""
        # Test help command
        result = self.agent._smart_route_command("help")
        self.assertIsNotNone(result)
        
        # Test context command
        result = self.agent._smart_route_command("context")
        self.assertIsNotNone(result)
        
        # Test clear command
        self.agent.context['files'] = ["test.py"]
        result = self.agent._smart_route_command("clear")
        self.assertEqual(self.agent.context['files'], [])
    
    def test_smart_route_command_unknown(self):
        """Test smart routing for unknown commands"""
        with patch('rich.console.Console.print') as mock_print:
            result = self.agent._smart_route_command("unknown_command")
            self.assertEqual(result, "Unknown command")
            mock_print.assert_called()

if __name__ == '__main__':
    unittest.main()

