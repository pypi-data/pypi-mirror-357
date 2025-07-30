#!/usr/bin/env python3
"""
Quick start script for PyPI upload process.
This script guides you through the entire process step by step.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def print_step(step, description):
    """Print a step with formatting."""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {description}")
    print('='*60)

def print_success(message):
    """Print success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print error message."""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message."""
    print(f"⚠️ {message}")

def print_info(message):
    """Print info message."""
    print(f"ℹ️ {message}")

def check_pyproject_toml():
    """Check if pyproject.toml exists and is properly configured."""
    if not Path("pyproject.toml").exists():
        print_error("pyproject.toml not found!")
        return False
    
    with open("pyproject.toml", "r") as f:
        content = f.read()
        
    required_fields = ["name", "version", "description", "authors"]
    missing_fields = []
    
    for field in required_fields:
        if field not in content:
            missing_fields.append(field)
    
    if missing_fields:
        print_error(f"Missing required fields in pyproject.toml: {missing_fields}")
        return False
    
    print_success("pyproject.toml is properly configured")
    return True

def install_build_tools():
    """Install required build tools."""
    print_info("Installing build tools...")
    
    tools = ["build", "twine"]
    for tool in tools:
        success, stdout, stderr = run_command(f"pip show {tool}")
        if not success:
            print_info(f"Installing {tool}...")
            success, stdout, stderr = run_command(f"pip install --upgrade {tool}")
            if success:
                print_success(f"{tool} installed successfully")
            else:
                print_error(f"Failed to install {tool}: {stderr}")
                return False
        else:
            print_success(f"{tool} is already installed")
    
    return True

def clean_build_directory():
    """Clean previous build artifacts."""
    print_info("Cleaning build directory...")
    
    dirs_to_clean = ["dist", "build", "*.egg-info"]
    for dir_pattern in dirs_to_clean:
        success, stdout, stderr = run_command(f"rm -rf {dir_pattern}")
    
    print_success("Build directory cleaned")

def build_package():
    """Build the package."""
    print_info("Building package...")
    
    success, stdout, stderr = run_command("python -m build")
    if success:
        print_success("Package built successfully")
        
        # List built files
        success, stdout, stderr = run_command("ls -la dist/")
        if success:
            print_info("Built files:")
            print(stdout)
        return True
    else:
        print_error(f"Build failed: {stderr}")
        return False

def check_package():
    """Check package with twine."""
    print_info("Checking package with twine...")
    
    success, stdout, stderr = run_command("python -m twine check dist/*")
    if success:
        print_success("Package check passed")
        return True
    else:
        print_error(f"Package check failed: {stderr}")
        return False

def upload_to_testpypi():
    """Upload to TestPyPI."""
    print_info("Uploading to TestPyPI...")
    print_warning("You will need your TestPyPI API token")
    print_warning("Username: __token__")
    print_warning("Password: [your-testpypi-api-token]")
    
    input("\nPress Enter when ready to upload to TestPyPI...")
    
    success, stdout, stderr = run_command("python -m twine upload --repository testpypi dist/*", check=False)
    if success:
        print_success("Upload to TestPyPI successful!")
        print_info("Test your package with:")
        print("pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cognify-sdk")
        return True
    else:
        print_error(f"Upload to TestPyPI failed: {stderr}")
        return False

def upload_to_pypi():
    """Upload to PyPI."""
    print_info("Uploading to PyPI...")
    print_warning("You will need your PyPI API token")
    print_warning("Username: __token__")
    print_warning("Password: [your-pypi-api-token]")
    
    confirm = input("\nAre you sure you want to upload to production PyPI? (y/N): ")
    if confirm.lower() != 'y':
        print_warning("Upload to PyPI cancelled")
        return False
    
    success, stdout, stderr = run_command("python -m twine upload dist/*", check=False)
    if success:
        print_success("Upload to PyPI successful!")
        print_info("Your package is now available at: https://pypi.org/project/cognify-sdk/")
        print_info("Install with: pip install cognify-sdk")
        return True
    else:
        print_error(f"Upload to PyPI failed: {stderr}")
        return False

def main():
    """Main function."""
    print("🚀 Cognify Python SDK - PyPI Upload Quick Start")
    print("=" * 60)
    
    # Step 1: Check project configuration
    print_step(1, "Checking project configuration")
    if not check_pyproject_toml():
        print_error("Please fix pyproject.toml configuration first")
        return False
    
    # Step 2: Install build tools
    print_step(2, "Installing build tools")
    if not install_build_tools():
        print_error("Failed to install build tools")
        return False
    
    # Step 3: Clean build directory
    print_step(3, "Cleaning build directory")
    clean_build_directory()
    
    # Step 4: Build package
    print_step(4, "Building package")
    if not build_package():
        print_error("Failed to build package")
        return False
    
    # Step 5: Check package
    print_step(5, "Checking package")
    if not check_package():
        print_error("Package check failed")
        return False
    
    # Step 6: Choose upload target
    print_step(6, "Upload package")
    print("Choose upload target:")
    print("1) TestPyPI only (recommended for first time)")
    print("2) PyPI only (production)")
    print("3) Both TestPyPI and PyPI")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        upload_to_testpypi()
    elif choice == "2":
        upload_to_pypi()
    elif choice == "3":
        if upload_to_testpypi():
            upload_to_pypi()
    else:
        print_error("Invalid choice")
        return False
    
    print_success("PyPI upload process completed!")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
