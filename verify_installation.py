#!/usr/bin/env python3
"""
Installation verification script
Checks that all components are properly installed and configured
"""

import os
import sys
from pathlib import Path


def check_mark(condition):
    """Return checkmark or X based on condition"""
    return "✅" if condition else "❌"


def verify_installation():
    """Verify all installation requirements"""
    
    print("\n" + "="*80)
    print(" PERPLEXITY-ALPACA TRADING INTEGRATION - INSTALLATION VERIFICATION")
    print("="*80 + "\n")
    
    all_checks_passed = True
    
    # Check 1: Python version
    print("1. Python Version")
    python_version = sys.version_info
    python_ok = python_version >= (3, 11)
    print(f"   {check_mark(python_ok)} Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    if not python_ok:
        print("   ⚠️  Python 3.11+ required")
        all_checks_passed = False
    
    # Check 2: Required files
    print("\n2. Project Files")
    required_files = [
        'main.py',
        'requirements.txt',
        'setup.sh',
        '.env.example',
        'README.md',
        'Dockerfile',
        'src/config.py',
        'src/perplexity_client.py',
        'src/prompt_generator.py',
        'src/data_handler.py',
        'src/strategy.py',
        'src/executor.py',
        'tests/test_strategy.py',
    ]
    
    files_ok = True
    for file in required_files:
        exists = Path(file).exists()
        print(f"   {check_mark(exists)} {file}")
        if not exists:
            files_ok = False
    
    if not files_ok:
        all_checks_passed = False
    
    # Check 3: Required directories
    print("\n3. Directory Structure")
    required_dirs = [
        'src',
        'tests',
        'local_tasks',
        'logs',
        'examples'
    ]
    
    dirs_ok = True
    for directory in required_dirs:
        exists = Path(directory).is_dir()
        print(f"   {check_mark(exists)} {directory}/")
        if not exists:
            dirs_ok = False
    
    if not dirs_ok:
        all_checks_passed = False
    
    # Check 4: Python dependencies
    print("\n4. Python Dependencies")
    dependencies = [
        'pandas',
        'numpy',
        'requests',
        'alpaca',
        'dotenv',
        'pytest'
    ]
    
    deps_ok = True
    for dep in dependencies:
        try:
            if dep == 'dotenv':
                __import__('dotenv')
            elif dep == 'alpaca':
                __import__('alpaca.trading')
            else:
                __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep}")
            deps_ok = False
    
    if not deps_ok:
        print("\n   ⚠️  Run: pip install -r requirements.txt")
        all_checks_passed = False
    
    # Check 5: Environment configuration
    print("\n5. Environment Configuration")
    env_file_exists = Path('.env').exists()
    print(f"   {check_mark(env_file_exists)} .env file exists")
    
    if env_file_exists:
        from dotenv import load_dotenv
        load_dotenv()
        
        env_vars = [
            'PERPLEXITY_API_KEY',
            'ALPACA_API_KEY',
            'ALPACA_SECRET_KEY'
        ]
        
        env_ok = True
        for var in env_vars:
            value = os.getenv(var)
            has_value = value and value != f'your_{var.lower()}_here'
            print(f"   {check_mark(has_value)} {var}")
            if not has_value:
                env_ok = False
        
        if not env_ok:
            print("\n   ⚠️  Edit .env file with your API keys")
            all_checks_passed = False
    else:
        print("   ℹ️  Copy .env.example to .env and add your API keys")
        all_checks_passed = False
    
    # Check 6: Import main modules
    print("\n6. Module Imports")
    modules = [
        'src.config',
        'src.perplexity_client',
        'src.prompt_generator',
        'src.data_handler',
        'src.strategy',
        'src.executor'
    ]
    
    imports_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module} - {str(e)[:50]}")
            imports_ok = False
    
    if not imports_ok:
        all_checks_passed = False
    
    # Final summary
    print("\n" + "="*80)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Installation verified successfully!")
        print("="*80)
        print("\nNext steps:")
        print("1. python main.py test --tickers SPY")
        print("2. python main.py analyze --tickers AAPL --strategy momentum")
        print("3. Check README.md for full documentation")
    else:
        print("❌ SOME CHECKS FAILED - Please review the issues above")
        print("="*80)
        print("\nCommon fixes:")
        print("1. Run: ./setup.sh")
        print("2. Run: source venv/bin/activate")
        print("3. Run: pip install -r requirements.txt")
        print("4. Copy .env.example to .env and add API keys")
    print("="*80 + "\n")
    
    return all_checks_passed


if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)
