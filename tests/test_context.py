#!/usr/bin/env python3
"""
Unit tests for Context functionality within CodeAgent
"""
import unittest
import sys
import os
import tempfile
import json

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CodeAgent

class TestContext(unittest.TestCase):
    def setUp(self):
        # Create temporary context file
        self.temp_context = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({"files": [], "history": []}, self.temp_context)
        self.temp_context.close()
        
        self.agent = CodeAgent()
        self.agent.file = self.temp_context.name
    
    def tearDown(self):
        os.unlink(self.temp_context.name)
    
    def test_context_initialization(self):
        """Test context initializes with default values"""
        # Context may have files from the current directory, so just check structure
        self.assertIn('files', self.agent.context)
        self.assertIn('history', self.agent.context)
        self.assertIsInstance(self.agent.context['files'], list)
        self.assertIsInstance(self.agent.context['history'], list)
    
    def test_context_with_values(self):
        """Test context with provided values"""
        files = ["test1.py", "test2.py"]
        history = ["AI: test response"]
        self.agent.context['files'] = files
        self.agent.context['history'] = history
        self.assertEqual(self.agent.context['files'], files)
        self.assertEqual(self.agent.context['history'], history)
    
    def test_context_add_file(self):
        """Test adding file to context"""
        self.agent.context['files'].append("new_file.py")
        self.assertIn("new_file.py", self.agent.context['files'])
    
    def test_context_add_history(self):
        """Test adding to history"""
        self.agent.context['history'].append("AI: new response")
        self.assertIn("AI: new response", self.agent.context['history'])
    
    def test_context_persistence(self):
        """Test context persistence through auto-save"""
        # Create a separate context file for this test
        temp_context = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({"files": [], "history": []}, temp_context)
        temp_context.close()
        
        # Create a separate agent for this test
        test_agent = CodeAgent()
        test_agent.file = temp_context.name
        
        try:
            # Set test data
            test_agent.context['files'] = ["test.py"]
            test_agent.context['history'] = ["AI: test response"]
            
            # Auto-save
            test_agent._auto_save()
            
            # Create new agent and load from file
            new_agent = CodeAgent()
            new_agent.file = temp_context.name
            
            # Load the context from the file
            try:
                with open(temp_context.name, 'r') as f:
                    data = json.load(f)
                    new_agent.context = {'files': data.get('files', []), 'history': data.get('history', [])}
            except:
                pass
            
            # Should load the saved context
            self.assertEqual(new_agent.context['files'], ["test.py"])
            self.assertEqual(new_agent.context['history'], ["AI: test response"])
        finally:
            os.unlink(temp_context.name)
    
    def test_context_commands(self):
        """Test context-related commands"""
        try:
            # Test clear command
            self.agent.context['files'] = ["test.py"]
            self.agent._smart_route_command("clear")
            self.assertEqual(self.agent.context['files'], [])
            
            # Test context command
            self.agent.context['files'] = ["test1.py", "test2.py"]
            result = self.agent._smart_route_command("context")
            self.assertIsNotNone(result)
        finally:
            # Clean up any test files that might have been created
            for test_file in ["test.py", "test1.py", "test2.py"]:
                if os.path.exists(test_file):
                    os.unlink(test_file)

if __name__ == '__main__':
    unittest.main()

