#!/usr/bin/env python3
"""
SMS Message Predictor/Extractor CLI

Command-line interface for extracting structured information from raw SMS messages.
"""

import argparse
import json
import sys
from sms_extractor import SMSExtractor


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Extract structured information from SMS messages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --text "₹499 paid to Amazon"
  %(prog)s --text "Rs 1,250 debited from your account" --merchant "Swiggy"
  %(prog)s --text "Your account has been credited with INR 5000" --format json
  %(prog)s --file sms_messages.txt
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--text',
        type=str,
        help='Raw SMS message text to extract information from'
    )
    input_group.add_argument(
        '--file',
        type=str,
        help='File containing SMS messages (one per line)'
    )
    
    # Optional parameters
    parser.add_argument(
        '--merchant',
        type=str,
        help='Merchant name hint (optional, for better extraction)'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed extraction information'
    )
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = SMSExtractor()
    
    # Process input
    if args.text:
        # Single SMS message
        result = extractor.extract_all(args.text, args.merchant)
        output_result(result, args.format, args.verbose, extractor)
    
    elif args.file:
        # Multiple SMS messages from file
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                messages = [line.strip() for line in f if line.strip()]
            
            results = []
            for msg in messages:
                result = extractor.extract_all(msg, args.merchant)
                results.append(result)
            
            output_multiple_results(results, args.format, args.verbose, extractor)
        
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)


def output_result(result, format_type, verbose, extractor):
    """Output a single extraction result."""
    if format_type == 'json':
        # Remove raw_text if not verbose
        if not verbose:
            result_copy = {k: v for k, v in result.items() if k != 'raw_text'}
        else:
            result_copy = result
        print(json.dumps(result_copy, indent=2))
    
    elif format_type == 'csv':
        # CSV header
        fields = ['amount', 'transaction_type', 'merchant', 'category', 'date', 'reference']
        if verbose:
            fields.append('raw_text')
        
        # CSV values
        values = [str(result.get(f, '')) for f in fields]
        print(','.join([f'"{v}"' for v in values]))
    
    else:  # text format
        print(extractor.format_output(result))


def output_multiple_results(results, format_type, verbose, extractor):
    """Output multiple extraction results."""
    if format_type == 'json':
        # Remove raw_text if not verbose
        if not verbose:
            results_copy = [{k: v for k, v in r.items() if k != 'raw_text'} for r in results]
        else:
            results_copy = results
        print(json.dumps(results_copy, indent=2))
    
    elif format_type == 'csv':
        # CSV header
        fields = ['amount', 'transaction_type', 'merchant', 'category', 'date', 'reference']
        if verbose:
            fields.append('raw_text')
        
        print(','.join(fields))
        
        # CSV rows
        for result in results:
            values = [str(result.get(f, '')) for f in fields]
            print(','.join([f'"{v}"' for v in values]))
    
    else:  # text format
        for i, result in enumerate(results, 1):
            print(f"\nMessage {i}:")
            print(extractor.format_output(result))
            if i < len(results):
                print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
