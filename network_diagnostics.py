"""
Network diagnostics for UAE eservices connectivity issues.
"""

import socket
import ssl
import requests
import subprocess
import platform
from urllib.parse import urlparse

def test_basic_connectivity():
    """Test basic network connectivity to UAE eservices."""
    
    print("🔍 NETWORK DIAGNOSTICS FOR UAE ESERVICES")
    print("=" * 50)
    
    host = "eservices.mohre.gov.ae"
    port = 443
    
    # Test 1: Basic DNS resolution
    print(f"\n1️⃣  DNS Resolution for {host}:")
    try:
        ip = socket.gethostbyname(host)
        print(f"   ✅ Resolved to: {ip}")
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        return False
    
    # Test 2: Port connectivity
    print(f"\n2️⃣  Port {port} connectivity:")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"   ✅ Port {port} is reachable")
        else:
            print(f"   ❌ Port {port} is not reachable")
            return False
    except Exception as e:
        print(f"   ❌ Connection test failed: {e}")
        return False
    finally:
        sock.close()
    
    # Test 3: SSL/TLS handshake
    print(f"\n3️⃣  SSL/TLS handshake:")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"   ✅ SSL handshake successful")
                print(f"   📋 SSL version: {ssock.version()}")
                print(f"   🔐 Cipher: {ssock.cipher()}")
    except ssl.SSLError as e:
        print(f"   ❌ SSL handshake failed: {e}")
        print(f"   💡 This suggests SSL/TLS compatibility issues")
        
        # Try with different SSL contexts
        print(f"\n   🔄 Trying with relaxed SSL settings:")
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            context.set_ciphers('DEFAULT:@SECLEVEL=1')
            
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    print(f"   ✅ SSL handshake successful with relaxed settings")
                    print(f"   📋 SSL version: {ssock.version()}")
                    return True
        except Exception as e:
            print(f"   ❌ Even relaxed SSL failed: {e}")
            return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    return True

def test_http_connectivity():
    """Test HTTP connectivity with curl if available."""
    
    print(f"\n4️⃣  HTTP connectivity test:")
    
    # Test with curl if available
    try:
        if platform.system() != "Windows":
            result = subprocess.run([
                'curl', '-I', '--connect-timeout', '10', 
                'https://eservices.mohre.gov.ae/TasheelWeb/'
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"   ✅ curl successful")
                print(f"   📋 Headers: {result.stdout[:200]}...")
            else:
                print(f"   ❌ curl failed: {result.stderr}")
        else:
            print(f"   ⚠️  curl test skipped on Windows")
    except Exception as e:
        print(f"   ⚠️  curl test failed: {e}")

def suggest_solutions():
    """Suggest potential solutions based on diagnostics."""
    
    print(f"\n💡 POTENTIAL SOLUTIONS:")
    print("=" * 30)
    
    solutions = [
        "1️⃣  **VPN/Proxy Issues**: Try disconnecting VPN or changing proxy settings",
        "2️⃣  **Firewall**: Check if corporate/personal firewall is blocking HTTPS to UAE sites",
        "3️⃣  **Geo-blocking**: The UAE site might block requests from certain countries",
        "4️⃣  **Network Location**: Try from a different network (mobile hotspot, different WiFi)",
        "5️⃣  **Browser Test**: Try accessing https://eservices.mohre.gov.ae manually in browser first",
        "6️⃣  **Timing**: UAE government sites might have maintenance windows",
        "7️⃣  **Certificates**: Your system might need updated certificate authorities",
    ]
    
    for solution in solutions:
        print(f"   {solution}")
    
    print(f"\n🔧 IMMEDIATE NEXT STEPS:")
    print("   1. Test manual access via browser")
    print("   2. Try from different network/location")
    print("   3. Check if tokens are still valid by testing in browser dev tools")
    print("   4. Contact network administrator if on corporate network")

def main():
    """Run complete network diagnostics."""
    
    connectivity_ok = test_basic_connectivity()
    test_http_connectivity()
    
    if not connectivity_ok:
        suggest_solutions()
    else:
        print(f"\n✅ Network connectivity appears normal")
        print(f"   The issue might be with tokens/cookies or request format")

if __name__ == "__main__":
    main()
