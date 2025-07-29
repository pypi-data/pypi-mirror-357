# Responses for Open Issues

## Issue #3: "pip install mssql-mcp-server" installs the wrong project

Thank you for reporting this. It appears there's a naming conflict on PyPI. For now, please install from source:

```bash
# Method 1: Clone and install
git clone https://github.com/RichardHan/mssql_mcp_server.git
cd mssql_mcp_server
pip install -e .

# Method 2: Using hatch (as documented in README)
pip install hatch
hatch build
pip install dist/mssql_mcp_server-*.tar.gz
```

We're investigating the PyPI package naming conflict and will update once resolved. The installation from source methods above work perfectly in the meantime.

---

## Issue #5: SQL Table Context File

Thank you for your suggestion. Could you please provide more details about what you're envisioning? For example:

- Are you looking for a way to export table schemas to a file?
- Would you like to generate documentation about table relationships?
- Do you need a context file that describes table structures for AI assistants?

Please elaborate on your use case so we can better understand how to implement this feature. You might also want to check if the current `list_resources()` functionality partially meets your needs - it already provides a list of available tables.

---

## Issue #2: want to add this to vscode

This MCP server is specifically designed for Claude Desktop and follows the Model Context Protocol specification. However, for VS Code integration, you have several options:

1. **Use existing SQL extensions**: Microsoft's official "SQL Server (mssql)" extension provides excellent SQL Server integration for VS Code

2. **Terminal integration**: You can run the MCP server from VS Code's integrated terminal

3. **Custom extension**: You could potentially build a VS Code extension that wraps this MCP server, though this would require significant development effort

For most VS Code SQL Server needs, I'd recommend using the official Microsoft SQL Server extension, which provides IntelliSense, query execution, and database exploration features.

---

## Issue #13: No module named mssql_mcp_server.__main__

This error indicates an installation or Python path issue. Please try the following:

1. **Check Python version**:
```bash
python --version  # Should be 3.11 or higher
```

2. **Clean reinstall**:
```bash
# Uninstall any existing version
pip uninstall mssql-mcp-server mssql_mcp_server

# Install from source
git clone https://github.com/RichardHan/mssql_mcp_server.git
cd mssql_mcp_server
pip install -e .
```

3. **Verify installation**:
```bash
pip list | grep mssql
```

4. **Run correctly**:
```bash
# From within the project directory
python -m mssql_mcp_server

# Or if installed globally
mssql_mcp_server
```

If you continue to experience issues, please share:
- Your operating system
- Python version (`python --version`)
- Pip version (`pip --version`)
- The complete error message and traceback

---

## Issue #15: Most of you are in the wrong repo

Could you please clarify what you mean by this? If you're referring to:

1. **Package naming confusion**: Yes, there appears to be another package on PyPI with a similar name. This repository is the correct one for the MCP (Model Context Protocol) server for SQL Server.

2. **Repository location**: This is the official repository at https://github.com/RichardHan/mssql_mcp_server

3. **Installation confusion**: Due to the PyPI naming issue, please install from source as described in the README

If you meant something else, please provide more context so we can address your concern properly.