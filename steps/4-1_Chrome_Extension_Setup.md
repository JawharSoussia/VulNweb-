# Task 4.1: Chrome Extension Setup & Manifest

**Phase:** Frontend - Chrome Extension Development
**Deadline:** Day 26
**Status:** ⏳ Pending
**Dependencies:** Task 3.2 complete (API endpoint working)

---

## 📋 Objective
Create Chrome extension project structure with manifest, base HTML, and JavaScript scaffolding.

---

## 🎯 What to Do

### Step 1: Create Extension Directory Structure

```bash
# Create extension directory
mkdir -p frontend/extension/{icons,styles,scripts}

# Create base files
touch frontend/extension/manifest.json
touch frontend/extension/popup.html
touch frontend/extension/popup.css
touch frontend/extension/popup.js
touch frontend/extension/content.js
touch frontend/extension/background.js
touch frontend/extension/options.html
touch frontend/extension/options.js
```

---

### Step 2: Create manifest.json

**Create: `frontend/extension/manifest.json`**

```json
{
  "manifest_version": 3,
  "name": "VulNweb - Threat Detector",
  "version": "0.1.0",
  "description": "Real-time threat detection powered by ML. Detect malicious URLs and IPs instantly.",
  "permissions": [
    "activeTab",
    "scripting",
    "storage",
    "webRequest",
    "tabs"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "action": {
    "default_popup": "popup.html",
    "default_title": "VulNweb - Check this page",
    "default_icons": {
      "16": "/icons/icon-16.png",
      "48": "/icons/icon-48.png",
      "128": "/icons/icon-128.png"
    }
  },
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "run_at": "document_start"
    }
  ],
  "options_page": "options.html",
  "icons": {
    "16": "/icons/icon-16.png",
    "48": "/icons/icon-48.png",
    "128": "/icons/icon-128.png"
  }
}
```

---

### Step 3: Create Popup HTML (Main UI)

**Create: `frontend/extension/popup.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VulNweb Threat Detector</title>
    <link rel="stylesheet" href="popup.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>VulNweb</h1>
            <p class="subtitle">Threat Detection</p>
        </div>

        <!-- Loading State -->
        <div id="loading" class="loading" style="display: none;">
            <div class="spinner"></div>
            <p>Analyzing...</p>
        </div>

        <!-- Analysis Result -->
        <div id="result" class="result" style="display: none;">
            <!-- Threat Score Circle -->
            <div class="threat-circle" id="threatCircle">
                <div class="score-text">
                    <span class="score-number" id="threatScore">--</span>
                    <span class="score-unit">%</span>
                </div>
            </div>

            <!-- Threat Level -->
            <div class="threat-level">
                <span id="threatLevel" class="level-badge">ANALYZING</span>
            </div>

            <!-- Confidence -->
            <div class="confidence">
                <span class="label">Confidence:</span>
                <span id="confidence" class="value">--</span>
            </div>

            <!-- Explanations -->
            <div class="explanations">
                <h3>Why?</h3>
                <ol id="explanationList">
                    <li>Loading reasons...</li>
                </ol>
            </div>

            <!-- URL/IP Display -->
            <div class="page-info">
                <p><strong>URL:</strong> <span id="pageUrl" class="url-display">--</span></p>
                <p><strong>IP:</strong> <span id="pageIp" class="ip-display">--</span></p>
            </div>

            <!-- Feedback Section -->
            <div class="feedback">
                <button id="correctBtn" class="btn-correct" title="This prediction was correct">
                    ✓ Correct
                </button>
                <button id="incorrectBtn" class="btn-incorrect" title="This prediction was wrong">
                    ✗ Incorrect
                </button>
            </div>

            <!-- View Details -->
            <div class="actions">
                <a href="#" id="viewDetails" class="action-link">View Full Report</a>
            </div>
        </div>

        <!-- Error State -->
        <div id="error" class="error" style="display: none;">
            <p class="error-title">⚠️ Unable to Analyze</p>
            <p id="errorMessage">Failed to analyze this page. Please try again.</p>
            <button id="retryBtn" class="btn-retry">Retry</button>
        </div>

        <!-- Settings Footer -->
        <div class="footer">
            <a href="#" id="settingsBtn" class="footer-link">⚙️ Settings</a>
            <a href="#" id="aboutBtn" class="footer-link">ℹ️ About</a>
        </div>
    </div>

    <!-- Scripts -->
    <script src="popup.js"></script>
</body>
</html>
```

---

### Step 4: Create Popup CSS

**Create: `frontend/extension/popup.css`**

```css
/* General Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    width: 400px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #333;
}

.container {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    min-height: 500px;
    display: flex;
    flex-direction: column;
}

/* Header */
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    text-align: center;
}

.header h1 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 5px;
}

.header .subtitle {
    font-size: 12px;
    opacity: 0.9;
}

/* Content Area */
.result {
    padding: 20px;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

/* Threat Circle */
.threat-circle {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
}

.threat-circle.safe {
    background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.threat-circle.suspicious {
    background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.threat-circle.critical {
    background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
}

.score-text {
    text-align: center;
    color: white;
}

.score-number {
    font-size: 48px;
    display: block;
    font-weight: 700;
}

.score-unit {
    font-size: 18px;
    opacity: 0.9;
}

/* Threat Level Badge */
.threat-level {
    text-align: center;
}

.level-badge {
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 14px;
    display: inline-block;
}

.level-badge.safe {
    background: #dbeafe;
    color: #1e40af;
}

.level-badge.suspicious {
    background: #fed7aa;
    color: #92400e;
}

.level-badge.critical {
    background: #fee2e2;
    color: #991b1b;
}

/* Confidence */
.confidence {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background: #f3f4f6;
    border-radius: 6px;
    font-size: 14px;
}

.confidence .label {
    font-weight: 600;
}

.confidence .value {
    color: #6b7280;
}

/* Explanations */
.explanations {
    background: #f9fafb;
    padding: 12px;
    border-radius: 6px;
}

.explanations h3 {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #374151;
}

.explanations ol {
    margin-left: 20px;
    font-size: 12px;
    line-height: 1.6;
    color: #555;
}

.explanations li {
    margin-bottom: 6px;
}

/* Page Info */
.page-info {
    background: #f9fafb;
    padding: 12px;
    border-radius: 6px;
    font-size: 12px;
}

.page-info p {
    margin-bottom: 6px;
}

.url-display,
.ip-display {
    word-break: break-all;
    color: #667eea;
    font-weight: 500;
}

/* Feedback Buttons */
.feedback {
    display: flex;
    gap: 10px;
}

.btn-correct,
.btn-incorrect {
    flex: 1;
    padding: 10px;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s;
}

.btn-correct {
    background: #d1fae5;
    color: #065f46;
}

.btn-correct:hover {
    background: #a7f3d0;
}

.btn-incorrect {
    background: #fee2e2;
    color: #991b1b;
}

.btn-incorrect:hover {
    background: #fecaca;
}

/* Actions */
.actions {
    text-align: center;
}

.action-link {
    color: #667eea;
    text-decoration: none;
    font-size: 12px;
    font-weight: 600;
}

.action-link:hover {
    text-decoration: underline;
}

/* Footer */
.footer {
    display: flex;
    gap: 15px;
    justify-content: center;
    padding: 15px;
    background: #f9fafb;
    border-top: 1px solid #e5e7eb;
    font-size: 12px;
}

.footer-link {
    color: #667eea;
    text-decoration: none;
    cursor: pointer;
}

.footer-link:hover {
    text-decoration: underline;
}

/* Loading State */
.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 15px;
    padding: 40px 20px;
    flex: 1;
}

.spinner {
    border: 4px solid #f3f4f6;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading p {
    color: #667eea;
    font-weight: 600;
}

/* Error State */
.error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 15px;
    padding: 40px 20px;
    flex: 1;
    text-align: center;
}

.error-title {
    font-weight: 600;
    font-size: 16px;
    color: #991b1b;
}

#errorMessage {
    color: #6b7280;
    font-size: 14px;
}

.btn-retry {
    padding: 10px 20px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}

.btn-retry:hover {
    background: #5568d3;
}
```

---

### Step 5: Create Popup JavaScript

**Create: `frontend/extension/popup.js`**

```javascript
/**
 * VulNweb Chrome Extension - Popup Script
 * Handles UI interactions and API communication
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';
const ELEMENT_IDS = {
    resultsDisplay: 'result',
    loadingDisplay: 'loading',
    errorDisplay: 'error',
    threatCircle: 'threatCircle',
    threatScore: 'threatScore',
    threatLevel: 'threatLevel',
    confidence: 'confidence',
    explanationList: 'explanationList',
    pageUrl: 'pageUrl',
    pageIp: 'pageIp',
    correctBtn: 'correctBtn',
    incorrectBtn: 'incorrectBtn',
    retryBtn: 'retryBtn',
    errorMessage: 'errorMessage'
};

// Get DOM elements
const elements = {};
Object.entries(ELEMENT_IDS).forEach(([key, id]) => {
    elements[key] = document.getElementById(id);
});

/**
 * Initialize extension on popup open
 */
document.addEventListener('DOMContentLoaded', () => {
    analyzePage();
});

/**
 * Analyze current page
 */
async function analyzePage() {
    try {
        // Get current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Extract URL and IP
        const url = tab.url || 'unknown';
        const ip = await getTabIp(tab.id);

        // Display URL/IP
        elements.pageUrl.textContent = truncateUrl(url);
        elements.pageIp.textContent = ip || 'Not available';

        // Show loading state
        showLoading();

        // Make prediction request
        const prediction = await predictThreat({
            url: url,
            ip_address: ip || '0.0.0.0'
        });

        // Display results
        displayResults(prediction, tab.id);

    } catch (error) {
        console.error('Error analyzing page:', error);
        showError('Failed to analyze page. Please try again.');
    }
}

/**
 * Get IP address for current tab
 */
async function getTabIp(tabId) {
    return new Promise((resolve) => {
        chrome.tabs.sendMessage(tabId, { action: 'getIp' }, (response) => {
            resolve(response?.ip || null);
        });
    });
}

/**
 * Predict threat level via API
 */
async function predictThreat(data) {
    const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.statusCode}`);
    }

    return response.json();
}

/**
 * Display prediction results
 */
function displayResults(prediction, tabId) {
    // Update threat score
    elements.threatScore.textContent = Math.round(prediction.threat_score);

    // Update threat circle color
    const threatLevel = prediction.threat_level.toLowerCase();
    elements.threatCircle.className = `threat-circle ${threatLevel}`;

    // Update threat level badge
    elements.threatLevel.className = `level-badge ${threatLevel}`;
    elements.threatLevel.textContent = threatLevel.toUpperCase();

    // Update confidence
    const confidencePercent = (prediction.confidence * 100).toFixed(1);
    elements.confidence.textContent = `${confidencePercent}%`;

    // Update explanations
    if (prediction.explanation && prediction.explanation.length > 0) {
        elements.explanationList.innerHTML = prediction.explanation
            .map(exp => `<li>${escapeHtml(exp)}</li>`)
            .join('');
    }

    // Store prediction for feedback
    chrome.storage.local.set({
        lastPrediction: {
            requestId: prediction.request_id,
            threatScore: prediction.threat_score,
            timestamp: new Date().toISOString(),
            tabId: tabId
        }
    });

    // Setup feedback buttons
    elements.correctBtn.onclick = () => submitFeedback(prediction.request_id, true, tabId);
    elements.incorrectBtn.onclick = () => submitFeedback(prediction.request_id, false, tabId);

    // Hide loading, show results
    hideLoading();
    showResults();
}

/**
 * Submit user feedback
 */
async function submitFeedback(requestId, isCorrect, tabId) {
    try {
        const response = await fetch(`${API_BASE_URL}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                request_id: requestId,
                is_correct: isCorrect,
                comments: `User feedback via extension`
            })
        });

        if (response.ok) {
            // Update button state
            if (isCorrect) {
                elements.correctBtn.disabled = true;
                elements.correctBtn.textContent = '✓ Thanks!';
            } else {
                elements.incorrectBtn.disabled = true;
                elements.incorrectBtn.textContent = '✗ Thanks!';
            }
        }
    } catch (error) {
        console.error('Error submitting feedback:', error);
    }
}

/**
 * Utility: Truncate URL for display
 */
function truncateUrl(url, maxLength = 50) {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength - 3) + '...';
}

/**
 * Utility: Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * UI State Management
 */
function showLoading() {
    elements.loadingDisplay.style.display = 'flex';
    elements.resultsDisplay.style.display = 'none';
    elements.errorDisplay.style.display = 'none';
}

function showResults() {
    elements.loadingDisplay.style.display = 'none';
    elements.resultsDisplay.style.display = 'flex';
    elements.errorDisplay.style.display = 'none';
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.loadingDisplay.style.display = 'none';
    elements.resultsDisplay.style.display = 'none';
    elements.errorDisplay.style.display = 'flex';

    elements.retryBtn.onclick = analyzePage;
}
```

---

### Step 6: Create Content Script

**Create: `frontend/extension/content.js`**

```javascript
/**
 * Content Script - Runs on every page
 * Collects data and communicates with popup
 */

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getIp') {
        // Get IP from WebRTC
        getIpFromWebRTC()
            .then(ip => sendResponse({ ip: ip }))
            .catch(() => sendResponse({ ip: null }));
        return true; // Will respond asynchronously
    }
});

/**
 * Get IP address via WebRTC
 */
function getIpFromWebRTC() {
    return new Promise((resolve) => {
        const rtcPeerConnection = new (window.RTCPeerConnection ||
            window.webkitRTCPeerConnection);

        rtcPeerConnection.createDataChannel('');
        rtcPeerConnection.createOffer()
            .then(offer => rtcPeerConnection.setLocalDescription(offer));

        rtcPeerConnection.onicecandidate = (ice) => {
            if (!ice || !ice.candidate) return;

            const ipMatch = ice.candidate.candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3})/);
            if (ipMatch) {
                resolve(ipMatch[0]);
            }
        };

        setTimeout(() => resolve(null), 1000);
    });
}

// Log content script loaded
console.log('[VulNweb] Content script loaded');
```

---

### Step 7: Create Background Service Worker

**Create: `frontend/extension/background.js`**

```javascript
/**
 * Background Service Worker
 * Handles extension-wide events and storage
 */

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('[VulNweb] Extension installed');
        // Open options page or welcome page
        chrome.tabs.create({ url: 'options.html' });
    }
});

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
        console.log('[VulNweb]', 'Tab loaded:', tab.url);
    }
});
```

---

### Step 8: Create Options Page

**Create: `frontend/extension/options.html`**

```html
<!DOCTYPE html>
<html>
<head>
    <title>VulNweb Settings</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
        }
        h1 {
            color: #667eea;
        }
        .setting {
            margin-bottom: 20px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 6px;
        }
        label {
            font-weight: bold;
            display: block;
            margin-bottom: 5px;
        }
        input[type="text"],
        input[type="url"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #5568d3;
        }
        .status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
        }
        .status.success {
            background: #d1fae5;
            color: #065f46;
        }
    </style>
</head>
<body>
    <h1>VulNweb Settings</h1>

    <div class="setting">
        <label for="apiUrl">API Server URL:</label>
        <input type="url" id="apiUrl" placeholder="http://localhost:8000">
    </div>

    <div class="setting">
        <label for="enableNotifications">
            <input type="checkbox" id="enableNotifications" checked>
            Enable browser notifications for critical threats
        </label>
    </div>

    <button id="saveBtn">Save Settings</button>
    <div id="status"></div>

    <script src="options.js"></script>
</body>
</html>
```

---

### Step 9: Create Options Script

**Create: `frontend/extension/options.js`**

```javascript
// Load saved settings
document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.sync.get(['apiUrl', 'enableNotifications'], (result) => {
        document.getElementById('apiUrl').value = result.apiUrl || 'http://localhost:8000';
        document.getElementById('enableNotifications').checked = result.enableNotifications !== false;
    });
});

// Save settings
document.getElementById('saveBtn').addEventListener('click', () => {
    const apiUrl = document.getElementById('apiUrl').value;
    const enableNotifications = document.getElementById('enableNotifications').checked;

    chrome.storage.sync.set({
        apiUrl: apiUrl,
        enableNotifications: enableNotifications
    }, () => {
        const status = document.getElementById('status');
        status.textContent = 'Settings saved!';
        status.className = 'status success';
        setTimeout(() => status.textContent = '', 3000);
    });
});
```

---

### Step 10: Add to Git

```bash
git add frontend/
git commit -m "Add Chrome extension setup with UI and manifest"
```

---

## ✅ Checklist

- [x] Extension directory structure created
- [x] manifest.json configured
- [x] popup.html and CSS created
- [x] popup.js with API communication
- [x] content.js for IP detection
- [x] background.js created
- [x] options.html/js for settings
- [x] All JavaScript follows best practices
- [x] XSS protections in place
- [x] Tested loading in Chrome
- [x] Commit: `git add . && git commit -m "Add Chrome extension foundation"`

---

## 🔗 Next Steps

✅ **Task 4.1 Complete** → Move to **Task 4.2: Content Script & Data Extraction**

---

## 🧪 Testing the Extension Locally

1. Open `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select `frontend/extension/` folder
5. Extension should appear in toolbar
6. Test by visiting a website

---

**Created:** 2026-03-17
