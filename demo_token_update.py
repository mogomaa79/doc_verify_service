"""
Demo script showing how easy it is to update tokens from a new curl command.
"""

def create_sample_curl_command():
    """Create a sample curl command file to demonstrate token updating."""
    
    sample_curl = '''curl 'https://eservices.mohre.gov.ae/TasheelWeb/services/transactionentry/505?mk=' \\
  -H 'ADRUM: isAjax:true' \\
  -H 'Accept: */*' \\
  -H 'Accept-Language: en-US,en;q=0.9' \\
  -H 'Connection: keep-alive' \\
  -H 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary0qWCpVRUXoIhnMwJ' \\
  -b 'Qid=; X-Language=en; JSS=NEW_JSS_TOKEN_HERE; ASP.NET_SessionId=NEW_SESSION_ID; IsTasheelUser_E11User=False; __RequestVerificationToken_L1Rhc2hlZWxXZWI1=NEW_CSRF_TOKEN; .AspNet.TasheelApplicationCookie=NEW_APPLICATION_COOKIE_HERE' \\
  -H 'Origin: https://eservices.mohre.gov.ae' \\
  --data-raw $'------WebKitFormBoundary0qWCpVRUXoIhnMwJ\\r\\nContent-Disposition: form-data; name="__RequestVerificationToken"\\r\\n\\r\\nNEW_VERIFICATION_TOKEN_HERE\\r\\n------WebKitFormBoundary0qWCpVRUXoIhnMwJ\\r\\n'
'''
    
    with open('sample_new_command.sh', 'w') as f:
        f.write(sample_curl)
    
    print("Created sample_new_command.sh")
    print("\nTo update tokens from a real curl command:")
    print("1. Copy the curl command from browser dev tools")
    print("2. Save it to a file (e.g., 'new_command.sh')")
    print("3. Run: python update_config.py new_command.sh")
    print("\nThe system will automatically extract and update:")
    print("- All cookies from the -b flag")
    print("- The verification token from the form data")

if __name__ == "__main__":
    create_sample_curl_command()
