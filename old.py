import threading
import re
import ssl
import urllib3
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter

# Configuration
BATCH_SIZE = 50  # Process 50 maids at a time
SUBMISSION_DELAY = 5  # 10 seconds between each submission
BATCH_WAIT_TIME = 60  # 5 minutes wait after batch submission
EMAIL_CHECK_DELAY = 2  # 5 seconds between email checks
MAX_RETRIES = 3  # Max retries for email checking
RETRY_INTERVAL = 180  # 3 minutes between retries

# Cookie lock for thread safety
cookie_lock = threading.Lock()

# ============= Cookie Management Functions =============

def read_cookie_from_file(cookie_file="cookie.txt"):
    try:
        with cookie_lock:
            if not Path(cookie_file).exists():
                print(f"Cookie file {cookie_file} not found")
                return ""

            with open(cookie_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            cookie_pattern = r'\.AspNet\.TasheelApplicationCookie=([^;]+)'
            match = re.search(cookie_pattern, content)

            if match:
                cookie_value = match.group(1)
                return cookie_value
            else:
                return ""

    except Exception as e:
        print(f"Error reading cookie file: {e}")
        return ""

def write_cookie_to_file(cookie_value, cookie_file="cookie.txt"):
    try:
        with cookie_lock:
            existing_content = ""
            if Path(cookie_file).exists():
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read().strip()

            # Pattern to match existing AspNet.TasheelApplicationCookie
            cookie_pattern = r'\.AspNet\.TasheelApplicationCookie=[^;]+'
            new_cookie = f".AspNet.TasheelApplicationCookie={cookie_value}"

            if re.search(cookie_pattern, existing_content):
                # Replace existing cookie
                updated_content = re.sub(cookie_pattern, new_cookie, existing_content)
            else:
                # Add new cookie
                if existing_content:
                    updated_content = existing_content + "; " + new_cookie
                else:
                    updated_content = new_cookie

            # Write back to file
            with open(cookie_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            print(f"Updated AspNet.TasheelApplicationCookie in {cookie_file}")

    except Exception as e:
        print(f"Error writing cookie file: {e}")

def extract_cookie_from_response(response):
    set_cookie_header = response.headers.get('Set-Cookie', '')

    if not set_cookie_header:
        return None

    cookie_pattern = r'\.AspNet\.TasheelApplicationCookie=([^;]+)'
    match = re.search(cookie_pattern, set_cookie_header)

    if match:
        cookie_value = match.group(1)
        print(f"Found new AspNet.TasheelApplicationCookie in response: {cookie_value[:50]}...")
        return cookie_value

    return None

def build_cookie_string(cookie_file="cookie.txt"):
    base_cookies = {
        'X-Language': 'en',
        'JSS': '02f0957673-730f-43wp7uoQHTqCoFUAMQ2zq-0jTn4DkJ5qViKqQM_5VlpD58_Hz78FawbHyTx-JsXlh0Dfs',
        'ADRUM': 's~1749474363456&r~aHR0cHMlM0ElMkYlMkZlc2VydmljZXMubW9ocmUuZ292LmFlJTJGVGFzaGVlbFdlYiUyRnNlcnZpY2VzJTJGdHJhbnNhY3Rpb25lbnRyeSUyRjUwNQ==',
        'ASP.NET_SessionId': 'zzro0xafmiqkwtl4mxkiakkk',
        'IsTasheelUser_E11User': 'False',
        '__RequestVerificationToken_L1Rhc2hlZWxXZWI1': 'KySulooKYagDaqhbZYOjdu-4FQ_pgvFW8gWt4PgKk2aVPyewSKf5KpzFfFNtjbZQOkZLb-5aqyuP2jRmWGKB8YATUK81'
    }

    app_cookie = read_cookie_from_file(cookie_file)
    if app_cookie:
        base_cookies['.AspNet.TasheelApplicationCookie'] = app_cookie

    cookie_parts = [f"{key}={value}" for key, value in base_cookies.items()]
    return "; ".join(cookie_parts)

# ============= MOHRE Check Function =============

def checkMOHRE(passport_number,
               nationality,
               original_dir,
               passport_image_path='passport.jpg',
               person_photo_path='photo.jpg',
               email='gomaa123456789268@gmail.com',
               phone_number='0581231235'):
    import os
    from PIL import Image
    import io

    url = "https://eservices.mohre.gov.ae/TasheelWeb/services/transactionentry/505?mk="

    session = requests.Session()
    cookie_file = f'{original_dir}/cookie.txt'

    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        class SSLAdapter(HTTPAdapter):
            def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
                ctx = ssl.create_default_context()
                ctx.set_ciphers('DEFAULT@SECLEVEL=1')  # Lower security level
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                pool_kwargs['ssl_context'] = ctx
                return super().init_poolmanager(connections, maxsize, block, **pool_kwargs)

        session.mount('https://', SSLAdapter())

    except Exception as e:
        print(f"SSL adapter setup failed: {e}")
        pass

    def compress_image_if_needed(image_path, max_size_mb=0.9):
        """Compress image if it's larger than max_size_mb"""
        if not os.path.exists(image_path):
            return None

        file_size = os.path.getsize(image_path) / (1024 * 1024)  # Size in MB

        if file_size <= max_size_mb:
            # Image is already small enough, return original file content
            with open(image_path, 'rb') as f:
                return f.read()

        print(f"Image {image_path} is {file_size:.2f}MB, compressing...")

        # Open and compress the image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            quality = 95
            while quality > 10:
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                compressed_size = len(output.getvalue()) / (1024 * 1024)

                if compressed_size <= max_size_mb:
                    print(f"Compressed to {compressed_size:.2f}MB with quality {quality}")
                    return output.getvalue()

                quality -= 5

    cookie_string = build_cookie_string(cookie_file)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Origin': 'https://eservices.mohre.gov.ae',
        'Connection': 'keep-alive',
        'Referer': 'https://eservices.mohre.gov.ae/TasheelWeb/services/transactionentry/505?mk=',
        'Cookie': cookie_string,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i'
    }

    form_data = {
        '__RequestVerificationToken': 'cznzDPqGNnZc07YMe0ipgNHldvrFOGVZknK2dGTcx-dnW_ibG6MRiC3_RO_HoLlh4TsTwCUPomQ7Tjgn6kyfssQaZ-F5edMBkXBv5PoDhFkgFt7Q2kV6NUpur-LK4n1cZMh-ZQ2',
        'Key': '',
        'AttachmentType': 'PassportAndPersonPhoto',
        'PassportNumber': passport_number,
        'Nationality.Value': nationality[1],
        'Nationality.Description': nationality[0],
        'TravelNationality.Value': '',
        'TravelNationality.Description': '',
        'Email': email,
        'ContactNo': phone_number,
        'EducationCertificateAvailable': 'false',
        'submitButton': 'Submit'
    }

    files = {}

    if passport_image_path and Path(passport_image_path).exists():
        passport_file_name = passport_image_path.split("/")[-1]
        compressed_passport_data = compress_image_if_needed(passport_image_path)
        if compressed_passport_data:
            files['PassportDocumentFirstPage'] = (
                passport_file_name,
                io.BytesIO(compressed_passport_data),
                'image/jpeg'
            )
        else:
            files['PassportDocumentFirstPage'] = ('', '', 'application/octet-stream')
    else:
        files['PassportDocumentFirstPage'] = ('', '', 'application/octet-stream')

    files['PassportDocumentSecondPage'] = ('', '', 'application/octet-stream')

    if person_photo_path and Path(person_photo_path).exists():
        photo_file_name = person_photo_path.split("/")[-1]
        compressed_photo_data = compress_image_if_needed(person_photo_path)
        if compressed_photo_data:
            files['PersonPhotoDocument'] = (
                photo_file_name,
                io.BytesIO(compressed_photo_data),
                'image/jpeg'
            )
        else:
            files['PersonPhotoDocument'] = ('', '', 'application/octet-stream')
    else:
        files['PersonPhotoDocument'] = ('', '', 'application/octet-stream')

    files['NationalIdentityDocumentFirstPage'] = ('', '', 'application/octet-stream')
    files['NationalIdentityDocumentSecondPage'] = ('', '', 'application/octet-stream')
    files['EducationCertificateFirstPage'] = ('', '', 'application/octet-stream')
    files['EducationCertificateSecondPage'] = ('', '', 'application/octet-stream')

    try:
        response = session.post(url, headers=headers, data=form_data, files=files,
                               timeout=30, verify=False)

        for file_obj in files.values():
            if hasattr(file_obj[1], 'close'):
                file_obj[1].close()

        new_cookie = extract_cookie_from_response(response)
        if new_cookie:
            write_cookie_to_file(new_cookie, cookie_file)
            print("Cookie updated successfully!")

        if response.status_code == 200:
            print("Request successful!")
            return response.text
        else:
            print(f"Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    checkMOHRE(
        passport_number="PA1285353",
        nationality=("ATHYUOBYA", "317"),
        original_dir="78797",
        passport_image_path="78797/78797_passport.jpg",
        person_photo_path="78797/78797_face.jpg"
    )