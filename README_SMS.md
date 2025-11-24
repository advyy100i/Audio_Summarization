# SMS Message Column Value Extraction

This system provides tools to extract structured information from raw SMS messages, particularly for financial transaction messages.

## Features

- **Amount Extraction**: Extracts monetary amounts with support for multiple currencies (₹, Rs, INR, $, USD)
- **Transaction Type Detection**: Identifies transaction types (debit, credit, refund)
- **Merchant/Vendor Extraction**: Extracts merchant names from SMS text
- **Category Classification**: Automatically categorizes transactions (food, shopping, transport, utilities, etc.)
- **Date Extraction**: Extracts transaction dates
- **Reference Number Extraction**: Extracts UPI references and transaction IDs

## Installation

No additional dependencies are required beyond Python 3.6+. The system uses only standard library modules.

```bash
# Make the prediction script executable (optional)
chmod +x predict_sms.py
```

## Usage

### Command Line Interface

The `predict_sms.py` script provides a simple CLI for extracting information from SMS messages.

#### Basic Usage

Extract information from a single SMS message:

```bash
python predict_sms.py --text "₹499 paid to Amazon"
```

Output:
```
Extracted Information:
==================================================
Amount              : 499.0
Transaction Type    : debit
Merchant            : Amazon
Category            : shopping
```

#### With Merchant Hint

Provide a merchant name hint for better extraction:

```bash
python predict_sms.py --text "Rs 1,250 debited from your account" --merchant "Swiggy"
```

#### JSON Output

Get results in JSON format:

```bash
python predict_sms.py --text "₹499 paid to Amazon" --format json
```

Output:
```json
{
  "amount": 499.0,
  "transaction_type": "debit",
  "merchant": "Amazon",
  "category": "shopping",
  "date": null,
  "reference": null
}
```

#### CSV Output

Get results in CSV format:

```bash
python predict_sms.py --text "₹499 paid to Amazon" --format csv
```

Output:
```
"499.0","debit","Amazon","shopping","",""
```

#### Process Multiple Messages from File

Create a file with SMS messages (one per line):

```bash
# sms_messages.txt
₹499 paid to Amazon on 23/11/2024. UPI Ref: 123456789
Rs 1,250.50 debited from your account at Swiggy. Txn ID: SWG123
Your account has been credited with INR 5000 from SALARY on 01-Dec-2024
```

Then process it:

```bash
python predict_sms.py --file sms_messages.txt --format json
```

### Python API

You can also use the SMS extractor directly in your Python code:

```python
from sms_extractor import SMSExtractor

# Initialize the extractor
extractor = SMSExtractor()

# Extract information from an SMS
sms_text = "₹499 paid to Amazon on 23/11/2024"
result = extractor.extract_all(sms_text)

print(result)
# Output:
# {
#     'amount': 499.0,
#     'transaction_type': 'debit',
#     'merchant': 'Amazon',
#     'category': 'shopping',
#     'date': '23/11/2024',
#     'reference': None,
#     'raw_text': '₹499 paid to Amazon on 23/11/2024'
# }

# Format the output nicely
print(extractor.format_output(result))
```

### Extract Specific Fields

```python
from sms_extractor import SMSExtractor

extractor = SMSExtractor()
sms_text = "₹499 paid to Amazon"

# Extract only amount
amount = extractor.extract_amount(sms_text)
print(f"Amount: {amount}")  # Amount: 499.0

# Extract only merchant
merchant = extractor.extract_merchant(sms_text)
print(f"Merchant: {merchant}")  # Merchant: Amazon

# Extract transaction type
trans_type = extractor.extract_transaction_type(sms_text)
print(f"Type: {trans_type}")  # Type: debit

# Categorize transaction
category = extractor.categorize_transaction(merchant, sms_text)
print(f"Category: {category}")  # Category: shopping
```

## Supported Transaction Types

- **Debit**: paid, debited, debit, spent, purchase, withdraw, transfer
- **Credit**: credited, credit, received, deposit
- **Refund**: refund, reversed

## Supported Categories

- **Food**: Restaurants, cafes, food delivery (Zomato, Swiggy, McDonald's, etc.)
- **Shopping**: E-commerce and retail (Amazon, Flipkart, Myntra, etc.)
- **Transport**: Ride services, metro, fuel (Uber, Ola, petrol pumps, etc.)
- **Utilities**: Bills, recharges, broadband
- **Entertainment**: Movies, streaming services (Netflix, Prime, Spotify, etc.)
- **Healthcare**: Hospitals, clinics, pharmacies
- **Education**: Schools, courses, books
- **Transfer**: UPI transfers, money sent to contacts
- **Other**: Uncategorized transactions

## Examples

### Example 1: Simple Transaction

**Input**: `₹499 paid to Amazon`

**Output**:
```
Amount              : 499.0
Transaction Type    : debit
Merchant            : Amazon
Category            : shopping
```

### Example 2: Complete Transaction with Date and Reference

**Input**: `₹499 paid to Amazon on 23/11/2024. UPI Ref: 123456789`

**Output**:
```
Amount              : 499.0
Transaction Type    : debit
Merchant            : Amazon
Category            : shopping
Date                : 23/11/2024
Reference           : 123456789
```

### Example 3: Credit Transaction

**Input**: `Your account has been credited with INR 5000 from SALARY on 01-Dec-2024`

**Output**:
```
Amount              : 5000.0
Transaction Type    : credit
Category            : other
Date                : 01-Dec-2024
```

### Example 4: Food Delivery

**Input**: `Rs 1,250.50 debited from your account at Swiggy. Txn ID: SWG123`

**Output**:
```
Amount              : 1250.5
Transaction Type    : debit
Merchant            : Swiggy
Category            : food
Reference           : SWG123
```

## How It Works

The SMS extractor uses regular expressions to identify patterns in SMS messages:

1. **Amount Detection**: Matches currency symbols (₹, Rs, INR, $, USD) followed by numbers
2. **Transaction Type**: Searches for keywords like "paid", "debited", "credited"
3. **Merchant Extraction**: Looks for patterns like "paid to [merchant]" or "at [merchant]"
4. **Category Classification**: Matches merchant names and keywords against known categories
5. **Date Extraction**: Identifies common date formats
6. **Reference Extraction**: Finds UPI references and transaction IDs

## Limitations

- The extractor uses pattern matching and may not catch all SMS formats
- Accuracy depends on the SMS format used by different banks/payment providers
- For best results with non-standard formats, provide a `--merchant` hint
- Currently optimized for English language SMS messages
- Categories are predefined and may not cover all transaction types

## Future Enhancements

Potential improvements for the system:

- Machine learning-based merchant extraction
- Support for multiple languages
- Bank/provider-specific parsers
- Account number extraction
- Balance information extraction
- Duplicate detection
- Time extraction (in addition to dates)

## Contributing

To add support for new SMS formats or improve extraction accuracy, modify the patterns in `sms_extractor.py`:

- `currency_patterns`: Add new currency formats
- `transaction_types`: Add transaction type keywords
- `merchant_patterns`: Add merchant extraction patterns
- `categorize_transaction()`: Add new categories or keywords

## License

This SMS extraction system is provided as-is for use in the Audio_Summarization project.
