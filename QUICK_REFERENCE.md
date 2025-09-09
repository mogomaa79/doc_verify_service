# 🚀 Quick Reference - Document Verification Service

## ⚡ Most Common Commands

### Update Tokens (when they expire)
```bash
python update_config.py new_command.sh
```

### Test Single Document  
```bash
python main.py test
```

### Interactive Mode
```bash
python main.py
```

### Process Directory of Documents
```bash
python main.py /path/to/documents
```

## 🔄 Token Update Process

1. **Browser**: Go to UAE eservices → Submit a form manually
2. **Dev Tools**: F12 → Network → Find POST request → Copy as cURL  
3. **Save**: Paste into file (e.g., `fresh_tokens.sh`)
4. **Update**: `python update_config.py fresh_tokens.sh`
5. **Test**: `python main.py test`

## 📊 Response Meanings

| Response | Meaning | Action |
|----------|---------|--------|
| 🔄 Session expired | Login page returned | Update tokens |
| ✅ Document submitted | Success response | Check confirmation |
| ❌ Validation error | Data issue | Check document format |
| 🚫 Access denied | Auth failed | Update tokens immediately |
| ⚠️ Server error | UAE site issue | Try later |

## 🗂️ File Structure

```
doc_verify_service/
├── config.py           # 🔧 Tokens & settings (auto-updated)
├── main.py             # 🎮 Main interface  
├── doc_verifier.py     # ⚙️  Core functionality
├── update_config.py    # 🔄 Token updater
├── country_mapping.csv # 🌍 436 nationalities
├── network_diagnostics.py # 🔍 Connection testing
└── 78797/              # 📂 Sample data
```

## 📋 Document JSON Format

```json
{
  "original_data": {
    "Passport Number": "PA1285353",
    "Nationality": "Nepal",  // Must match CSV
    "Maid Name": "LILA KUMARI THAPA"
  },
  "downloaded_images": {
    "face_photo": {"filename": "face.jpg"},
    "passport": {"filename": "passport.jpg"}
  }
}
```

## 🆘 Troubleshooting

### SSL Errors
```bash
python network_diagnostics.py
```

### Test Connection
```bash
python -c "from doc_verifier import DocumentVerifier; v = DocumentVerifier(); print(v.test_connection())"
```

### Check Available Nationalities
```bash
python -c "import csv; print([row['english_name'] for row in csv.DictReader(open('country_mapping.csv'))][:20])"
```

## 🎯 Production Tips

- **Rate Limit**: 2 seconds between requests (adjustable)
- **Batch Size**: Process 50-100 documents at a time
- **Best Time**: UAE business hours (GMT+4)
- **Logging**: Check `document_verification.log` for details
- **Backup**: Save working tokens in multiple files

---
**Status: ✅ FULLY OPERATIONAL** | **Last Updated: 2025-09-09**
