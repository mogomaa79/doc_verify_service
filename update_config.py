"""
Utility to update configuration from new curl commands.
When you get a new curl command, save it to a file and run this script.
"""

import re
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_curl_command(curl_file_path: str):
    """Parse curl command and extract cookies and verification token."""
    
    try:
        with open(curl_file_path, 'r') as f:
            content = f.read()
        
        # Extract cookies from -b flag
        cookie_match = re.search(r"-b\s+'([^']+)'", content)
        if not cookie_match:
            cookie_match = re.search(r'-b\s+"([^"]+)"', content)
        
        cookies_dict = {}
        if cookie_match:
            cookie_string = cookie_match.group(1)
            # Parse cookie string
            for cookie in cookie_string.split('; '):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies_dict[key] = value
            logger.info(f"Extracted {len(cookies_dict)} cookies")
        else:
            logger.warning("No cookies found in curl command")
        
        # Extract verification token from form data
        token_match = re.search(r'name="__RequestVerificationToken"[^\\]*\\r\\n\\r\\n([^\\]+)', content)
        verification_token = None
        if token_match:
            verification_token = token_match.group(1)
            logger.info("Extracted verification token")
        else:
            logger.warning("No verification token found in curl command")
        
        return cookies_dict, verification_token
        
    except Exception as e:
        logger.error(f"Failed to parse curl command: {e}")
        return {}, None

def update_config_file(cookies_dict: dict, verification_token: str):
    """Update config.py with new values."""
    
    config_path = Path(__file__).parent / 'config.py'
    
    try:
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        # Update cookies
        if cookies_dict:
            # Build new COOKIES dict string
            cookies_lines = []
            for key, value in cookies_dict.items():
                cookies_lines.append(f"    '{key}': '{value}',")
            
            new_cookies_block = "COOKIES = {\n" + "\n".join(cookies_lines) + "\n}"
            
            # Replace COOKIES block
            config_content = re.sub(
                r'COOKIES = \{[^}]*\}',
                new_cookies_block,
                config_content,
                flags=re.DOTALL
            )
            logger.info("Updated COOKIES in config.py")
        
        # Update verification token
        if verification_token:
            config_content = re.sub(
                r"REQUEST_VERIFICATION_TOKEN = '[^']*'",
                f"REQUEST_VERIFICATION_TOKEN = '{verification_token}'",
                config_content
            )
            logger.info("Updated REQUEST_VERIFICATION_TOKEN in config.py")
        
        # Write back to file
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        logger.info("Configuration file updated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update config file: {e}")
        return False

def main():
    """Main function to update configuration from curl command."""
    
    if len(sys.argv) != 2:
        print("Usage: python update_config.py <curl_command_file>")
        print("Example: python update_config.py new_command.sh")
        sys.exit(1)
    
    curl_file = sys.argv[1]
    
    if not Path(curl_file).exists():
        logger.error(f"File not found: {curl_file}")
        sys.exit(1)
    
    logger.info(f"Parsing curl command from: {curl_file}")
    
    # Parse the curl command
    cookies_dict, verification_token = parse_curl_command(curl_file)
    
    if not cookies_dict and not verification_token:
        logger.error("No cookies or verification token found. Please check the curl command format.")
        sys.exit(1)
    
    # Update config file
    success = update_config_file(cookies_dict, verification_token)
    
    if success:
        logger.info("✅ Configuration updated successfully!")
        logger.info("You can now run document verification with the updated tokens.")
    else:
        logger.error("❌ Failed to update configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()
