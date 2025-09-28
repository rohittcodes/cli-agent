"""
Test file operations and management
"""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
import main


class TestFileOperations:
    """Test file operations functionality"""
    
    def test_read_file_success(self):
        """Test successful file reading"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write("print('hello world')")
            temp_path = f.name
        
        agent = main.AICodeAgent()
        content = agent._read_file(temp_path)
        assert "hello world" in content
        
        # Cleanup
        os.unlink(temp_path)
    
    def test_read_file_not_found(self):
        """Test reading non-existent file"""
        agent = main.AICodeAgent()
        content = agent._read_file("nonexistent_file.py")
        assert content == ""
    
    def test_write_file_success(self):
        """Test successful file writing"""
        agent = main.AICodeAgent()
        test_content = "print('test content')"
        test_path = "test_write.py"
        
        result = agent._write_file(test_path, test_content)
        assert result is True
        
        # Verify file was created
        with open(test_path, 'r') as f:
            content = f.read()
            assert content == test_content
        
        # Cleanup
        os.unlink(test_path)
    
    def test_write_file_with_directory_creation(self):
        """Test file writing with directory creation"""
        agent = main.AICodeAgent()
        test_content = "test content"
        test_path = "test_dir/test_file.py"
        
        result = agent._write_file(test_path, test_content)
        assert result is True
        
        # Verify file and directory were created
        assert os.path.exists(test_path)
        assert os.path.exists("test_dir")
        
        # Cleanup
        os.unlink(test_path)
        os.rmdir("test_dir")
    
    def test_find_files_basic(self):
        """Test basic file finding"""
        agent = main.AICodeAgent()
        files = agent._find_files("")
        assert isinstance(files, list)
        assert len(files) <= 20  # Should be limited to 20 files
    
    def test_find_files_with_pattern(self):
        """Test file finding with pattern"""
        agent = main.AICodeAgent()
        files = agent._find_files(".py")
        assert isinstance(files, list)
        # All files should be Python files
        for file in files:
            assert file.endswith('.py')
    
    def test_find_files_excludes_hidden(self):
        """Test that hidden files are excluded"""
        agent = main.AICodeAgent()
        files = agent._find_files("")
        # Should not include hidden files
        for file in files:
            assert not os.path.basename(file).startswith('.')
    
    def test_find_files_excludes_cache_dirs(self):
        """Test that cache directories are excluded"""
        agent = main.AICodeAgent()
        files = agent._find_files("")
        # Should not include cache directories
        for file in files:
            path_parts = file.split(os.sep)
            assert '__pycache__' not in path_parts
            assert 'node_modules' not in path_parts
            assert '.git' not in path_parts
    
    def test_search_in_files_basic(self):
        """Test basic content search"""
        # Create test files
        with open("test_search1.py", "w") as f:
            f.write("def test_function():\n    pass")
        with open("test_search2.py", "w") as f:
            f.write("def another_function():\n    pass")
        
        agent = main.AICodeAgent()
        agent.context['files'] = ["test_search1.py", "test_search2.py"]
        
        results = agent._search_in_files("def")
        assert isinstance(results, list)
        assert len(results) >= 2  # Should find both functions
        
        # Cleanup
        os.unlink("test_search1.py")
        os.unlink("test_search2.py")
    
    def test_search_in_files_no_context(self):
        """Test content search with no context files"""
        agent = main.AICodeAgent()
        agent.context['files'] = []
        
        results = agent._search_in_files("test")
        assert results == []
    
    def test_search_in_files_limit_results(self):
        """Test that search results are limited"""
        # Create test file with many lines
        with open("test_many_lines.py", "w") as f:
            for i in range(100):
                f.write(f"line {i} with test content\n")
        
        agent = main.AICodeAgent()
        agent.context['files'] = ["test_many_lines.py"]
        
        results = agent._search_in_files("test")
        assert len(results) <= 15  # Should be limited to 15 results
        
        # Cleanup
        os.unlink("test_many_lines.py")
    
    def test_get_code_templates_scraper(self):
        """Test code template for scraper"""
        agent = main.AICodeAgent()
        template = agent._get_code_templates("scraper")
        assert "import requests" in template
        assert "BeautifulSoup" in template
        assert "def scrape_page" in template
    
    def test_get_code_templates_calculator(self):
        """Test code template for calculator"""
        agent = main.AICodeAgent()
        template = agent._get_code_templates("calculator")
        assert "def safe_calculate" in template
        assert "math" in template
        assert "while True" in template
    
    def test_get_code_templates_hello(self):
        """Test code template for hello"""
        agent = main.AICodeAgent()
        template = agent._get_code_templates("hello")
        assert "Hello, World!" in template
    
    def test_get_code_templates_api(self):
        """Test code template for API"""
        agent = main.AICodeAgent()
        template = agent._get_code_templates("api")
        assert "import requests" in template
        assert "def make_api_request" in template
        assert "json" in template
    
    def test_get_code_templates_server(self):
        """Test code template for server"""
        agent = main.AICodeAgent()
        template = agent._get_code_templates("server")
        assert "HTTPServer" in template
        assert "BaseHTTPRequestHandler" in template
        assert "def start_server" in template
    
    def test_get_code_templates_unknown(self):
        """Test code template for unknown type"""
        agent = main.AICodeAgent()
        template = agent._get_code_templates("unknown")
        assert "Generated by AI Code Agent" in template
        assert "File created successfully" in template
    
    def test_file_operations_integration(self):
        """Test file operations integration"""
        agent = main.AICodeAgent()
        
        # Test creating a file
        content = "print('integration test')"
        result = agent._write_file("integration_test.py", content)
        assert result is True
        
        # Test reading the file
        read_content = agent._read_file("integration_test.py")
        assert content in read_content
        
        # Test finding the file
        files = agent._find_files("integration_test")
        assert any("integration_test.py" in f for f in files)
        
        # Test searching content
        agent.context['files'] = ["integration_test.py"]
        results = agent._search_in_files("integration")
        assert len(results) > 0
        
        # Cleanup
        os.unlink("integration_test.py")
    
    def test_file_operations_error_handling(self):
        """Test file operations error handling"""
        agent = main.AICodeAgent()
        
        # Test reading non-existent file
        content = agent._read_file("nonexistent.py")
        assert content == ""
        
        # Test writing to invalid path (should still work with directory creation)
        result = agent._write_file("invalid/path/test.py", "content")
        assert result is True
        
        # Cleanup
        if os.path.exists("invalid/path/test.py"):
            os.unlink("invalid/path/test.py")
            os.rmdir("invalid/path")
            os.rmdir("invalid")
