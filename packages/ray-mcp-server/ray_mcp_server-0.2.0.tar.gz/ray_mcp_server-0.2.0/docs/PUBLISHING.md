# 🚀 Publishing Guide

This document describes how to publish `ray-mcp-server` to PyPI using GitHub Actions.

## 🔧 Setup Requirements

### 1. GitHub Repository Secrets

You'll need to configure these secrets in your GitHub repository settings:

**For TestPyPI:**
- `TEST_PYPI_API_TOKEN` - Your TestPyPI API token

**For PyPI (Production):**
The workflow uses PyPI's trusted publishing feature, so no API token is needed. However, you need to configure trusted publishing on PyPI.

### 2. PyPI Trusted Publishing Setup

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher with these details:
   - **PyPI Project Name**: `ray-mcp-server`
   - **Owner**: `vaskin` (your GitHub username)
   - **Repository name**: `ray-mcp`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`

### 3. GitHub Environments

Create these environments in your GitHub repository settings:

**Environment: `pypi`**
- Protection rules: Required reviewers (optional)
- Environment URL: `https://pypi.org/p/ray-mcp-server`

**Environment: `testpypi`**
- Add secret: `TEST_PYPI_API_TOKEN`
- Environment URL: `https://test.pypi.org/p/ray-mcp-server`

## 📦 Publishing Methods

### Method 1: Automatic Publishing (Recommended)

**For production releases:**
1. Create a new tag and push it:
   ```bash
   git tag v0.2.1
   git push origin v0.2.1
   ```

2. The workflow will automatically:
   - Build the package
   - Publish to PyPI
   - Create a GitHub release
   - Upload signed artifacts

**For GitHub releases:**
1. Go to GitHub > Releases > Create a new release
2. Choose or create a tag (e.g., `v0.2.1`)
3. Publish the release
4. The workflow will automatically publish to PyPI

### Method 2: Manual Publishing

**To TestPyPI:**
1. Go to GitHub Actions > Build and Publish
2. Click "Run workflow"
3. Select `testpypi` as target
4. Click "Run workflow"

**To PyPI:**
1. Go to GitHub Actions > Build and Publish
2. Click "Run workflow"
3. Select `pypi` as target
4. Click "Run workflow"

## 🔍 Verification

After publishing, verify the package:

**From PyPI:**
```bash
uvx ray-mcp-server --help
```

**From TestPyPI:**
```bash
uvx --index-url https://test.pypi.org/simple/ ray-mcp-server --help
```

## 📋 Release Checklist

Before creating a release:

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` (if exists)
- [ ] Run tests locally: `uv run pytest`
- [ ] Run linting: `make lint`
- [ ] Commit all changes
- [ ] Create and push tag
- [ ] Verify the GitHub Action completes successfully
- [ ] Test installation with uvx
- [ ] Update Claude Desktop config with new version

## 🛠️ Troubleshooting

**Build fails:**
- Check Python version compatibility (>=3.12)
- Ensure all dependencies are in `pyproject.toml`
- Verify uv.lock is committed

**Trusted publishing fails:**
- Verify PyPI trusted publishing is configured correctly
- Check the repository name, workflow name, and environment name match exactly
- Ensure the workflow runs from the correct branch/tag

**Manual publishing fails:**
- Verify GitHub secrets are set correctly
- Check environment configuration
- Ensure API tokens have correct permissions

## 🔄 Updating Versions

Version format: `MAJOR.MINOR.PATCH` (e.g., `0.2.1`)

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.2.1"
   ```

2. Commit the change:
   ```bash
   git add pyproject.toml
   git commit -m "bump: version 0.2.1"
   ```

3. Create and push tag:
   ```bash
   git tag v0.2.1
   git push origin main
   git push origin v0.2.1
   ```

The workflow will handle the rest automatically! 🎉