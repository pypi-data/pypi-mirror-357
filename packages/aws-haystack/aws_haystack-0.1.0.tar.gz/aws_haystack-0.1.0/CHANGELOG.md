# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-06-23

### Added
- Initial release of Haystack CLI
- AWS SSO authentication with device flow
- CloudFormation stack search across multiple AWS accounts and regions
- Intelligent role selection (admin > power > first available)
- Parallel search with progress bars
- Smart caching of SSO tokens (8+ hour validity)
- Case-insensitive partial matching for stack names
- Automatic deduplication of results
- Rich CLI output with tables and progress indicators
- Configuration management (save SSO settings)
- Clear command to reset cached credentials

### Features
- **One-time setup**: Configure SSO URL once, authenticate via browser
- **Smart search**: Partial, case-insensitive stack name matching
- **Fast parallel search**: Search all accounts/regions simultaneously
- **Efficient role usage**: One optimal role per account
- **Clean output**: Rich tables with stack details
- **Progress tracking**: Real-time progress bars for all operations
- **Secure caching**: Token-based authentication with auto-refresh

### Supported Environments
- Python 3.8+
- AWS Identity Center (SSO) required
- Cross-platform (macOS, Linux, Windows)