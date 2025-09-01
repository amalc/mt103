#!/usr/bin/env python3
"""
Generate diverse MT103 test samples to test the robustness of the JSON converter.
Creates random variations of MT103 messages with different field combinations.
"""

import os
import random
import string
from datetime import datetime, timedelta
from pathlib import Path


def random_string(length, chars=string.ascii_uppercase):
    """Generate random string of specified length"""
    return ''.join(random.choice(chars) for _ in range(length))


def random_bic():
    """Generate random BIC/SWIFT code"""
    return random_string(8, string.ascii_uppercase) + random.choice(['XXX', 'AXX', 'BXX'])


def random_amount():
    """Generate random amount"""
    amount = random.uniform(100, 1000000)
    return f"{amount:.2f}".replace('.', ',')


def random_date():
    """Generate random date in YYMMDD format"""
    base_date = datetime(2020, 1, 1)
    random_days = random.randint(0, 1000)
    date = base_date + timedelta(days=random_days)
    return date.strftime("%y%m%d")


def random_currency():
    """Return random currency code"""
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'SGD', 'HKD', 'NOK']
    return random.choice(currencies)


def random_country():
    """Return random country"""
    countries = ['US', 'GB', 'FR', 'DE', 'JP', 'CH', 'CA', 'AU', 'SG', 'HK', 'NO', 'SE', 'DK', 'NL', 'BE']
    return random.choice(countries)


def random_city():
    """Return random city"""
    cities = ['NEW YORK', 'LONDON', 'PARIS', 'FRANKFURT', 'TOKYO', 'ZURICH', 
              'TORONTO', 'SYDNEY', 'SINGAPORE', 'HONG KONG', 'OSLO', 'STOCKHOLM',
              'COPENHAGEN', 'AMSTERDAM', 'BRUSSELS', 'GENEVA', 'MELBOURNE']
    return random.choice(cities)


def random_name():
    """Generate random person or company name"""
    first_names = ['JOHN', 'JANE', 'ROBERT', 'MARIA', 'DAVID', 'SARAH', 'MICHAEL', 'EMMA']
    last_names = ['SMITH', 'JOHNSON', 'WILLIAMS', 'BROWN', 'JONES', 'GARCIA', 'MILLER', 'DAVIS']
    companies = ['ACME CORP', 'GLOBAL TECH INC', 'INTERNATIONAL TRADE LLC', 'PRIME INDUSTRIES']
    
    if random.choice([True, False]):
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    else:
        return random.choice(companies)


def generate_mt103_sample(sample_id, include_optional=True):
    """Generate a single MT103 message with variations"""
    
    # Basic Header (Block 1)
    app_id = "F01"
    lt_address = random_bic()[:12].ljust(12, 'X')
    session = str(random.randint(1, 9999)).zfill(4)
    sequence = str(random.randint(1, 999999)).zfill(6)
    block1 = f"{{1:{app_id}{lt_address}{session}{sequence}}}"
    
    # Application Header (Block 2)
    io_id = "I"
    mt_type = "103"
    recipient = random_bic()[:12].ljust(12, 'X')
    priority = random.choice(['N', 'U'])
    block2 = f"{{2:{io_id}{mt_type}{recipient}{priority}}}"
    
    # User Header (Block 3) - Optional
    block3 = ""
    if include_optional and random.choice([True, False]):
        mur = f"REF-{sample_id:04d}-{random_string(6)}"
        uetr = f"{random_string(8, string.hexdigits.lower())}-{random_string(4, string.hexdigits.lower())}-"
        uetr += f"4{random_string(3, string.hexdigits.lower())}-{random.choice('89ab')}{random_string(3, string.hexdigits.lower())}-"
        uetr += f"{random_string(12, string.hexdigits.lower())}"
        
        block3_parts = []
        if random.choice([True, False]):
            block3_parts.append(f"{{108:{mur}}}")
        if random.choice([True, False]):
            block3_parts.append(f"{{113:{random_string(4)}}}")
        if random.choice([True, False]):
            block3_parts.append(f"{{111:{str(random.randint(1, 999)).zfill(3)}}}")
        block3_parts.append(f"{{121:{uetr}}}")
        
        if block3_parts:
            block3 = f"{{3:{''.join(block3_parts)}}}"
    
    # Text Block (Block 4)
    fields = []
    
    # Field 20 - Transaction Reference (Mandatory)
    trans_ref = f"TX{sample_id:04d}-{random_string(8, string.ascii_uppercase + string.digits)}"
    fields.append(f":20:{trans_ref}")
    
    # Field 13C - Time Indication (Optional, Repeatable)
    if include_optional and random.choice([True, False]):
        time_codes = ['CLSTIME', 'RNCTIME', 'SNDTIME']
        num_times = random.randint(1, 2)
        for _ in range(num_times):
            code = random.choice(time_codes)
            time_val = str(random.randint(0, 2359)).zfill(4)
            sign = random.choice(['+', '-'])
            offset = str(random.randint(0, 1200)).zfill(4)
            fields.append(f":13C:/{code}/{time_val}{sign}{offset}")
    
    # Field 23B - Bank Operation Code
    bank_ops = ['SPRI', 'SSTD', 'SPAY', 'CRED', 'CRTS', 'HOLD']
    fields.append(f":23B:{random.choice(bank_ops)}")
    
    # Field 23E - Instruction Code (Optional)
    if include_optional and random.choice([True, False]):
        inst_codes = ['PHOB', 'PHON', 'PHOI', 'TELI', 'TELE']
        fields.append(f":23E:{random.choice(inst_codes)}/INSTRUCTION")
    
    # Field 26T - Transaction Type Code (Optional)
    if include_optional and random.choice([True, False]):
        trans_types = ['K90', 'K91', 'K92']
        fields.append(f":26T:{random.choice(trans_types)}")
    
    # Field 32A - Value Date, Currency, Amount
    date_val = random_date()
    currency1 = random_currency()
    amount1 = random_amount()
    fields.append(f":32A:{date_val}{currency1}{amount1}")
    
    # Field 33B - Original Currency and Amount (Optional)
    if include_optional and random.choice([True, False]):
        currency2 = random_currency()
        amount2 = random_amount()
        fields.append(f":33B:{currency2}{amount2}")
        
        # Field 36 - Exchange Rate (if 33B is present)
        rate = f"{random.uniform(0.5, 2.0):.4f}".replace('.', ',')
        fields.append(f":36:{rate}")
    
    # Field 50 - Ordering Customer
    customer_name = random_name()
    customer_addr = f"{random_city()}\n{random_country()}"
    if random.choice([True, False]):
        # 50K format
        account = f"/{random.randint(100000, 999999999)}"
        fields.append(f":50K:{account}\n{customer_name}\n{customer_addr}")
    else:
        # 50F format
        party_id = f"/{random.randint(100000, 999999)}"
        fields.append(f":50F:{party_id}\n1/{customer_name}\n6/{random_country()}/ISSUER/{random.randint(100000, 999999)}")
    
    # Field 52 - Ordering Institution (Optional)
    if include_optional and random.choice([True, False]):
        if random.choice([True, False]):
            fields.append(f":52A:{random_bic()}")
        else:
            inst_name = f"{random_name()} BANK"
            fields.append(f":52D://ACC{random.randint(100000, 999999)}\n{inst_name}\n{random_city()}\n{random_country()}")
    
    # Field 53 - Sender's Correspondent (Optional)
    if include_optional and random.choice([True, False]):
        fields.append(f":53B:/{random.randint(10000000000000, 99999999999999)}")
    
    # Field 54 - Receiver's Correspondent (Optional)
    if include_optional and random.choice([True, False]):
        fields.append(f":54A:/C/{random.randint(100000000, 999999999)}\n{random_bic()}")
    
    # Field 56 - Intermediary (Optional)
    if include_optional and random.choice([True, False]):
        suffix = random.choice(['A', 'C', 'D'])
        if suffix == 'A':
            fields.append(f":56A:{random_bic()}")
        else:
            fields.append(f":56{suffix}:{random_name()} BANK\n{random_city()}")
    
    # Field 57 - Account With Institution (Optional)
    if include_optional and random.choice([True, False]):
        suffix = random.choice(['A', 'B', 'C', 'D'])
        if suffix in ['A', 'B']:
            fields.append(f":57{suffix}:{random_bic()}")
        else:
            fields.append(f":57{suffix}://SC{random.randint(100000, 999999)}")
    
    # Field 59 - Beneficiary
    benef_account = f"/{random.randint(100000, 999999999)}"
    benef_name = random_name()
    benef_addr = f"{random_city()}\n{random_country()}"
    fields.append(f":59:{benef_account}\n{benef_name}\n{benef_addr}")
    
    # Field 70 - Remittance Information
    invoice_nums = [str(random.randint(10000, 99999)) for _ in range(random.randint(1, 5))]
    remit_info = f"/INV/{datetime.now().strftime('%y%m%d')}, INVOICE\nNUMBERS {', '.join(invoice_nums)}"
    fields.append(f":70:{remit_info}")
    
    # Field 71A - Details of Charges
    charge_codes = ['BEN', 'OUR', 'SHA']
    fields.append(f":71A:{random.choice(charge_codes)}")
    
    # Field 71F - Sender's Charges (Optional, Repeatable)
    if include_optional and random.choice([True, False]):
        num_charges = random.randint(1, 3)
        for _ in range(num_charges):
            charge_curr = random_currency()
            charge_amt = f"{random.uniform(10, 500):.2f}".replace('.', ',')
            fields.append(f":71F:{charge_curr}{charge_amt}")
    
    # Field 71G - Receiver's Charges (Optional)
    if include_optional and random.choice([True, False]):
        fields.append(f":71G:{random_currency()}{random.uniform(10, 200):.2f}".replace('.', ','))
    
    # Field 72 - Sender to Receiver Information (Optional)
    if include_optional and random.choice([True, False]):
        info_types = ['/REC/', '/INS/', '/ACC/']
        info_type = random.choice(info_types)
        fields.append(f":72:{info_type}INSTRUCTIONS FOR\n//PROCESSING THIS PAYMENT\n//AS REQUESTED")
    
    # Field 77B - Regulatory Reporting (Optional)
    if include_optional and random.choice([True, False]):
        fields.append(f":77B:/ORDERRES/{random_country()}//REGULATORY INFO\n//ADDITIONAL DETAILS")
    
    # Combine text block
    text_block = '\n'.join(fields)
    block4 = f"{{4:\n{text_block}\n-}}"
    
    # Block 5 - Trailer (Optional)
    block5 = ""
    if include_optional and random.choice([True, False, False]):  # Less frequent
        mac = random_string(8, string.hexdigits.upper())
        chk = random_string(12, string.hexdigits.upper())
        block5 = f"{{5:{{MAC:{mac}}}{{CHK:{chk}}}}}"
    
    # Combine all blocks
    mt103_message = block1 + block2 + block3 + block4 + block5
    
    return mt103_message


def create_edge_case_samples():
    """Create specific edge case samples"""
    samples = []
    
    # Sample 1: Minimal required fields only
    minimal = (
        "{1:F01MINIMAL0AXXX0001000001}"
        "{2:I103MINIMAL0XXXXN}"
        "{4:\n"
        ":20:MINIMAL-001\n"
        ":23B:SSTD\n"
        ":32A:240101EUR1000,00\n"
        ":59:/123456\n"
        "JOHN DOE\n"
        ":71A:SHA\n"
        "-}"
    )
    samples.append(('minimal', minimal))
    
    # Sample 2: Maximum fields with repetitions
    maximal = (
        "{1:F01MAXIMAL0AXXX9999999999}"
        "{2:I103MAXIMAL0XXXXU}"
        "{3:{108:MAX-REF-001}{113:URGT}{111:999}{121:aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee}}"
        "{4:\n"
        ":20:MAXIMAL-REFERENCE-001\n"
        ":13C:/CLSTIME/0800+0100\n"
        ":13C:/RNCTIME/0900+0100\n"
        ":13C:/SNDTIME/1000+0100\n"
        ":23B:SPRI\n"
        ":23E:PHOB/123.456.789\n"
        ":26T:K90\n"
        ":32A:240101USD999999999,99\n"
        ":33B:EUR888888888,88\n"
        ":36:1,1234\n"
        ":50F:/123456789\n"
        "1/MAXIMUM CORPORATION INTERNATIONAL\n"
        "2/HEADQUARTERS BUILDING SUITE 1000\n"
        "3/US/NEW YORK/10001\n"
        "4/1980-01-01\n"
        "5/US\n"
        "6/US/PASSPORT/A12345678\n"
        ":51A:SENDUS33XXX\n"
        ":52D://CH987654321\n"
        "ORDERING BANK NAME\n"
        "123 MAIN STREET\n"
        "ZURICH\n"
        "SWITZERLAND\n"
        ":53B:/98765432109876543210\n"
        ":54A:/C/111222333\n"
        "RCVRUS44XXX\n"
        ":56A:INTRUS55XXX\n"
        ":57C://SC999999\n"
        ":59:/999888777\n"
        "BENEFICIARY MAXIMUM NAME\n"
        "999 END STREET\n"
        "LONDON\n"
        "UNITED KINGDOM\n"
        ":70:/INV/240101, MAXIMUM INVOICE\n"
        "NUMBERS 11111, 22222, 33333,\n"
        "44444, 55555, 66666, 77777,\n"
        "88888, 99999, 00000\n"
        ":71A:OUR\n"
        ":71F:USD100,00\n"
        ":71F:EUR50,00\n"
        ":71F:GBP25,00\n"
        ":71G:CHF75,50\n"
        ":72:/REC/MAXIMUM INSTRUCTIONS\n"
        "//FOR PROCESSING THIS\n"
        "//VERY IMPORTANT PAYMENT\n"
        "//WITH MULTIPLE LINES\n"
        "//OF DETAILED INSTRUCTIONS\n"
        ":77B:/ORDERRES/US//MAXIMUM REGULATORY\n"
        "//REPORTING INFORMATION\n"
        "//WITH MULTIPLE LINES\n"
        "//OF COMPLIANCE DATA\n"
        "-}"
        "{5:{MAC:FFFFFFFF}{CHK:AAAAAAAAAAAA}}"
    )
    samples.append(('maximal', maximal))
    
    # Sample 3: Special characters and edge cases
    special = (
        "{1:F01SPECIAL0AXXX0000000001}"
        "{2:I103SPECIAL0XXXXN}"
        "{4:\n"
        ":20:SPEC-001/2024\n"
        ":23B:CRED\n"
        ":32A:240229EUR12345,67\n"  # Leap year date
        ":50K:/ACC-123/456\n"
        "O'MALLEY & SONS, LTD.\n"
        "123 RUE DE LA PAIX\n"
        "PARIS, FRANCE\n"
        ":59:/789-ABC-XYZ\n"
        "MÜLLER-SCHMIDT GMBH & CO.\n"
        "STRAßE 456\n"
        "MÜNCHEN\n"
        ":70:/RFB/2024-SP-ÄÖÜ\n"
        ":71A:SHA\n"
        "-}"
    )
    samples.append(('special_chars', special))
    
    return samples


def main():
    """Generate test MT103 samples"""
    # Create test_samples directory
    output_dir = Path('test_samples')
    output_dir.mkdir(exist_ok=True)
    
    print("Generating MT103 test samples...")
    
    # Generate random samples with variations
    num_random_samples = 10
    for i in range(1, num_random_samples + 1):
        # Half with all fields, half with minimal fields
        include_optional = i <= num_random_samples // 2
        
        sample = generate_mt103_sample(i, include_optional=include_optional)
        
        filename = f"sample_{i:03d}.txt"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(sample)
        
        print(f"  Created: {filename} ({'full' if include_optional else 'minimal'} fields)")
    
    # Add edge case samples
    edge_cases = create_edge_case_samples()
    for name, sample in edge_cases:
        filename = f"sample_{name}.txt"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(sample)
        
        print(f"  Created: {filename} (edge case)")
    
    print(f"\nGenerated {num_random_samples + len(edge_cases)} test samples in {output_dir}/")
    
    # Also copy the original sample
    original_sample = Path('samples/mt103-input.txt')
    if original_sample.exists():
        import shutil
        shutil.copy(original_sample, output_dir / 'sample_original.txt')
        print(f"  Copied original sample as sample_original.txt")
    
    print("\nYou can now test the converter with:")
    print(f"  python mt103_to_json.py test_samples/sample_001.txt")
    print(f"  python mt103_to_json.py --batch test_samples/")


if __name__ == '__main__':
    main()