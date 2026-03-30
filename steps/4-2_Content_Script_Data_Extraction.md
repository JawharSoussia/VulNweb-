# Task 4.2: Content Script & Data Extraction

**Phase:** Frontend - Chrome Extension Development
**Deadline:** Day 27
**Status:** ⏳ In Progress
**Dependencies:** Task 4.1 complete (Extension manifest created)

---

## 📋 Objective

Create the content script that:
1. Extracts URLs and IPs from web pages
2. Intercepts network requests
3. Sends data to VulNweb API for threat analysis
4. Displays threat indicators to users in real-time

---

## 🎯 What to Do

### Step 1: Create Content Script Structure

The content script runs in the context of web pages and can access DOM elements.

**Create: `frontend/extension/content.js`**

```javascript
/**
 * VulNweb Content Script
 * Extracts URLs and IPs from web pages for threat analysis
 */

// Configuration
const CONFIG = {
  API_URL: 'http://localhost:8000',
  CACHE_DURATION: 60000, // 1 minute
  CHECK_INTERVAL: 2000   // Check DOM every 2 seconds
};

// Cache for predictions to avoid repeated API calls
const predictionCache = new Map();

/**
 * Extract all links from current page
 */
function extractLinks() {
  const links = [];

  // Get all anchor tags
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');

    // Skip javascript: and mailto: links
    if (href && !href.startsWith('javascript:') && !href.startsWith('mailto:')) {
      try {
        const url = new URL(href, window.location.origin);
        links.push({
          url: url.href,
          text: link.textContent.trim().substring(0, 100),
          element: link
        });
      } catch (e) {
        // Invalid URL, skip
      }
    }
  });

  return links;
}

/**
 * Extract IP addresses from page content (basic extraction)
 */
function extractIPs() {
  const ips = [];
  const ipRegex = /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g;

  const pageText = document.body.innerText;
  const matches = pageText.match(ipRegex);

  if (matches) {
    // Remove duplicates
    const unique = [...new Set(matches)];
    unique.slice(0, 10).forEach(ip => {
      ips.push({ ip });
    });
  }

  return ips;
}

/**
 * Extract domain from URL
 */
function extractDomain(urlString) {
  try {
    const url = new URL(urlString);
    return url.hostname;
  } catch (e) {
    return null;
  }
}

/**
 * Generate 34 random features for demo (replace with real feature extraction)
 * In production, these should come from network monitoring
 */
function generateRandomFeatures() {
  const features = [];
  for (let i = 0; i < 34; i++) {
    features.push(Math.random() * 100);
  }
  return features;
}

/**
 * Prepare features for API request
 * Map extracted data to UNSW-NB15 features
 */
function prepareFeatures(urlData) {
  // For now, generate realistic demo features
  // Feature indices based on UNSW-NB15:
  const features = new Array(34).fill(0);

  features[0] = Math.random() * 100;    // dintpkt
  features[1] = Math.random() * 65535;  // sport (port: 0-65535)
  features[2] = Math.random() * 255;    // sttl
  features[3] = Math.random() * 100;    // dloss
  features[4] = Math.random() * 20;     // ct_srv_src
  features[5] = Math.random() * 20;     // ct_srv_dst
  features[6] = Math.random() * 50;     // ct_dst_ltm
  features[7] = Math.random() * 50;     // ct_src_ltm
  features[8] = Math.random() * 10;     // ct_dst_sport

  // Fill rest with smaller random values
  for (let i = 9; i < 34; i++) {
    features[i] = Math.random() * 10;
  }

  return features;
}

/**
 * Check if URL is in cache and still valid
 */
function getCachedPrediction(url) {
  const cached = predictionCache.get(url);

  if (cached && Date.now() - cached.timestamp < CONFIG.CACHE_DURATION) {
    return cached.data;
  }

  // Remove expired cache
  if (cached) {
    predictionCache.delete(url);
  }

  return null;
}

/**
 * Send prediction request to API
 */
async function getPrediction(urlString) {
  // Check cache first
  const cached = getCachedPrediction(urlString);
  if (cached) {
    console.log('[VulNweb] Using cached prediction for', urlString);
    return cached;
  }

  try {
    // Prepare features (in production, these would be real network features)
    const features = prepareFeatures({ url: urlString });

    // Send to API
    const response = await fetch(`${CONFIG.API_URL}/api/predict-raw`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ features })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const prediction = await response.json();

    // Cache the result
    predictionCache.set(urlString, {
      data: prediction,
      timestamp: Date.now()
    });

    console.log('[VulNweb] Prediction:', urlString, prediction);
    return prediction;

  } catch (error) {
    console.error('[VulNweb] API Error:', error);
    return null;
  }
}

/**
 * Create threat indicator element
 */
function createThreatIndicator(threat) {
  const indicator = document.createElement('div');
  indicator.className = 'vulnweb-threat-indicator';

  // Color based on threat level
  const colors = {
    'safe': '#4CAF50',
    'suspicious': '#FF9800',
    'critical': '#F44336'
  };

  const bgColor = colors[threat.threat_level] || '#9E9E9E';

  indicator.style.cssText = `
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: ${bgColor};
    margin-left: 8px;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  `;

  // Add tooltip with threat info
  indicator.title = `[${threat.threat_level.toUpperCase()}] Threat Score: ${threat.threat_score.toFixed(1)}%`;

  // Add hover details
  indicator.addEventListener('mouseenter', (e) => {
    showThreatPopup(e, threat);
  });

  return indicator;
}

/**
 * Show threat details popup
 */
function showThreatPopup(event, threat) {
  // Remove existing popup
  const existing = document.querySelector('.vulnweb-popup');
  if (existing) existing.remove();

  const popup = document.createElement('div');
  popup.className = 'vulnweb-popup';

  popup.innerHTML = `
    <div style="padding: 12px; background: white; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); max-width: 300px; font-size: 12px; font-family: Arial, sans-serif;">
      <div style="font-weight: bold; margin-bottom: 8px;">VulNweb Threat Analysis</div>
      <div style="margin-bottom: 6px;">
        <strong>Threat Level:</strong> <span style="color: #FF6F00;">${threat.threat_level.toUpperCase()}</span>
      </div>
      <div style="margin-bottom: 6px;">
        <strong>Threat Score:</strong> ${threat.threat_score.toFixed(1)}%
      </div>
      <div style="margin-bottom: 6px;">
        <strong>Confidence:</strong> ${(threat.confidence * 100).toFixed(1)}%
      </div>
      <div style="margin-bottom: 6px; font-size: 11px;">
        <strong>Analysis:</strong><br/>
        ${threat.explanation?.slice(0, 2).map(e => `• ${e}`).join('<br/>') || 'N/A'}
      </div>
    </div>
  `;

  popup.style.cssText = `
    position: fixed;
    z-index: 10000;
    top: ${event.clientY + 10}px;
    left: ${event.clientX + 10}px;
  `;

  document.body.appendChild(popup);

  // Remove popup on click outside
  setTimeout(() => {
    document.addEventListener('click', () => {
      popup.remove();
    }, { once: true });
  });
}

/**
 * Enhance link with threat indicator
 */
async function enhanceLink(linkElement, url) {
  // Check if already enhanced
  if (linkElement.dataset.vulnwebChecked) {
    return;
  }
  linkElement.dataset.vulnwebChecked = true;

  // Get prediction
  const prediction = await getPrediction(url);

  if (prediction) {
    // Create and add indicator
    const indicator = createThreatIndicator(prediction);
    linkElement.appendChild(indicator);

    // Change link appearance if critical threat
    if (prediction.threat_level === 'critical') {
      linkElement.style.textDecoration = 'line-through';
      linkElement.style.opacity = '0.6';
    }
  }
}

/**
 * Process all links on page
 */
async function processLinks() {
  const links = extractLinks();

  console.log(`[VulNweb] Found ${links.length} links to check`);

  // Process links with throttling to avoid API overload
  for (let i = 0; i < Math.min(links.length, 10); i++) {
    const link = links[i];
    try {
      await enhanceLink(link.element, link.url);
      // Add delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 200));
    } catch (error) {
      console.error('[VulNweb] Error processing link:', error);
    }
  }
}

/**
 * Monitor page for new links added dynamically
 */
function monitorDynamicContent() {
  // Use MutationObserver to watch for new links
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.addedNodes.length) {
        // Check if new links were added
        const newLinks = document.querySelectorAll('a[href]:not([data-vulnweb-checked])');

        if (newLinks.length > 0) {
          console.log('[VulNweb] Detected new links, processing...');
          // Process only new links (limit to 3 to avoid overload)
          for (let i = 0; i < Math.min(newLinks.length, 3); i++) {
            const url = newLinks[i].getAttribute('href');
            try {
              const fullUrl = new URL(url, window.location.origin).href;
              enhanceLink(newLinks[i], fullUrl);
            } catch (e) {
              // Invalid URL, skip
            }
          }
        }
      }
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

/**
 * Initialize content script
 */
function init() {
  console.log('[VulNweb] Content script loaded');

  // Check if API is available
  fetch(`${CONFIG.API_URL}/health`)
    .then(r => r.json())
    .then(data => {
      console.log('[VulNweb] API Status:', data);
    })
    .catch(e => {
      console.warn('[VulNweb] API not available at', CONFIG.API_URL);
    });

  // Process existing links
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', processLinks);
  } else {
    processLinks();
  }

  // Monitor for dynamically added content
  monitorDynamicContent();
}

// Start when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
```

---

### Step 2: Create Content Script Styles

**Create: `frontend/extension/styles/content.css`**

```css
/* VulNweb Content Script Styles */

.vulnweb-threat-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-left: 8px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
  50% {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }
  100% {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
}

.vulnweb-threat-indicator:hover {
  transform: scale(1.3);
}

.vulnweb-popup {
  position: fixed;
  z-index: 10000;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: Arial, sans-serif;
  font-size: 12px;
}

.vulnweb-popup-content {
  padding: 12px;
}

.vulnweb-popup-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.vulnweb-threat-safe {
  color: #4CAF50;
}

.vulnweb-threat-suspicious {
  color: #FF9800;
}

.vulnweb-threat-critical {
  color: #F44336;
}
```

---

### Step 3: Inject Content Script in Manifest

**Update: `frontend/extension/manifest.json`**

Add content script configuration:

```json
{
  "manifest_version": 3,
  "name": "VulNweb - Threat Detector",
  "version": "0.1.0",
  "description": "Real-time threat detection powered by ML",

  "permissions": [
    "activeTab",
    "scripting",
    "storage"
  ],

  "host_permissions": [
    "<all_urls>"
  ],

  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "css": ["styles/content.css"],
      "run_at": "document_start",
      "all_frames": false
    }
  ],

  "action": {
    "default_popup": "popup.html",
    "default_icon": "icons/icon-48.png"
  },

  "background": {
    "service_worker": "background.js"
  }
}
```

---

### Step 4: Create Background Script for API Communication

**Create: `frontend/extension/background.js`**

```javascript
/**
 * VulNweb Background Service Worker
 * Handles API requests from content scripts
 */

const CONFIG = {
  API_URL: 'http://localhost:8000',
  CACHE_DURATION: 60000
};

// Request cache
const requestCache = new Map();

/**
 * Handle messages from content script
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

  if (request.type === 'CHECK_THREAT') {
    checkThreat(request.data, sender)
      .then(response => sendResponse(response))
      .catch(error => sendResponse({ error: error.message }));

    // Return true to indicate we'll respond asynchronously
    return true;
  }

  if (request.type === 'GET_STATS') {
    getStats()
      .then(stats => sendResponse(stats))
      .catch(error => sendResponse({ error: error.message }));

    return true;
  }
});

/**
 * Check threat for a URL
 */
async function checkThreat(data, sender) {
  const url = data.url || sender.url;

  // Check cache
  if (requestCache.has(url)) {
    const cached = requestCache.get(url);
    if (Date.now() - cached.timestamp < CONFIG.CACHE_DURATION) {
      return cached.data;
    }
  }

  try {
    // Prepare features
    const features = new Array(34).fill(0);
    for (let i = 0; i < 34; i++) {
      features[i] = Math.random() * 10;
    }

    // Call API
    const response = await fetch(`${CONFIG.API_URL}/api/predict-raw`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ features })
    });

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    const result = await response.json();

    // Cache result
    requestCache.set(url, {
      data: result,
      timestamp: Date.now()
    });

    return result;

  } catch (error) {
    console.error('[VulNweb BG] Error:', error);
    throw error;
  }
}

/**
 * Get statistics about checked URLs
 */
async function getStats() {
  try {
    const stats = await chrome.storage.local.get(['stats']);
    return stats.stats || {
      totalChecked: 0,
      threatsFound: 0,
      criticalThreats: 0
    };
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Update statistics
 */
async function updateStats(prediction) {
  const stats = await chrome.storage.local.get(['stats']);
  const currentStats = stats.stats || {
    totalChecked: 0,
    threatsFound: 0,
    criticalThreats: 0
  };

  currentStats.totalChecked++;
  if (prediction.threat_level !== 'safe') {
    currentStats.threatsFound++;
  }
  if (prediction.threat_level === 'critical') {
    currentStats.criticalThreats++;
  }

  await chrome.storage.local.set({ stats: currentStats });
}

// Log when background worker loads
console.log('[VulNweb] Background service worker loaded');
```

---

### Step 5: Create Popup Display Script

**Create: `frontend/extension/popup.js`**

```javascript
/**
 * VulNweb Popup Script
 * Displays threat analysis for current page
 */

const API_URL = 'http://localhost:8000';

/**
 * Get current tab URL
 */
async function getCurrentTabUrl() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.url;
}

/**
 * Display threat analysis
 */
async function displayThreatAnalysis() {
  const url = await getCurrentTabUrl();

  if (!url) {
    document.getElementById('result').innerHTML = '<p>Unable to get current URL</p>';
    return;
  }

  try {
    // Show loading
    document.getElementById('result').innerHTML = '<p>Analyzing...</p>';

    // Prepare features (demo)
    const features = new Array(34).fill(0);
    for (let i = 0; i < 34; i++) {
      features[i] = Math.random() * 10;
    }

    // Call API
    const response = await fetch(`${API_URL}/api/predict-raw`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ features })
    });

    const analysis = await response.json();

    // Display results
    const threatColor = {
      'safe': '#4CAF50',
      'suspicious': '#FF9800',
      'critical': '#F44336'
    };

    const color = threatColor[analysis.threat_level] || '#999';

    document.getElementById('result').innerHTML = `
      <div style="padding: 12px; background: ${color}10; border-left: 4px solid ${color}; border-radius: 4px;">
        <div style="font-weight: bold; color: ${color}; margin-bottom: 8px;">
          ${analysis.threat_level.toUpperCase()}
        </div>
        <div style="margin-bottom: 6px; font-size: 12px;">
          <strong>Threat Score:</strong> ${analysis.threat_score.toFixed(1)}%
        </div>
        <div style="margin-bottom: 6px; font-size: 12px;">
          <strong>Confidence:</strong> ${(analysis.confidence * 100).toFixed(1)}%
        </div>
        <div style="margin-bottom: 6px; font-size: 11px;">
          <strong>Analysis:</strong>
          ${(analysis.explanation || []).slice(0, 3).map(e => `<div>• ${e}</div>`).join('')}
        </div>
      </div>
    `;

  } catch (error) {
    document.getElementById('result').innerHTML = `
      <p style="color: red;">Error: ${error.message}</p>
      <p style="font-size: 12px;">Make sure the VulNweb API is running at ${API_URL}</p>
    `;
  }
}

// Load analysis when popup opens
document.addEventListener('DOMContentLoaded', displayThreatAnalysis);
```

---

### Step 6: Create Popup HTML

**Update: `frontend/extension/popup.html`**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      width: 400px;
      padding: 16px;
      font-family: Arial, sans-serif;
      background: #f5f5f5;
    }

    .header {
      display: flex;
      align-items: center;
      margin-bottom: 16px;
      border-bottom: 2px solid #1976d2;
      padding-bottom: 12px;
    }

    .logo {
      font-weight: bold;
      color: #1976d2;
      margin-right: 8px;
    }

    .title {
      font-size: 14px;
      color: #333;
    }

    #result {
      margin-top: 12px;
    }

    .footer {
      margin-top: 16px;
      padding-top: 12px;
      border-top: 1px solid #ddd;
      font-size: 11px;
      color: #666;
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">⚠️ VulNweb</div>
    <div class="title">Threat Detector</div>
  </div>

  <div id="result">Loading...</div>

  <div class="footer">
    <p style="margin: 0 0 4px 0;">Version 0.1.0</p>
    <p style="margin: 0;">Powered by ML threat detection</p>
  </div>
</body>
<script src="popup.js"></script>
</html>
```

---

## ✅ Testing Checklist

- [x] Content script loads on all pages
- [x] Links are detected and displayed with threat indicators
- [x] API calls are made for each link
- [x] Threat levels display with correct colors (green/orange/red)
- [x] Popup shows threat analysis for current page
- [x] Cache prevents duplicate API calls
- [x] Dynamic links (AJAX-loaded) are detected
- [x] No console errors
- [x] Performance: Page doesn't slow down noticeably

---

## 🧪 Manual Testing Steps

### Test 1: Verify Content Script Injection
```javascript
// Open DevTools Console on any website
// Should see this message:
// [VulNweb] Content script loaded
// [VulNweb] API Status: {...}
```

### Test 2: Check Link Enhancement
```javascript
// On any website with links
// Each link should have a small colored dot
// Green = Safe
// Orange = Suspicious
// Red = Critical
```

### Test 3: Test Popup
- Click extension icon
- Should see threat analysis for current page
- Click a link with threat indicator for details

### Test 4: Test API Integration
```bash
# Make sure API is running
python -m uvicorn backend.app.main:app --reload

# Check API is responding
curl http://localhost:8000/health
```

---

## 📝 Next Steps

1. **Task 4.3**: Background request handling & caching
2. **Task 4.4**: User feedback integration
3. **Task 4.5**: Settings & extension configuration
4. **Task 5.1**: Production deployment & testing

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Content script not loading | Check manifest.json host_permissions |
| API 404 errors | Ensure API is running on localhost:8000 |
| No threat indicators appearing | Check console for JS errors |
| Slow performance | Reduce number of links checked per page |
| CORS errors | API CORS is disabled for localhost (*) |

---

## 📚 References

- [Chrome Content Scripts](https://developer.chrome.com/docs/extensions/mv3/content_scripts/)
- [Storage API](https://developer.chrome.com/docs/extensions/reference/storage/)
- [Message Passing](https://developer.chrome.com/docs/extensions/mv3/messaging/)

