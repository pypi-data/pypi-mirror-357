# Fork Setup Guide

This guide helps you complete the setup for publishing your maintained fork of the DuckDuckGo MCP Server.

## Quick Setup Checklist

### 1. Update Personal Information

Edit `pyproject.toml` and replace the placeholder information:

```toml
authors = [
    { name = "Nick Clyde", email = "nick@clyde.tech" },
    { name = "Your Name", email = "your.email@example.com" }  # ← Update this
]
```

### 2. Verify Repository URLs

Check that all repository URLs in `pyproject.toml` point to your fork:

```toml
[project.urls]
Homepage = "https://github.com/scalabrese/duckduckgo-mcp-server"  # ← Verify this
Issues = "https://github.com/scalabrese/duckduckgo-mcp-server/issues"  # ← Verify this
```

### 3. Set Up PyPI Account

1. Create account at [PyPI.org](https://pypi.org)
2. Go to Account Settings → Publishing → Add a new trusted publisher
3. Configure:
   - **PyPI project name**: `duckduckgo-mcp-server-maintained`
   - **Owner**: `scalabrese` (your GitHub username)
   - **Repository name**: `duckduckgo-mcp-server`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`

### 4. Configure GitHub Repository

In your GitHub repository settings:

1. **Enable Actions**: Settings → Actions → General → Allow all actions
2. **Set Permissions**: Settings → Actions → General → Workflow permissions → Read and write permissions
3. **Create Environment**: Settings → Environments → New environment → Name: `pypi`

### 5. Test the Setup

```bash
# Test the release script (dry run)
./scripts/release.sh 0.2.0 --dry-run

# When ready, do your first release
./scripts/release.sh 0.2.0
```

## Package Name Strategy

The fork uses `duckduckgo-mcp-server-maintained` as the package name because:

✅ **Clear Attribution**: Keeps reference to original project  
✅ **Distinguishable**: Users know it's a maintained version  
✅ **No Conflicts**: Won't conflict with original on PyPI  
✅ **Professional**: Indicates active maintenance  

## Alternative Names Considered

If you prefer a different name, you could use:
- `duckduckgo-mcp-server-plus`
- `duckduckgo-mcp-server-enhanced`  
- `duckduckgo-mcp-server-updated`
- `scalabrese-duckduckgo-mcp-server`

To change the name, update these files:
- `pyproject.toml` → `name` field
- `.github/workflows/release.yml` → PyPI URLs
- `scripts/release.sh` → PyPI URLs  
- `RELEASE.md` → Documentation
- `README.md` → Installation instructions

## First Release

Your first release should probably be `0.2.0` to indicate:
- It's based on the original `0.1.1`
- It includes your enhancements
- It's the first release of your maintained fork

## Communication

Consider:
1. **Opening an issue** in the original repo to let the author know about your maintained fork
2. **Adding a link** in your fork's README to the original project
3. **Contributing back** improvements that could benefit the original project

## Support

If you run into issues:
1. Check the detailed `RELEASE.md` guide
2. Review GitHub Actions logs
3. Verify PyPI trusted publishing setup
4. Test with `--dry-run` first 