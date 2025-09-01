# Changelog

## 2.0.0

* **Major Feature Release**: JSON Conversion and CLI Tools
* Added complete MT103 to JSON conversion module (`mt103_json.py`)
  * Parse all 5 MT103 blocks (Basic, Application, User, Text, Trailer)
  * Support for 30+ MT103 fields with specialized parsers
  * Handle repeatable fields (13C, 71F) as arrays
  * Convert dates to ISO format (YYYY-MM-DD)
  * Convert amounts to decimal notation
* Added command-line interface (`mt103_to_json.py`)
  * Single file and batch processing modes
  * JSON validation and pretty-printing options
  * Verbose mode for debugging
* Added test data generator (`generate_test_data.py`)
  * Generate diverse MT103 samples with realistic data
  * Edge case samples (minimal, maximal, special characters)
  * Multiple currencies and field combinations
* Added comprehensive test suite (`tests_json.py`)
  * 15+ unit and integration tests
  * 100% function coverage
  * File I/O and batch processing tests
* Documentation improvements:
  * Complete rewrite of README.rst with examples
  * Added module architecture documentation
  * Created RELEASE_NOTES.md with detailed changes
* Bug fixes:
  * Fixed user header parsing for nested braces
  * Fixed application header parsing for output messages
  * Improved field extraction for multi-line content

## 1.1.0

* Added support for a few more portions of the `text` section:

    * instruction_code
    * transaction_type_code
    * exchange_rate
    * sending_institution
    * sender_charges
    * receiver_charges

  Big thanks to [Broto](https://github.com/bbroto06) again for reporting the
  problem.


## 1.0.1

* Bugfix [#3](https://github.com/danielquinn/mt103/issues/3): account for
application headers for outgoing messages, MUR values containing spaces, and
trailer sections containing `{}`.  Thanks to [Broto Bhattacharjee](https://github.com/bbroto06)
for the report!


## 1.0.0

* Changed the nature of the `.user_header` attribute from a string to a
  `UserHeader` object.  This new object has the same string representation
  (`str(mt103.user_header)`), but now also possesses new sub-attributes.
* Added support for user header fields including `bank_priority_code` (`bpc`),
  `message_user_reference` (`mur`), `service_type_identifier` (`sti`), and
  `unique_end_to_end_transaction_reference` (`uetr`).


## 0.0.1

Initial release.
