#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
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

print_info "Manual First Release to PyPI"
print_info "This script will help you do the initial release manually"
echo

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    print_error "pyproject.toml not found. Run this script from the project root."
    exit 1
fi

# Check if build tools are installed
if ! command -v python >/dev/null 2>&1; then
    print_error "Python not found. Please install Python."
    exit 1
fi

print_info "Installing build tools..."
python -m pip install --upgrade build twine

print_info "Building the package..."
python -m build

print_info "Package built successfully!"
print_info "Contents of dist/:"
ls -la dist/

echo
print_warning "NEXT STEPS:"
echo "1. Go to https://pypi.org and create an account if you don't have one"
echo "2. Create an API token at https://pypi.org/manage/account/token/"
echo "3. Run: python -m twine upload dist/*"
echo "4. Enter your username: __token__"
echo "5. Enter your password: <your-api-token>"
echo
print_info "After the manual upload succeeds:"
echo "1. Go to https://pypi.org/manage/project/duckduckgo-mcp-server-maintained/settings/publishing/"
echo "2. Add trusted publisher with these EXACT settings:"
echo "   - Owner: scalabrese"
echo "   - Repository: duckduckgo-mcp-server"  
echo "   - Workflow: release.yml"
echo "   - Environment: pypi"
echo "3. Then future releases will work automatically!"

echo
read -p "Press Enter to continue with manual upload, or Ctrl+C to stop..."

print_info "Starting manual upload..."
python -m twine upload dist/*

if [[ $? -eq 0 ]]; then
    print_success "Manual upload successful!"
    print_info "Your package is now available at:"
    print_info "https://pypi.org/project/duckduckgo-mcp-server-maintained/"
    echo
    print_info "Now set up trusted publishing for future releases:"
    print_info "https://pypi.org/manage/project/duckduckgo-mcp-server-maintained/settings/publishing/"
else
    print_error "Upload failed. Check the error message above."
    exit 1
fi
