#!/usr/bin/env python3
"""
EASY DOCUMENT SUBMISSION
Simple command-line interface for document automation.
Usage: python easy_submit.py
"""

import json
import os
import sys
from automated_submit import DocumentSubmitter

def main():
    """Simple interactive interface."""
    
    print("🇦🇪 UAE DOCUMENT VERIFICATION - EASY SUBMIT")
    print("=" * 60)
    print("Based on working curl command analysis")
    print("Key insight: Files are empty (filenames only)")
    print()
    
    submitter = DocumentSubmitter()
    
    while True:
        print("\nOptions:")
        print("1. Submit single document")
        print("2. Submit from JSON file") 
        print("3. Test with sample data")
        print("4. Exit")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == '1':
            submit_single(submitter)
        elif choice == '2':
            submit_from_json(submitter)
        elif choice == '3':
            submit_sample(submitter)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

def submit_single(submitter):
    """Submit single document with user input."""
    
    print("\n📝 SINGLE DOCUMENT SUBMISSION")
    print("-" * 40)
    
    # Get document details
    passport_num = input("Passport Number: ").strip()
    person_name = input("Person Name: ").strip()
    email = input("Email (or press Enter for default): ").strip() or "visaprocessing@maids.cc"
    contact = input("Contact (or press Enter for default): ").strip() or "0505544143"
    
    print("\nAvailable nationalities:")
    print("philippines, nepal, india, pakistan, bangladesh, sri lanka, indonesia")
    nationality = input("Nationality: ").strip().lower()
    
    # Check for fresh tokens
    curl_file = None
    if os.path.exists("instant_tokens.sh"):
        use_fresh = input("\nUse fresh tokens from instant_tokens.sh? (y/n): ").strip().lower()
        if use_fresh == 'y':
            curl_file = "instant_tokens.sh"
    
    # Submit
    print(f"\n🚀 Submitting {passport_num}...")
    result = submitter.submit_document(
        passport_num=passport_num,
        email=email,
        contact=contact,
        nationality=nationality,
        person_name=person_name,
        curl_file=curl_file
    )
    
    print_result(result)

def submit_from_json(submitter):
    """Submit documents from JSON file."""
    
    print("\n📦 BATCH SUBMISSION FROM JSON")
    print("-" * 40)
    
    json_file = input("JSON file path: ").strip()
    
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        documents = data if isinstance(data, list) else [data]
        
        # Check for fresh tokens
        curl_file = None
        if os.path.exists("instant_tokens.sh"):
            use_fresh = input("Use fresh tokens from instant_tokens.sh? (y/n): ").strip().lower()
            if use_fresh == 'y':
                curl_file = "instant_tokens.sh"
        
        # Submit batch
        results = submitter.batch_submit(documents, curl_file)
        
        # Save results
        output_file = f"results_{json_file.replace('.json', '')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error processing JSON: {e}")

def submit_sample(submitter):
    """Submit with sample test data."""
    
    print("\n🧪 SAMPLE SUBMISSION")
    print("-" * 40)
    
    # Check for fresh tokens
    curl_file = None
    if os.path.exists("instant_tokens.sh"):
        use_fresh = input("Use fresh tokens from instant_tokens.sh? (y/n): ").strip().lower()
        if use_fresh == 'y':
            curl_file = "instant_tokens.sh"
        else:
            print("⚠️ Using default tokens - may not work without fresh ones")
    
    result = submitter.submit_document(
        passport_num="TEST123456",
        email="test@example.com", 
        contact="0505544143",
        nationality="philippines",
        person_name="SAMPLE TEST USER",
        curl_file=curl_file
    )
    
    print_result(result)

def print_result(result):
    """Print formatted result."""
    
    print(f"\n📊 SUBMISSION RESULT")
    print("-" * 40)
    print(f"Passport: {result.get('passport_number', 'Unknown')}")
    print(f"Status: {result.get('status', 'Unknown')}")
    print(f"Success: {'✅ YES' if result.get('success') else '❌ NO'}")
    print(f"Message: {result.get('message', 'No message')}")
    
    if not result.get('success'):
        print(f"\n💡 TROUBLESHOOTING:")
        status = result.get('status', '')
        
        if status == 'LOGIN_REDIRECT':
            print("- Get fresh tokens from UAE machine")
            print("- Copy working curl command to instant_tokens.sh")
            print("- Make sure you're running from UAE network")
        elif 'HTTP_' in status:
            print("- Check network connectivity")
            print("- Verify SSL configuration")
        else:
            print("- Check response manually")
            print("- Verify all input parameters")

if __name__ == "__main__":
    main()
