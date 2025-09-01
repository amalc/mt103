#!/usr/bin/env python3
"""
Test suite for MT103 to JSON conversion functionality.
"""

import unittest
import json
import os
import tempfile
from pathlib import Path
from mt103_json import (
    parse_basic_header,
    parse_application_header,
    parse_user_header,
    parse_field_13c,
    parse_field_50f,
    parse_amount,
    parse_date,
    parse_text_block,
    mt103_to_json,
    convert_file
)


class TestParsingFunctions(unittest.TestCase):
    """Test individual parsing functions"""
    
    def test_parse_basic_header(self):
        """Test basic header parsing"""
        header = "F01PTSBCHSSAXXX0001000001"
        result = parse_basic_header(header)
        
        self.assertEqual(result["Application_Id"], "F")
        self.assertEqual(result["Service_Id"], "01")
        self.assertEqual(result["LT_Address"], "PTSBCHSSAXXX")
        self.assertEqual(result["Session"], "0001")
        self.assertEqual(result["Sequence_No"], "000001")
    
    def test_parse_application_header_input(self):
        """Test application header parsing for input message"""
        header = "I103PTSBCHSSXXXXN"
        result = parse_application_header(header)
        
        self.assertEqual(result["IO_ID"], "I")
        self.assertEqual(result["MT"], "103")
        self.assertEqual(result["Recipient"], "PTSBCHSSXXXX")
        self.assertEqual(result["Message_Priority"], "N")
    
    def test_parse_application_header_output(self):
        """Test application header parsing for output message"""
        header = "O1030919010321BBBBGRA0AXXX00570001710103210920N"
        result = parse_application_header(header)
        
        self.assertEqual(result["IO_ID"], "O")
        self.assertEqual(result["MT"], "103")
        self.assertEqual(result["Message_Priority"], "N")
        self.assertIn("MIR", result)
    
    def test_parse_user_header(self):
        """Test user header parsing"""
        header = "{108:10-103-NVR-0033}{121:cc0e4a2e-0473-4574-be3b-de639be5252e}"
        result = parse_user_header(header)
        
        self.assertEqual(result["MUR"], "10-103-NVR-0033")
        self.assertEqual(result["UniqueEndToEndTransactionReference_121"], 
                        "cc0e4a2e-0473-4574-be3b-de639be5252e")
    
    def test_parse_field_13c_single(self):
        """Test parsing single 13C field"""
        text = ":13C:/CLSTIME/0945+0100"
        result = parse_field_13c(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["F13C_Code"], "CLSTIME")
        self.assertEqual(result[0]["F13C_Time"], "09:45:00")
        self.assertEqual(result[0]["F13C_Sign"], "+")
        self.assertEqual(result[0]["F13C_Offset"], "01:00:00")
    
    def test_parse_field_13c_multiple(self):
        """Test parsing multiple 13C fields"""
        text = ":13C:/CLSTIME/0945+0100:13C:/RNCTIME/1030-0500"
        result = parse_field_13c(text)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["F13C_Code"], "CLSTIME")
        self.assertEqual(result[1]["F13C_Code"], "RNCTIME")
        self.assertEqual(result[1]["F13C_Sign"], "-")
    
    def test_parse_field_50f(self):
        """Test parsing field 50F"""
        value = "/123456\n1/Name of customer\n6/US/Issuer/123456"
        result = parse_field_50f(value)
        
        self.assertEqual(result["F50F_PartyIdentifier"], "/123456")
        self.assertIn("1/Name of customer", result["F50F_NameAddr"])
    
    def test_parse_amount(self):
        """Test amount parsing"""
        self.assertEqual(parse_amount("15000,11"), "15000.11")
        self.assertEqual(parse_amount("1234567,89"), "1234567.89")
        self.assertEqual(parse_amount("100,00"), "100.00")
    
    def test_parse_date(self):
        """Test date parsing"""
        self.assertEqual(parse_date("091120"), "2009-11-20")
        self.assertEqual(parse_date("240101"), "2024-01-01")
        self.assertEqual(parse_date("991231"), "1999-12-31")
        self.assertEqual(parse_date("500101"), "2050-01-01")
        self.assertEqual(parse_date("510101"), "1951-01-01")


class TestTextBlockParsing(unittest.TestCase):
    """Test text block parsing"""
    
    def test_parse_simple_text_block(self):
        """Test parsing a simple text block"""
        text = (
            ":20:REF001\n"
            ":23B:CRED\n"
            ":32A:240101EUR1000,00\n"
            ":59:/123456\n"
            "JOHN DOE\n"
            ":71A:SHA"
        )
        result = parse_text_block(text)
        
        self.assertIn("F20", result["A"])
        self.assertEqual(result["A"]["F20"]["F20_TRN"], "REF001")
        
        self.assertIn("F23B", result["A"])
        self.assertEqual(result["A"]["F23B"]["F23B_BankOpCode"], "CRED")
        
        self.assertIn("F32A", result["A"])
        self.assertEqual(result["A"]["F32A"]["F32A_Date"], "2024-01-01")
        self.assertEqual(result["A"]["F32A"]["F32A_Curr"], "EUR")
        self.assertEqual(result["A"]["F32A"]["F32A_Amount"], "1000.00")
        
        self.assertIn("F59", result["A"])
        self.assertEqual(result["A"]["F59"]["F59_ACC_ID_Party"], "/123456")
        
        self.assertIn("F71A", result["A"])
        self.assertEqual(result["A"]["F71A"]["F71A_ChargesCode"], "SHA")
    
    def test_parse_complex_text_block(self):
        """Test parsing a complex text block with optional fields"""
        text = (
            ":20:COMPLEX001\n"
            ":13C:/CLSTIME/0945+0100\n"
            ":23B:SPRI\n"
            ":23E:PHOB/123.456\n"
            ":26T:K90\n"
            ":32A:091120EUR15000,11\n"
            ":33B:AUD16500,00\n"
            ":36:0,91\n"
            ":50F:/123456\n"
            "1/Customer Name\n"
            "6/US/Issuer/789\n"
            ":52D://CH123\n"
            "BANK NAME\n"
            "CITY\n"
            ":71A:BEN\n"
            ":71F:AUD150,00\n"
            ":71F:USD100,00\n"
            ":72:/REC/INSTRUCTIONS\n"
            ":77B:/ORDERRES/US//INFO"
        )
        result = parse_text_block(text)
        
        # Check time indication
        self.assertIn("A1", result["A"])
        self.assertIn("F13C", result["A"]["A1"])
        
        # Check instruction code
        self.assertIn("F23E", result["A"])
        
        # Check transaction type
        self.assertIn("F26T", result["A"])
        
        # Check exchange rate
        self.assertIn("F36", result["A"])
        self.assertEqual(result["A"]["F36"]["F36_ExchangeRate"], "0,91")
        
        # Check ordering institution
        self.assertIn("F52D", result["A"])
        
        # Check multiple charges
        self.assertIn("A3", result["A"])
        charges = result["A"]["A3"]["F71F"]
        if isinstance(charges, list):
            self.assertEqual(len(charges), 2)
        
        # Check sender to receiver info
        self.assertIn("F72", result["A"])
        
        # Check regulatory reporting
        self.assertIn("F77B", result["A"])


class TestMT103ToJSON(unittest.TestCase):
    """Test complete MT103 to JSON conversion"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_mt103 = (
            "{1:F01TESTBANK0XXX0001000001}"
            "{2:I103TESTBANK1XXXN}"
            "{3:{108:TEST-REF-001}{121:aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee}}"
            "{4:\n"
            ":20:TEST-001\n"
            ":23B:CRED\n"
            ":32A:240101USD10000,00\n"
            ":50K:/987654\n"
            "TEST CUSTOMER\n"
            "NEW YORK\n"
            ":59:/123456\n"
            "BENEFICIARY NAME\n"
            "LONDON\n"
            ":71A:SHA\n"
            "-}"
        )
    
    def test_complete_conversion(self):
        """Test complete MT103 to JSON conversion"""
        result = mt103_to_json(self.sample_mt103)
        
        self.assertIn("MT103", result)
        mt103 = result["MT103"]
        
        # Check header fields
        self.assertEqual(mt103["Application_Id"], "F")
        self.assertEqual(mt103["Service_Id"], "01")
        self.assertEqual(mt103["LT_Address"], "TESTBANK0XXX")
        
        # Check application header
        self.assertEqual(mt103["IO_ID"], "I")
        self.assertEqual(mt103["MT"], "103")
        
        # Check user header
        self.assertEqual(mt103["MUR"], "TEST-REF-001")
        
        # Check text block
        self.assertIn("A", mt103)
        self.assertIn("F20", mt103["A"])
        self.assertEqual(mt103["A"]["F20"]["F20_TRN"], "TEST-001")
    
    def test_original_sample_conversion(self):
        """Test conversion of the original sample file"""
        sample_path = Path("samples/mt103-input.txt")
        if sample_path.exists():
            with open(sample_path, 'r') as f:
                content = f.read()
            
            result = mt103_to_json(content)
            
            self.assertIn("MT103", result)
            mt103 = result["MT103"]
            
            # Verify key fields from original sample
            self.assertEqual(mt103["LT_Address"], "PTSBCHSSAXXX")
            self.assertIn("A", mt103)
            self.assertIn("F20", mt103["A"])


class TestFileConversion(unittest.TestCase):
    """Test file conversion functionality"""
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        
        # Write test MT103 content
        with open(self.test_file, 'w') as f:
            f.write(
                "{1:F01FILETEST0XXX0001000001}"
                "{2:I103FILETEST1XXXN}"
                "{4:\n"
                ":20:FILE-TEST-001\n"
                ":23B:SSTD\n"
                ":32A:240101EUR5000,00\n"
                ":59:/999888\n"
                "TEST BENEFICIARY\n"
                ":71A:SHA\n"
                "-}"
            )
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_convert_file(self):
        """Test file conversion"""
        output_file = convert_file(self.test_file)
        
        # Check output file was created
        self.assertTrue(os.path.exists(output_file))
        self.assertEqual(output_file, self.test_file[:-4] + '.json')
        
        # Verify JSON content
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("MT103", data)
        self.assertEqual(data["MT103"]["A"]["F20"]["F20_TRN"], "FILE-TEST-001")
    
    def test_convert_file_with_output_path(self):
        """Test file conversion with specified output path"""
        output_path = os.path.join(self.test_dir, "custom_output.json")
        result_path = convert_file(self.test_file, output_path)
        
        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify content
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn("MT103", data)


if __name__ == '__main__':
    unittest.main(verbosity=2)