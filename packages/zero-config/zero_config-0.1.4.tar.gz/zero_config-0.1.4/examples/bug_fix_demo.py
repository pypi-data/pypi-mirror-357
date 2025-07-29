#!/usr/bin/env python3
"""
Demo showing the bug fix for environment variable consistency.

This script demonstrates the bug that was fixed where environment variables
were only applied if they already existed in defaults, while env file variables
were always added even if they didn't exist in defaults.
"""

import os
import tempfile
from pathlib import Path
from zero_config import setup_environment, get_config
from zero_config.config import _reset_for_testing


def demo_bug_fix():
    """Demonstrate the environment variable consistency bug fix."""
    print("🐛 Zero Config Bug Fix Demo: Environment Variable Consistency")
    print("=" * 70)
    print()
    
    # Create a temporary directory for our demo
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create an .env file with a new variable not in defaults
        env_file = tmpdir_path / ".env.zero_config"
        env_file.write_text("""
# New variables not in defaults
database.test_url=file://test.db
api.timeout=30
feature.new_ui=enabled
""".strip())
        
        print(f"📁 Created .env file at: {env_file}")
        print(f"📄 .env file contents:")
        print(env_file.read_text())
        print()
        
        # Set environment variables (some new, some matching .env)
        test_env = {
            'DATABASE__HOST': 'env.db.com',        # New from env var
            'DATABASE__TEST_URL': 'env://test.db',  # Conflicts with .env file
            'API__KEY': 'sk-env-key',               # New from env var
            'FEATURE__ENABLED': 'true'              # New from env var
        }
        
        print("🌍 Setting environment variables:")
        for key, value in test_env.items():
            print(f"   {key}={value}")
            os.environ[key] = value
        print()
        
        try:
            # Reset zero-config state
            _reset_for_testing()

            # Setup with minimal defaults (no database, api, or feature keys)
            print("⚙️  Setting up zero-config with minimal defaults:")
            default_config = {
                'app_name': 'bug_fix_demo',
                'version': '1.0.0'
            }
            print(f"   Default config: {default_config}")
            print()

            # Mock the project root to point to our temp directory
            from unittest.mock import patch
            with patch('zero_config.config.find_project_root', return_value=tmpdir_path):
                setup_environment(default_config=default_config)
                config = get_config()

            print("✅ AFTER BUG FIX - All variables are now available:")
            print()

            # Show that environment variables are now available without predefinition
            print("🔧 Environment variables (converted to dot notation):")
            print(f"   database.host = {config.get('database.host')}")
            print(f"   database.test_url = {config.get('database.test_url')}")  # env file wins
            print(f"   api.key = {config.get('api.key')}")
            print(f"   feature.enabled = {config.get('feature.enabled')}")
            print()

            # Show that .env file variables are still available
            print("📄 .env file variables:")
            print(f"   database.test_url = {config.get('database.test_url')}")  # env file wins
            print(f"   api.timeout = {config.get('api.timeout')}")
            print(f"   feature.new_ui = {config.get('feature.new_ui')}")
            print()

            # Show section access works with new variables
            print("📂 Section access with new variables:")
            database_section = config.get('database')
            api_section = config.get('api')
            feature_section = config.get('feature')

            print(f"   database section: {database_section}")
            print(f"   api section: {api_section}")
            print(f"   feature section: {feature_section}")
            print()

            # Show priority order
            print("🏆 Priority demonstration:")
            print("   database.test_url shows env file priority over env var")
            print(f"   Environment variable: DATABASE__TEST_URL='env://test.db'")
            print(f"   .env file variable: database.test_url='file://test.db'")
            print(f"   Result: {config.get('database.test_url')} (env file wins)")
            print()

            print("🎯 Key Benefits of the Fix:")
            print("   ✅ Environment variables work without predefinition in defaults")
            print("   ✅ Consistent behavior between env vars and .env files")
            print("   ✅ Section access works with dynamically added variables")
            print("   ✅ Type conversion still works when defaults are provided")
            print("   ✅ Priority order maintained: defaults < env vars < .env files")
            
        finally:
            # Clean up environment variables
            for key in test_env:
                os.environ.pop(key, None)


def demo_before_fix_simulation():
    """Simulate what would have happened before the fix."""
    print()
    print("❌ BEFORE BUG FIX - What would have happened:")
    print()
    print("🚫 Environment variables without defaults would be IGNORED:")
    print("   DATABASE__HOST -> database.host = None (ignored)")
    print("   API__KEY -> api.key = None (ignored)")
    print("   FEATURE__ENABLED -> feature.enabled = None (ignored)")
    print()
    print("✅ .env file variables would still work:")
    print("   database.test_url = 'file://test.db' (loaded)")
    print("   api.timeout = '30' (loaded)")
    print("   feature.new_ui = 'enabled' (loaded)")
    print()
    print("🔍 The inconsistency:")
    print("   - Same variable DATABASE__TEST_URL ignored from env var")
    print("   - But database.test_url loaded from .env file")
    print("   - This created confusing and inconsistent behavior!")


def demo_type_conversion():
    """Demonstrate that type conversion still works correctly."""
    print()
    print("🔄 Type Conversion Demo")
    print("=" * 30)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        original_cwd = os.getcwd()
        os.chdir(tmpdir_path)
        
        try:
            _reset_for_testing()
            
            # Set environment variables
            os.environ['DATABASE__PORT'] = '3306'      # Should convert to int
            os.environ['LLM__TEMPERATURE'] = '0.9'     # Should convert to float
            os.environ['DEBUG'] = 'true'               # Should convert to bool
            os.environ['NEW_TIMEOUT'] = '60'           # Should stay string (no default)
            
            # Setup with some typed defaults
            setup_environment(default_config={
                'database.port': 5432,      # int default
                'llm.temperature': 0.7,     # float default
                'debug': False              # bool default
            })
            
            config = get_config()
            
            print("🔢 Type conversion with defaults:")
            print(f"   database.port = {config.get('database.port')} ({type(config.get('database.port')).__name__})")
            print(f"   llm.temperature = {config.get('llm.temperature')} ({type(config.get('llm.temperature')).__name__})")
            print(f"   debug = {config.get('debug')} ({type(config.get('debug')).__name__})")
            print()
            print("📝 No conversion without defaults:")
            print(f"   new_timeout = {config.get('new_timeout')} ({type(config.get('new_timeout')).__name__})")
            
        finally:
            # Clean up
            for key in ['DATABASE__PORT', 'LLM__TEMPERATURE', 'DEBUG', 'NEW_TIMEOUT']:
                os.environ.pop(key, None)
            os.chdir(original_cwd)


if __name__ == "__main__":
    demo_bug_fix()
    demo_before_fix_simulation()
    demo_type_conversion()
    
    print()
    print("🎉 Bug fix demonstration complete!")
    print()
    print("📋 Summary:")
    print("   The bug was that environment variables required predefinition in defaults,")
    print("   while .env file variables did not. This created inconsistent behavior.")
    print("   The fix makes both sources behave consistently - both can add new keys!")
