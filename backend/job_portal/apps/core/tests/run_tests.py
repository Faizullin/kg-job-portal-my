#!/usr/bin/env python
"""
Test runner script for Job Portal app.
This script runs the complete test suite in the proper order.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def setup_django():
    """Setup Django environment for testing."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.dev')
    django.setup()


def run_tests():
    """Run the complete test suite."""
    setup_django()
    
    # Get test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Define test modules in order of execution
    test_modules = [
        'job_portal.apps.core.tests.test_simple_requirements',
        'job_portal.apps.core.tests.test_authentication',
        'job_portal.apps.core.tests.test_advanced_search',
        'job_portal.apps.core.tests.test_chat_system',
    ]
    
    print("🚀 Starting Job Portal Test Suite...")
    print("=" * 50)
    
    total_failures = 0
    total_errors = 0
    total_tests = 0
    
    for module in test_modules:
        print(f"\n📋 Testing: {module}")
        print("-" * 30)
        
        try:
            # Run tests for this module
            failures, errors, tests_run = test_runner.run_tests([module])
            
            total_failures += failures
            total_errors += errors
            total_tests += tests_run
            
            if failures == 0 and errors == 0:
                print(f"✅ {module}: {tests_run} tests passed")
            else:
                print(f"❌ {module}: {failures} failures, {errors} errors")
                
        except Exception as e:
            print(f"💥 Error running {module}: {e}")
            total_errors += 1
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_failures + total_errors} test(s) failed")
        return 1


def run_specific_test(test_name):
    """Run a specific test module."""
    setup_django()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    print(f"🧪 Running specific test: {test_name}")
    
    try:
        failures, errors, tests_run = test_runner.run_tests([test_name])
        
        if failures == 0 and errors == 0:
            print(f"✅ {test_name}: {tests_run} tests passed")
            return 0
        else:
            print(f"❌ {test_name}: {failures} failures, {errors} errors")
            return 1
            
    except Exception as e:
        print(f"💥 Error running {test_name}: {e}")
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        exit_code = run_specific_test(test_name)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code)

