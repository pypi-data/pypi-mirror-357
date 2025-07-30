#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

show_help() {
    cat << EOF
Release Script for DuckDuckGo MCP Server (Maintained Fork)

Usage: $0 [OPTIONS] VERSION

OPTIONS:
    -h, --help          Show this help message
    -p, --prerelease    Mark as pre-release
    -d, --dry-run       Show what would be done without actually doing it
    -t, --tag-only      Only create and push the tag (don't trigger release)

VERSION:
    Semantic version (e.g., 1.0.0, 1.0.1-alpha.1)

EXAMPLES:
    $0 1.2.3                    # Release version 1.2.3
    $0 1.2.3-beta.1 --prerelease # Release pre-release version
    $0 1.2.3 --dry-run          # Show what would happen
    $0 1.2.3 --tag-only         # Only create and push tag

EOF
}

# Parse arguments
VERSION=""
PRERELEASE=false
DRY_RUN=false
TAG_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--prerelease)
            PRERELEASE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -t|--tag-only)
            TAG_ONLY=true
            shift
            ;;
        -*)
            print_error "Unknown option $1"
            show_help
            exit 1
            ;;
        *)
            if [[ -z "$VERSION" ]]; then
                VERSION="$1"
            else
                print_error "Multiple versions specified"
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate version
if [[ -z "$VERSION" ]]; then
    print_error "Version is required"
    show_help
    exit 1
fi

if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+(\.[0-9]+)?)?$'; then
    print_error "Invalid version format: $VERSION"
    print_info "Expected format: X.Y.Z or X.Y.Z-suffix"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    print_error "Working directory is not clean. Please commit or stash your changes."
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    print_warning "You're not on the main branch (current: $CURRENT_BRANCH)"
    read -p "Continue anyway? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if tag already exists
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    print_error "Tag v$VERSION already exists"
    exit 1
fi

# Show what will be done
echo
print_info "Release Summary:"
echo "  Version: $VERSION"
echo "  Pre-release: $PRERELEASE"
echo "  Current branch: $CURRENT_BRANCH"
echo "  Tag only: $TAG_ONLY"
echo "  Dry run: $DRY_RUN"
echo

if [[ "$DRY_RUN" == "true" ]]; then
    print_info "DRY RUN - The following actions would be performed:"
    echo "  1. Update version in pyproject.toml to $VERSION"
    echo "  2. Create and push git tag v$VERSION"
    if [[ "$TAG_ONLY" == "false" ]]; then
        echo "  3. Trigger GitHub Actions release workflow"
        echo "     - Build and test Python package"
        echo "     - Build and push Docker image to ghcr.io"
        echo "     - Create GitHub release with artifacts"
        echo "     - Publish to PyPI"
    fi
    exit 0
fi

# Confirm release
echo "This will:"
echo "  1. Update version in pyproject.toml"
echo "  2. Create and push git tag v$VERSION"
if [[ "$TAG_ONLY" == "false" ]]; then
    echo "  3. Trigger automated release to PyPI, Docker, and GitHub Releases"
fi
echo

read -p "Proceed with release? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Release cancelled"
    exit 0
fi

# Update version in pyproject.toml
print_info "Updating version in pyproject.toml..."
if command -v sed >/dev/null 2>&1; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
    else
        # Linux
        sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
    fi
else
    print_error "sed command not found"
    exit 1
fi

# Commit version update
print_info "Committing version update..."
git add pyproject.toml
git commit -m "Bump version to $VERSION"

# Create and push tag
print_info "Creating tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION"

print_info "Pushing changes and tag..."
git push origin "$CURRENT_BRANCH"
git push origin "v$VERSION"

if [[ "$TAG_ONLY" == "true" ]]; then
    print_success "Tag v$VERSION created and pushed successfully!"
    print_info "To trigger the release workflow, go to:"
    print_info "https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
    exit 0
fi

print_success "Release v$VERSION initiated!"
print_info "GitHub Actions will now:"
print_info "  • Build and test the package"
print_info "  • Create GitHub release with artifacts"
print_info "  • Publish to PyPI"
print_info "  • Build and push Docker image"
print_info ""
print_info "Monitor the release at:"
print_info "https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
print_info ""
print_info "The package will be available at:"
print_info "  • PyPI: https://pypi.org/project/duckduckgo-mcp-server-maintained/$VERSION"
print_info "  • Docker: ghcr.io/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/'):$VERSION" 