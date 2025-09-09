"""
Document Verification Service for UAE eservices portal.
Replicates the curl requests for document submission.
"""

import requests
import json
import os
import time
import logging
import csv
import urllib3
from typing import Dict, Optional, Any
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    STATIC_HEADERS, COOKIES, REQUEST_VERIFICATION_TOKEN, 
    API_URL, DEFAULT_FORM_DATA, NATIONALITY_MAPPING
)

# Disable SSL warnings for problematic servers
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentVerifier:
    """Handles document verification requests to UAE eservices portal."""
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 2  # Minimum seconds between requests
        self.auto_refresh_enabled = True
        self.max_retries = 3
        self.nationality_map = {}
        
        # Configure SSL and retry strategy
        self._configure_session()
        
        # Load country mapping from CSV
        self._load_country_mapping()
        
    def _configure_session(self):
        """Configure session with SSL and retry settings for UAE eservices."""
        
        import ssl
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        
        # Create custom HTTPAdapter with SSL configuration for UAE eservices
        class UAESSLAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                # Create SSL context with relaxed settings for UAE site compatibility
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                ssl_context.set_ciphers('DEFAULT:@SECLEVEL=1')
                
                kwargs['ssl_context'] = ssl_context
                return super().init_poolmanager(*args, **kwargs)
        
        # Create adapters
        uae_adapter = UAESSLAdapter(max_retries=retry_strategy)
        standard_adapter = HTTPAdapter(max_retries=retry_strategy)
        
        # Mount UAE-specific adapter for the UAE site
        self.session.mount("https://eservices.mohre.gov.ae", uae_adapter)
        self.session.mount("http://", standard_adapter)
        self.session.mount("https://", standard_adapter)
        
        # Set timeouts for requests (connect_timeout, read_timeout)
        # UAE government servers can be slow with document processing
        self.session.timeout = (10, 120)  # 10s connect, 120s read
        
        logger.info("Session configured with UAE-compatible SSL and retry settings")
    
    def _load_country_mapping(self):
        """Load country mapping from CSV file."""
        
        csv_path = 'country_mapping.csv'
        if not os.path.exists(csv_path):
            logger.warning(f"Country mapping CSV not found: {csv_path}")
            # Fall back to hardcoded mapping
            self.nationality_map = NATIONALITY_MAPPING
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    english_name = row['english_name']
                    site_name = row['site_name']
                    code = row['code']
                    
                    # Create mapping for both English and site names
                    self.nationality_map[english_name] = {
                        'Value': code,
                        'Description': site_name
                    }
                    
                    # Also add the site name as key for flexibility
                    if site_name != english_name:
                        self.nationality_map[site_name] = {
                            'Value': code,
                            'Description': site_name
                        }
            
            logger.info(f"Loaded {len(self.nationality_map)} nationality mappings from CSV")
            
        except Exception as e:
            logger.error(f"Failed to load country mapping CSV: {e}")
            # Fall back to hardcoded mapping
            self.nationality_map = NATIONALITY_MAPPING
    
    def check_session_expiry(self) -> Dict[str, Any]:
        """Check session expiry time using the UAE eservices endpoint."""
        
        session_url = "https://eservices.mohre.gov.ae/TasheelWeb/GetSessionExpirytime"
        
        try:
            logger.info("Checking session expiry time...")
            
            # Use exact headers from the session check curl command
            headers = {
                'ADRUM': 'isAjax:true',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Length': '0',
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
            
            response = self.session.post(
                session_url,
                headers=headers,
                cookies=COOKIES,
                timeout=(5, 10)
            )
            
            # Update cookies if server provides new ones
            self._update_cookies_from_response(response)
            
            # Parse the response
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_text': response.text,
                'headers': dict(response.headers),
                'timestamp': time.time()
            }
            
            # Try to interpret the expiry response
            if result['success']:
                response_text = response.text.strip()
                logger.info(f"Session expiry response: {response_text}")
                
                # Parse session expiry information
                if response_text.isdigit():
                    expiry_minutes = int(response_text)
                    result['expiry_minutes'] = expiry_minutes
                    result['expiry_status'] = 'valid' if expiry_minutes > 0 else 'expired'
                    logger.info(f"Session expires in {expiry_minutes} minutes")
                elif 'login' in response_text.lower():
                    result['expiry_status'] = 'expired'
                    logger.warning("Session appears to be expired (redirected to login)")
                else:
                    result['expiry_status'] = 'unknown'
                    logger.warning(f"Unknown session expiry response: {response_text}")
            else:
                logger.error(f"Session expiry check failed: {response.status_code}")
                
            return result
            
        except Exception as e:
            logger.error(f"Session expiry check failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the UAE eservices portal with different configurations."""
        
        test_url = "https://eservices.mohre.gov.ae/TasheelWeb/services/transactionentry/505?mk="
        results = []
        
        # Test configurations
        configs = [
            {"name": "Standard SSL", "verify": True, "user_agent": STATIC_HEADERS['User-Agent']},
            {"name": "No SSL Verification", "verify": False, "user_agent": STATIC_HEADERS['User-Agent']},
            {"name": "Firefox User-Agent", "verify": True, "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"},
        ]
        
        for config in configs:
            try:
                logger.info(f"Testing connection with {config['name']}")
                
                # Create test session
                test_session = requests.Session()
                test_session.verify = config['verify']
                
                headers = STATIC_HEADERS.copy()
                headers['User-Agent'] = config['user_agent']
                
                # Simple GET request to test connectivity
                response = test_session.get(
                    test_url,
                    headers=headers,
                    cookies=COOKIES,
                    timeout=(5, 10)
                )
                
                result = {
                    'config': config['name'],
                    'success': True,
                    'status_code': response.status_code,
                    'response_length': len(response.text),
                    'ssl_verify': config['verify']
                }
                
                logger.info(f"{config['name']}: Status {response.status_code}")
                results.append(result)
                
            except Exception as e:
                result = {
                    'config': config['name'],
                    'success': False,
                    'error': str(e),
                    'ssl_verify': config['verify']
                }
                logger.error(f"{config['name']}: {e}")
                results.append(result)
        
        return {'test_results': results}
    
    def perform_session_warmup(self) -> Dict[str, Any]:
        """Perform session warmup using authenticated endpoints to establish valid session."""
        
        logger.info("Performing session warmup with authenticated endpoints...")
        
        # Endpoints that are called immediately after successful login
        warmup_endpoints = [
            {
                'name': 'eDirham Session Token',
                'method': 'POST',
                'url': 'https://eservices.mohre.gov.ae/TasheelWeb/GetEDirhamSessionToken',
                'headers': {
                    'ADRUM': 'isAjax:true',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Length': '0',
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
            },
            {
                'name': 'User Transactions Count',
                'method': 'GET',
                'url': f'https://eservices.mohre.gov.ae/TasheelWeb/usertransactionscount?_={int(time.time() * 1000)}',
                'headers': {
                    'ADRUM': 'isAjax:true',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
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
            },
            {
                'name': 'Fetch Favourites',
                'method': 'GET',
                'url': f'https://eservices.mohre.gov.ae/TasheelWeb/common/FetchFavourites?_={int(time.time() * 1000)}',
                'headers': {
                    'ADRUM': 'isAjax:true',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
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
            }
        ]
        
        results = []
        session_valid = False
        
        for endpoint in warmup_endpoints:
            try:
                logger.info(f"Testing {endpoint['name']}...")
                
                if endpoint['method'] == 'POST':
                    response = self.session.post(
                        endpoint['url'],
                        headers=endpoint['headers'],
                        cookies=COOKIES,
                        timeout=(5, 10)
                    )
                else:
                    response = self.session.get(
                        endpoint['url'],
                        headers=endpoint['headers'],
                        cookies=COOKIES,
                        timeout=(5, 10)
                    )
                
                # Update cookies from response
                self._update_cookies_from_response(response)
                
                # Analyze response
                result = {
                    'endpoint': endpoint['name'],
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'response_text': response.text[:200] if response.text else '',
                    'response_length': len(response.text) if response.text else 0,
                    'headers': dict(response.headers)
                }
                
                # Check if this looks like a valid authenticated response
                if response.status_code == 200:
                    response_text = response.text.lower()
                    if ('login' not in response_text and 
                        'unauthorized' not in response_text and
                        len(response.text) > 0):
                        result['appears_authenticated'] = True
                        session_valid = True
                        logger.info(f"✅ {endpoint['name']}: Appears authenticated")
                    else:
                        result['appears_authenticated'] = False
                        logger.warning(f"❌ {endpoint['name']}: Authentication required")
                else:
                    result['appears_authenticated'] = False
                    logger.warning(f"❌ {endpoint['name']}: {response.status_code}")
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"❌ {endpoint['name']}: {e}")
                results.append({
                    'endpoint': endpoint['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'session_valid': session_valid,
            'successful_endpoints': len([r for r in results if r.get('appears_authenticated', False)]),
            'total_endpoints': len(results),
            'results': results,
            'timestamp': time.time()
        }
    
    def submit_with_session_warmup(self, passport_number: str, nationality: str, 
                                  face_photo_path: str, passport_photo_path: str,
                                  email: str = None, contact_no: str = None, 
                                  person_name: str = None) -> Dict[str, Any]:
        """Submit document with session warmup sequence to improve authentication success."""
        
        logger.info("Starting document submission with session warmup...")
        
        # Step 1: Perform session warmup
        warmup_result = self.perform_session_warmup()
        
        # Step 2: Small delay to mimic browser behavior
        time.sleep(1)
        
        # Step 3: Submit document
        submission_result = self.submit_document(
            passport_number=passport_number,
            nationality=nationality,
            face_photo_path=face_photo_path,
            passport_photo_path=passport_photo_path,
            email=email,
            contact_no=contact_no,
            person_name=person_name
        )
        
        # Combine results
        submission_result['warmup_performed'] = True
        submission_result['warmup_success'] = warmup_result['session_valid']
        submission_result['warmup_endpoints'] = f"{warmup_result['successful_endpoints']}/{warmup_result['total_endpoints']}"
        
        if warmup_result['session_valid']:
            logger.info("✅ Session warmup successful - proceeding with enhanced authentication")
        else:
            logger.warning("⚠️ Session warmup failed - authentication may not work")
        
        return submission_result
        
    def _analyze_response(self, response) -> Dict[str, Any]:
        """Analyze response from UAE eservices to provide user-friendly interpretation."""
        
        analysis = {
            'likely_cause': 'unknown',
            'user_message': '',
            'action_needed': '',
            'success_indicators': []
        }
        
        content_lower = response.text.lower() if response.text else ''
        
        # Check for different response patterns
        if response.status_code == 200:
            if 'login' in content_lower or 'تسجيل الدخول' in content_lower:
                analysis.update({
                    'likely_cause': 'expired_session',
                    'user_message': '🔄 Session expired - redirected to login page',
                    'action_needed': 'Update tokens/cookies from a fresh browser session'
                })
                
            elif 'success' in content_lower or 'submitted' in content_lower or 'received' in content_lower:
                analysis.update({
                    'likely_cause': 'successful_submission',
                    'user_message': '✅ Document appears to have been submitted successfully',
                    'action_needed': 'Check the response content for confirmation details'
                })
                
            elif 'error' in content_lower or 'invalid' in content_lower:
                analysis.update({
                    'likely_cause': 'validation_error', 
                    'user_message': '❌ Validation error in submission data',
                    'action_needed': 'Check document data and format'
                })
                
            elif 'maintenance' in content_lower or 'unavailable' in content_lower:
                analysis.update({
                    'likely_cause': 'site_maintenance',
                    'user_message': '🔧 Site appears to be under maintenance',
                    'action_needed': 'Try again later'
                })
                
            else:
                analysis.update({
                    'likely_cause': 'needs_review',
                    'user_message': '📋 Response received - needs manual review',
                    'action_needed': 'Check response content manually'
                })
                
        elif response.status_code == 302 or response.status_code == 301:
            analysis.update({
                'likely_cause': 'redirect_response',
                'user_message': '🔀 Server redirected the request',
                'action_needed': 'Check if tokens are valid or if submission was processed'
            })
            
        elif response.status_code == 403:
            analysis.update({
                'likely_cause': 'access_denied',
                'user_message': '🚫 Access denied - authentication issue',
                'action_needed': 'Update authentication tokens/cookies immediately'
            })
            
        elif response.status_code == 404:
            analysis.update({
                'likely_cause': 'endpoint_not_found',
                'user_message': '❓ Endpoint not found - API may have changed',
                'action_needed': 'Check if API URL is still correct'
            })
            
        elif response.status_code >= 500:
            analysis.update({
                'likely_cause': 'server_error',
                'user_message': '⚠️ Server error on UAE eservices side',
                'action_needed': 'Try again later or during different hours'
            })
            
        return analysis
    
    def _debug_print_form_data(self, all_fields, boundary):
        """Print form data structure for debugging (without binary content)."""
        
        logger.info("=== FORM DATA STRUCTURE DEBUG ===")
        logger.info(f"Boundary: ----{boundary}")
        
        for name, value, is_file in all_fields:
            if is_file:
                filename, content_type, content = value
                content_size = len(content) if isinstance(content, bytes) else len(str(content))
                logger.info(f"Field: {name} (FILE)")
                logger.info(f"  filename: '{filename}'")
                logger.info(f"  content-type: {content_type}")
                logger.info(f"  content size: {content_size} bytes")
            else:
                logger.info(f"Field: {name} = '{value}'")
        
        logger.info("=== END FORM DATA DEBUG ===")
    
    def _debug_print_cookies(self):
        """Print current cookies for debugging."""
        
        logger.info("=== CURRENT COOKIES DEBUG ===")
        for name, value in COOKIES.items():
            if value:
                logger.info(f"Cookie: {name} = {value[:30]}{'...' if len(value) > 30 else ''}")
            else:
                logger.info(f"Cookie: {name} = (empty)")
        logger.info("=== END COOKIES DEBUG ===")
    
    def _update_cookies_from_response(self, response):
        """Update global cookies if server provides new ones."""
        
        global COOKIES
        
        if 'Set-Cookie' in response.headers:
            logger.info("Server provided new cookies - updating...")
            
            # Parse Set-Cookie headers
            set_cookies = response.headers.get('Set-Cookie', '')
            if isinstance(set_cookies, str):
                set_cookies = [set_cookies]
            elif hasattr(set_cookies, '__iter__'):
                set_cookies = list(set_cookies)
            
            cookies_updated = 0
            for cookie_header in set_cookies:
                # Parse individual cookie
                for cookie_part in cookie_header.split(','):
                    if '=' in cookie_part:
                        cookie_pair = cookie_part.split(';')[0].strip()  # Get just name=value part
                        if '=' in cookie_pair:
                            name, value = cookie_pair.split('=', 1)
                            name = name.strip()
                            value = value.strip()
                            
                            # Update if this cookie exists in our config
                            if name in COOKIES:
                                old_value = COOKIES[name]
                                COOKIES[name] = value
                                logger.info(f"Updated cookie {name}: {old_value[:20]}... -> {value[:20]}...")
                                cookies_updated += 1
                            elif name.startswith('__') or name.startswith('.AspNet'):
                                # Add new authentication cookies
                                COOKIES[name] = value
                                logger.info(f"Added new cookie {name}: {value[:20]}...")
                                cookies_updated += 1
            
            if cookies_updated > 0:
                logger.info(f"Updated {cookies_updated} cookies from server response")
                # Update session cookies as well
                self.session.cookies.update(COOKIES)
            else:
                logger.info("No relevant cookies found in server response")
    
    def update_config_from_curl(self, curl_command_file: str):
        """
        Update configuration from a new curl command file.
        
        Args:
            curl_command_file: Path to file containing the new curl command
        """
        try:
            with open(curl_command_file, 'r') as f:
                curl_content = f.read()
            
            # Extract cookies from curl command
            if '-b ' in curl_content:
                cookie_line = curl_content.split('-b ')[1].split(' \\')[0].strip("'\"")
                self._parse_cookies(cookie_line)
                
            # Extract verification token from form data
            if '__RequestVerificationToken' in curl_content:
                token_start = curl_content.find('__RequestVerificationToken\\r\\n\\r\\n') + len('__RequestVerificationToken\\r\\n\\r\\n')
                token_end = curl_content.find('\\r\\n', token_start)
                if token_start > 0 and token_end > token_start:
                    new_token = curl_content[token_start:token_end]
                    self._update_verification_token(new_token)
                    
            logger.info("Configuration updated from curl command")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update config from curl: {e}")
            return False
    
    def _parse_cookies(self, cookie_string: str):
        """Parse cookie string and update COOKIES dict."""
        # This is a simplified parser - you might need to enhance it
        # based on the exact format of your cookie strings
        cookies = {}
        for cookie in cookie_string.split('; '):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key] = value
        
        # Update global COOKIES
        COOKIES.update(cookies)
        logger.info(f"Updated {len(cookies)} cookies")
    
    def _update_verification_token(self, token: str):
        """Update the request verification token."""
        global REQUEST_VERIFICATION_TOKEN
        REQUEST_VERIFICATION_TOKEN = token
        logger.info("Updated request verification token")
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def submit_document(self, 
                       passport_number: str,
                       nationality: str,
                       face_photo_path: str,
                       passport_photo_path: str,
                       email: str = None,
                       contact_no: str = None,
                       person_name: str = None) -> Dict[str, Any]:
        """
        Submit document verification request.
        
        Args:
            passport_number: Passport number
            nationality: Nationality (must be in NATIONALITY_MAPPING)
            face_photo_path: Path to face photo file
            passport_photo_path: Path to passport photo file
            email: Email address (optional, uses default if not provided)
            contact_no: Contact number (optional, uses default if not provided)
            person_name: Person name for filenames (optional)
            
        Returns:
            Dict containing response data and status
        """
        self._rate_limit()
        
        # Validate inputs
        if not os.path.exists(face_photo_path):
            raise FileNotFoundError(f"Face photo not found: {face_photo_path}")
        if not os.path.exists(passport_photo_path):
            raise FileNotFoundError(f"Passport photo not found: {passport_photo_path}")
        if nationality not in self.nationality_map:
            # Try to find a close match
            available = list(self.nationality_map.keys())
            close_matches = [n for n in available if nationality.lower() in n.lower() or n.lower() in nationality.lower()]
            if close_matches:
                suggestion = f". Did you mean one of: {close_matches[:3]}?"
            else:
                suggestion = f". Available nationalities: {available[:10]}{'...' if len(available) > 10 else ''}"
            raise ValueError(f"Nationality '{nationality}' not found in mapping{suggestion}")
        
        # Build the multipart form data manually to match curl exactly
        import uuid
        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:16]}"
        
        # Prepare filenames
        if person_name:
            face_filename = f"{person_name} - photo.jpg"
            passport_filename = f"{person_name} - passport.jpg"
        else:
            face_filename = os.path.basename(face_photo_path)
            passport_filename = os.path.basename(passport_photo_path)
        
        # Read file contents
        with open(face_photo_path, 'rb') as f:
            face_content = f.read()
        with open(passport_photo_path, 'rb') as f:
            passport_content = f.read()
        
        # Build multipart form data manually to match curl format exactly
        form_parts = []
        
        # Add all fields in the exact order from curl
        all_fields = [
            # Form fields
            ('__RequestVerificationToken', REQUEST_VERIFICATION_TOKEN, False),
            ('Key', '', False),
            ('PassportNumber', passport_number, False),
            ('Email', email or DEFAULT_FORM_DATA['Email'], False),
            ('ContactNo', contact_no or '0505544143', False),
            ('Nationality.Value', self.nationality_map[nationality]['Value'], False),
            ('Nationality.Description', self.nationality_map[nationality]['Description'], False),
            # File fields
            ('PersonPhotoDocument', (face_filename, 'image/jpeg', face_content), True),
            ('PassportDocumentFirstPage', (passport_filename, 'image/jpeg', passport_content), True),
            ('PassportDocumentSecondPage', ('', 'application/octet-stream', b''), True),
            ('NationalIdentityDocumentFirstPage', ('', 'application/octet-stream', b''), True),
            ('NationalIdentityDocumentSecondPage', ('', 'application/octet-stream', b''), True),
            # Regular form field (not file)
            ('EducationCertificateAvailable', 'false', False),
            # More file fields
            ('EducationCertificateFirstPage', ('', 'application/octet-stream', b''), True),
            ('EducationCertificateSecondPage', ('', 'application/octet-stream', b''), True)
        ]
        
        for name, value, is_file in all_fields:
            form_parts.append(f'------{boundary}')
            
            if is_file:
                filename, content_type, content = value
                if filename:
                    form_parts.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"')
                    form_parts.append(f'Content-Type: {content_type}')
                else:
                    form_parts.append(f'Content-Disposition: form-data; name="{name}"; filename=""')
                    form_parts.append(f'Content-Type: {content_type}')
                form_parts.append('')
                
                if isinstance(content, bytes) and len(content) > 0:
                    # For binary data, we'll handle it separately
                    form_parts.append('BINARY_PLACEHOLDER_' + name)
                else:
                    form_parts.append('')
            else:
                # Regular form field
                form_parts.append(f'Content-Disposition: form-data; name="{name}"')
                form_parts.append('')
                form_parts.append(str(value))
        
        # Add closing boundary
        form_parts.append(f'------{boundary}--')
        
        # Join text parts
        form_text = '\r\n'.join(form_parts)
        
        # Replace binary placeholders with actual binary data
        form_bytes = form_text.encode('utf-8')
        form_bytes = form_bytes.replace(b'BINARY_PLACEHOLDER_PersonPhotoDocument', face_content)
        form_bytes = form_bytes.replace(b'BINARY_PLACEHOLDER_PassportDocumentFirstPage', passport_content)
        form_bytes = form_bytes.replace(b'BINARY_PLACEHOLDER_PassportDocumentSecondPage', b'')
        form_bytes = form_bytes.replace(b'BINARY_PLACEHOLDER_NationalIdentityDocumentFirstPage', b'')
        form_bytes = form_bytes.replace(b'BINARY_PLACEHOLDER_NationalIdentityDocumentSecondPage', b'')
        form_bytes = form_bytes.replace(b'BINARY_PLACEHOLDER_EducationCertificateFirstPage', b'')
        form_bytes = form_bytes.replace(b'BINARY_PLACEHOLDER_EducationCertificateSecondPage', b'')
        
        # Prepare headers with exact Content-Type
        headers = STATIC_HEADERS.copy()
        headers['Content-Type'] = f'multipart/form-data; boundary=----{boundary}'
        
        try:
            # Make the request with manually built multipart data
            logger.info(f"Submitting document for passport: {passport_number}")
            logger.info(f"Using boundary: ----{boundary}")
            logger.info(f"Form data size: {len(form_bytes)} bytes")
            
            # DEBUG: Print form data structure (without binary content)
            self._debug_print_form_data(all_fields, boundary)
            
            # DEBUG: Print current cookies
            self._debug_print_cookies()
            
            response = self.session.post(
                API_URL,
                headers=headers,
                cookies=COOKIES,
                data=form_bytes,
                timeout=(10, 60)  # Connect timeout 10s, read timeout 60s
            )
            
            # DEBUG: Print response info
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            # Update cookies if server provides new ones
            self._update_cookies_from_response(response)
            
            # Analyze response
            response_analysis = self._analyze_response(response)
            
            # Prepare result
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'passport_number': passport_number,
                'nationality': nationality,
                'timestamp': time.time(),
                'response_text': response.text[:1000] if response.text else '',  # Truncate for logging
                'headers': dict(response.headers),
                'interpretation': response_analysis
            }
            
            if result['success']:
                logger.info(f"Successfully submitted document for {passport_number}")
            else:
                logger.warning(f"Request failed for {passport_number}. Status: {response.status_code}")
                
            return result
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL error for {passport_number}: {e}")
            logger.info("Trying with relaxed SSL settings...")
            
            # Try with relaxed SSL settings as fallback
            try:
                original_verify = self.session.verify
                self.session.verify = False
                
                response = self.session.post(
                    API_URL,
                    headers=headers,
                    cookies=COOKIES,
                    data=form_bytes,
                    timeout=(10, 60)
                )
                
                # Restore SSL verification
                self.session.verify = original_verify
                
                # Update cookies if server provides new ones
                self._update_cookies_from_response(response)
                
                # Process the response normally
                result = {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'passport_number': passport_number,
                    'nationality': nationality,
                    'timestamp': time.time(),
                    'response_text': response.text[:1000] if response.text else '',
                    'headers': dict(response.headers),
                    'ssl_fallback_used': True
                }
                
                if result['success']:
                    logger.warning(f"Successfully submitted document for {passport_number} using SSL fallback")
                else:
                    logger.warning(f"Request failed for {passport_number} even with SSL fallback. Status: {response.status_code}")
                
                return result
                
            except Exception as fallback_error:
                # Restore SSL verification
                self.session.verify = original_verify
                logger.error(f"SSL fallback also failed for {passport_number}: {fallback_error}")
                
                return {
                    'success': False,
                    'error': f"SSL Error: {str(e)}. Fallback attempt: {str(fallback_error)}",
                    'passport_number': passport_number,
                    'nationality': nationality,
                    'timestamp': time.time(),
                    'ssl_error': True
                }
        
        except requests.RequestException as e:
            logger.error(f"Request failed for {passport_number}: {e}")
            return {
                'success': False,
                'error': str(e),
                'passport_number': passport_number,
                'nationality': nationality,
                'timestamp': time.time()
            }
        
        finally:
            # No need to close file handles since we read them manually
            pass
    
    def submit_from_json(self, json_path: str) -> Dict[str, Any]:
        """
        Submit document from JSON configuration file.
        
        Args:
            json_path: Path to JSON file containing document info
            
        Returns:
            Dict containing response data and status
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Extract required information
            passport_number = data['original_data']['Passport Number']
            nationality = data['original_data']['Nationality']
            person_name = data['original_data']['Maid Name'].strip()
            
            # Build file paths
            json_dir = os.path.dirname(json_path)
            face_photo_path = os.path.join(json_dir, data['downloaded_images']['face_photo']['filename'])
            passport_photo_path = os.path.join(json_dir, data['downloaded_images']['passport']['filename'])
            
            logger.info(f"Processing {person_name} (ID: {data.get('maid_id', 'Unknown')})")
            
            return self.submit_document(
                passport_number=passport_number,
                nationality=nationality,
                face_photo_path=face_photo_path,
                passport_photo_path=passport_photo_path,
                person_name=person_name
            )
            
        except Exception as e:
            logger.error(f"Failed to process JSON file {json_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'json_path': json_path,
                'timestamp': time.time()
            }
    
    def batch_process(self, data_dir: str) -> list:
        """
        Process all JSON files in a directory.
        
        Args:
            data_dir: Directory containing JSON files with document data
            
        Returns:
            List of results for each processed document
        """
        results = []
        data_path = Path(data_dir)
        
        # Find all info.json files
        json_files = list(data_path.rglob('info.json'))
        
        if not json_files:
            logger.warning(f"No info.json files found in {data_dir}")
            return results
        
        logger.info(f"Found {len(json_files)} documents to process")
        
        for json_file in json_files:
            try:
                result = self.submit_from_json(str(json_file))
                results.append(result)
                
                # Add a delay between batch requests
                if len(results) < len(json_files):  # Not the last request
                    time.sleep(self.min_request_interval)
                    
            except Exception as e:
                logger.error(f"Failed to process {json_file}: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'json_path': str(json_file),
                    'timestamp': time.time()
                })
        
        # Summary
        successful = sum(1 for r in results if r.get('success', False))
        logger.info(f"Batch processing complete: {successful}/{len(results)} successful")
        
        return results
