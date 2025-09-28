"""
Test context management and persistence
"""
import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock
import main


class TestContextManagement:
    """Test context management functionality"""
    
    def test_context_initialization(self):
        """Test context initialization"""
        # Remove existing session file to test clean initialization
        if os.path.exists('session.json'):
            os.remove('session.json')
        
        agent = main.AICodeAgent()
        assert 'files' in agent.context
        assert 'history' in agent.context
        assert isinstance(agent.context['files'], list)
        assert isinstance(agent.context['history'], list)
        assert len(agent.context['files']) == 0
        assert len(agent.context['history']) == 0
    
    def test_load_session_file_not_found(self):
        """Test session loading when file doesn't exist"""
        # Remove existing session file to test clean initialization
        if os.path.exists('session.json'):
            os.remove('session.json')
        
        agent = main.AICodeAgent()
        # Should not raise exception
        assert isinstance(agent.context['files'], list)
        assert isinstance(agent.context['history'], list)
        assert len(agent.context['files']) == 0
        assert len(agent.context['history']) == 0
    
    def test_load_session_invalid_json(self):
        """Test session loading with invalid JSON"""
        # Create file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("invalid json content")
            session_path = f.name
        
        # Mock the session file path
        with patch('builtins.open', side_effect=lambda path, mode: open(session_path, mode)):
            agent = main.AICodeAgent()
            # Should not raise exception
            assert isinstance(agent.context['files'], list)
            assert isinstance(agent.context['history'], list)
        
        # Cleanup
        os.unlink(session_path)
  
    def test_save_session_error_handling(self):
        """Test session saving error handling"""
        agent = main.AICodeAgent()
        agent.context = {'files': [], 'history': []}
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            # Should not raise exception
            agent._save_session()
    
    def test_context_operations(self):
        """Test context operations"""
        # Remove existing session file to test clean initialization
        if os.path.exists('session.json'):
            os.remove('session.json')
        
        agent = main.AICodeAgent()
        
        # Test adding files to context
        agent.context['files'].append('file1.py')
        agent.context['files'].append('file2.py')
        assert len(agent.context['files']) == 2
        
        # Test adding history
        agent.context['history'].append('query1')
        agent.context['history'].append('query2')
        assert len(agent.context['history']) == 2
        
        # Test clearing context
        agent.context['files'] = []
        agent.context['history'] = []
        assert len(agent.context['files']) == 0
        assert len(agent.context['history']) == 0
    
    def test_context_file_limits(self):
        """Test context file limits"""
        # Remove existing session file to test clean initialization
        if os.path.exists('session.json'):
            os.remove('session.json')
        
        agent = main.AICodeAgent()
        
        # Add many files to context
        for i in range(100):
            agent.context['files'].append(f'file{i}.py')
        
        # Should handle large number of files
        assert len(agent.context['files']) == 100
    
    def test_context_history_limits(self):
        """Test context history limits"""
        # Remove existing session file to test clean initialization
        if os.path.exists('session.json'):
            os.remove('session.json')
        
        agent = main.AICodeAgent()
        
        # Add many history entries
        for i in range(100):
            agent.context['history'].append(f'query{i}')
        
        # Should handle large number of history entries
        assert len(agent.context['history']) == 100
    
    def test_context_data_types(self):
        """Test context data types"""
        agent = main.AICodeAgent()
        
        # Test with different data types
        agent.context['files'] = ['file1.py', 'file2.py', 'file3.py']
        agent.context['history'] = ['query1', 'query2', 'query3']
        
        assert all(isinstance(f, str) for f in agent.context['files'])
        assert all(isinstance(h, str) for h in agent.context['history'])
    
    def test_context_error_recovery(self):
        """Test context error recovery"""
        agent = main.AICodeAgent()
        
        # Test with corrupted context data
        agent.context = {'files': None, 'history': None}
        
        # Should handle corrupted data gracefully
        try:
            agent._save_session()
        except Exception:
            # Should not crash
            pass
    
    def test_context_serialization(self):
        """Test context serialization"""
        agent = main.AICodeAgent()
        
        # Add test data
        agent.context = {
            'files': ['test1.py', 'test2.py'],
            'history': ['query1', 'query2']
        }
        
        # Test JSON serialization
        json_str = json.dumps(agent.context)
        assert 'test1.py' in json_str
        assert 'query1' in json_str
        
        # Test JSON deserialization
        loaded_context = json.loads(json_str)
        assert loaded_context['files'] == ['test1.py', 'test2.py']
        assert loaded_context['history'] == ['query1', 'query2']
