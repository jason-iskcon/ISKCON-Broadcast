#!/usr/bin/env python3
"""
ISKCON-Broadcast Test Runner

Comprehensive test runner with coverage reporting, performance testing,
and different test execution modes.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description or ' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description or 'Command'} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or 'Command'} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install -r requirements.txt")
        return False


def run_unit_tests(coverage=False, verbose=False):
    """Run unit tests"""
    cmd = ["python", "-m", "pytest", "tests/unit/"]
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["-x", "--tb=short"])
    
    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose=False):
    """Run integration tests"""
    cmd = ["python", "-m", "pytest", "tests/sys/", "-m", "integration"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["-x", "--tb=short"])
    
    return run_command(cmd, "Integration Tests")


def run_performance_tests(verbose=False):
    """Run performance tests"""
    cmd = ["python", "-m", "pytest", "tests/perf/", "-m", "performance"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["--tb=short"])
    
    return run_command(cmd, "Performance Tests")


def run_all_tests(coverage=False, verbose=False):
    """Run all tests"""
    cmd = ["python", "-m", "pytest", "tests/"]
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term", "--cov-report=xml"])
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["--tb=short", "--durations=10"])
    
    return run_command(cmd, "All Tests")


def run_smoke_tests():
    """Run smoke tests for basic functionality"""
    cmd = ["python", "-m", "pytest", "tests/", "-m", "smoke", "-v"]
    
    return run_command(cmd, "Smoke Tests")


def run_linting():
    """Run code linting (if available)"""
    linters = [
        (["python", "-m", "flake8", "src/", "tests/"], "Flake8 Linting"),
        (["python", "-m", "black", "--check", "src/", "tests/"], "Black Code Formatting Check"),
        (["python", "-m", "isort", "--check-only", "src/", "tests/"], "Import Sorting Check")
    ]
    
    results = []
    for cmd, description in linters:
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ {description} passed")
            results.append(True)
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed")
            if e.stdout:
                print(f"Output: {e.stdout}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            results.append(False)
        except FileNotFoundError:
            print(f"⚠️  {description} skipped (tool not installed)")
            results.append(None)
    
    return all(r is not False for r in results)


def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        "pytest", "pytest-cov", "pytest-mock", "numpy", "opencv-python", 
        "pygame", "PyYAML", "requests", "urllib3"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies satisfied")
    return True


def generate_coverage_report():
    """Generate detailed coverage report"""
    print("\nGenerating coverage report...")
    
    # Run tests with coverage
    cmd = [
        "python", "-m", "pytest", "tests/",
        "--cov=src",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ]
    
    success = run_command(cmd, "Coverage Analysis")
    
    if success:
        print("\n📊 Coverage reports generated:")
        print("  - HTML: htmlcov/index.html")
        print("  - XML: coverage.xml")
        print("  - Terminal output above")
    
    return success


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="ISKCON-Broadcast Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🧪 ISKCON-Broadcast Test Runner")
    print(f"Working directory: {os.getcwd()}")
    
    success = True
    
    # Check dependencies first if requested
    if args.check_deps or args.all:
        if not check_dependencies():
            return 1
    
    # Run specific test types
    if args.unit:
        success &= run_unit_tests(coverage=args.coverage, verbose=args.verbose)
    elif args.integration:
        success &= run_integration_tests(verbose=args.verbose)
    elif args.performance:
        success &= run_performance_tests(verbose=args.verbose)
    elif args.smoke:
        success &= run_smoke_tests()
    elif args.coverage:
        success &= generate_coverage_report()
    elif args.lint:
        success &= run_linting()
    elif args.all:
        # Run everything
        success &= run_linting()
        success &= run_smoke_tests()
        success &= run_unit_tests(verbose=args.verbose)
        success &= run_integration_tests(verbose=args.verbose)
        success &= run_performance_tests(verbose=args.verbose)
        success &= generate_coverage_report()
    else:
        # Default: run all tests with coverage
        success &= run_all_tests(coverage=True, verbose=args.verbose)
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ Test suite passed")
    else:
        print("💥 Some tests failed!")
        print("❌ Test suite failed")
    print(f"{'='*60}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 