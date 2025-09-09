# Document Verification Service

A Python program that replicates HTTP requests to the UAE eservices portal for document verification. This tool automates the submission of maid documents and handles token/cookie management.

## Features

- ✅ Replicates multipart form requests from curl commands
- ✅ Easy token/cookie refreshing from new curl commands
- ✅ Auto-refresh mechanism during runtime
- ✅ Batch processing of multiple documents
- ✅ Rate limiting to avoid overwhelming the server
- ✅ Comprehensive logging and error handling
- ✅ JSON-based document configuration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your sample data is in place (like the `78797/` directory with images and `info.json`)

## Quick Start

### Test with Sample Data
```bash
python main.py test
```

### Interactive Mode
```bash
python main.py
```

## Usage Examples

### 1. Update Tokens from New Curl Command

When you get a new curl command from the browser:

1. Save the curl command to a file (e.g., `new_command.sh`)
2. Update the configuration:
```bash
python main.py update new_command.sh
```

Or use the standalone updater:
```bash
python update_config.py new_command.sh
```

### 2. Process Single Document
```bash
python main.py path/to/document/info.json
```

### 3. Batch Process Directory
```bash
python main.py path/to/documents_directory
```

### 4. Interactive Mode
```bash
python main.py
```
Then choose from the menu options.

## Configuration

### Manual Token Updates

Edit `config.py` directly to update:

1. **Cookies** - Update the `COOKIES` dictionary
2. **Verification Token** - Update `REQUEST_VERIFICATION_TOKEN`
3. **Nationality Mapping** - Add new nationalities to `NATIONALITY_MAPPING`

### Auto Token Updates

The system can automatically extract tokens from new curl commands:

1. Copy a new curl command from your browser's developer tools
2. Save it to a file
3. Run: `python update_config.py <file>`

## Document Format

Documents should follow this JSON structure (see `78797/info.json` for example):

```json
{
  "maid_id": "78797",
  "original_data": {
    "Passport Number": "PA1285353",
    "Nationality": "Nepali",
    "Maid Name": "LILA KUMARI THAPA"
  },
  "downloaded_images": {
    "face_photo": {
      "filename": "78797_face.jpg"
    },
    "passport": {
      "filename": "78797_passport.jpg"
    }
  }
}
```

## Rate Limiting

The system includes built-in rate limiting:
- Minimum 2 seconds between requests
- Configurable in `DocumentVerifier` class
- Helps avoid overwhelming the server

## Error Handling

- **Token Expiration**: Update tokens using the update mechanism
- **File Not Found**: Ensure image files exist in the document directory
- **Network Errors**: Built-in retry mechanism for failed requests
- **Invalid Nationality**: Add missing nationalities to `NATIONALITY_MAPPING`

## Logging

All activities are logged to:
- Console output
- `document_verification.log` file

## File Structure

```
doc_verify_service/
├── config.py              # Configuration (tokens, cookies, mappings)
├── doc_verifier.py         # Main DocumentVerifier class
├── main.py                 # CLI interface and examples
├── update_config.py        # Utility to update config from curl
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── 78797/                 # Sample document data
    ├── info.json
    ├── 78797_face.jpg
    └── 78797_passport.jpg
```

## Token Management Workflow

1. **Initial Setup**: Use tokens from your first curl command
2. **When Tokens Expire**: 
   - Go to the website in your browser
   - Open Developer Tools → Network tab
   - Perform the document submission manually
   - Copy the curl command for the request
   - Save it to a file and run the update script
3. **Auto-refresh**: The system will detect some token expiration scenarios and prompt for updates

## Troubleshooting

### Common Issues

1. **403/401 Errors**: Tokens have expired - update using new curl command
2. **File Not Found**: Check that image files exist in the correct directory
3. **Invalid Nationality**: Add the nationality to `NATIONALITY_MAPPING` in config.py
4. **Rate Limiting**: The system automatically handles this, but you can adjust the interval

### Getting New Curl Commands

1. Open UAE eservices portal in browser
2. Open Developer Tools (F12) → Network tab
3. Fill out and submit a document form manually
4. Find the POST request to `transactionentry/505`
5. Right-click → Copy as cURL
6. Save to a file and use the update mechanism

## Security Notes

- Never commit real tokens/cookies to version control
- Tokens are session-specific and expire after some time
- The configuration file contains sensitive authentication data

## Support

For issues or questions:
1. Check the logs in `document_verification.log`
2. Verify your token configuration is up to date
3. Ensure all required files exist
4. Check network connectivity to the UAE eservices portal
