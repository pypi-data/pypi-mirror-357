# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet

## [1.0.0] - 2024-06-24

### Added
- 🎯 **Core Analysis Modules**
  - DNS resolution and reverse DNS lookup
  - Comprehensive DNS records fetching (A, AAAA, MX, NS, TXT, CNAME, SOA)
  - WHOIS information for domains and IP addresses
  - IP geolocation with detailed geographic information

- 🔒 **Security Analysis**
  - SSL/TLS certificate validation and grading
  - Security headers analysis (HSTS, CSP, X-Frame-Options, etc.)
  - WAF detection for multiple providers
  - Multi-provider blacklist checking
  - Overall security scoring system

- 🌐 **Connectivity & Performance**
  - Ping functionality for domains and IPs
  - HTTP status code checking
  - Response time measurement
  - TCP port connectivity testing
  - Network traceroute analysis
  - HTTP headers and redirect chain analysis

- 💻 **Technology Detection**
  - Web technology stack identification
  - CMS detection (WordPress, Joomla, Drupal, etc.)
  - JavaScript framework detection
  - Analytics tools identification
  - CDN detection
  - Web server identification

- 🌍 **Multi-language Support**
  - English and Persian (فارسی) interface
  - Internationalization framework
  - Localized error messages and UI text

- 📊 **Flexible Output Formats**
  - JSON structured output
  - CSV export functionality
  - Human-readable pretty print
  - Command-line interface with rich options

- 🛠️ **Developer Features**
  - Modular architecture for easy extension
  - Comprehensive input validation
  - Type hints throughout codebase
  - Configurable timeouts and settings
  - Error handling and graceful degradation

- 📱 **Command Line Interface**
  - Full-featured CLI with argument parsing
  - Module selection capability
  - Output format selection
  - File export functionality
  - Quiet mode support
  - Language selection

### Technical Features
- Python 3.8+ compatibility
- Cross-platform support (Windows, macOS, Linux)
- Comprehensive error handling
- Timeout management
- Input validation and sanitization
- Caching support for improved performance
- Clean separation of concerns
- Extensive configuration options

### Dependencies
- `requests` - HTTP client library
- `dnspython` - DNS toolkit
- `python-whois` - WHOIS client
- `ipwhois` - IP WHOIS client
- `pyOpenSSL` - SSL/TLS toolkit
- `beautifulsoup4` - HTML parser
- `lxml` - XML/HTML parser

## [0.1.0] - 2024-06-20

### Added
- Initial project structure
- Basic domain resolution functionality
- Core utility functions

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities 