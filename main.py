"""
Main script for document verification service.
Usage examples and test interface.
"""

import json
import sys
import os
import logging
from pathlib import Path
from doc_verifier import DocumentVerifier

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('document_verification.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_single_document():
    """Test with the provided sample document."""
    
    verifier = DocumentVerifier()
    
    # Test with the sample data
    sample_json = "78797/info.json"
    
    if not os.path.exists(sample_json):
        logger.error(f"Sample data not found: {sample_json}")
        return False
    
    logger.info("Testing with sample document...")
    result = verifier.submit_from_json(sample_json)
    
    # Display user-friendly result
    print(f"\n{'='*60}")
    print("SUBMISSION RESULT")
    print(f"{'='*60}")
    print(f"Passport: {result.get('passport_number', 'Unknown')}")
    print(f"Status Code: {result.get('status_code', 'Unknown')}")
    
    if 'interpretation' in result:
        interp = result['interpretation']
        print(f"Result: {interp.get('user_message', 'Unknown')}")
        print(f"Action Needed: {interp.get('action_needed', 'None')}")
    
    print(f"\nDetailed Result:")
    logger.info(json.dumps(result, indent=2, default=str))
    
    return result.get('success', False)

def batch_process_directory(directory: str):
    """Process all documents in a directory."""
    
    verifier = DocumentVerifier()
    
    logger.info(f"Starting batch processing of directory: {directory}")
    results = verifier.batch_process(directory)
    
    # Save results
    results_file = "batch_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Results saved to: {results_file}")
    
    # Print summary
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"\n{'='*50}")
    print(f"BATCH PROCESSING SUMMARY")
    print(f"{'='*50}")
    print(f"Total documents: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success rate: {(successful/total*100):.1f}%" if total > 0 else "N/A")
    print(f"Results saved to: {results_file}")
    
    # Show failed documents
    failed = [r for r in results if not r.get('success', False)]
    if failed:
        print(f"\nFailed documents:")
        for result in failed:
            passport = result.get('passport_number', 'Unknown')
            error = result.get('error', 'Unknown error')
            print(f"  - {passport}: {error}")

def update_tokens_from_file(curl_file: str):
    """Update tokens from a new curl command file."""
    
    verifier = DocumentVerifier()
    
    if not os.path.exists(curl_file):
        logger.error(f"Curl file not found: {curl_file}")
        return False
    
    success = verifier.update_config_from_curl(curl_file)
    
    if success:
        logger.info("✅ Tokens updated successfully!")
    else:
        logger.error("❌ Failed to update tokens")
    
    return success

def interactive_mode():
    """Interactive mode for testing."""
    
    print("\n" + "="*60)
    print("DOCUMENT VERIFICATION SERVICE - INTERACTIVE MODE")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Test with sample document (78797)")
        print("2. Process single JSON file")
        print("3. Batch process directory")
        print("4. Update tokens from curl file")
        print("5. Test connection to UAE eservices")
        print("6. Test session warmup endpoints")
        print("7. Test with session warmup")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            print("\nTesting with sample document...")
            test_single_document()
            
        elif choice == '2':
            json_path = input("Enter path to JSON file: ").strip()
            if os.path.exists(json_path):
                verifier = DocumentVerifier()
                result = verifier.submit_from_json(json_path)
                print("\nResult:")
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"File not found: {json_path}")
                
        elif choice == '3':
            directory = input("Enter directory path: ").strip()
            if os.path.exists(directory):
                batch_process_directory(directory)
            else:
                print(f"Directory not found: {directory}")
                
        elif choice == '4':
            curl_file = input("Enter path to curl command file: ").strip()
            update_tokens_from_file(curl_file)
            
        elif choice == '5':
            print("\nTesting connection to UAE eservices...")
            verifier = DocumentVerifier()
            test_results = verifier.test_connection()
            
            print("\nConnection Test Results:")
            print("-" * 40)
            for result in test_results['test_results']:
                status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
                print(f"{result['config']}: {status}")
                if result['success']:
                    print(f"  Status Code: {result['status_code']}")
                    print(f"  Response Length: {result['response_length']} chars")
                else:
                    print(f"  Error: {result['error']}")
                print()
            
        elif choice == '6':
            print("\nTesting session warmup endpoints...")
            verifier = DocumentVerifier()
            warmup_result = verifier.perform_session_warmup()
            
            print("\nSession Warmup Results:")
            print("-" * 40)
            print(f"Session Valid: {'✅ YES' if warmup_result['session_valid'] else '❌ NO'}")
            print(f"Successful Endpoints: {warmup_result['successful_endpoints']}/{warmup_result['total_endpoints']}")
            
            print("\nEndpoint Details:")
            for result in warmup_result['results']:
                status = "✅ SUCCESS" if result.get('appears_authenticated', False) else "❌ FAILED"
                print(f"  {result['endpoint']}: {status}")
                if 'status_code' in result:
                    print(f"    Status: {result['status_code']}")
                    print(f"    Response: {result['response_length']} chars")
                print()
                
        elif choice == '7':
            print("\nTesting with session warmup...")
            verifier = DocumentVerifier()
            result = verifier.submit_with_session_warmup(
                passport_number="PA1285353",
                nationality="Nepal",
                face_photo_path="78797/78797_face.jpg",
                passport_photo_path="78797/78797_passport.jpg",
                person_name="LILA KUMARI THAPA"
            )
            
            # Display user-friendly result
            print(f"\n{'='*60}")
            print("SUBMISSION RESULT WITH SESSION WARMUP")
            print(f"{'='*60}")
            print(f"Passport: {result.get('passport_number', 'Unknown')}")
            print(f"Status Code: {result.get('status_code', 'Unknown')}")
            print(f"Warmup Success: {'✅ YES' if result.get('warmup_success', False) else '❌ NO'}")
            print(f"Warmup Endpoints: {result.get('warmup_endpoints', 'Unknown')}")
            
            if 'interpretation' in result:
                interp = result['interpretation']
                print(f"Result: {interp.get('user_message', 'Unknown')}")
                print(f"Action Needed: {interp.get('action_needed', 'None')}")
            
            print(f"\nDetailed Result:")
            print(json.dumps(result, indent=2, default=str))
            
        elif choice == '8':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-8.")

def main():
    """Main function."""
    
    print("Document Verification Service")
    print("="*40)
    
    if len(sys.argv) == 1:
        # No arguments - run interactive mode
        interactive_mode()
        
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        
        if arg == "test":
            # Test with sample document
            success = test_single_document()
            sys.exit(0 if success else 1)
            
        elif os.path.isdir(arg):
            # Batch process directory
            batch_process_directory(arg)
            
        elif os.path.isfile(arg) and arg.endswith('.json'):
            # Process single JSON file
            verifier = DocumentVerifier()
            result = verifier.submit_from_json(arg)
            print(json.dumps(result, indent=2, default=str))
            
        else:
            print(f"Unknown argument or file not found: {arg}")
            sys.exit(1)
            
    elif len(sys.argv) == 3 and sys.argv[1] == "update":
        # Update tokens from curl file
        curl_file = sys.argv[2]
        success = update_tokens_from_file(curl_file)
        sys.exit(0 if success else 1)
        
    else:
        print("Usage:")
        print("  python main.py                    # Interactive mode")
        print("  python main.py test               # Test with sample document")
        print("  python main.py <directory>        # Batch process directory")
        print("  python main.py <json_file>        # Process single JSON file")
        print("  python main.py update <curl_file> # Update tokens from curl file")
        sys.exit(1)

if __name__ == "__main__":
    main()
