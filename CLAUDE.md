# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python library for parsing MT103 messages from the Swift payments network. MT103 is a standard banking format used for international wire transfers. The library provides a clean Python API to parse these complex message formats into accessible Python objects.

## Development Setup

### Dependencies
- Python 3.6+
- Poetry for dependency management
- Development dependencies: black (code formatting), isort (import sorting)

### Install Dependencies
```bash
poetry install
```

## Common Commands

### Running Tests
```bash
# Run all tests with verbose output
python3 -m unittest tests.py -v

# Run a specific test class
python3 -m unittest tests.SwiftMT103TestCase -v

# Run a specific test method
python3 -m unittest tests.SwiftMT103TestCase.test__populate_by_parsing_message1
```

### Code Formatting
```bash
# Format code with Black (79 character line limit)
poetry run black mt103.py tests.py

# Sort imports with isort
poetry run isort mt103.py tests.py
```

Note: Black and isort need to be installed via `poetry install` first.

## Code Architecture

### Core Components

1. **MT103 Class** (`mt103.py:6-90`)
   - Main parser class that takes an MT103 string and breaks it into components
   - Uses regex to parse the five main sections: basic_header, application_header, user_header, text, and trailer
   - Implements string-like behavior with `__str__` and boolean evaluation
   - The MESSAGE_REGEX pattern handles the complete MT103 structure

2. **UserHeader Class** (`mt103.py:92-163`)
   - Parses the user header section (block 3) which contains:
     - Bank Priority Code (BPC)
     - Message User Reference (MUR)
     - Service Type Identifier (STI)
     - Unique End-to-End Transaction Reference (UETR)
   - Provides property accessors for abbreviated field names

3. **Text Class** (`mt103.py:165-289`)
   - Parses the main text section (block 4) containing transaction details
   - Extracts 20+ fields including amounts, currencies, dates, and party information
   - Complex regex pattern handles optional fields and varying formats
   - Special handling for date parsing (converts to Python date object)

### Message Structure

MT103 messages follow this block structure:
- Block 1: Basic Header (sender info)
- Block 2: Application Header (message type and priority)
- Block 3: User Header (optional metadata)
- Block 4: Text (actual transaction data)
- Block 5: Trailer (checksums and authentication)

### Testing Approach

The test suite (`tests.py`) uses four real-world MT103 message examples to validate parsing:
- MESSAGE1-4: Different variations of MT103 formats
- Tests verify both individual component parsing and complete message handling
- Mock objects are used to test initialization flow

### Field Parsing Notes

- All fields are optional except the basic structure
- Section 13C handling is incomplete (unclear if it can repeat)
- Date fields use 2-digit years (assumed 2000+)
- Amount fields preserve comma separators as strings
- Regex patterns use named groups for field extraction