#!/usr/bin/env python3
"""
Example usage of the SMS Extractor system

This script demonstrates various ways to use the SMS extraction functionality.
"""

from sms_extractor import SMSExtractor


def example_1_basic_extraction():
    """Example 1: Basic extraction from a single SMS."""
    print("=" * 70)
    print("Example 1: Basic Extraction")
    print("=" * 70)
    
    extractor = SMSExtractor()
    sms = "₹499 paid to Amazon"
    
    result = extractor.extract_all(sms)
    print(f"\nInput SMS: {sms}")
    print(f"\nExtracted Data:")
    print(extractor.format_output(result))


def example_2_complete_transaction():
    """Example 2: Complete transaction with all fields."""
    print("\n" + "=" * 70)
    print("Example 2: Complete Transaction Details")
    print("=" * 70)
    
    extractor = SMSExtractor()
    sms = "₹499 paid to Amazon on 23/11/2024. UPI Ref: 123456789"
    
    result = extractor.extract_all(sms)
    print(f"\nInput SMS: {sms}")
    print(f"\nExtracted Data:")
    print(extractor.format_output(result))


def example_3_specific_fields():
    """Example 3: Extracting specific fields only."""
    print("\n" + "=" * 70)
    print("Example 3: Extracting Specific Fields")
    print("=" * 70)
    
    extractor = SMSExtractor()
    sms = "Rs 1,250.50 debited from your account at Swiggy. Txn ID: SWG123"
    
    print(f"\nInput SMS: {sms}\n")
    
    # Extract specific fields
    amount = extractor.extract_amount(sms)
    print(f"Amount: ₹{amount}")
    
    transaction_type = extractor.extract_transaction_type(sms)
    print(f"Transaction Type: {transaction_type}")
    
    merchant = extractor.extract_merchant(sms)
    print(f"Merchant: {merchant}")
    
    reference = extractor.extract_reference(sms)
    print(f"Reference: {reference}")
    
    category = extractor.categorize_transaction(merchant, sms)
    print(f"Category: {category}")


def example_4_multiple_messages():
    """Example 4: Processing multiple SMS messages."""
    print("\n" + "=" * 70)
    print("Example 4: Processing Multiple Messages")
    print("=" * 70)
    
    extractor = SMSExtractor()
    
    messages = [
        "₹499 paid to Amazon on 23/11/2024",
        "Rs 1,250.50 debited from your account at Swiggy",
        "Your account has been credited with INR 5000 from SALARY",
        "$50 spent at McDonald's on 24/11/2024",
    ]
    
    print(f"\nProcessing {len(messages)} SMS messages...\n")
    
    for i, sms in enumerate(messages, 1):
        result = extractor.extract_all(sms)
        print(f"Message {i}: {sms}")
        print(f"  → Amount: {result['amount']}, Merchant: {result['merchant']}, Category: {result['category']}")


def example_5_with_merchant_hint():
    """Example 5: Using merchant hint for better extraction."""
    print("\n" + "=" * 70)
    print("Example 5: Using Merchant Hint")
    print("=" * 70)
    
    extractor = SMSExtractor()
    sms = "Rs 1,250 debited from your account"
    
    print(f"\nInput SMS: {sms}")
    print("\nWithout merchant hint:")
    result1 = extractor.extract_all(sms)
    print(f"  Merchant: {result1['merchant']}")
    print(f"  Category: {result1['category']}")
    
    print("\nWith merchant hint (Swiggy):")
    result2 = extractor.extract_all(sms, merchant_hint="Swiggy")
    print(f"  Merchant: {result2['merchant']}")
    print(f"  Category: {result2['category']}")


def example_6_different_formats():
    """Example 6: Different SMS formats from various banks."""
    print("\n" + "=" * 70)
    print("Example 6: Different SMS Formats")
    print("=" * 70)
    
    extractor = SMSExtractor()
    
    # Different bank SMS formats
    formats = [
        ("HDFC", "INR 1,234.56 debited from A/C XX1234 at BigBazaar on 24-Nov-2024. Ref:HDC123"),
        ("SBI", "Rs.500.00 paid to PayTM on 24/11/24. UPI Ref:987654321"),
        ("ICICI", "Your A/c XX5678 debited with Rs 750.00 for txn at Swiggy"),
        ("Paytm", "₹250 sent to john@paytm via UPI/123456789"),
    ]
    
    print("\nExtracting from different bank formats:\n")
    
    for bank, sms in formats:
        result = extractor.extract_all(sms)
        print(f"{bank}: {sms}")
        print(f"  → Amount: {result['amount']}, Type: {result['transaction_type']}, Merchant: {result['merchant']}")
        print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "SMS EXTRACTOR - USAGE EXAMPLES" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    example_1_basic_extraction()
    example_2_complete_transaction()
    example_3_specific_fields()
    example_4_multiple_messages()
    example_5_with_merchant_hint()
    example_6_different_formats()
    
    print("\n" + "=" * 70)
    print("For more information, see README_SMS.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
