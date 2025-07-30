#!/bin/bash

# 🚀 Cognify SDK PyPI Upload Script
# This script automates the process of building and uploading to PyPI

set -e  # Exit on any error

echo "🚀 Cognify Python SDK - PyPI Upload Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed"
        exit 1
    fi
    
    if ! python -m pip show build &> /dev/null; then
        print_warning "Installing build package..."
        python -m pip install --upgrade build
    fi
    
    if ! python -m pip show twine &> /dev/null; then
        print_warning "Installing twine package..."
        python -m pip install --upgrade twine
    fi
    
    print_success "All requirements satisfied"
}

# Clean previous builds
clean_build() {
    print_status "Cleaning previous builds..."
    rm -rf dist/ build/ *.egg-info/
    print_success "Build directory cleaned"
}

# Build the package
build_package() {
    print_status "Building package..."
    python -m build
    
    if [ $? -eq 0 ]; then
        print_success "Package built successfully"
        echo "Built files:"
        ls -la dist/
    else
        print_error "Package build failed"
        exit 1
    fi
}

# Check package
check_package() {
    print_status "Checking package with twine..."
    python -m twine check dist/*
    
    if [ $? -eq 0 ]; then
        print_success "Package check passed"
    else
        print_error "Package check failed"
        exit 1
    fi
}

# Upload to TestPyPI
upload_test() {
    print_status "Uploading to TestPyPI..."
    print_warning "You will need your TestPyPI API token"
    print_warning "Username: __token__"
    print_warning "Password: [your-testpypi-api-token]"
    
    python -m twine upload --repository testpypi dist/*
    
    if [ $? -eq 0 ]; then
        print_success "Upload to TestPyPI successful"
        echo "Test your package:"
        echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cognify-sdk"
    else
        print_error "Upload to TestPyPI failed"
        exit 1
    fi
}

# Upload to PyPI
upload_production() {
    print_status "Uploading to PyPI..."
    print_warning "You will need your PyPI API token"
    print_warning "Username: __token__"
    print_warning "Password: [your-pypi-api-token]"
    
    read -p "Are you sure you want to upload to production PyPI? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python -m twine upload dist/*
        
        if [ $? -eq 0 ]; then
            print_success "Upload to PyPI successful!"
            echo "Your package is now available at: https://pypi.org/project/cognify-sdk/"
            echo "Install with: pip install cognify-sdk"
        else
            print_error "Upload to PyPI failed"
            exit 1
        fi
    else
        print_warning "Upload to PyPI cancelled"
    fi
}

# Main execution
main() {
    echo "Select upload target:"
    echo "1) TestPyPI (recommended for testing)"
    echo "2) PyPI (production)"
    echo "3) Both (TestPyPI first, then PyPI)"
    read -p "Enter your choice (1-3): " choice
    
    check_requirements
    clean_build
    build_package
    check_package
    
    case $choice in
        1)
            upload_test
            ;;
        2)
            upload_production
            ;;
        3)
            upload_test
            echo ""
            upload_production
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    print_success "Upload process completed!"
}

# Run main function
main
