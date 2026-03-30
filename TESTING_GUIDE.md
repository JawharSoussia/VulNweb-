# VulNweb Extension Testing Guide

## 🚀 Quick Start

### Prerequisites
1. Backend running on `http://localhost:8000`
2. Chrome extension loaded in developer mode
3. Python 3.8+ with requests library

## 📋 Testing Options

### Option 1: Python Test Suite (Recommended)

Run comprehensive automated tests:

```bash
# From project root
python test_extension.py
```

**What it tests:**
- ✅ API health check
- ✅ Network threat analysis (threat levels 1, 4, 7, 10)
- ✅ VirusTotal scanning
- ✅ Batch analysis
- ✅ Connection error handling

**Output:**
```
API is HEALTHY
  - Model Loaded: True
  - Version: 0.1.0

Network Analysis Response:
  - Threat Score: 42
  - Threat Level: MEDIUM
  - Decision: ['feature_1', 'feature_2', 'feature_3']
```

---

### Option 2: Test Page in Browser

Open the interactive test page:

```bash
# From project root
# Open this file in your browser:
file:///path/to/test_extension.html
```

**Features:**
- Click safe, suspicious, and critical URLs
- Test with real websites
- Visual testing checklist
- Direct API commands
- Form field detection

---

### Option 3: Direct API Calls

**Test with curl:**

```bash
# 1. Health Check
curl http://localhost:8000/health

# 2. Network Analysis
curl -X POST http://localhost:8000/threats/network/analyze \
  -H "Content-Type: application/json" \
  -d '{"flow_data": {...network_features...}}'

# 3. Batch Analysis
curl -X POST http://localhost:8000/threats/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://google.com", "https://github.com"]}'
```

**Or use bash script:**

```bash
bash test_api_commands.sh
```

---

## 🧪 Test Scenarios

### Scenario 1: Basic Functionality
1. Start backend: `python -m uvicorn backend.app.main:app --reload`
2. Open `chrome://extensions/`
3. Right-click extension → Inspect popup
4. Open test page: `test_extension.html`
5. Click a link from safe websites section
6. Check popup for threat score

### Scenario 2: API Connection
1. Open extension settings (Options)
2. Verify API URL: `http://localhost:8000`
3. Click "Test Connection"
4. Should see: `✓ API Connected! Status: healthy`

### Scenario 3: Network Threat Analysis
1. Run: `python test_extension.py`
2. Check network analysis responses
3. Verify threat scores 0-100
4. Check decision reasons

### Scenario 4: Batch Processing
1. Run: `python test_extension.py`
2. Scroll to "Batch Analysis" output
3. Should process multiple URLs/flows
4. Verify results for each item

### Scenario 5: Error Handling
1. Stop the backend API
2. Try to test connection in extension settings
3. Should see: `API Error: ...` message
4. Restart backend
5. Should reconnect successfully

---

## 📊 Expected Responses

### Health Check ✅
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "0.1.0"
}
```

### Network Analysis ✅
```json
{
  "threat_score": 42,
  "threat_level": "MEDIUM",
  "decision_reasons": {
    "top_features": [
      "sbytes: 523450",
      "spkts: 1250",
      "sload: 834.2"
    ]
  }
}
```

### Batch Analysis ✅
```json
{
  "url_results": [
    {
      "url": "https://google.com",
      "threat_score": 5,
      "threat_level": "LOW"
    }
  ],
  "flow_results": [
    {
      "threat_score": 32,
      "threat_level": "MEDIUM"
    }
  ]
}
```

---

## 🐛 Debugging

### Extension Not Loading Icons
```
Error: Could not load icon 'icons/icon-48.png' specified in 'icons'
```
**Fix:** Run the setup script or verify icons exist in `frontend/extension/icons/`

### API Connection Fails
```
Error: Failed to fetch
```
**Checklist:**
- [ ] Backend is running: `python -m uvicorn backend.app.main:app --reload`
- [ ] Backend is on `http://localhost:8000`
- [ ] CORS is enabled in `backend/app/main.py`
- [ ] API endpoint exists: `http://localhost:8000/health`
- [ ] Check browser console (F12) for detailed error

### Model Not Loading
```
"status": "degraded"
"model_loaded": false
```
**Actions:**
- Check if ML model files exist in `ml_model/`
- Verify model training completed successfully
- Check backend logs for model loading errors

### Network Analysis Returns Error
**Check:**
- All required network features are provided
- Features are numeric (not strings)
- Feature names match expected schema

---

## ✅ Testing Checklist

Use this to verify everything works:

- [ ] **Icons Loaded** - Extension icon appears in toolbar
- [ ] **Popup Opens** - Click icon to see popup
- [ ] **Settings Accessible** - Right-click icon → Options
- [ ] **API Connection Works** - Settings → Test Connection succeeds
- [ ] **Health Check** - `curl localhost:8000/health` returns 200
- [ ] **Safe URL Analysis** - Visit Google, see low threat score
- [ ] **Threat Scoring** - See different scores for different URLs
- [ ] **Color Coding** - Safe (green), suspicious (yellow), critical (red)
- [ ] **Feedback Works** - Can submit feedback in popup
- [ ] **Cache Enabled** - Second visit to same URL is faster
- [ ] **Background Console** - No JavaScript errors in DevTools
- [ ] **Batch Testing** - `python test_extension.py` runs successfully

---

## 📈 Performance Notes

**Expected speeds:**
- Health check: < 100ms
- Network analysis: 50-200ms
- VirusTotal scan: 1-5 seconds (depends on API)
- Batch analysis (10 items): 2-10 seconds

**Optimization tips:**
- Cache enabled reduces repeated analyses to < 50ms
- Batch processing is faster than individual requests
- Network analysis is faster than external API calls

---

## 🔐 Production Testing

Before deploying:

1. **Test with production API**
   - Update settings to production URL
   - Verify API connection
   - Test with production dataset

2. **Test with real URLs**
   - Use VirusTotal API with your key
   - Monitor rate limits
   - Check threat accuracy

3. **Test error scenarios**
   - API down
   - Network timeout
   - Invalid response
   - Missing features

4. **Test privacy features**
   - Verify no data leakage
   - Check feedback anonymization
   - Confirm cache cleanup

---

## 📞 Troubleshooting

**Issue:** Extension doesn't detect URLs on page
- Check: `frontend/extension/content.js` is loaded
- Verify: Content script matches patterns in `manifest.json`
- Solution: Hard reload the page (Ctrl+Shift+R)

**Issue:** Analysis is always returning same score
- Check: Is cache disabled?
- Solution: Clear cache in settings
- Verify: Model is properly loaded

**Issue:** Slow response times
- Check: Backend CPU/memory usage
- Solution: Check if model training is running
- Verify: No other processes blocking port 8000

**Issue:** VirusTotal scans not working
- Check: `VIRUSTOTAL_API_KEY` environment variable set
- Verify: API key is valid in VirusTotal dashboard
- Solution: Check rate limits and remaining quota

---

## 📚 Additional Resources

- **Backend Docs:** http://localhost:8000/docs
- **API Reference:** See `API_REFERENCE.md`
- **Setup Guide:** See `SETUP_GUIDE.md`
- **Extension Files:** `frontend/extension/`
- **Test Data:** `test_prediction.py`

---

## 🎯 Next Steps

After successful testing:

1. **Integration Testing**
   - Test with real user workflows
   - Monitor threat detection accuracy

2. **Performance Testing**
   - Test with slow connections
   - Test with heavy web pages

3. **Security Testing**
   - Test input validation
   - Test for XSS/injection vulnerabilities

4. **Deployment**
   - Package extension
   - Submit to Chrome Web Store
   - Monitor user feedback

---

**Last Updated:** 2024
**Version:** 0.2.0
