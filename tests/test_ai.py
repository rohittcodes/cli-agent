#!/usr/bin/env python3
"""
Unit tests for AI class functionality
"""
import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CodeAgent

class TestAI(unittest.TestCase):
    def setUp(self):
        self.agent = CodeAgent()
        self.ai = self.agent  # AI functionality is now part of CodeAgent
    
    def test_ai_initialization(self):
        """Test AI class initializes with correct URL"""
        self.assertEqual(self.ai.url, "http://localhost:11434")
    
    @patch('requests.get')
    def test_available_success(self, mock_get):
        """Test AI available when server responds with 200"""
        mock_get.return_value.status_code = 200
        self.assertTrue(self.ai.available())
    
    @patch('requests.get')
    def test_available_failure(self, mock_get):
        """Test AI not available when server responds with 404"""
        mock_get.return_value.status_code = 404
        self.assertFalse(self.ai.available())
    
    @patch('requests.get')
    def test_available_timeout(self, mock_get):
        """Test AI not available when request times out"""
        mock_get.side_effect = Exception("Connection timeout")
        self.assertFalse(self.ai.available())
    
    def test_file_operations(self):
        """Test file operations through tool execution"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_file = f.name
        
        try:
            # Test create file
            result = self.ai._execute_single_tool("create_file", {"filename": test_file, "content": "test content"})
            self.assertIn("Created", result)
            
            # Test read file
            result = self.ai._execute_single_tool("read_file", {"filename": test_file})
            self.assertIn("test content", result)
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def test_performance_stats(self):
        """Test performance statistics tracking"""
        self.assertIn('queries', self.ai.performance_stats)
        self.assertIn('files_processed', self.ai.performance_stats)
        self.assertIn('start_time', self.ai.performance_stats)
        self.assertEqual(self.ai.performance_stats['queries'], 0)
    
    def test_auto_save(self):
        """Test auto-save functionality"""
        # Test that auto-save method exists and works
        self.assertTrue(hasattr(self.ai, '_auto_save'))
        # Should not raise an exception
        self.ai._auto_save()
    
    def test_stats_functionality(self):
        """Test statistics functionality"""
        self.assertTrue(hasattr(self.ai, '_get_stats'))
        stats = self.ai._get_stats()
        self.assertIn('files', stats)
        self.assertIn('lines', stats)
        self.assertIn('history', stats)
        self.assertIn('queries', stats)
        self.assertIn('uptime', stats)

if __name__ == '__main__':
    unittest.main()


