# Quick Reference Guide - SMS Message Extraction

## TL;DR - How to Extract Column Values from Raw SMS

### Problem: 
"I want to input a raw SMS message and get the extracted column values"

### Solution:
```bash
python predict_sms.py --text "₹499 paid to Amazon"
```

## Quick Examples

### 1. Extract from Single SMS (Text Format)
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

### 2. Extract as JSON
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

### 3. Extract as CSV
```bash
python predict_sms.py --text "₹499 paid to Amazon" --format csv
```
Output:
```
"499.0","debit","Amazon","shopping","",""
```

### 4. With Merchant Hint (for ambiguous SMS)
```bash
python predict_sms.py --text "Rs 1,250 debited" --merchant "Swiggy" --format json
```

### 5. Process Multiple SMS from File
Create `my_sms.txt`:
```
₹499 paid to Amazon on 23/11/2024
Rs 1,250 debited from your account at Swiggy
Your account has been credited with INR 5000
```

Run:
```bash
python predict_sms.py --file my_sms.txt --format json
```

## Extracted Columns

The system extracts the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `amount` | Transaction amount | 499.0 |
| `transaction_type` | Type of transaction | debit, credit, refund |
| `merchant` | Merchant/vendor name | Amazon, Swiggy |
| `category` | Transaction category | shopping, food, transport |
| `date` | Transaction date | 23/11/2024 |
| `reference` | Transaction/UPI reference | 123456789 |

## Python API Usage

```python
from sms_extractor import SMSExtractor

extractor = SMSExtractor()
result = extractor.extract_all("₹499 paid to Amazon")

# Access extracted values
print(f"Amount: {result['amount']}")
print(f"Merchant: {result['merchant']}")
print(f"Category: {result['category']}")
```

## Supported Formats

### Currency
- ₹ (Indian Rupee)
- Rs/Rs.
- INR
- $ (Dollar)
- USD

### Transaction Types
- **Debit**: paid, debited, spent, purchase, withdraw
- **Credit**: credited, received, deposit
- **Refund**: refund, reversed

### Categories
- Food (Zomato, Swiggy, McDonald's, etc.)
- Shopping (Amazon, Flipkart, Myntra, etc.)
- Transport (Uber, Ola, fuel, etc.)
- Utilities (bills, recharge, etc.)
- Entertainment (Netflix, Prime, movies, etc.)
- Healthcare (hospitals, pharmacies, etc.)
- Education (schools, courses, etc.)
- Transfer (UPI, bank transfers)

## For More Information

See [README_SMS.md](README_SMS.md) for complete documentation.
