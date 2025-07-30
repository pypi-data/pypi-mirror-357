---
name: Release Checklist
about: Checklist for creating a new release
title: 'Release v[VERSION]'
labels: release
assignees: ''

---

## Release Checklist for v[VERSION]

### Pre-release
- [ ] Update version in `pyproject.toml`
- [ ] Update version references in documentation
- [ ] Run full test suite: `uv run pytest`
- [ ] Run linting: `make lint`
- [ ] Test local build: `uv build`
- [ ] Test local installation: `uvx --from ./dist/ray_mcp_server-[VERSION]-py3-none-any.whl ray-mcp-server`

### Release Process
- [ ] Commit all changes
- [ ] Create and push tag: `git tag v[VERSION] && git push origin v[VERSION]`
- [ ] Verify GitHub Actions workflow completes successfully
- [ ] Verify package appears on PyPI: https://pypi.org/p/ray-mcp-server/
- [ ] Create GitHub release with release notes

### Post-release
- [ ] Test installation from PyPI: `uvx ray-mcp-server`
- [ ] Update Claude Desktop config example in README
- [ ] Update `docs/config/claude_desktop_config.json` if needed
- [ ] Announce release (if applicable)

### Release Notes Template

```markdown
## What's New in v[VERSION]

### ✨ Features
- 

### 🐛 Bug Fixes
- 

### 📚 Documentation
- 

### 🔧 Technical Changes
- 

## Installation

```bash
uvx ray-mcp-server
```

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "ray-mcp": {
      "command": "uvx",
      "args": ["ray-mcp-server"]
    }
  }
}
```
```