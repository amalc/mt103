mt103
=====

Parse and convert MT103 messages from the Swift payments network to JSON format

.. image:: https://img.shields.io/pypi/v/mt103.svg
   :target: https://pypi.org/project/mt103/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/l/mt103.svg
   :target: https://github.com/danielquinn/mt103/blob/master/LICENSE
   :alt: License

.. image:: https://img.shields.io/pypi/pyversions/mt103.svg
   :target: https://pypi.org/project/mt103/
   :alt: Python Versions


What's an MT103?
----------------

Banks don't really deal with cash much any more. Instead, they push bits
around the internet tracking where your money goes digitally. The network that
handles much of that movement is called `Swift`_, and the transfers are
documented in a special format native to that network called *MT103*.

.. _Swift: https://en.wikipedia.org/wiki/ISO_9362


Features
--------

* **Complete MT103 Parsing**: Parse all 5 blocks of MT103 messages (Basic Header, Application Header, User Header, Text Block, Trailer)
* **JSON Conversion**: Convert MT103 messages to structured JSON format for easy integration
* **Field Extraction**: Extract and parse 30+ different fields including amounts, dates, currencies, and party information
* **Command-Line Interface**: Convert files directly from the command line with batch processing support
* **Robust Testing**: Comprehensive test suite with edge cases and validation
* **Test Data Generation**: Built-in generator for creating diverse MT103 test samples


Installation
------------

Install via pip:

.. code-block:: shell

    $ pip install mt103

Or using Poetry:

.. code-block:: shell

    $ poetry add mt103


Quick Start
-----------

Python API
~~~~~~~~~~

Parse MT103 messages using the Python API:

.. code-block:: python

    from mt103 import MT103

    # Parse MT103 message
    mt103_message = "{1:F01BANKCODE0AXXX0000000000}..."
    mt103 = MT103(mt103_message)
    
    # Access parsed components
    print(f"Basic Header: {mt103.basic_header}")
    print(f"Transaction Reference: {mt103.text.transaction_reference}")
    print(f"Amount: {mt103.text.interbank_settled_currency} {mt103.text.interbank_settled_amount}")
    print(f"Beneficiary: {mt103.text.beneficiary}")


JSON Conversion
~~~~~~~~~~~~~~~

Convert MT103 messages to JSON format:

.. code-block:: python

    from mt103_json import mt103_to_json

    # Convert to JSON
    mt103_message = "{1:F01BANKCODE0AXXX0000000000}..."
    json_data = mt103_to_json(mt103_message)
    
    # Access JSON fields
    print(json_data["MT103"]["Application_Id"])
    print(json_data["MT103"]["A"]["F20"]["F20_TRN"])  # Transaction reference
    print(json_data["MT103"]["A"]["F32A"]["F32A_Amount"])  # Amount


Command-Line Usage
------------------

Convert MT103 files to JSON from the command line:

.. code-block:: shell

    # Convert single file (creates output.json automatically)
    $ python mt103_to_json.py input.txt

    # Specify output file
    $ python mt103_to_json.py input.txt output.json

    # Pretty print with validation
    $ python mt103_to_json.py input.txt --pretty --validate

    # Batch convert all .txt files in a directory
    $ python mt103_to_json.py --batch samples/

    # Verbose mode for debugging
    $ python mt103_to_json.py input.txt --verbose


Command-Line Options
~~~~~~~~~~~~~~~~~~~~

* ``input``: Input MT103 file path or directory (with --batch)
* ``output``: Output JSON file path (optional, auto-generated if not specified)
* ``-p, --pretty``: Pretty print JSON output with indentation
* ``-b, --batch``: Process all .txt files in the input directory
* ``-v, --verbose``: Show detailed processing information
* ``--validate``: Validate the output JSON structure


Module Architecture
-------------------

Core Modules
~~~~~~~~~~~~

**mt103.py**
  Original MT103 parser with three main classes:
  
  * ``MT103``: Main parser class for complete MT103 messages
  * ``UserHeader``: Parser for block 3 (user header) with MUR, UETR fields
  * ``Text``: Parser for block 4 (text block) with transaction details

**mt103_json.py**
  JSON conversion module with specialized parsing functions:
  
  * ``mt103_to_json()``: Main conversion function
  * ``parse_basic_header()``: Parse block 1 (basic header)
  * ``parse_application_header()``: Parse block 2 (application header)
  * ``parse_user_header()``: Parse block 3 (user header)
  * ``parse_text_block()``: Parse block 4 (text block) with all fields
  * ``parse_field_*``: Specialized parsers for complex fields

**mt103_to_json.py**
  Command-line interface utility:
  
  * Argument parsing and validation
  * Single file and batch processing
  * JSON validation and pretty printing
  * Error handling and reporting


Utility Modules
~~~~~~~~~~~~~~~

**generate_test_data.py**
  Test data generator for creating diverse MT103 samples:
  
  * Random field generation with realistic values
  * Edge case samples (minimal, maximal, special characters)
  * Multiple currencies, amounts, and date formats
  * Configurable optional field inclusion

**tests_json.py**
  Comprehensive test suite:
  
  * Unit tests for all parsing functions
  * Integration tests for complete conversion
  * File I/O and batch processing tests
  * Edge case validation


JSON Output Structure
---------------------

The JSON output follows this structure:

.. code-block:: json

    {
      "MT103": {
        "Application_Id": "F",
        "Service_Id": "01",
        "LT_Address": "BANKCODE0AXXX",
        "Session": "0001",
        "Sequence_No": "000001",
        "IO_ID": "I",
        "MT": "103",
        "Recipient": "BANKCODE1XXXX",
        "Message_Priority": "N",
        "MUR": "REFERENCE-001",
        "UniqueEndToEndTransactionReference_121": "uuid-string",
        "A": {
          "F20": {"F20_TRN": "TRANSACTION-REF"},
          "F23B": {"F23B_BankOpCode": "CRED"},
          "F32A": {
            "F32A_Date": "2024-01-01",
            "F32A_Curr": "EUR",
            "F32A_Amount": "10000.00"
          },
          "F50K": {"F50K_OrderingCustomer": "CUSTOMER NAME"},
          "F59": {
            "F59_ACC_ID_Party": "/123456789",
            "F59_Name_addr_Party": "BENEFICIARY NAME"
          },
          "F71A": {"F71A_ChargesCode": "SHA"}
        }
      }
    }


Supported MT103 Fields
----------------------

The parser supports all standard MT103 fields:

**Header Fields**
  * Block 1: Basic Header (Application ID, Service ID, LT Address, Session, Sequence)
  * Block 2: Application Header (I/O ID, Message Type, Recipient, Priority)
  * Block 3: User Header (MUR, Bank Priority Code, UETR)
  * Block 5: Trailer (MAC, CHK)

**Text Block Fields (Block 4)**
  * :20: Transaction Reference
  * :13C: Time Indication (repeatable)
  * :23B: Bank Operation Code
  * :23E: Instruction Code
  * :26T: Transaction Type Code
  * :32A: Value Date, Currency, Amount
  * :33B: Original Ordered Currency and Amount
  * :36: Exchange Rate
  * :50A/F/K: Ordering Customer
  * :51A: Sending Institution
  * :52A/D: Ordering Institution
  * :53A/B/D: Sender's Correspondent
  * :54A/B/D: Receiver's Correspondent
  * :56A/C/D: Intermediary
  * :57A/B/C/D: Account With Institution
  * :59/59A: Beneficiary
  * :70: Remittance Information
  * :71A: Details of Charges
  * :71F: Sender's Charges (repeatable)
  * :71G: Receiver's Charges
  * :72: Sender to Receiver Information
  * :77B: Regulatory Reporting


Development
-----------

Running Tests
~~~~~~~~~~~~~

.. code-block:: shell

    # Run all tests
    $ python -m unittest tests.py tests_json.py -v

    # Run specific test class
    $ python -m unittest tests_json.TestMT103ToJSON -v

    # Run with coverage (requires coverage package)
    $ coverage run -m unittest tests_json.py
    $ coverage report


Generating Test Data
~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

    # Generate test MT103 samples
    $ python generate_test_data.py

This creates various test samples in the ``test_samples/`` directory with different field combinations and edge cases.


Contributing
------------

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (``git checkout -b feature/AmazingFeature``)
3. Commit your changes (``git commit -m 'Add some AmazingFeature'``)
4. Push to the branch (``git push origin feature/AmazingFeature``)
5. Open a Pull Request


License
-------

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.


Author
------

Original MT103 parser by Daniel Quinn <code@danielquinn.org>

JSON conversion and CLI tools developed with assistance from Claude AI.


Links
-----

* GitHub Repository: https://github.com/danielquinn/mt103
* PyPI Package: https://pypi.org/project/mt103/
* Swift MT103 Documentation: https://www.sepaforcorporates.com/swift-for-corporates/
* ISO 9362 (Swift/BIC codes): https://en.wikipedia.org/wiki/ISO_9362