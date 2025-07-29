# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Fixed missing `__main__.py` file for proper module execution (Issue #13)
- Added support for custom SQL Server port via `MSSQL_PORT` environment variable (Issue #8)
- Added Windows Authentication support via `MSSQL_WINDOWS_AUTH` environment variable (Issue #7)
- Added SQL Server LocalDB support - automatically detects and formats LocalDB connections (Issue #6)
- Added Docker support with Dockerfile and docker-compose example (Issue #4)
- Added comprehensive `.gitignore` and `.dockerignore` files
- Added encryption support for Azure SQL Database connections (Issue #11)
- Enhanced connection configuration with debug logging (Issue #12)
- Improved test_connection.py script to use the same configuration as the server
- Added proper package metadata in pyproject.toml for pip installation (Issue #3)

### Fixed
- **Security**: Fixed SQL injection vulnerability in table name handling by adding proper validation and escaping
- Azure SQL connections now automatically enable encryption and use correct TDS version
- Connection configuration now properly uses all environment variables with clear logging

### Changed
- Updated README with comprehensive configuration documentation including:
  - LocalDB configuration examples
  - Azure SQL configuration examples
  - Docker usage instructions
  - Windows Authentication setup

### Security
- Added table name validation using regex pattern matching
- Implemented proper SQL identifier escaping with square brackets
- Tables names are now restricted to alphanumeric characters, underscores, and single dots (for schema.table format)

## [0.1.0] - 2025-01-05

### Added
- Initial release with basic MSSQL MCP server functionality
- List tables as resources
- Read table contents
- Execute SQL queries
- Environment-based configuration