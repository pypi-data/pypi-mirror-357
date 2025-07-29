# Publishing to PyPI

This guide explains how to publish the mssql-mcp-server package to PyPI using GitHub Actions.

## Prerequisites

1. PyPI account at https://pypi.org
2. (Optional) Test PyPI account at https://test.pypi.org

## Setup Instructions

### 1. Configure PyPI Trusted Publishing

Modern PyPI uses "Trusted Publishing" which is more secure than API tokens. Here's how to set it up:

1. Go to your PyPI account settings
2. Navigate to "Publishing" → "Add a new publisher"
3. Fill in:
   - **PyPI Project Name**: `microsoft_sql_server_mcp`
   - **Owner**: `RichardHan`
   - **Repository**: `mssql_mcp_server`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi` (for production) or `test-pypi` (for testing)

### 2. GitHub Repository Settings

1. Go to Settings → Environments
2. Create two environments:
   - `pypi` - for production PyPI
   - `test-pypi` - for Test PyPI

No secrets are needed when using Trusted Publishing!

## Publishing Process

### Automatic Publishing (Recommended)

1. **Create a new release**:
   ```bash
   # Update version in pyproject.toml
   git add pyproject.toml
   git commit -m "Bump version to X.Y.Z"
   
   # Create and push a tag
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub will automatically**:
   - Create a draft release
   - Build the package
   - Publish to PyPI when you publish the release

### Manual Publishing

1. Go to Actions → "Publish to PyPI"
2. Click "Run workflow"
3. Choose to publish to Test PyPI first (recommended)
4. If Test PyPI works, run again with Test PyPI disabled

## Workflow Files

- `.github/workflows/ci.yml` - Runs tests on every push/PR
- `.github/workflows/publish.yml` - Publishes to PyPI on release
- `.github/workflows/release.yml` - Creates GitHub releases from tags

## Testing Before Publishing

1. **Test locally**:
   ```bash
   # Build the package
   hatch build
   
   # Check the distribution
   twine check dist/*
   
   # Test installation
   pip install dist/mssql_mcp_server-*.whl
   ```

2. **Test on Test PyPI**:
   ```bash
   # Install from Test PyPI
   pip install -i https://test.pypi.org/simple/ microsoft_sql_server_mcp
   ```

## Troubleshooting

### Package Name Conflicts

If `microsoft_sql_server_mcp` is taken on PyPI, you may need to:
1. Use a different name (e.g., `mssql-mcp`, `mcp-server-mssql`)
2. Contact PyPI support if you believe you should own the name

### Build Failures

Check that:
- `pyproject.toml` is properly formatted
- All dependencies are specified correctly
- Version number follows semantic versioning (X.Y.Z)

### Publishing Failures

1. Verify Trusted Publishing is configured correctly
2. Check environment names match exactly
3. Ensure workflow file name matches configuration

## Version Management

Follow semantic versioning:
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes

Update version in:
- `pyproject.toml`
- `src/mssql_mcp_server/__init__.py` (if version is defined there)

## Security Notes

- Never commit PyPI tokens to the repository
- Use Trusted Publishing instead of API tokens
- Review all dependencies before publishing
- Run security scans before each release