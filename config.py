"""
Configuration file for document verification service.
Update this file when you get new curl commands with fresh tokens/cookies.
"""

# Headers that rarely change
STATIC_HEADERS = {
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

# **UPDATE THESE FROM NEW CURL COMMANDS**
# Copy these values from the Cookie header (-b flag) in your curl command
COOKIES = {
    'Qid': '',
    'X-Language': 'en',
    'JSS': '02f0957673-730f-437kmw3C7_NIsXfjZKJuPO01TwjCvs_jDr6HmNJJINHdGXc53Iz7vztuihdFPDICTwQrI',
    'ASP.NET_SessionId': 'wwrjvns4wpvaprxaqtgqk2bj',
    'IsTasheelUser_E11User': 'False',
    '__RequestVerificationToken_L1Rhc2hlZWxXZWI1': 'Pi75r0A1ftC-8Z_xu8j0yiHiab9gIX7ow4szyQ3ze-Pjft6fxDpzTi8n5KZl6gVzXU9fD5lClchJuVc3gBJEG8LQ7TE1',
    '.AspNet.TasheelApplicationCookie': 'osoRjdVYmXVoAh5T19sP5YK_4afqkCYaquYJx7iMBmIdiWlAPXLlR5Ma0DzrshOcKwg9M4zKJPCJ9Zv9U1tJmqTkdvKZmEKWWSCQxLgU5qOcQ4IRyNpyAGdpJwMzzSid1DFqymp5ZhEbtsWYG6pMdQYaCTnuYs5GPkD4_aH5CIHd0tWwQvO0q6bOX15dVJC8dhwWBLVFncA6NqN4omnFbN3Fi_i7n0em_Wye_IDTVAUUa103F-AJRL4ZaGu7ePa3s-NRHG6Yp8-3LUxc4O4wv979DP-g1sceL2xx1s-1Qc0Busai4Q145OEVedQC9bg15w6KxrbGWQ0BiIgIIydXcj_VsQOBQK1h0BnOec3UU6DqbKr0O6Zdiorrx0mA-FedWQSopBUjNDJ4nsNNOQcXYE57l-tqDFaFAi8TmjIC2evZb93YvKZspFuMwa7x4g3hMNUN_NGgsbtNlKzaRDM_PmmOL5qVPKXYzjFT9eurjGAiJ6yRilL0FZQ-f9arskBI1MVFILhC5hC3qhG4Elt6AJ2CesWadVYd8KbawWhTuHLQjMyphtlu0ylue4fxevkc-xqhSgFqyOOqTQYv41pjov5R2DiHsFhazBKtUPSVvF_3qFEi0RpA1ax1hJq0v_HIcUjDLo25hBbfWDJ6-Wy9QrA15X2zSdlOj88gs05LAX-xNYx-479jOuMSKOj4dKQtB2bj6Z_zL98TooGfFzwBm-lNcss3FGTpbXX0M2gHKnvYxUjx1nGIol9e31vSGwgbiSX96DL8alvJJHGIK_mjXjmCTbg',
    'ADRUM': 's~1757445674737&r~aHR0cHMlM0ElMkYlMkZlc2VydmljZXMubW9ocmUuZ292LmFlJTJGVGFzaGVlbFdlYiUyRmhvbWUlM0ZoYXNoJTNEMzU=',
}

# **UPDATE THIS FROM NEW CURL COMMANDS**
# Copy this value from the __RequestVerificationToken field in the form data
REQUEST_VERIFICATION_TOKEN = 'apS713vpQqMV3WzxL8-YgT8zSmVkcwqRf-YjOjsI6mksRckBeZyTU4FyG3GhYBveulHFH2tCxX30xcriDAbCCt97lS-EaDIJgNV_oliKlXm0B5fiVdjp_KvEkwQJL1mkRpjqzQ2'

# API endpoint
API_URL = 'https://eservices.mohre.gov.ae/TasheelWeb/services/transactionentry/505?mk='

# Default form data (can be overridden per request)
DEFAULT_FORM_DATA = {
    'Key': '',
    'Email': 'gomaa123456789268@gmail.com',
    'ContactNo': '0505544143',
    'EducationCertificateAvailable': 'false'
}

# Nationality mapping (add more as needed)
NATIONALITY_MAPPING = {
    'Nepali': {'Value': '235', 'Description': 'NIPAL'},
    'Ethiopian': {'Value': '317', 'Description': 'ATHYUOBYA'},  # Update these values
    'Filipina': {'Value': '237', 'Description': 'PHILIPPINES'},   # Update these values
    # Add more nationalities as needed
}
