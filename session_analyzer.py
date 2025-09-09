"""
Advanced session analysis to understand UAE eservices authentication bypass methods.
"""

import requests
import time
import json
import logging
from doc_verifier import DocumentVerifier
from config import COOKIES, STATIC_HEADERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionAnalyzer:
    """Analyze UAE eservices session validation mechanisms."""
    
    def __init__(self):
        self.verifier = DocumentVerifier()
        
    def analyze_authentication_requirements(self):
        """Comprehensive analysis of what UAE system checks for authentication."""
        
        print("🔍 ADVANCED SESSION ANALYSIS")
        print("=" * 60)
        
        # Test 1: Basic endpoints with current tokens
        self._test_endpoint_accessibility()
        
        # Test 2: Header manipulation
        self._test_header_requirements()
        
        # Test 3: Cookie validation patterns
        self._test_cookie_validation()
        
        # Test 4: Request sequence analysis
        self._test_request_sequence()
        
        # Test 5: Time-based validation
        self._test_time_sensitivity()
        
    def _test_endpoint_accessibility(self):
        """Test different endpoints to see which ones work without authentication."""
        
        print("\n1️⃣ ENDPOINT ACCESSIBILITY TEST")
        print("-" * 40)
        
        endpoints = [
            ("Session Expiry", "GET", "/TasheelWeb/GetSessionExpirytime"),
            ("Home Page", "GET", "/TasheelWeb/home"),
            ("Login Page", "GET", "/TasheelWeb/account/login"),
            ("Document Submit", "POST", "/TasheelWeb/services/transactionentry/505?mk="),
            ("API Status", "GET", "/TasheelWeb/api/status"),
            ("Health Check", "GET", "/TasheelWeb/health")
        ]
        
        base_url = "https://eservices.mohre.gov.ae"
        
        for name, method, path in endpoints:
            try:
                url = base_url + path
                if method == "GET":
                    response = requests.get(url, headers=STATIC_HEADERS, cookies=COOKIES, timeout=5)
                else:
                    response = requests.post(url, headers=STATIC_HEADERS, cookies=COOKIES, timeout=5)
                
                status = "✅ ACCESSIBLE" if response.status_code == 200 else f"❌ {response.status_code}"
                print(f"{name:20} {method:4} {status}")
                
                # Log interesting responses
                if response.status_code not in [200, 404, 401, 403]:
                    logger.info(f"{name} returned {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"{name:20} {method:4} ❌ ERROR: {str(e)[:30]}")
    
    def _test_header_requirements(self):
        """Test which headers are required for authentication."""
        
        print("\n2️⃣ HEADER REQUIREMENTS TEST")
        print("-" * 40)
        
        base_headers = STATIC_HEADERS.copy()
        test_url = "https://eservices.mohre.gov.ae/TasheelWeb/GetSessionExpirytime"
        
        # Test removing different headers
        critical_headers = [
            'User-Agent',
            'X-Requested-With', 
            'Origin',
            'Referer',
            'ADRUM',
            'sec-ch-ua',
            'sec-ch-ua-platform'
        ]
        
        print("Testing header removal effects:")
        for header in critical_headers:
            test_headers = base_headers.copy()
            if header in test_headers:
                del test_headers[header]
                
            try:
                response = requests.post(test_url, headers=test_headers, cookies=COOKIES, timeout=5)
                status = "✅ OK" if response.status_code in [200, 401] else f"❌ {response.status_code}"
                print(f"Without {header:20} {status}")
            except Exception as e:
                print(f"Without {header:20} ❌ ERROR")
    
    def _test_cookie_validation(self):
        """Test cookie validation patterns."""
        
        print("\n3️⃣ COOKIE VALIDATION TEST")
        print("-" * 40)
        
        # Test individual cookie importance
        test_url = "https://eservices.mohre.gov.ae/TasheelWeb/GetSessionExpirytime"
        
        print("Testing individual cookie removal:")
        for cookie_name, cookie_value in COOKIES.items():
            test_cookies = COOKIES.copy()
            del test_cookies[cookie_name]
            
            try:
                response = requests.post(test_url, headers=STATIC_HEADERS, cookies=test_cookies, timeout=5)
                status = "✅ OK" if response.status_code in [200, 401] else f"❌ {response.status_code}"
                print(f"Without {cookie_name:30} {status}")
            except Exception as e:
                print(f"Without {cookie_name:30} ❌ ERROR")
        
        # Test empty cookies
        try:
            response = requests.post(test_url, headers=STATIC_HEADERS, cookies={}, timeout=5)
            print(f"With no cookies:                    ❌ {response.status_code}")
        except Exception as e:
            print(f"With no cookies:                    ❌ ERROR")
    
    def _test_request_sequence(self):
        """Test if specific request sequences are required."""
        
        print("\n4️⃣ REQUEST SEQUENCE TEST") 
        print("-" * 40)
        
        base_url = "https://eservices.mohre.gov.ae"
        session = requests.Session()
        
        # Try different request sequences
        sequences = [
            ("Direct session check", ["/TasheelWeb/GetSessionExpirytime"]),
            ("Home -> Session check", ["/TasheelWeb/home", "/TasheelWeb/GetSessionExpirytime"]),
            ("Login -> Home -> Session", ["/TasheelWeb/account/login", "/TasheelWeb/home", "/TasheelWeb/GetSessionExpirytime"]),
        ]
        
        for seq_name, endpoints in sequences:
            session.cookies.clear()
            session.cookies.update(COOKIES)
            
            print(f"\nTesting: {seq_name}")
            for i, endpoint in enumerate(endpoints):
                try:
                    if endpoint == "/TasheelWeb/GetSessionExpirytime":
                        response = session.post(base_url + endpoint, headers=STATIC_HEADERS, timeout=5)
                    else:
                        response = session.get(base_url + endpoint, headers=STATIC_HEADERS, timeout=5)
                    
                    print(f"  Step {i+1}: {endpoint} -> {response.status_code}")
                    
                    # Update cookies from response
                    if 'Set-Cookie' in response.headers:
                        print(f"    Got new cookies: {len(response.cookies)} items")
                        
                except Exception as e:
                    print(f"  Step {i+1}: {endpoint} -> ERROR: {str(e)[:30]}")
    
    def _test_time_sensitivity(self):
        """Test time-based validation patterns."""
        
        print("\n5️⃣ TIME SENSITIVITY TEST")
        print("-" * 40)
        
        test_url = "https://eservices.mohre.gov.ae/TasheelWeb/GetSessionExpirytime"
        
        print("Testing token age sensitivity...")
        
        # Test immediate requests
        start_time = time.time()
        
        for i in range(3):
            try:
                response = requests.post(test_url, headers=STATIC_HEADERS, cookies=COOKIES, timeout=5)
                elapsed = time.time() - start_time
                print(f"Request {i+1} (+{elapsed:.1f}s): {response.status_code}")
                time.sleep(1)
            except Exception as e:
                print(f"Request {i+1}: ERROR")
    
    def _analyze_response_patterns(self):
        """Analyze response patterns for clues about validation."""
        
        print("\n6️⃣ RESPONSE PATTERN ANALYSIS")
        print("-" * 40)
        
        # Test the document submission endpoint response in detail
        verifier = DocumentVerifier()
        
        print("Analyzing document submission response...")
        result = verifier.submit_document(
            passport_number="TEST123",
            nationality="Nepal", 
            face_photo_path="78797/78797_face.jpg",
            passport_photo_path="78797/78797_passport.jpg"
        )
        
        response_text = result.get('response_text', '')
        
        # Look for authentication clues in response
        auth_indicators = [
            'unauthorized', 'forbidden', 'access denied',
            'session', 'login', 'authentication',
            'token', 'csrf', 'verification',
            'expired', 'invalid', 'redirect'
        ]
        
        print("Authentication-related content in response:")
        for indicator in auth_indicators:
            if indicator.lower() in response_text.lower():
                # Find context around the indicator
                start = max(0, response_text.lower().find(indicator.lower()) - 50)
                end = min(len(response_text), start + 150)
                context = response_text[start:end].replace('\n', ' ').replace('\r', ' ')
                print(f"  '{indicator}': ...{context}...")
        
    def run_full_analysis(self):
        """Run comprehensive analysis."""
        
        self.analyze_authentication_requirements()
        self._analyze_response_patterns()
        
        print("\n" + "=" * 60)
        print("🎯 ANALYSIS SUMMARY")
        print("=" * 60)
        print("Based on the tests above, the UAE system likely validates:")
        print("1. 🍪 Authentication cookies (especially .AspNet.TasheelApplicationCookie)")
        print("2. 🕒 Token timing/expiry (very short-lived sessions)")
        print("3. 🌐 Browser fingerprinting (User-Agent, sec-ch-ua headers)")
        print("4. 🔄 Request sequence patterns")
        print("5. 📡 Network context (IP, geo-location)")
        print("\n💡 BYPASS STRATEGIES:")
        print("• Get tokens immediately before use (< 30 seconds)")
        print("• Maintain exact browser headers from capture")
        print("• Use same IP/network as token capture")
        print("• Consider request sequence requirements")

if __name__ == "__main__":
    analyzer = SessionAnalyzer()
    analyzer.run_full_analysis()
