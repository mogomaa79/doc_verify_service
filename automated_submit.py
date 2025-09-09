#!/usr/bin/env python3
"""
AUTOMATED DOCUMENT SUBMISSION
Based on working curl command analysis.
Key insights: Empty files (filenames only) + exact multipart format.
"""

import requests
import ssl
import urllib3
import json
import time
import os
from requests.adapters import HTTPAdapter
from typing import Dict, Any

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class UAESSLAdapter(HTTPAdapter):
    """SSL adapter for UAE eservices."""
    def init_poolmanager(self, *args, **kwargs):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.set_ciphers('DEFAULT:@SECLEVEL=1')
        kwargs['ssl_context'] = ssl_context
        return super().init_poolmanager(*args, **kwargs)

class DocumentSubmitter:
    """Automated document submission using working curl method."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.mount('https://eservices.mohre.gov.ae', UAESSLAdapter())
        self.url = "https://eservices.mohre.gov.ae/TasheelWeb/services/transactionentry/505?mk="
        
        # Base headers (never change)
        self.base_headers = {
            'ADRUM': 'isAjax:true',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://eservices.mohre.gov.ae',
            'Referer': 'https://eservices.mohre.gov.ae/TasheelWeb/home',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # Nationality mapping
        self.nationalities = {
            'philippines': {'value': '237', 'description': 'PHILIPPINES'},
            'nepal': {'value': '235', 'description': 'NIPAL'},
            'india': {'value': '356', 'description': 'INDIA'},
            'pakistan': {'value': '586', 'description': 'PAKISTAN'},
            'bangladesh': {'value': '050', 'description': 'BANGLADESH'},
            'sri lanka': {'value': '144', 'description': 'SRI LANKA'},
            'indonesia': {'value': '360', 'description': 'INDONESIA'}
        }
    
    def load_fresh_tokens(self, curl_file: str = None):
        """Load fresh tokens from curl file or config."""
        
        if curl_file and os.path.exists(curl_file):
            print(f"Loading tokens from {curl_file}...")
            with open(curl_file, 'r') as f:
                content = f.read()
            
            # Extract cookies from curl command
            cookies = {}
            if '-b ' in content:
                # Find the cookie line
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('-b '):
                        cookie_line = line[3:].strip('\'"')
                        # Parse cookies
                        for cookie in cookie_line.split('; '):
                            if '=' in cookie:
                                key, value = cookie.split('=', 1)
                                cookies[key.strip()] = value.strip()
                        break
            
            # Extract verification token from form data
            verification_token = ""
            if '__RequestVerificationToken' in content:
                # Find token in the data section (handle $'...' format)
                start_marker = 'name="__RequestVerificationToken"\\r\\n\\r\\n'
                if start_marker in content:
                    start = content.find(start_marker) + len(start_marker)
                    end = content.find('\\r\\n------', start)
                    if end > start:
                        verification_token = content[start:end].strip()
                else:
                    # Try alternative format
                    start_marker = '__RequestVerificationToken"\r\n\r\n'
                    if start_marker in content:
                        start = content.find(start_marker) + len(start_marker)
                        end = content.find('\r\n------', start)
                        if end > start:
                            verification_token = content[start:end].strip()
            
            print(f"Extracted {len(cookies)} cookies and token: {'✅' if verification_token else '❌'}")
            return cookies, verification_token
        else:
            # Use default/config tokens
            print("Using default tokens (update with fresh ones for success)")
            return {}, ""
    
    def create_multipart_form(self, passport_num: str, email: str, contact: str, 
                            nationality: str, verification_token: str,
                            person_name: str = "TEST USER") -> str:
        """Create exact multipart form matching working curl command."""
        
        # Get nationality info
        nat_info = self.nationalities.get(nationality.lower(), 
                                        {'value': '237', 'description': 'PHILIPPINES'})
        
        # Generate unique boundary
        boundary = "----WebKitFormBoundary48BlJyyBFw9hi4gn"
        
        # Create form with EMPTY files (just filenames!)
        form_data = f"""------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="__RequestVerificationToken"\r
\r
{verification_token}\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="Key"\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="PassportNumber"\r
\r
{passport_num}\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="Email"\r
\r
{email}\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="ContactNo"\r
\r
{contact}\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="Nationality.Value"\r
\r
{nat_info['value']}\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="Nationality.Description"\r
\r
{nat_info['description']}\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="PersonPhotoDocument"; filename="{person_name} - photo.jpg"\r
Content-Type: image/jpeg\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="PassportDocumentFirstPage"; filename="{person_name} - passport.jpg"\r
Content-Type: image/jpeg\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="PassportDocumentSecondPage"; filename=""\r
Content-Type: application/octet-stream\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="NationalIdentityDocumentFirstPage"; filename=""\r
Content-Type: application/octet-stream\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="NationalIdentityDocumentSecondPage"; filename=""\r
Content-Type: application/octet-stream\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="EducationCertificateAvailable"\r
\r
false\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="EducationCertificateFirstPage"; filename=""\r
Content-Type: application/octet-stream\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="EducationCertificateSecondPage"; filename=""\r
Content-Type: application/octet-stream\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn--\r
"""
        return form_data, boundary
    
    def submit_document(self, passport_num: str, email: str, contact: str,
                       nationality: str, person_name: str, 
                       curl_file: str = None) -> Dict[str, Any]:
        """Submit document using working method."""
        
        print(f"🚀 SUBMITTING DOCUMENT")
        print(f"Passport: {passport_num}")
        print(f"Person: {person_name}")
        print(f"Nationality: {nationality}")
        print("=" * 50)
        
        # Load fresh tokens
        cookies, verification_token = self.load_fresh_tokens(curl_file)
        
        if not cookies or not verification_token:
            return {
                'success': False,
                'error': 'No valid tokens found. Provide curl file with fresh tokens.'
            }
        
        # Create form
        form_data, boundary = self.create_multipart_form(
            passport_num, email, contact, nationality, verification_token, person_name
        )
        
        # Set headers
        headers = self.base_headers.copy()
        headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        
        try:
            print("Sending request...")
            start_time = time.time()
            
            response = self.session.post(
                self.url,
                headers=headers,
                cookies=cookies,
                data=form_data.encode('utf-8'),
                timeout=30
            )
            
            elapsed = time.time() - start_time
            
            print(f"Response: {response.status_code} ({elapsed:.1f}s)")
            print(f"Length: {len(response.text)} chars")
            
            # Analyze response
            result = self._analyze_response(response, passport_num)
            
            return result
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'passport_number': passport_num
            }
    
    def _analyze_response(self, response: requests.Response, passport_num: str) -> Dict[str, Any]:
        """Analyze response to determine success/failure."""
        
        response_lower = response.text.lower()
        
        result = {
            'success': False,
            'status_code': response.status_code,
            'passport_number': passport_num,
            'response_length': len(response.text),
            'timestamp': time.time()
        }
        
        if response.status_code == 200:
            if 'login' in response_lower:
                result['status'] = 'LOGIN_REDIRECT'
                result['message'] = 'Redirected to login - tokens expired or network issue'
                print("❌ LOGIN REDIRECT - Need fresh tokens or check network")
                
            elif any(word in response_lower for word in ['success', 'submitted', 'confirmed', 'received']):
                result['success'] = True
                result['status'] = 'SUCCESS'
                result['message'] = 'Document submitted successfully'
                print("🎉 SUCCESS! Document submitted!")
                
            elif 'error' in response_lower:
                result['status'] = 'SERVER_ERROR'
                result['message'] = 'Server error in processing'
                print("⚠️ SERVER ERROR")
                
            else:
                result['status'] = 'UNKNOWN_RESPONSE'
                result['message'] = 'Unknown response - manual analysis needed'
                print("🤔 UNKNOWN RESPONSE")
                print("First 200 chars:", response.text[:200])
                
        else:
            result['status'] = f'HTTP_{response.status_code}'
            result['message'] = f'HTTP {response.status_code} error'
            print(f"❌ HTTP {response.status_code} ERROR")
        
        return result
    
    def batch_submit(self, documents: list, curl_file: str = None) -> list:
        """Submit multiple documents."""
        
        print(f"📦 BATCH SUBMISSION: {len(documents)} documents")
        print("=" * 60)
        
        results = []
        
        for i, doc in enumerate(documents, 1):
            print(f"\n[{i}/{len(documents)}] Processing {doc.get('passport_number', 'Unknown')}...")
            
            result = self.submit_document(
                passport_num=doc['passport_number'],
                email=doc.get('email', 'test@example.com'),
                contact=doc.get('contact', '0505544143'),
                nationality=doc.get('nationality', 'philippines'),
                person_name=doc.get('person_name', 'TEST USER'),
                curl_file=curl_file
            )
            
            results.append(result)
            
            # Small delay between requests
            if i < len(documents):
                time.sleep(2)
        
        # Summary
        successful = len([r for r in results if r.get('success')])
        print(f"\n📊 BATCH SUMMARY:")
        print(f"Successful: {successful}/{len(documents)}")
        print(f"Failed: {len(documents) - successful}/{len(documents)}")
        
        return results

def main():
    """Main function for testing."""
    
    submitter = DocumentSubmitter()
    
    # Test single submission
    result = submitter.submit_document(
        passport_num="TEST123456",
        email="test@example.com",
        contact="0505544143",
        nationality="philippines",
        person_name="TEST USER",
        curl_file="instant_tokens.sh"  # Use fresh tokens
    )
    
    print(f"\n📋 RESULT:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
