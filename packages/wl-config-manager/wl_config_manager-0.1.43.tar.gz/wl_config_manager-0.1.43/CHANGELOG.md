# Changelog

All notable changes to the config_manager package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.37]

### Added
- Support for `.env` files to keep secrets out of version control
  - Automatically loads `.env` file from config directory
  - Supports `KEY=VALUE` format with comments and quoted values
  - Converts double underscore to nested keys (e.g., `DATABASE__PASSWORD` → `database.password`)
  - Type conversion for booleans, integers, and floats
  - New `load_dotenv` parameter in `ConfigManager` constructor (default: `True`)
  - `--no-dotenv` CLI flag to disable .env loading
- `__main__.py` module to allow running as `python -m config_manager`
- Comprehensive documentation for .env file usage and best practices

### Fixed
- Fixed `NameError` in `cli.py` where `Config` was used instead of `ConfigManager`
- Corrected all import statements in CLI module
- Fixed inconsistent class naming throughout the codebase

### Changed
- Enhanced error messages to show masked values for sensitive keys (password/secret)
- Improved logging to show when .env files are loaded

## [1.0.0] - 2024-061-04

### Added
- Initial release of config_manager package
- Multi-format configuration file support (YAML, JSON, INI)
- Dot notation access for nested configuration values
- Environment variable override support with configurable prefix
- Comprehensive CLI with the following commands:
  - `get` - Retrieve configuration values
  - `set` - Set configuration values
  - `create` - Create new configuration files
  - `validate` - Validate configuration against required keys
  - `convert` - Convert between configuration formats
  - `list` - List configuration values
  - `env` - Load configuration from environment variables
- Search paths functionality for auto-discovering config files
- Deep merge capability for configuration precedence
- Type conversion for environment variables
- Validation for required configuration keys
- Iterable namespace objects for better developer experience
- Comprehensive error handling with custom exception types:
  - `ConfigError` - Base exception
  - `ConfigFileError` - File-related errors
  - `ConfigFormatError` - Format parsing errors
  - `ConfigValidationError` - Validation errors
- File logging support with configurable log levels
- Class methods for creating configs from dictionaries or environment
- Reload functionality to refresh configuration from files

### Security
- Designed to keep sensitive data separate from configuration structure
- Support for environment variable overrides for production deployments

## Development Notes

### Versioning Strategy
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality additions
- PATCH version for backwards-compatible bug fixes

### Future Considerations
- Schema validation support
- Configuration file watching and auto-reload
- Encrypted secrets support
- Configuration inheritance/includes
- Remote configuration sources (HTTP, S3, etc.)
- Configuration templates with variable substitution
- Type hints and better IDE support
- Async support for configuration loading
- Plugin system for custom configuration sources