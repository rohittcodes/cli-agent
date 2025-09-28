#!/usr/bin/env python3
"""
Unit tests for new features: auto-save, stats, export, performance tracking
"""
import unittest
import tempfile
import os
import sys
import json
import time
from unittest.mock import patch, MagicMock

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CodeAgent

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        # Create temporary context file
        self.temp_context = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({"files": [], "history": []}, self.temp_context)
        self.temp_context.close()
        
        self.agent = CodeAgent()
        self.agent.file = self.temp_context.name
    
    def tearDown(self):
        os.unlink(self.temp_context.name)
    
    def test_performance_stats_initialization(self):
        """Test performance stats are initialized correctly"""
        self.assertIn('queries', self.agent.performance_stats)
        self.assertIn('files_processed', self.agent.performance_stats)
        self.assertIn('start_time', self.agent.performance_stats)
        self.assertEqual(self.agent.performance_stats['queries'], 0)
        self.assertEqual(self.agent.performance_stats['files_processed'], 0)
        self.assertIsInstance(self.agent.performance_stats['start_time'], float)
    
    def test_query_tracking(self):
        """Test that queries are tracked correctly"""
        initial_queries = self.agent.performance_stats['queries']
        
        # Simulate a query
        self.agent._ai_tool_route_command("test query")
        
        self.assertEqual(self.agent.performance_stats['queries'], initial_queries + 1)
    
    def test_auto_save_functionality(self):
        """Test auto-save saves context correctly"""
        # Set up test data
        self.agent.context['files'] = ["test1.py", "test2.py"]
        self.agent.context['history'] = ["AI: test response"]
        
        # Auto-save
        self.agent._auto_save()
        
        # Verify file was written
        with open(self.agent.file, 'r') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data['files'], ["test1.py", "test2.py"])
            self.assertEqual(saved_data['history'], ["AI: test response"])
    
    def test_stats_functionality(self):
        """Test statistics display functionality"""
        # Set up test data
        self.agent.context['files'] = ["test1.py", "test2.py"]
        self.agent.context['history'] = ["AI: response 1", "AI: response 2"]
        self.agent.performance_stats['queries'] = 5
        
        stats = self.agent._get_stats()
        
        # Check that stats contain expected information
        self.assertIn("2 files", stats)
        self.assertIn("2 history", stats)
        self.assertIn("5 queries", stats)
        self.assertIn("uptime", stats)
    
    def test_stats_command(self):
        """Test stats command functionality"""
        self.agent.context['files'] = ["test.py"]
        self.agent.context['history'] = ["AI: test"]
        
        with patch('rich.console.Console.print') as mock_print:
            result = self.agent._smart_route_command("stats")
            mock_print.assert_called()
            self.assertEqual(result, "Stats displayed")
    
    def test_save_command(self):
        """Test save command functionality"""
        self.agent.context['files'] = ["test.py"]
        self.agent.context['history'] = ["AI: test"]
        
        with patch('rich.console.Console.print') as mock_print:
            result = self.agent._smart_route_command("save")
            mock_print.assert_called()
            self.assertEqual(result, "Saved")
    
    def test_export_command(self):
        """Test export command functionality"""
        self.agent.context['history'] = ["AI: response 1", "AI: response 2"]
        
        try:
            with patch('rich.console.Console.print') as mock_print:
                result = self.agent._smart_route_command("export")
                mock_print.assert_called()
                self.assertEqual(result, "Exported")
        finally:
            # Clean up export.txt if it was created
            if os.path.exists("export.txt"):
                os.unlink("export.txt")
    
    def test_quick_actions(self):
        """Test quick actions functionality"""
        actions = self.agent._quick_actions()
        
        # Check that all expected actions exist
        self.assertIn('stats', actions)
        self.assertIn('save', actions)
        self.assertIn('export', actions)
        
        # Test that actions are callable
        self.assertTrue(callable(actions['stats']))
        self.assertTrue(callable(actions['save']))
        self.assertTrue(callable(actions['export']))
    
    def test_uptime_calculation(self):
        """Test uptime calculation in stats"""
        # Wait a small amount to ensure uptime > 0
        time.sleep(0.01)
        
        stats = self.agent._get_stats()
        self.assertIn("uptime", stats)
        
        # Just verify uptime is mentioned in stats
        self.assertIn("uptime", stats)
    
    def test_performance_stats_persistence(self):
        """Test that performance stats are maintained across operations"""
        initial_queries = self.agent.performance_stats['queries']
        
        # Perform multiple operations
        self.agent._ai_tool_route_command("test query 1")
        self.agent._ai_tool_route_command("test query 2")
        
        # Check that queries were tracked
        self.assertEqual(self.agent.performance_stats['queries'], initial_queries + 2)
    
    def test_stats_with_empty_context(self):
        """Test stats display with empty context"""
        self.agent.context['files'] = []
        self.agent.context['history'] = []
        
        try:
            stats = self.agent._get_stats()
            self.assertIn("0 files", stats)
            self.assertIn("0 history", stats)
            self.assertIn("queries", stats)
            self.assertIn("uptime", stats)
        finally:
            # Clean up any test files that might have been created
            for test_file in ["test.py", "export.txt"]:
                if os.path.exists(test_file):
                    os.unlink(test_file)
    
    def test_export_with_empty_history(self):
        """Test export with empty history"""
        self.agent.context['history'] = []
        
        try:
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
