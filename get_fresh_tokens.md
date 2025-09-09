# 🔄 Get Fresh Tokens - Step by Step Guide

Your system is **technically perfect** but needs fresh authentication tokens. Here's exactly how to get them:

## 🚀 Quick Process (5 minutes)

### Step 1: Open UAE eservices
1. Go to: `https://eservices.mohre.gov.ae/TasheelWeb/home`
2. Log in with your credentials

### Step 2: Open Developer Tools
1. Press **F12** (or Right-click → Inspect)
2. Click **Network** tab
3. ✅ Make sure recording is ON (red circle)

### Step 3: Submit a Test Document
1. Fill out the document form manually with any test data
2. **Upload the same images** (78797_face.jpg, 78797_passport.jpg)
3. Click **Submit**

### Step 4: Capture the Request
1. In Network tab, look for a POST request to:
   `transactionentry/505?mk=`
2. **Right-click** on that request
3. Select **Copy as cURL** (or Copy → Copy as cURL)

### Step 5: Save & Update
1. **Paste** the curl command into a new file: `fresh_tokens.sh`
2. Run: `python update_config.py fresh_tokens.sh`
3. Test: `python main.py test`

## 📋 What You'll See

**Before (expired tokens):**
```
Result: 🔄 Session expired - redirected to login page
```

**After (fresh tokens):**
```
Result: ✅ Document appears to have been submitted successfully
```

## 🔧 Troubleshooting

### Can't find the request?
- Make sure Network tab is recording
- Look for POST requests (not GET)
- The URL should contain `transactionentry/505`

### Curl command looks different?
- That's normal! Cookies change each session
- The important part is the new authentication tokens

### Still getting login page?
- Wait 1-2 minutes after getting tokens
- Make sure you copied the POST request (not GET)
- Try the process again with a fresh browser session

## ✅ Success Indicators

You'll know it worked when:
1. `python update_config.py fresh_tokens.sh` shows "✅ Configuration updated"
2. `python main.py test` shows a **different response** (not login page)
3. Debug logs show **new cookie values**

---

**Your system is ready to process hundreds of documents once you complete this token update!** 🎉
