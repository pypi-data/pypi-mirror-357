# GitHub Issue Responses

## Issue #8: Support MSSQL_PORT
**Status: FIXED ✅**

This has been implemented! You can now use the `MSSQL_PORT` environment variable:

```bash
MSSQL_PORT=1433  # Or any custom port
```

The implementation includes:
- Default port of 1433 if not specified
- Proper integer conversion with error handling
- Full support for non-standard SQL Server ports

Example configuration:
```json
{
  "env": {
    "MSSQL_SERVER": "localhost",
    "MSSQL_PORT": "1433",
    "MSSQL_DATABASE": "your_database"
  }
}
```

Closing this issue as it's been fully implemented and tested.

---

## Issue #7: Windows Authentication
**Status: FIXED ✅**

Windows Authentication is now fully supported! Simply set:

```bash
MSSQL_WINDOWS_AUTH=true
```

When enabled:
- No need to provide MSSQL_USER or MSSQL_PASSWORD
- The server will use Windows integrated authentication
- Works with both standard SQL Server and LocalDB

Example configuration:
```json
{
  "env": {
    "MSSQL_SERVER": "localhost",
    "MSSQL_DATABASE": "your_database",
    "MSSQL_WINDOWS_AUTH": "true"
  }
}
```

Closing this issue as it's been implemented and tested.

---

## Issue #6: SQL Local DB
**Status: FIXED ✅**

LocalDB support has been implemented! The server now automatically detects and handles LocalDB connections:

```bash
MSSQL_SERVER=(localdb)\MSSQLLocalDB
MSSQL_DATABASE=your_database
MSSQL_WINDOWS_AUTH=true  # LocalDB typically uses Windows Auth
```

The implementation:
- Automatically detects LocalDB format `(localdb)\instancename`
- Converts to pymssql-compatible format
- Works seamlessly with Windows Authentication

Closing this issue as LocalDB support is now fully functional.

---

## Issue #11: Azure SQL unable to connect seems to be due to encryption
**Status: FIXED ✅**

Azure SQL Database connections are now fully supported with automatic encryption handling!

The server automatically:
- Detects Azure SQL connections (by checking for `.database.windows.net`)
- Enables encryption automatically for Azure SQL
- Sets the required TDS version (7.4)

Configuration example:
```bash
MSSQL_SERVER=your-server.database.windows.net
MSSQL_DATABASE=your_database
MSSQL_USER=your_username
MSSQL_PASSWORD=your_password
# Encryption is automatically enabled for Azure SQL
```

For non-Azure connections, you can control encryption with:
```bash
MSSQL_ENCRYPT=true  # or false
```

Closing this issue as Azure SQL support with proper encryption is now implemented.

---

## Issue #4: Docker?
**Status: FIXED ✅**

Docker support has been added! The repository now includes:

- `Dockerfile` for containerizing the MCP server
- `docker-compose.yml` with SQL Server 2019 for testing
- Comprehensive `Makefile` with Docker commands

Quick start:
```bash
# Build and start containers
make docker-build
make docker-up

# Run tests in Docker
make docker-test

# Tear down
make docker-down
```

Docker environment variables are fully configurable. See the README for complete Docker documentation.

Closing this issue as Docker support is now available.

---

## Issue #12: Tries to connect to localhost even when MSSQL_SERVER is explicitly specified
**Status: FIXED ✅**

This issue has been resolved! The server now:

1. Properly reads the `MSSQL_SERVER` environment variable
2. Logs the server being used for debugging
3. Only defaults to "localhost" if MSSQL_SERVER is not set

The fix includes enhanced logging:
```
INFO - MSSQL_SERVER environment variable: your-server-value
INFO - Using server: your-server-value
```

If you're still experiencing issues, check:
- Environment variable is properly set in your configuration
- No typos in the variable name (MSSQL_SERVER)
- The value is correctly quoted in JSON config files

Closing this issue as the server configuration is now working correctly.

---

## Issue #3: "pip install mssql-mcp-server" installs the wrong project
**Status: NEEDS INVESTIGATION**

Great news! The package is now available on PyPI. You can install it directly:

```bash
pip install microsoft_sql_server_mcp
```

Alternatively, you can still install from source:
```bash
git clone https://github.com/RichardHan/mssql_mcp_server.git
cd mssql_mcp_server
pip install -e .
```

---

## Issue #5: SQL Table Context File
**Status: NEEDS CLARIFICATION**

Could you provide more details about what you're looking for? Are you asking for:
- A way to export table schemas to a file?
- Context about table relationships?
- Documentation generation for tables?

Please provide more information so we can better understand and address your needs.

---

## Issue #2: want to add this to vscode
**Status: DOCUMENTATION NEEDED**

While this MCP server is designed for Claude Desktop, you could potentially use it with VS Code through:

1. Terminal integration - run queries through VS Code terminal
2. Custom extension development
3. Integration with existing SQL extensions

For direct VS Code integration, you might want to look at existing SQL Server extensions like "SQL Server (mssql)" by Microsoft.

---

## Issue #13: No module named mssql_mcp_server.__main__
**Status: NEEDS INVESTIGATION**

This error suggests an installation or module structure issue. Please try:

1. Ensure you're using Python 3.11+
2. Reinstall using:
```bash
pip uninstall mssql-mcp-server
pip install -e .  # From the repository directory
```

3. Run with:
```bash
python -m mssql_mcp_server
```

If the issue persists, please share:
- Your Python version
- Installation method used
- Full error traceback

---

## Issue #15: Most of you are in the wrong repo
**Status: NEEDS CLARIFICATION**

Could you please clarify what you mean? If there's confusion about:
- Repository location
- Package naming
- Installation source

Please let us know so we can provide proper guidance or update documentation.