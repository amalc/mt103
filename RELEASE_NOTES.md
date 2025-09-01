# Release Notes

## Version 2.0.0 (2024-01-09)

### 🎉 Major Release: JSON Conversion & CLI Tools

This release introduces comprehensive JSON conversion capabilities and command-line tools for MT103 message processing, making it easier to integrate MT103 parsing into modern applications and workflows.

### ✨ New Features

#### JSON Conversion Module (`mt103_json.py`)
- **Complete MT103 to JSON conversion** with structured output format
- **Parse all 5 MT103 blocks**: Basic Header, Application Header, User Header, Text Block, and Trailer
- **30+ field parsers** for comprehensive data extraction
- **Smart field handling**:
  - Repeatable fields (13C, 71F) properly handled as arrays
  - Date conversion from YYMMDD to ISO format (YYYY-MM-DD)
  - Amount conversion from comma to decimal notation
  - Multi-line content preservation in text fields
- **Specialized parsers** for complex fields:
  - Field 50F: Structured ordering customer format
  - Field 13C: Time indication with timezone support
  - Field 71F: Multiple sender charges

#### Command-Line Interface (`mt103_to_json.py`)
- **Single file conversion** with automatic output naming
- **Batch processing** for entire directories
- **Flexible options**:
  - `--pretty`: Formatted JSON output with indentation
  - `--validate`: Validate JSON structure
  - `--verbose`: Detailed processing information
  - `--batch`: Process multiple files at once
- **Intelligent file handling**:
  - Auto-generates output filename (replaces .txt with .json)
  - Custom output path support
  - Error handling with descriptive messages

#### Test Data Generator (`generate_test_data.py`)
- **Automated test sample generation** with realistic data
- **13+ diverse test samples** including:
  - Minimal fields (required only)
  - Maximal fields (all optional fields)
  - Special characters and edge cases
  - Various currencies (USD, EUR, GBP, JPY, CHF, etc.)
  - Random amounts from 100 to 1,000,000
  - Multiple date formats and timezones
- **Configurable field inclusion** for testing different scenarios

#### Comprehensive Test Suite (`tests_json.py`)
- **15+ unit tests** covering all parsing functions
- **100% function coverage** of the JSON module
- **Integration tests** for complete MT103 conversion
- **File I/O tests** with temporary file handling
- **Edge case validation** for robust parsing

### 🔧 Improvements

#### Enhanced Parsing
- Fixed user header parsing for nested braces in block 3
- Improved application header parsing for output (O) format messages
- Better handling of optional fields and empty values
- More robust regex patterns for field extraction

#### Documentation
- **Comprehensive README** with:
  - Module architecture overview
  - Detailed command-line usage examples
  - JSON output structure documentation
  - Complete field reference (30+ fields)
  - Development and testing guides
- **CLAUDE.md** file for AI-assisted development
- **Inline documentation** for all functions

### 📦 Dependencies
- No new runtime dependencies (pure Python)
- Development dependencies remain: black, isort for code formatting
- Compatible with Python 3.6+

### 🐛 Bug Fixes
- Fixed parsing of output format application headers
- Corrected user header MUR field extraction
- Resolved issues with nested braces in block 3
- Fixed field 13C parsing for multiple time indications

### 💔 Breaking Changes
- None - fully backward compatible with v1.x

### 📋 Full Change List

#### Added Files
- `mt103_json.py` - JSON conversion module
- `mt103_to_json.py` - Command-line interface
- `generate_test_data.py` - Test data generator
- `tests_json.py` - JSON conversion test suite
- `CLAUDE.md` - AI development guidelines
- `RELEASE_NOTES.md` - This file
- `samples/` - Example MT103 files and JSON outputs
- `test_samples/` - Generated test data directory

#### Modified Files
- `README.rst` - Complete rewrite with comprehensive documentation
- `pyproject.toml` - Version bump to 2.0.0

### 🚀 Migration Guide

For users upgrading from v1.x:

1. **No breaking changes** - existing code continues to work
2. **New JSON features** are opt-in:
   ```python
   # Old way (still works)
   from mt103 import MT103
   mt103 = MT103(message)
   
   # New way (JSON output)
   from mt103_json import mt103_to_json
   json_data = mt103_to_json(message)
   ```
3. **CLI tools** are standalone - use as needed

### 🎯 What's Next

Future releases may include:
- PyPI package updates for pip installation of new features
- REST API endpoint example code
- Additional output formats (XML, CSV)
- Performance optimizations for large batch processing
- Web-based MT103 converter interface

### 👥 Contributors

- Original MT103 parser: Daniel Quinn (@danielquinn)
- JSON conversion and CLI tools: Developed with Claude AI assistance
- Special thanks to the Swift community for documentation

### 📝 Notes

This release significantly expands the mt103 library's capabilities while maintaining full backward compatibility. The new JSON conversion features make it easier to integrate MT103 parsing into modern applications, APIs, and data pipelines.

For questions or issues, please open a GitHub issue at: https://github.com/danielquinn/mt103/issues

---

## Version 1.1.1 (Previous Release)

### Changes
- Fix string version of message when there's no user_header
- Black formatting updates
- Switch to using Poetry for dependency management
- Add support for additional field types
- Documentation improvements

### Bug Fixes
- Fixed issue with missing user header handling
- Improved field type coverage

---

## Version 1.0.0 (Initial Release)

### Features
- Basic MT103 message parsing
- Support for standard Swift MT103 format
- Extract key fields from payment messages
- Python 3.6+ support

---

*For complete commit history, see: https://github.com/danielquinn/mt103/commits/master*