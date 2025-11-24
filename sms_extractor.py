"""
SMS Message Column Value Extractor

This module provides functionality to extract structured information from raw SMS messages,
particularly for financial transaction messages.
"""

import re
from typing import Dict, Optional, Any
from datetime import datetime


class SMSExtractor:
    """Extract structured data from SMS messages."""
    
    def __init__(self):
        """Initialize the SMS extractor with common patterns."""
        # Common currency symbols and patterns
        self.currency_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # Indian Rupee
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # Rupees
            r'INR\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # INR
            r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # Dollar
            r'USD\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # USD
        ]
        
        # Transaction type patterns
        self.transaction_types = {
            'debit': [
                r'\bpaid\b', r'\bdebited\b', r'\bdebit\b', r'\bspent\b',
                r'\bpurchase\b', r'\bwithdraw', r'\btransfer'
            ],
            'credit': [
                r'\bcredited\b', r'\bcredit\b', r'\breceived\b', r'\bdeposit'
            ],
            'refund': [r'\brefund', r'\breversed\b'],
        }
        
        # Common merchant/payment patterns
        self.merchant_patterns = [
            r'(?:paid\s+to|at)\s+([A-Z][A-Za-z0-9\s&.-]+?)(?:\s+on|\s+for|\s+dated|\.|\s*$)',
            r'(?:account\s+at|from)\s+([A-Z][A-Za-z0-9\s&.-]+?)(?:\s+on|\s+for|\.|\s*$)',
            r'(?:merchant|vendor):\s*([A-Za-z0-9\s&.-]+)',
            r'@\s*([A-Za-z0-9\s&.-]+)',
        ]
        
        # UPI patterns
        self.upi_pattern = r'UPI/(\d+)/([A-Za-z0-9@.-]+)'
        
        # Date patterns
        self.date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',
        ]
        
        # Reference/Transaction ID patterns
        self.ref_patterns = [
            r'(?:Ref|Reference|Txn|Transaction)(?:\s*No\.?|\s*ID)?:?\s*([A-Z0-9]+)',
            r'UPI/(\d+)',
        ]
        
        # Category keywords
        self.categories = {
            'food': ['restaurant', 'cafe', 'food', 'zomato', 'swiggy', 'mcdonald', 'kfc', 'pizza', 'domino'],
            'shopping': ['amazon', 'flipkart', 'myntra', 'shopping', 'mall', 'store', 'mart', 'retail'],
            'transport': ['uber', 'ola', 'taxi', 'cab', 'metro', 'bus', 'fuel', 'petrol', 'diesel'],
            'utilities': ['electricity', 'water', 'gas', 'bill', 'recharge', 'mobile', 'broadband', 'internet'],
            'entertainment': ['movie', 'cinema', 'netflix', 'prime', 'spotify', 'game', 'entertainment'],
            'healthcare': ['hospital', 'clinic', 'doctor', 'pharmacy', 'medical', 'medicine', 'health'],
            'education': ['school', 'college', 'university', 'course', 'tuition', 'book', 'education'],
            'transfer': ['transfer', 'sent to', 'paid to', 'upi'],
        }
    
    def extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount from SMS text."""
        for pattern in self.currency_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return None
    
    def extract_transaction_type(self, text: str) -> Optional[str]:
        """Determine the transaction type (debit/credit/refund)."""
        text_lower = text.lower()
        
        for trans_type, patterns in self.transaction_types.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return trans_type
        
        return 'unknown'
    
    def extract_merchant(self, text: str) -> Optional[str]:
        """Extract merchant/vendor name from SMS text."""
        # Words to exclude from merchant names
        exclude_words = ['your account', 'account', 'a/c', 'ac']
        
        for pattern in self.merchant_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                merchant = match.group(1).strip()
                # Clean up merchant name
                merchant = re.sub(r'\s+', ' ', merchant)
                # Remove trailing punctuation
                merchant = merchant.rstrip('.,;:')
                
                # Check if merchant is not in exclude list
                if len(merchant) > 2 and merchant.lower() not in exclude_words:
                    return merchant
        
        return None
    
    def extract_upi_ref(self, text: str) -> Optional[str]:
        """Extract UPI reference number."""
        match = re.search(self.upi_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extract transaction date from SMS text."""
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_reference(self, text: str) -> Optional[str]:
        """Extract reference/transaction ID."""
        for pattern in self.ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def categorize_transaction(self, merchant: Optional[str], text: str) -> str:
        """Categorize transaction based on merchant and text content."""
        if not merchant:
            merchant = ""
        
        text_combined = f"{merchant} {text}".lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text_combined:
                    return category
        
        return 'other'
    
    def extract_all(self, sms_text: str, merchant_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract all available information from an SMS message.
        
        Args:
            sms_text: The raw SMS message text
            merchant_hint: Optional merchant name hint for better extraction
            
        Returns:
            Dictionary containing extracted fields
        """
        # Extract basic fields
        amount = self.extract_amount(sms_text)
        transaction_type = self.extract_transaction_type(sms_text)
        merchant = merchant_hint if merchant_hint else self.extract_merchant(sms_text)
        date = self.extract_date(sms_text)
        reference = self.extract_reference(sms_text)
        upi_ref = self.extract_upi_ref(sms_text)
        category = self.categorize_transaction(merchant, sms_text)
        
        return {
            'amount': amount,
            'transaction_type': transaction_type,
            'merchant': merchant,
            'category': category,
            'date': date,
            'reference': reference or upi_ref,
            'raw_text': sms_text,
        }
    
    def format_output(self, extracted_data: Dict[str, Any]) -> str:
        """Format extracted data as a readable string."""
        lines = ["Extracted Information:"]
        lines.append("=" * 50)
        
        for key, value in extracted_data.items():
            if key != 'raw_text' and value is not None:
                formatted_key = key.replace('_', ' ').title()
                lines.append(f"{formatted_key:20s}: {value}")
        
        return "\n".join(lines)


def main():
    """Example usage of SMSExtractor."""
    extractor = SMSExtractor()
    
    # Example SMS messages
    examples = [
        "₹499 paid to Amazon on 23/11/2024. UPI Ref: 123456789",
        "Rs 1,250.50 debited from your account at Swiggy. Txn ID: SWG123",
        "Your account has been credited with INR 5000 from SALARY on 01-Dec-2024",
        "$50 spent at McDonald's on 24/11/2024",
        "UPI/123456789/john@paytm paid ₹750 to BigBasket",
    ]
    
    print("SMS Extraction Examples:")
    print("=" * 70)
    
    for i, sms in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print(f"SMS: {sms}")
        print()
        
        result = extractor.extract_all(sms)
        print(extractor.format_output(result))
        print("-" * 70)


if __name__ == "__main__":
    main()
