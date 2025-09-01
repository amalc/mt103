import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List


def parse_basic_header(header: str) -> Dict[str, str]:
    """Parse block 1 - Basic Header"""
    pattern = r"F(?P<app_id>\d{2})(?P<lt_address>[A-Z0-9]{12})(?P<session>\d{4})(?P<sequence>\d{6})"
    match = re.match(pattern, header)
    if match:
        return {
            "Application_Id": "F",
            "Service_Id": match.group("app_id"),
            "LT_Address": match.group("lt_address"),
            "Session": match.group("session"),
            "Sequence_No": match.group("sequence")
        }
    return {}


def parse_application_header(header: str) -> Dict[str, str]:
    """Parse block 2 - Application Header"""
    if header.startswith("I"):
        pattern = r"I(?P<mt>\d{3})(?P<recipient>[A-Z0-9]{12})(?P<priority>[A-Z])"
        match = re.match(pattern, header)
        if match:
            return {
                "IO_ID": "I",
                "MT": match.group("mt"),
                "Recipient": match.group("recipient"),
                "Message_Priority": match.group("priority")
            }
    elif header.startswith("O"):
        pattern = r"O(?P<mt>\d{3})(?P<input_time>\d{10})(?P<mir>[A-Z0-9]{28})(?P<priority>[A-Z])"
        match = re.match(pattern, header)
        if match:
            return {
                "IO_ID": "O",
                "MT": match.group("mt"),
                "Input_Time": match.group("input_time"),
                "MIR": match.group("mir"),
                "Message_Priority": match.group("priority")
            }
    return {}


def parse_user_header(header: str) -> Dict[str, str]:
    """Parse block 3 - User Header"""
    result = {}
    
    # Parse MUR (108)
    mur_match = re.search(r"{108:([^}]+)}", header)
    if mur_match:
        result["MUR"] = mur_match.group(1)
    
    # Parse Bank Priority Code (113)
    bpc_match = re.search(r"{113:([^}]+)}", header)
    if bpc_match:
        result["Bank_Priority_Code"] = bpc_match.group(1)
    
    # Parse Service Type Identifier (111)
    sti_match = re.search(r"{111:([^}]+)}", header)
    if sti_match:
        result["Service_Type_Identifier"] = sti_match.group(1)
    
    # Parse UETR (121)
    uetr_match = re.search(r"{121:([^}]+)}", header)
    if uetr_match:
        result["UniqueEndToEndTransactionReference_121"] = uetr_match.group(1)
    
    return result


def parse_field_13c(text: str) -> List[Dict[str, str]]:
    """Parse field 13C - Time Indication (can repeat)"""
    results = []
    pattern = r":13C:/(?P<code>[^/]+)/(?P<time>\d{4})(?P<sign>[+-])(?P<offset>\d{4})"
    for match in re.finditer(pattern, text):
        time_str = match.group("time")
        offset_str = match.group("offset")
        results.append({
            "F13C_Code": match.group("code"),
            "F13C_Time": f"{time_str[:2]}:{time_str[2:]}:00",
            "F13C_Sign": match.group("sign"),
            "F13C_Offset": f"{offset_str[:2]}:{offset_str[2:]}:00"
        })
    return results


def parse_field_50f(value: str) -> Dict[str, str]:
    """Parse field 50F - Ordering Customer (structured format)"""
    lines = value.strip().split('\n')
    result = {}
    
    # First line is usually party identifier
    if lines:
        result["F50F_PartyIdentifier"] = lines[0]
    
    # Remaining lines are name/address
    if len(lines) > 1:
        result["F50F_NameAddr"] = '\n'.join(lines[1:])
    
    return result


def parse_amount(amount_str: str) -> str:
    """Convert amount from MT103 format to decimal format"""
    # Replace comma with period for decimal point
    return amount_str.replace(',', '.')


def parse_date(date_str: str) -> str:
    """Convert date from YYMMDD to YYYY-MM-DD format"""
    if len(date_str) == 6:
        year = int(date_str[:2])
        # Assume 20xx for years 00-50, 19xx for years 51-99
        if year <= 50:
            year = 2000 + year
        else:
            year = 1900 + year
        month = date_str[2:4]
        day = date_str[4:6]
        return f"{year}-{month}-{day}"
    return date_str


def parse_text_block(text: str) -> Dict[str, Any]:
    """Parse block 4 - Text block with all fields"""
    result = {"A": {}}
    
    # Field 20 - Transaction Reference
    match = re.search(r":20:([^\s:]+)", text)
    if match:
        result["A"]["F20"] = {"F20_TRN": match.group(1).strip()}
    
    # Field 13C - Time Indication (repeatable)
    time_indications = parse_field_13c(text)
    if time_indications:
        # If only one, store as dict, otherwise as list
        if len(time_indications) == 1:
            result["A"]["A1"] = {"F13C": time_indications[0]}
        else:
            result["A"]["A1"] = {"F13C": time_indications}
    
    # Field 23B - Bank Operation Code
    match = re.search(r":23B:([^\s:]+)", text)
    if match:
        result["A"]["F23B"] = {"F23B_BankOpCode": match.group(1).strip()}
    
    # Field 23E - Instruction Code
    match = re.search(r":23E:([^:]+)", text)
    if match:
        result["A"]["F23E"] = {"F23E_InstructionCode": match.group(1).strip()}
    
    # Field 26T - Transaction Type Code
    match = re.search(r":26T:([^:]+)", text)
    if match:
        result["A"]["F26T"] = {"F26T_TransType": match.group(1).strip()}
    
    # Field 32A - Value Date, Currency, Amount
    match = re.search(r":32A:(\d{6})([A-Z]{3})([\d,]+)", text)
    if match:
        result["A"]["F32A"] = {
            "F32A_Date": parse_date(match.group(1)),
            "F32A_Curr": match.group(2),
            "F32A_Amount": parse_amount(match.group(3))
        }
    
    # Field 33B - Currency, Amount
    match = re.search(r":33B:([A-Z]{3})([\d,]+)", text)
    if match:
        result["A"]["F33B"] = {
            "F33B_Curr": match.group(1),
            "F33B_Amount": parse_amount(match.group(2))
        }
    
    # Field 36 - Exchange Rate
    match = re.search(r":36:([^:]+)", text)
    if match:
        result["A"]["F36"] = {"F36_ExchangeRate": match.group(1).strip()}
    
    # Field 50F - Ordering Customer (structured)
    match = re.search(r":50F:(.+?)(?=:\d{2}[A-Z]?:|$)", text, re.DOTALL)
    if match:
        result["A"]["F50F"] = parse_field_50f(match.group(1))
    
    # Field 50K - Ordering Customer (unstructured)
    if ":50F:" not in text:
        match = re.search(r":50K:(.+?)(?=:\d{2}[A-Z]?:|$)", text, re.DOTALL)
        if match:
            result["A"]["F50K"] = {"F50K_OrderingCustomer": match.group(1).strip()}
    
    # Field 51A - Sending Institution
    match = re.search(r":51A:([^:]+)", text)
    if match:
        result["A"]["F51A"] = {"F51A_SendingInstitution": match.group(1).strip()}
    
    # Field 52D - Ordering Institution
    match = re.search(r":52D:(.+?)(?=:\d{2}[A-Z]?:|$)", text, re.DOTALL)
    if match:
        lines = match.group(1).strip().split('\n', 1)
        field_data = {}
        if lines[0].startswith('/'):
            field_data["F52D_AccountId"] = lines[0]
            if len(lines) > 1:
                field_data["F52D_NameAddr"] = lines[1]
        else:
            field_data["F52D_NameAddr"] = match.group(1).strip()
        result["A"]["F52D"] = field_data
    
    # Field 52A - Ordering Institution BIC
    match = re.search(r":52A:([^:]+)", text)
    if match:
        result["A"]["F52A"] = {"F52A_BIC": match.group(1).strip()}
    
    # Field 53B - Sender's Correspondent
    match = re.search(r":53B:([^:]+)", text)
    if match:
        result["A"]["F53B"] = {"F53B_Account": match.group(1).strip()}
    
    # Field 54A - Receiver's Correspondent
    match = re.search(r":54A:(.+?)(?=:\d{2}[A-Z]?:|$)", text, re.DOTALL)
    if match:
        lines = match.group(1).strip().split('\n', 1)
        field_data = {}
        if lines[0].startswith('/'):
            field_data["F54A_AccountId"] = lines[0]
            if len(lines) > 1:
                field_data["F54A_BIC"] = lines[1]
        else:
            field_data["F54A_BIC"] = lines[0]
        result["A"]["F54A"] = field_data
    
    # Field 56 - Intermediary
    for suffix in ['A', 'C', 'D']:
        pattern = rf":56{suffix}:(.+?)(?=:\d{{2}}[A-Z]?:|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            result["A"][f"F56{suffix}"] = {f"F56{suffix}_Intermediary": match.group(1).strip()}
            break
    
    # Field 57 - Account With Institution
    for suffix in ['A', 'B', 'C', 'D']:
        pattern = rf":57{suffix}:(.+?)(?=:\d{{2}}[A-Z]?:|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            result["A"][f"F57{suffix}"] = {f"F57{suffix}_AccountWithInstitution": match.group(1).strip()}
            break
    
    # Field 59 - Beneficiary
    match = re.search(r":59A?:(.+?)(?=:\d{2}[A-Z]?:|$)", text, re.DOTALL)
    if match:
        lines = match.group(1).strip().split('\n', 1)
        field_data = {}
        if lines[0].startswith('/'):
            field_data["F59_ACC_ID_Party"] = lines[0]
            if len(lines) > 1:
                field_data["F59_Name_addr_Party"] = lines[1]
        else:
            field_data["F59_Name_addr_Party"] = match.group(1).strip()
        result["A"]["F59"] = field_data
    
    # Field 70 - Remittance Information
    match = re.search(r":70:(.+?)(?=:\d{2}[A-Z]?:|$)", text, re.DOTALL)
    if match:
        result["A"]["F70"] = {"F70_PaymentDetails": match.group(1).strip()}
    
    # Field 71A - Details of Charges
    match = re.search(r":71A:([^:]+)", text)
    if match:
        result["A"]["F71A"] = {"F71A_ChargesCode": match.group(1).strip()}
    
    # Field 71F - Sender's Charges (repeatable)
    charges = []
    for match in re.finditer(r":71F:([A-Z]{3})([\d,]+)", text):
        charges.append({
            "F71F_Curr": match.group(1),
            "F71F_Amount": parse_amount(match.group(2))
        })
    if charges:
        if len(charges) == 1:
            result["A"]["A3"] = {"F71F": charges[0]}
        else:
            result["A"]["A3"] = {"F71F": charges}
    
    # Field 71G - Receiver's Charges
    match = re.search(r":71G:([^:]+)", text)
    if match:
        result["A"]["F71G"] = {"F71G_ReceiverCharges": match.group(1).strip()}
    
    # Field 72 - Sender to Receiver Information
    match = re.search(r":72:(.+?)(?=:\d{2}[A-Z]?:|$)", text, re.DOTALL)
    if match:
        result["A"]["F72"] = {"F72_General": match.group(1).strip()}
    
    # Field 77B - Regulatory Reporting
    match = re.search(r":77B:(.+?)(?=:\d{2}[A-Z]?:|$)", text, re.DOTALL)
    if match:
        result["A"]["F77B"] = {"F77B_Narrative": match.group(1).strip()}
    
    return result


def mt103_to_json(mt103_message: str) -> Dict[str, Any]:
    """Convert MT103 message to JSON format"""
    result = {"MT103": {}}
    
    # Preprocess: ensure the message is on a single line for regex matching
    # but preserve newlines within field values
    mt103_message = mt103_message.strip()
    
    # Parse blocks using regex
    blocks = {}
    
    # Block 1 - Basic Header
    match = re.search(r"{1:([^}]+)}", mt103_message)
    if match:
        blocks[1] = match.group(1)
        header_data = parse_basic_header(blocks[1])
        result["MT103"].update(header_data)
    
    # Block 2 - Application Header
    match = re.search(r"{2:([^}]+)}", mt103_message)
    if match:
        blocks[2] = match.group(1)
        app_data = parse_application_header(blocks[2])
        result["MT103"].update(app_data)
    
    # Block 3 - User Header (optional)
    match = re.search(r"{3:([^}]+)}", mt103_message)
    if match:
        blocks[3] = match.group(1)
        user_data = parse_user_header(blocks[3])
        result["MT103"].update(user_data)
    
    # Block 4 - Text
    match = re.search(r"{4:\s*(.+?)\s*-}", mt103_message, re.DOTALL)
    if match:
        blocks[4] = match.group(1)
        text_data = parse_text_block(blocks[4])
        result["MT103"].update(text_data)
    
    # Block 5 - Trailer (optional)
    match = re.search(r"{5:([^}]+)}", mt103_message)
    if match:
        blocks[5] = match.group(1)
        # Parse trailer if needed
        result["MT103"]["Trailer"] = blocks[5]
    
    return result


def convert_file(input_path: str, output_path: Optional[str] = None) -> str:
    """Convert MT103 file to JSON file"""
    if output_path is None:
        # Generate output path by replacing extension
        if input_path.endswith('.txt'):
            output_path = input_path[:-4] + '.json'
        else:
            output_path = input_path + '.json'
    
    # Read input file
    with open(input_path, 'r') as f:
        mt103_content = f.read()
    
    # Convert to JSON
    json_data = mt103_to_json(mt103_content)
    
    # Write output file
    with open(output_path, 'w') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return output_path