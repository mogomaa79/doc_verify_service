#!/usr/bin/env python3
"""
MINIMAL working version - exact curl replica with SSL fix.
Key insight: curl command had EMPTY files (just filenames, no content)!
"""

import requests
import ssl
import urllib3
from requests.adapters import HTTPAdapter

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class UAESSLAdapter(HTTPAdapter):
    """Minimal SSL adapter for UAE eservices (same as what worked before)."""
    
    def init_poolmanager(self, *args, **kwargs):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.set_ciphers('DEFAULT:@SECLEVEL=1')
        kwargs['ssl_context'] = ssl_context
        return super().init_poolmanager(*args, **kwargs)

def submit_minimal():
    """Submit using EXACT curl replica with minimal SSL fix."""
    
    print("🎯 MINIMAL DOCUMENT SUBMISSION")
    print("Replicating EXACT curl command that worked in PowerShell")
    print("=" * 60)
    
    # Create session with SSL fix
    session = requests.Session()
    session.mount('https://eservices.mohre.gov.ae', UAESSLAdapter())
    
    # EXACT URL from working curl
    url = "https://eservices.mohre.gov.ae/TasheelWeb/services/transactionentry/505?mk="
    
    # EXACT headers from working curl
    headers = {
        'ADRUM': 'isAjax:true',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary48BlJyyBFw9hi4gn',
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
    
    # EXACT cookies from working curl  
    cookies = {
        'Qid': '',
        'X-Language': 'en',
        'JSS': '02f0957673-730f-437kmw3C7_NIsXfjZKJuPO01TwjCvs_jDr6HmNJJINHdGXc53Iz7vztuihdFPDICTwQrI',
        'ASP.NET_SessionId': 'wwrjvns4wpvaprxaqtgqk2bj',
        'IsTasheelUser_E11User': 'False',
        '__RequestVerificationToken_L1Rhc2hlZWxXZWI1': 'Pi75r0A1ftC-8Z_xu8j0yiHiab9gIX7ow4szyQ3ze-Pjft6fxDpzTi8n5KZl6gVzXU9fD5lClchJuVc3gBJEG8LQ7TE1',
        '.AspNet.TasheelApplicationCookie': 'osoRjdVYmXVoAh5T19sP5YK_4afqkCYaquYJx7iMBmIdiWlAPXLlR5Ma0DzrshOcKwg9M4zKJPCJ9Zv9U1tJmqTkdvKZmEKWWSCQxLgU5qOcQ4IRyNpyAGdpJwMzzSid1DFqymp5ZhEbtsWYG6pMdQYaCTnuYs5GPkD4_aH5CIHd0tWwQvO0q6bOX15dVJC8dhwWBLVFncA6NqN4omnFbN3Fi_i7n0em_Wye_IDTVAUUa103F-AJRL4ZaGu7ePa3s-NRHG6Yp8-3LUxc4O4wv979DP-g1sceL2xx1s-1Qc0Busai4Q145OEVedQC9bg15w6KxrbGWQ0BiIgIIydXcj_VsQOBQK1h0BnOec3UU6DqbKr0O6Zdiorrx0mA-FedWQSopBUjNDJ4nsNNOQcXYE57l-tqDFaFAi8TmjIC2evZb93YvKZspFuMwa7x4g3hMNUN_NGgsbtNlKzaRDM_PmmOL5qVPKXYzjFT9eurjGAiJ6yRilL0FZQ-f9arskBI1MVFILhC5hC3qhG4Elt6AJ2CesWadVYd8KbawWhTuHLQjMyphtlu0ylue4fxevkc-xqhSgFqyOOqTQYv41pjov5R2DiHsFhazBKtUPSVvF_3qFEi0RpA1ax1hJq0v_HIcUjDLo25hBbfWDJ6-Wy9QrA15X2zSdlOj88gs05LAX-xNYx-479jOuMSKOj4dKQtB2bj6Z_zL98TooGfFzwBm-lNcss3FGTpbXX0M2gHKnvYxUjx1nGIol9e31vSGwgbiSX96DL8alvJJHGIK_mjXjmCTbg',
        'ADRUM': 's~1757445674737&r~aHR0cHMlM0ElMkYlMkZlc2VydmljZXMubW9ocmUuZ292LmFlJTJGVGFzaGVlbFdlYiUyRmhvbWUlM0ZoYXNoJTNEMzU='
    }
    
    # EXACT multipart data from working curl 
    # KEY INSIGHT: Files are EMPTY (just filenames, no binary content)!
    boundary = "----WebKitFormBoundary48BlJyyBFw9hi4gn"
    
    form_data = f"""------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="__RequestVerificationToken"\r
\r
apS713vpQqMV3WzxL8-YgT8zSmVkcwqRf-YjOjsI6mksRckBeZyTU4FyG3GhYBveulHFH2tCxX30xcriDAbCCt97lS-EaDIJgNV_oliKlXm0B5fiVdjp_KvEkwQJL1mkRpjqzQ2\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="Key"\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="PassportNumber"\r
\r
P2064022B\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="Email"\r
\r
visaprocessing2@maids.cc\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="ContactNo"\r
\r
0505544143\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="Nationality.Value"\r
\r
237\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="Nationality.Description"\r
\r
PHILIPPINES\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="PersonPhotoDocument"; filename="JOSEPHINE SAMALI NAMUGENYI - passport.jpg"\r
Content-Type: image/jpeg\r
\r
\r
------WebKitFormBoundary48BlJyyBFw9hi4gn\r
Content-Disposition: form-data; name="PassportDocumentFirstPage"; filename="JOSEPHINE SAMALI NAMUGENYI - photo.jpg"\r
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

    print("📝 Request Details:")
    print(f"URL: {url}")
    print(f"Boundary: {boundary}")
    print(f"Form data length: {len(form_data)} chars")
    print(f"Key insight: FILES ARE EMPTY (just filenames)")
    
    try:
        print("\n🚀 Sending request...")
        
        # Make the exact same request with SSL fix
        response = session.post(
            url,
            headers=headers,
            cookies=cookies,
            data=form_data.encode('utf-8'),
            timeout=30
        )
        
        print(f"\n📊 RESPONSE ANALYSIS:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} chars")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        
        # Analyze response content
        response_lower = response.text.lower()
        
        if response.status_code == 200:
            if 'login' in response_lower:
                print("❌ RESULT: Still redirected to login page")
                print("💡 ISSUE: Authentication/network still blocking")
            elif any(word in response_lower for word in ['success', 'submitted', 'confirmed', 'received']):
                print("🎉 RESULT: SUCCESS! Document submission worked!")
                print("✅ BREAKTHROUGH: Found the working approach!")
            elif 'error' in response_lower:
                print("⚠️ RESULT: Server error in processing")
                print("📄 Response preview:")
                print(response.text[:500])
            else:
                print("🤔 RESULT: 200 OK but unclear response")
                print("📄 Response preview (first 800 chars):")
                print(response.text[:800])
                print("\n📄 Response preview (last 200 chars):")
                print(response.text[-200:] if len(response.text) > 200 else "")
                
        else:
            print(f"❌ RESULT: HTTP {response.status_code} error")
            print(f"📄 Error response: {response.text[:300]}")
        
        # Check response headers for clues
        print(f"\n🔍 Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['set-cookie', 'location', 'content-type']:
                print(f"  {key}: {value}")
        
        return {
            'success': response.status_code == 200 and 'login' not in response_lower,
            'status_code': response.status_code,
            'response_preview': response.text[:1000],
            'is_login_redirect': 'login' in response_lower,
            'appears_successful': any(word in response_lower for word in ['success', 'submitted', 'confirmed'])
        }
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    result = submit_minimal()
    
    print(f"\n{'='*60}")
    print("MINIMAL SUBMISSION ANALYSIS")
    print(f"{'='*60}")
    
    if result.get('appears_successful'):
        print("🎉 SUCCESS! This approach works!")
        print("💡 Key insight: Empty files (just filenames) is the secret!")
        print("🚀 Ready to build automation on this foundation")
    elif result.get('is_login_redirect'):
        print("❌ Still getting login redirect")
        print("🔍 Need to check: Network location or token freshness")
    else:
        print("🤔 Unclear result - need manual analysis")
        print("💡 Check response content above for clues")
