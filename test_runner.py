import pytest
import sys
from datetime import datetime

def main():
    """Run test suite with formatting and reporting"""
    print(f"\nStarting test run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Configure test collection
    test_args = [
        'test_lecture_processor.py',
        '-v',
        '--cov=lecture_processor',
        '--cov=content_extractor',
        '--cov-report=term-missing',
        '--cov-report=html'
    ]
    
    # Add markers for integration tests
    if '--integration' in sys.argv:
        print("Running integration tests...")
    else:
        test_args.append('-m', 'not integration')
        print("Skipping integration tests. Use --integration to run them.")
    
    # Run tests
    result = pytest.main(test_args)
    
    print("\n" + "=" * 80)
    print(f"Test run completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return result

if __name__ == "__main__":
    sys.exit(main())
