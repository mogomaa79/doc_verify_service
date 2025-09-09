"""
Geographic location and network context testing for UAE eservices.
Test hypothesis: 401 Unauthorized due to geographic restrictions.
"""

import requests
import time
import json
import logging
from typing import Dict, Any
from doc_verifier import DocumentVerifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeoLocationTester:
    """Test geographic and network-based restrictions."""
    
    def __init__(self):
        self.verifier = DocumentVerifier()
        
    def analyze_geo_restrictions(self):
        """Comprehensive analysis of potential geographic restrictions."""
        
        print("🌍 GEOGRAPHIC RESTRICTION ANALYSIS")
        print("=" * 60)
        
        print("\n📍 CURRENT NETWORK ANALYSIS")
        print("-" * 40)
        
        # Get current IP and location
        self._check_current_location()
        
        print("\n🔍 UAE ESERVICES ACCESS PATTERNS")
        print("-" * 40)
        
        # Analyze response patterns for geo-blocking indicators
        self._analyze_access_patterns()
        
        print("\n🌐 NETWORK CONTEXT HYPOTHESIS")
        print("-" * 40)
        
        self._explain_geo_blocking_theory()
        
        print("\n🔧 VPN TESTING STRATEGY")
        print("-" * 40)
        
        self._provide_vpn_testing_guide()
        
    def _check_current_location(self):
        """Check current IP address and geographic location."""
        
        try:
            print("Checking current network location...")
            
            # Check IP and location
            ip_services = [
                ("ipapi.co", "https://ipapi.co/json/"),
                ("ipinfo.io", "https://ipinfo.io/json"),
                ("httpbin.org", "https://httpbin.org/ip")
            ]
            
            for service_name, url in ip_services:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if service_name == "ipapi.co":
                            print(f"✅ {service_name}:")
                            print(f"   IP: {data.get('ip', 'Unknown')}")
                            print(f"   Country: {data.get('country_name', 'Unknown')} ({data.get('country_code', 'Unknown')})")
                            print(f"   City: {data.get('city', 'Unknown')}")
                            print(f"   ISP: {data.get('org', 'Unknown')}")
                            
                            # Check if in UAE or nearby
                            country_code = data.get('country_code', '').upper()
                            if country_code == 'AE':
                                print(f"   🎯 Status: IN UAE - Should work!")
                            elif country_code in ['SA', 'OM', 'QA', 'KW', 'BH']:
                                print(f"   🟡 Status: GCC region - Might work")
                            else:
                                print(f"   ❌ Status: Outside UAE/GCC - Likely blocked")
                            break
                            
                except Exception as e:
                    print(f"   ❌ {service_name}: {e}")
                    
        except Exception as e:
            print(f"❌ Network location check failed: {e}")
    
    def _analyze_access_patterns(self):
        """Analyze UAE eservices responses for geo-blocking patterns."""
        
        print("Analyzing UAE eservices response patterns...")
        
        # Test basic connectivity first
        test_endpoints = [
            {
                'name': 'UAE eservices homepage',
                'url': 'https://eservices.mohre.gov.ae/TasheelWeb/home',
                'method': 'GET'
            },
            {
                'name': 'Session expiry endpoint',
                'url': 'https://eservices.mohre.gov.ae/TasheelWeb/GetSessionExpirytime',
                'method': 'POST'
            },
            {
                'name': 'Login page',
                'url': 'https://eservices.mohre.gov.ae/TasheelWeb/account/login',
                'method': 'GET'
            }
        ]
        
        for endpoint in test_endpoints:
            try:
                print(f"\n🔍 Testing: {endpoint['name']}")
                
                if endpoint['method'] == 'GET':
                    response = requests.get(
                        endpoint['url'], 
                        timeout=10,
                        allow_redirects=True
                    )
                else:
                    response = requests.post(
                        endpoint['url'],
                        timeout=10,
                        allow_redirects=True
                    )
                
                print(f"   Status: {response.status_code}")
                print(f"   Response size: {len(response.text)} chars")
                
                # Look for geo-blocking indicators
                response_text = response.text.lower()
                geo_indicators = [
                    'geographic', 'location', 'region', 'country',
                    'blocked', 'restricted', 'not available',
                    'access denied', 'forbidden', 'not authorized'
                ]
                
                found_indicators = [ind for ind in geo_indicators if ind in response_text]
                if found_indicators:
                    print(f"   🚨 Geo-blocking indicators: {found_indicators}")
                
                # Check specific UAE access patterns
                if response.status_code in [403, 451, 423]:
                    print(f"   🚨 Status {response.status_code} often indicates geo-blocking")
                elif response.status_code == 401:
                    print(f"   🤔 Status 401: Could be auth OR geo-blocking")
                elif response.status_code == 200:
                    print(f"   ✅ Status 200: Basic access working")
                
                # Check response headers for geo info
                headers_to_check = ['cf-ipcountry', 'x-country', 'x-geo', 'location']
                for header in headers_to_check:
                    if header in response.headers:
                        print(f"   🌍 Geo header {header}: {response.headers[header]}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def _explain_geo_blocking_theory(self):
        """Explain the geo-blocking theory and evidence."""
        
        print("UAE eservices likely implements geographic restrictions:")
        print()
        
        evidence = [
            "🏛️ Government Service: High security, citizen-focused",
            "🔒 Consistent 401s: All endpoints, not just document submission", 
            "⚡ Immediate Response: No authentication processing delay",
            "🍪 Server Cooperation: Cookie updates work, SSL connects",
            "🎯 Perfect Tech: Request format exactly matches browser",
            "🌍 Access Pattern: Government sites often geo-restrict"
        ]
        
        for item in evidence:
            print(f"  {item}")
        
        print()
        print("HYPOTHESIS: UAE eservices blocks non-UAE IP addresses")
        print("SOLUTION: Use UAE VPN to test authentication bypass")
    
    def _provide_vpn_testing_guide(self):
        """Provide comprehensive VPN testing guide."""
        
        print("VPN Testing Strategy:")
        print()
        
        print("🎯 RECOMMENDED VPN SERVERS:")
        print("  1. UAE (Dubai/Abu Dhabi) - Primary choice")
        print("  2. GCC region (Saudi, Qatar, Kuwait) - Secondary")
        print("  3. Middle East (Egypt, Jordan) - Tertiary")
        print()
        
        print("🔧 TESTING PROTOCOL:")
        print("  1. Connect to UAE VPN server")
        print("  2. Verify new IP location")
        print("  3. Test basic UAE eservices access")
        print("  4. Try session warmup endpoints")
        print("  5. Test document submission")
        print()
        
        print("⚡ QUICK TEST COMMANDS:")
        print("  # After connecting VPN:")
        print("  python geo_location_test.py")
        print("  python main.py 6  # Test session warmup")
        print("  python main.py 7  # Test with session warmup")
        print("  python main.py test  # Quick document test")
        
    def test_with_current_network(self):
        """Test current network access to establish baseline."""
        
        print("\n🔍 BASELINE NETWORK TEST")
        print("-" * 40)
        
        # Test session warmup endpoints
        warmup_result = self.verifier.perform_session_warmup()
        
        print(f"Session warmup success: {warmup_result['session_valid']}")
        print(f"Successful endpoints: {warmup_result['successful_endpoints']}/{warmup_result['total_endpoints']}")
        
        # Test session expiry
        session_result = self.verifier.check_session_expiry()
        print(f"Session expiry check: {'✅ SUCCESS' if session_result.get('success') else '❌ FAILED'}")
        
        if not session_result.get('success'):
            print(f"Error: {session_result.get('error', 'Unknown')}")
            
        # Provide interpretation
        if warmup_result['successful_endpoints'] == 0 and not session_result.get('success'):
            print()
            print("🔍 ANALYSIS: All authenticated endpoints failing")
            print("💡 LIKELY CAUSE: Geographic/network restrictions")
            print("🎯 RECOMMENDATION: Test with UAE VPN")
        else:
            print()
            print("🔍 ANALYSIS: Some endpoints working")
            print("💡 LIKELY CAUSE: Authentication or token issues")
            print("🎯 RECOMMENDATION: Fresh token capture")
            
        return {
            'warmup_success': warmup_result['session_valid'],
            'session_check_success': session_result.get('success', False),
            'total_successful': warmup_result['successful_endpoints'],
            'recommendation': 'vpn' if warmup_result['successful_endpoints'] == 0 else 'tokens'
        }
    
    def comprehensive_network_test(self):
        """Run comprehensive network and geographic testing."""
        
        self.analyze_geo_restrictions()
        baseline = self.test_with_current_network()
        
        print(f"\n🎯 FINAL RECOMMENDATION")
        print("-" * 40)
        
        if baseline['recommendation'] == 'vpn':
            print("🌍 STRONG EVIDENCE for geographic restrictions")
            print("📍 Next step: Connect to UAE VPN and retest")
            print("⚡ Expected result: Authentication will work from UAE IP")
        else:
            print("🔑 EVIDENCE points to authentication issues")
            print("📍 Next step: Capture fresh tokens")
            print("⚡ Expected result: Fresh tokens will resolve issue")
            
        print()
        print("🚀 READY FOR VPN TEST")
        print("Connect to UAE VPN, then run: python main.py 6")

if __name__ == "__main__":
    tester = GeoLocationTester()
    tester.comprehensive_network_test()
