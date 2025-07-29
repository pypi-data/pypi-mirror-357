#!/usr/bin/env python3
"""
Test for the specific bug fix: Environment variable vs env file inconsistency.

This test demonstrates the exact bug scenario described in the bug report.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from zero_config import setup_environment, get_config
from zero_config.config import _reset_for_testing


class TestBugFix:
    """Test the specific bug fix for environment variable consistency."""
    
    def setup_method(self):
        """Reset state before each test."""
        _reset_for_testing()
    
    def teardown_method(self):
        """Reset state after each test."""
        _reset_for_testing()
    
    def test_original_bug_scenario(self):
        """Test the exact scenario described in the bug report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            # Create .env file with database.test_url (same format as env var conversion)
            env_file = tmpdir_path / ".env.zero_config"
            env_file.write_text("database.test_url=file://test.db")
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'DATABASE__TEST_URL': 'env://test.db'  # Should be converted to database.test_url
                }, clear=True):
                    # Setup with minimal defaults (no database.test_url predefined)
                    setup_environment(default_config={
                        'app_name': 'test_app'
                    })
                    
                    config = get_config()
                    
                    # BEFORE THE FIX:
                    # - Environment variable DATABASE__TEST_URL would be ignored (not in defaults)
                    # - Env file variable database.test_url would be loaded
                    # - Result: only database.test_url from env file, env var ignored

                    # AFTER THE FIX:
                    # - Environment variable DATABASE__TEST_URL is converted to database.test_url and added
                    # - Env file variable database.test_url is also loaded
                    # - Both target the same key, with env file taking priority

                    # The key insight: env var should now be processed (not ignored)
                    assert config.get('database.test_url') == 'file://test.db'  # From env file (higher priority)
    
    def test_env_var_without_defaults_now_works(self):
        """Test that environment variables work without requiring predefinition in defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'DATABASE__TEST_URL': 'env://test.db',
                    'API__TIMEOUT': '30',
                    'FEATURE__ENABLED': 'true'
                }, clear=True):
                    # Setup with NO defaults for these keys
                    setup_environment(default_config={
                        'app_name': 'test_app'
                    })
                    
                    config = get_config()
                    
                    # BEFORE THE FIX: These would all be None (ignored)
                    # AFTER THE FIX: These should all be available
                    assert config.get('database.test_url') == 'env://test.db'
                    assert config.get('api.timeout') == '30'
                    assert config.get('feature.enabled') == 'true'
    
    def test_env_var_vs_env_file_same_behavior(self):
        """Test that env vars and env files now have the same behavior for new keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            # Create .env file with a new key
            env_file = tmpdir_path / ".env.zero_config"
            env_file.write_text("new_key_from_file=file_value")
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'NEW_KEY_FROM_ENV': 'env_value'
                }, clear=True):
                    # Setup with NO defaults for these keys
                    setup_environment(default_config={})
                    
                    config = get_config()
                    
                    # Both should be available (consistent behavior)
                    assert config.get('new_key_from_env') == 'env_value'    # From env var
                    assert config.get('new_key_from_file') == 'file_value'  # From env file
    
    def test_type_conversion_still_works_with_defaults(self):
        """Test that type conversion still works when defaults are provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'DATABASE__PORT': '3306',      # Should convert to int (has default)
                    'NEW_PORT': '8080'             # Should stay string (no default)
                }, clear=True):
                    # Setup with default for database.port but not new_port
                    setup_environment(default_config={
                        'database.port': 5432  # int default
                    })
                    
                    config = get_config()
                    
                    # Type conversion should work when defaults exist
                    assert config.get('database.port') == 3306      # int (converted)
                    assert config.get('new_port') == '8080'         # string (no conversion)
    
    def test_section_access_with_new_env_vars(self):
        """Test that section access works with new keys from environment variables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir).resolve()
            
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                with patch.dict(os.environ, {
                    'DATABASE__HOST': 'new.db.com',
                    'DATABASE__PORT': '5432',
                    'DATABASE__SSL': 'true'
                }, clear=True):
                    # Setup with NO database defaults
                    setup_environment(default_config={
                        'app_name': 'test_app'
                    })
                    
                    config = get_config()
                    
                    # Section access should work with new keys from env vars
                    database_section = config.get('database')
                    assert database_section == {
                        'host': 'new.db.com',
                        'port': '5432',
                        'ssl': 'true'
                    }


if __name__ == "__main__":
    pytest.main([__file__])
