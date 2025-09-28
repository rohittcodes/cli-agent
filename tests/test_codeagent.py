#!/usr/bin/env python3
"""
Unit tests for CodeAgent class functionality
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

class TestCodeAgent(unittest.TestCase):
    def setUp(self):
        # Create temporary context file
        self.temp_context = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({"files": [], "history": []}, self.temp_context)
        self.temp_context.close()
        
        self.agent = CodeAgent()
        self.agent.file = self.temp_context.name
    
    def tearDown(self):
        os.unlink(self.temp_context.name)
    
    def test_codeagent_initialization(self):
        """Test CodeAgent initializes correctly"""
        self.assertIsInstance(self.agent.context, dict)
        self.assertIn('files', self.agent.context)
        self.assertIn('history', self.agent.context)
        self.assertIsNotNone(self.agent.performance_stats)
    
    def test_list_files_context_mode(self):
        """Test list_files in context mode"""
        self.agent.context['files'] = ["test1.py", "test2.py"]
        result = self.agent.list_files("", interactive=False, title="Context Files")
        self.assertEqual(len(result), 2)
    
    def test_list_files_search_mode(self):
        """Test list_files in search mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_file.py")
            with open(test_file, 'w') as f:
                f.write("test content")
            
            result = self.agent.list_files("test", directory=temp_dir, interactive=False)
            self.assertIn(test_file, result)
    
    def test_list_files_browse_mode(self):
        """Test list_files in browse mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("test")
            
            result = self.agent.list_files("", directory=temp_dir, interactive=False)
            self.assertIn(test_file, result)
    
    def test_walk_files_basic(self):
        """Test _walk_files method"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("test")
            
            files = list(self.agent._walk_files(temp_dir))
            self.assertIn(test_file, files)
    
    def test_walk_files_ignore_dirs(self):
        """Test _walk_files ignores specified directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create ignored directory
            ignored_dir = os.path.join(temp_dir, "__pycache__")
            os.makedirs(ignored_dir)
            ignored_file = os.path.join(ignored_dir, "test.py")
            with open(ignored_file, 'w') as f:
                f.write("test")
            
            files = list(self.agent._walk_files(temp_dir))
            self.assertNotIn(ignored_file, files)
    
    def test_add_context_single_file(self):
        """Test adding single file to context"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            test_file = f.name
            f.write("test content")
        
        try:
            self.agent.add_context([test_file])
            self.assertIn(test_file, self.agent.context['files'])
        finally:
            os.unlink(test_file)
    
    def test_add_context_directory(self):
        """Test adding directory to context"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("test")
            
            self.agent.add_context([temp_dir])
            self.assertIn(test_file, self.agent.context['files'])
    
    def test_status_with_files(self):
        """Test _status method with files in context"""
        self.agent.context['files'] = ["test1.py", "test2.py"]
        with patch('rich.console.Console.print') as mock_print:
            result = self.agent._status()
            mock_print.assert_called()
            self.assertIn("2 files in context", result)
    
    def test_status_without_files(self):
        """Test _status method without files"""
        self.agent.context['files'] = []
        with patch('rich.console.Console.print') as mock_print:
            result = self.agent._status()
            mock_print.assert_called()
            self.assertIn("No files in context", result)
    
    def test_auto_save_functionality(self):
        """Test auto-save functionality"""
        self.agent.context['files'] = ["test.py"]
        self.agent.context['history'] = ["test history"]
        
        try:
            # Should not raise an exception
            self.agent._auto_save()
            
            # Verify file was written
            with open(self.agent.file, 'r') as f:
                saved_data = json.load(f)
                self.assertEqual(saved_data['files'], ["test.py"])
                self.assertEqual(saved_data['history'], ["test history"])
        finally:
            # Clean up any test.py file that might have been created
            if os.path.exists("test.py"):
                os.unlink("test.py")
    
    def test_stats_functionality(self):
        """Test statistics functionality"""
        self.agent.context['files'] = ["test.py"]
        self.agent.context['history'] = ["test1", "test2"]
        
        try:
            stats = self.agent._get_stats()
            self.assertIn("1 files", stats)
            self.assertIn("2 history", stats)
            self.assertIn("queries", stats)
            self.assertIn("uptime", stats)
        finally:
            # Clean up any test.py file that might have been created
            if os.path.exists("test.py"):
                os.unlink("test.py")
    
    def test_export_functionality(self):
        """Test export functionality"""
        self.agent.context['history'] = ["test1", "test2", "test3"]
        
        try:
            # Test export command
            with patch('rich.console.Console.print') as mock_print:
                result = self.agent._smart_route_command("export")
                mock_print.assert_called()
                self.assertEqual(result, "Exported")
        finally:
            # Clean up export.txt if it was created
            if os.path.exists("export.txt"):
                os.unlink("export.txt")

if __name__ == '__main__':
    unittest.main()

