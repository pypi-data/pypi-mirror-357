# Release Guide

This document describes how to release the DuckDuckGo MCP Server (Maintained Fork) to multiple free artifact hosting platforms.

## About This Fork

This is a maintained fork of the original [duckduckgo-mcp-server](https://github.com/nickclyde/duckduckgo-mcp-server) project by Nick Clyde. This fork includes:

- Updated dependencies and security patches
- Enhanced features and bug fixes
- Active maintenance and support
- Improved release automation

The package is published as `duckduckgo-mcp-server-maintained` to distinguish it from the original while maintaining attribution.

## Release Destinations

The release process publishes to these free hosting platforms:

1. **PyPI** (Python Package Index) - Python packages
2. **GitHub Container Registry** - Docker images  
3. **GitHub Releases** - Source code and binaries

## Prerequisites

### 1. PyPI Trusted Publishing Setup

To enable secure publishing to PyPI without API tokens:

1. Go to [PyPI](https://pypi.org) and create an account if you don't have one
2. Create the project on PyPI (can be done on first release)
3. Go to your project settings → Publishing → Add a new trusted publisher
4. Configure:
   - **PyPI project name**: `duckduckgo-mcp-server-maintained`
   - **Owner**: Your GitHub username
   - **Repository name**: `duckduckgo-mcp-server`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`

### 2. GitHub Repository Settings

Ensure your repository has:
- **Actions enabled** (Settings → Actions → General)
- **Packages write permission** (Settings → Actions → General → Workflow permissions)
- **Environment protection** (Settings → Environments → Create `pypi` environment)

### 3. Local Development Setup

Ensure you have:
- Git configured with your credentials
- Python 3.10+ installed
- `uv` package manager installed

## Release Process

### Option 1: Using the Release Script (Recommended)

The easiest way to release is using the provided script:

```bash
# Basic release
./scripts/release.sh 1.2.3

# Pre-release
./scripts/release.sh 1.2.3-beta.1 --prerelease

# Dry run (see what would happen)
./scripts/release.sh 1.2.3 --dry-run

# Create tag only (manual workflow trigger)
./scripts/release.sh 1.2.3 --tag-only
```

### Option 2: Manual Release Process

1. **Update version** in `pyproject.toml`
2. **Commit changes**: `git commit -am "Bump version to X.Y.Z"`
3. **Create tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. **Push**: `git push origin main && git push origin vX.Y.Z`

### Option 3: GitHub UI Release

1. Go to your repository → Releases → Draft a new release
2. Create a new tag (e.g., `v1.2.3`)
3. Generate release notes
4. Publish release

This will trigger the same automated workflow.

## Release Workflow

When you create a release (by any method above), the following happens automatically:

### 1. Validation & Testing
- Validates version format
- Tests on Python 3.10, 3.11, 3.12, 3.13
- Builds Python package

### 2. Docker Image Build
- Builds multi-arch Docker image (AMD64, ARM64)
- Publishes to GitHub Container Registry
- Tags: `latest`, version number, `main`

### 3. GitHub Release
- Creates GitHub release with auto-generated changelog
- Attaches Python wheel and source distributions
- Includes installation instructions

### 4. PyPI Publication
- Publishes Python package to PyPI
- Uses trusted publishing (no API keys needed)
- Available via `pip install duckduckgo-mcp-server-maintained`

## Version Numbers

Use [Semantic Versioning](https://semver.org/):

- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes, backward compatible

### Pre-release versions:
- `1.0.0-alpha.1`: Alpha releases
- `1.0.0-beta.1`: Beta releases  
- `1.0.0-rc.1`: Release candidates

## Monitoring Releases

### GitHub Actions
Monitor release progress at:
`https://github.com/YOUR_USERNAME/duckduckgo-mcp-server/actions`

### Release Artifacts
After successful release, packages are available at:

- **PyPI**: https://pypi.org/project/duckduckgo-mcp-server-maintained/
- **Docker**: `ghcr.io/YOUR_USERNAME/duckduckgo-mcp-server:VERSION`
- **GitHub**: Repository releases page

## Installation Instructions for Users

### Python Package (PyPI)
```bash
# Latest version
pip install duckduckgo-mcp-server-maintained

# Specific version  
pip install duckduckgo-mcp-server-maintained==1.2.3

# Using uvx (recommended)
uvx duckduckgo-mcp-server-maintained
```

### Docker Image (GitHub Container Registry)
```bash
# Latest version
docker pull ghcr.io/YOUR_USERNAME/duckduckgo-mcp-server:latest

# Specific version
docker pull ghcr.io/YOUR_USERNAME/duckduckgo-mcp-server:1.2.3

# Run container
docker run -it ghcr.io/YOUR_USERNAME/duckduckgo-mcp-server:latest
```

### Source Code (GitHub Releases)
```bash
# Download and extract from GitHub releases
wget https://github.com/YOUR_USERNAME/duckduckgo-mcp-server/archive/v1.2.3.tar.gz
tar -xzf v1.2.3.tar.gz
cd duckduckgo-mcp-server-1.2.3
```

## Troubleshooting

### Release Failed
1. Check the GitHub Actions logs
2. Ensure all prerequisites are met
3. Verify PyPI trusted publishing is configured
4. Check if the version tag already exists

### PyPI Publishing Issues
- Ensure trusted publishing is set up correctly
- Check that the environment name matches (`pypi`)
- Verify repository and workflow names are exact

### Docker Issues
- GitHub Container Registry is automatically available
- Ensure the repository has packages write permission
- Multi-arch builds require GitHub Actions (automatic)

### Version Conflicts
- Check if the version already exists on PyPI
- Ensure the git tag doesn't already exist
- Use `--dry-run` to preview changes

## Advanced Configuration

### Custom Release Notes
Edit the workflow file to customize release notes generation:
```yaml
# In .github/workflows/release.yml
- name: Generate changelog
  run: |
    # Add your custom changelog generation logic
```

### Additional Platforms
The workflow can be extended to publish to:
- **conda-forge**: For conda packages
- **Docker Hub**: Alternative to GitHub Container Registry
- **npm**: If you add JavaScript bindings

### Security
- Uses GitHub's OIDC tokens for PyPI (no secrets needed)
- Docker images are signed and scanned
- All builds run in isolated GitHub Actions environments

## Cost

All platforms used are **completely free**:
- ✅ **PyPI**: Free for open source
- ✅ **GitHub Container Registry**: Free for public repositories  
- ✅ **GitHub Releases**: Free for public repositories
- ✅ **GitHub Actions**: 2000 minutes/month free

## Support

For issues with the release process:
1. Check this documentation
2. Review GitHub Actions logs
3. Open an issue in the repository
4. Check platform-specific documentation (PyPI, GitHub) 

print_info "The package will be available at:"
print_info "  • PyPI: https://pypi.org/project/duckduckgo-mcp-server-maintained/$VERSION" 