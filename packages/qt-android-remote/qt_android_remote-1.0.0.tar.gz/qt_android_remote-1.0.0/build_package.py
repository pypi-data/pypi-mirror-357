#!/usr/bin/env python3
"""
Build script for Qt Android Remote

This script helps build and prepare the package for PyPI distribution.
"""

import subprocess
import sys
import shutil
from pathlib import Path


def run_command(cmd, description, capture_output=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            # For commands that might hang with captured output, run without capturing
            result = subprocess.run(cmd, shell=True, check=True)
            print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if capture_output and hasattr(e, 'stderr') and e.stderr:
            print(e.stderr)
        return False


def clean_build():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removed directory: {path}")
            elif path.is_file():
                path.unlink()
                print(f"   Removed file: {path}")
    
    return True


def check_requirements():
    """Check if build requirements are installed"""
    print("\n📋 Checking build requirements...")
    
    required_packages = ["build", "twine"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        cmd = f"{sys.executable} -m pip install {' '.join(missing_packages)}"
        if not run_command(cmd, "Installing build dependencies"):
            return False
    
    return True


def run_tests():
    """Run tests if available"""
    print("\n🧪 Running tests...")
    
    # Check if pytest is available and if there are tests
    try:
        __import__("pytest")
        test_files = list(Path(".").glob("test*.py")) + list(Path("tests").glob("*.py")) if Path("tests").exists() else []
        
        if test_files:
            return run_command(f"{sys.executable} -m pytest", "Running tests")
        else:
            print("   ℹ️  No test files found, skipping tests")
            return True
    except ImportError:
        print("   ℹ️  pytest not installed, skipping tests")
        return True


def run_linting():
    """Run code quality checks"""
    print("\n🔍 Running code quality checks...")
    
    # Check if black is available
    try:
        __import__("black")
        if not run_command(f"{sys.executable} -m black --check qt_android_remote/", "Checking code formatting with black"):
            print("   💡 Run 'python -m black qt_android_remote/' to fix formatting")
            return False
    except ImportError:
        print("   ℹ️  black not installed, skipping formatting check")
    
    # Check if flake8 is available
    try:
        __import__("flake8")
        if not run_command(f"{sys.executable} -m flake8 qt_android_remote/", "Running flake8 linting"):
            return False
    except ImportError:
        print("   ℹ️  flake8 not installed, skipping linting")
    
    return True


def build_package():
    """Build the package"""
    return run_command(f"{sys.executable} -m build", "Building package", capture_output=False)


def check_package():
    """Check the built package"""
    return run_command("twine check dist/*", "Checking package")


def upload_to_test_pypi():
    """Upload to Test PyPI"""
    print("\n⚠️  This will upload to Test PyPI. Continue? (y/N): ", end="")
    if input().lower() != 'y':
        print("Upload cancelled.")
        return True
    
    return run_command("twine upload --repository testpypi dist/*", "Uploading to Test PyPI")


def upload_to_pypi():
    """Upload to PyPI"""
    print("\n⚠️  This will upload to PyPI. This action cannot be undone! Continue? (y/N): ", end="")
    if input().lower() != 'y':
        print("Upload cancelled.")
        return True
    
    return run_command("twine upload dist/*", "Uploading to PyPI")


def main():
    """Main build process"""
    print("📱 Qt Android Remote - Build Script")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
    else:
        print("\nAvailable actions:")
        print("  build       - Clean, build, and check package")
        print("  test        - Run tests and linting only")
        print("  test-upload - Upload to Test PyPI")
        print("  upload      - Upload to PyPI")
        print("  clean       - Clean build artifacts only")
        print("\nUsage: python build_package.py [action]")
        action = input("\nEnter action (or press Enter for 'build'): ").lower() or "build"
    
    if action == "clean":
        clean_build()
        print("\n✅ Clean completed!")
        return
    
    if action == "test":
        steps = [
            (run_tests, "Run tests"),
            (run_linting, "Run linting"),
        ]
        
        for step_func, step_name in steps:
            if not step_func():
                print(f"\n❌ Testing failed at step: {step_name}")
                sys.exit(1)
        
        print("\n✅ All tests and checks passed!")
        return
    
    # Standard build process
    if action in ["build", "test-upload", "upload"]:
        steps = [
            (clean_build, "Clean build artifacts"),
            (check_requirements, "Check requirements"),
            (run_tests, "Run tests"),
            (run_linting, "Run linting"),
            (build_package, "Build package"),
            (check_package, "Check package"),
        ]
        
        for step_func, step_name in steps:
            if not step_func():
                print(f"\n❌ Build failed at step: {step_name}")
                sys.exit(1)
        
        print("\n✅ Package built successfully!")
        
        # Additional actions
        if action == "test-upload":
            upload_to_test_pypi()
        elif action == "upload":
            upload_to_pypi()
    
    else:
        print(f"❌ Unknown action: {action}")
        sys.exit(1)
    
    print("\n🎉 Build process completed!")


if __name__ == "__main__":
    main()