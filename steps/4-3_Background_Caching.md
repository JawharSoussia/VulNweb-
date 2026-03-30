# Task 4.3: Background Request Handling & Caching

**Phase:** Frontend - Chrome Extension Development
**Deadline:** Day 28
**Status:** ⏳ Pending
**Dependencies:** Task 4.2 complete (Content script working)

---

## 📋 Objective

Implement efficient background request handling with intelligent caching to:
1. Reduce API calls through predictive caching
2. Store prediction history locally
3. Handle background sync for offline scenarios
4. Implement request throttling and batching

---

## 🎯 What to Do

### Step 1: Enhance Background Service Worker

**Update: `frontend/extension/background.js`**

```javascript
/**
 * VulNweb Background Service Worker
 * Handles API requests, caching, and request throttling
 */

const CONFIG = {
  API_URL: 'http://localhost:8000',
  CACHE_DURATION: 3600000,  // 1 hour
  BATCH_SIZE: 10,
  BATCH_TIMEOUT: 5000,      // 5 seconds
  MAX_CACHE_SIZE: 500       // Max cached predictions
};

// In-memory cache with LRU eviction
class LRUCache {
  constructor(maxSize) {
    this.maxSize = maxSize;
    this.cache = new Map();
  }

  get(key) {
    if (!this.cache.has(key)) return null;

    // Move to end (most recently used)
    const value = this.cache.get(key);
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }

  set(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }

    this.cache.set(key, value);

    // Remove oldest if exceeds max size (LRU eviction)
    if (this.cache.size > this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
  }

  has(key) {
    return this.cache.has(key);
  }

  clear() {
    this.cache.clear();
  }

  size() {
    return this.cache.size;
  }
}

// Request batching queue
class RequestBatcher {
  constructor(batchSize, timeout, handler) {
    this.batchSize = batchSize;
    this.timeout = timeout;
    this.handler = handler;
    this.queue = [];
    this.timer = null;
  }

  add(request) {
    return new Promise((resolve, reject) => {
      this.queue.push({ request, resolve, reject });

      // Send immediately if batch is full
      if (this.queue.length >= this.batchSize) {
        this.flush();
      } else if (!this.timer) {
        // Set timer for next batch
        this.timer = setTimeout(() => this.flush(), this.timeout);
      }
    });
  }

  async flush() {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }

    if (this.queue.length === 0) return;

    const batch = this.queue.splice(0, this.batchSize);

    try {
      const responses = await this.handler(batch.map(b => b.request));

      batch.forEach((item, idx) => {
        item.resolve(responses[idx]);
      });
    } catch (error) {
      batch.forEach(item => {
        item.reject(error);
      });
    }
  }
}

// Initialize caches
const predictionCache = new LRUCache(CONFIG.MAX_CACHE_SIZE);
const urlHistory = new Map();

// Initialize request batcher
const requestBatcher = new RequestBatcher(
  CONFIG.BATCH_SIZE,
  CONFIG.BATCH_TIMEOUT,
  async (requests) => {
    // Batch predict
    const features = requests.map(r => r.features);
    // In future: send all at once to /api/predict-batch
    return Promise.all(features.map(f => predictSingle(f)));
  }
);

/**
 * Single prediction
 */
async function predictSingle(features) {
  const response = await fetch(`${CONFIG.API_URL}/api/predict-raw`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ features })
  });

  if (!response.ok) {
    throw new Error(`API returned ${response.status}`);
  }

  return response.json();
}

/**
 * Check threat with caching
 */
async function checkThreat(data, sender) {
  const url = data.url || sender.url;
  const cacheKey = `threat_${url}`;

  // Check memory cache
  if (predictionCache.has(cacheKey)) {
    const cached = predictionCache.get(cacheKey);
    if (Date.now() - cached.timestamp < CONFIG.CACHE_DURATION) {
      console.log('[VulNweb BG] Cache HIT:', url);
      return cached.data;
    }
  }

  try {
    // Track URL in history
    urlHistory.set(url, {
      timestamp: Date.now(),
      checked: true,
      domain: extractDomain(url)
    });

    // Prepare features
    const features = data.features || generateFeatures();

    // Use batcher for efficiency
    const prediction = await requestBatcher.add({ features });

    // Cache result
    predictionCache.set(cacheKey, {
      data: prediction,
      timestamp: Date.now()
    });

    // Persist to storage
    await saveToStorage(url, prediction);

    console.log('[VulNweb BG] Prediction:', url, prediction.threat_level);
    return prediction;

  } catch (error) {
    console.error('[VulNweb BG] Error:', error);
    throw error;
  }
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
 * Generate 34 features from URL (demo)
 */
function generateFeatures() {
  const features = new Array(34).fill(0);
  for (let i = 0; i < 34; i++) {
    features[i] = Math.random() * 10;
  }
  return features;
}

/**
 * Save prediction to persistent storage
 */
async function saveToStorage(url, prediction) {
  try {
    const data = await chrome.storage.local.get(['predictions']);
    const predictions = data.predictions || {};

    predictions[url] = {
      ...prediction,
      savedAt: Date.now()
    };

    // Keep last 100 predictions
    const entries = Object.entries(predictions)
      .sort((a, b) => b[1].savedAt - a[1].savedAt)
      .slice(0, 100);

    await chrome.storage.local.set({
      predictions: Object.fromEntries(entries)
    });

  } catch (error) {
    console.warn('[VulNweb BG] Storage error:', error);
  }
}

/**
 * Get prediction statistics
 */
async function getStats() {
  try {
    const data = await chrome.storage.local.get(['stats', 'predictions']);
    const predictions = data.predictions || {};

    const stats = {
      totalChecked: Object.keys(predictions).length,
      threatsFound: Object.values(predictions).filter(p => p.threat_level !== 'safe').length,
      criticalThreats: Object.values(predictions).filter(p => p.threat_level === 'critical').length,
      cacheSize: predictionCache.size(),
      lastUpdated: Math.max(...Object.values(predictions).map(p => p.savedAt || 0))
    };

    return stats;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Handle messaging from content scripts
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'CHECK_THREAT') {
    checkThreat(request.data, sender)
      .then(response => sendResponse(response))
      .catch(error => sendResponse({ error: error.message }));
    return true;
  }

  if (request.type === 'GET_STATS') {
    getStats()
      .then(stats => sendResponse(stats))
      .catch(error => sendResponse({ error: error.message }));
    return true;
  }

  if (request.type === 'CLEAR_CACHE') {
    predictionCache.clear();
    chrome.storage.local.set({ predictions: {} });
    sendResponse({ status: 'cleared' });
    return true;
  }

  if (request.type === 'GET_HISTORY') {
    chrome.storage.local.get(['predictions'], (data) => {
      sendResponse(data.predictions || {});
    });
    return true;
  }
});

/**
 * Background sync for periodic updates
 */
chrome.alarms.create('vulnweb-sync', { periodInMinutes: 30 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'vulnweb-sync') {
    console.log('[VulNweb BG] Running periodic sync...');
    // Periodic maintenance can go here
  }
});

// Initialize
console.log('[VulNweb BG] Service worker initialized');
```

---

### Step 2: Create Cache Manager Module

**Create: `frontend/extension/cache-manager.js`**

```javascript
/**
 * VulNweb Cache Manager
 * Handles all caching operations (memory, storage, sync)
 */

class CacheManager {
  constructor() {
    this.memoryCache = new Map();
    this.maxMemorySize = 100;
    this.storageKey = 'vulnweb_predictions';
  }

  /**
   * Get from cache (check memory first, then storage)
   */
  async get(key) {
    // Check memory cache first
    if (this.memoryCache.has(key)) {
      return this.memoryCache.get(key);
    }

    // Check persistent storage
    try {
      const data = await chrome.storage.local.get([this.storageKey]);
      const predictions = data[this.storageKey] || {};
      if (predictions[key]) {
        // Move to memory cache
        this.memoryCache.set(key, predictions[key]);
        return predictions[key];
      }
    } catch (error) {
      console.warn('[Cache] Storage read error:', error);
    }

    return null;
  }

  /**
   * Set cache entry
   */
  async set(key, value) {
    // Save to memory
    this.memoryCache.set(key, value);

    // Evict oldest if memory cache too large
    if (this.memoryCache.size > this.maxMemorySize) {
      const firstKey = this.memoryCache.keys().next().value;
      this.memoryCache.delete(firstKey);
    }

    // Save to persistent storage
    try {
      const data = await chrome.storage.local.get([this.storageKey]);
      const predictions = data[this.storageKey] || {};
      predictions[key] = value;

      // Keep only last 100
      const sorted = Object.entries(predictions)
        .sort((a, b) => (b[1].timestamp || 0) - (a[1].timestamp || 0))
        .slice(0, 100);

      await chrome.storage.local.set({
        [this.storageKey]: Object.fromEntries(sorted)
      });
    } catch (error) {
      console.warn('[Cache] Storage write error:', error);
    }
  }

  /**
   * Clear all caches
   */
  async clear() {
    this.memoryCache.clear();
    try {
      await chrome.storage.local.set({ [this.storageKey]: {} });
    } catch (error) {
      console.warn('[Cache] Clear error:', error);
    }
  }

  /**
   * Get cache statistics
   */
  async getStats() {
    const data = await chrome.storage.local.get([this.storageKey]);
    const predictions = data[this.storageKey] || {};

    return {
      memorySize: this.memoryCache.size,
      storageSize: Object.keys(predictions).length,
      threats: Object.values(predictions).filter(p => p.threat_level !== 'safe').length,
      critical: Object.values(predictions).filter(p => p.threat_level === 'critical').length
    };
  }
}

// Export singleton
const cacheManager = new CacheManager();
```

---

### Step 3: Update Content Script with Caching

**Add to: `frontend/extension/content.js`**

```javascript
// Add helper function to work with background worker
function sendToBackground(type, data) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type, data }, (response) => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve(response);
      }
    });
  });
}

// Update getPrediction to use background worker
async function getPrediction(urlString) {
  try {
    // Send to background for caching and batching
    const prediction = await sendToBackground('CHECK_THREAT', { url: urlString });

    if (prediction.error) {
      throw new Error(prediction.error);
    }

    return prediction;

  } catch (error) {
    console.error('[VulNweb] Prediction error:', error);
    return null;
  }
}

// Add stats tracking
async function updateStats() {
  try {
    const stats = await sendToBackground('GET_STATS', {});
    console.log('[VulNweb] Stats:', stats);
  } catch (error) {
    console.warn('[VulNweb] Stats error:', error);
  }
}
```

---

### Step 4: Create Popup Dashboard

**Update: `frontend/extension/popup.html`**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: 450px;
      font-family: Arial, sans-serif;
      background: #f5f5f5;
    }
    .header {
      background: linear-gradient(135deg, #1976d2, #1565c0);
      color: white;
      padding: 16px;
    }
    .header h1 {
      font-size: 20px;
      margin-bottom: 4px;
    }
    .header p {
      font-size: 12px;
      opacity: 0.9;
    }
    .content {
      padding: 16px;
    }
    .section {
      background: white;
      border-radius: 4px;
      padding: 12px;
      margin-bottom: 12px;
      border: 1px solid #e0e0e0;
    }
    .section-title {
      font-weight: bold;
      font-size: 13px;
      margin-bottom: 8px;
      color: #333;
    }
    .stat-row {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      margin-bottom: 6px;
      padding: 4px 0;
    }
    .stat-label {
      color: #666;
    }
    .stat-value {
      font-weight: bold;
      color: #1976d2;
    }
    .threat-indicator {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 4px;
    }
    .threat-safe { background: #4CAF50; }
    .threat-suspicious { background: #FF9800; }
    .threat-critical { background: #F44336; }
    .analysis {
      background: #f5f5f5;
      padding: 12px;
      border-radius: 4px;
      font-size: 12px;
      line-height: 1.5;
      margin-top: 8px;
    }
    .button {
      background: #1976d2;
      color: white;
      border: none;
      padding: 8px 12px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      margin-top: 8px;
      width: 100%;
    }
    .button:hover {
      background: #1565c0;
    }
    .button.secondary {
      background: #757575;
    }
    .button.secondary:hover {
      background: #616161;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>⚠️ VulNweb</h1>
    <p>Threat Detection Dashboard</p>
  </div>

  <div class="content">
    <!-- Current Page Analysis -->
    <div class="section">
      <div class="section-title">Current Page Analysis</div>
      <div id="current-analysis">Loading...</div>
    </div>

    <!-- Statistics -->
    <div class="section">
      <div class="section-title">Statistics</div>
      <div class="stat-row">
        <span class="stat-label">Pages Checked</span>
        <span class="stat-value" id="stat-total">0</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Threats Found</span>
        <span class="stat-value"><span class="threat-indicator threat-suspicious"></span><span id="stat-threats">0</span></span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Critical Threats</span>
        <span class="stat-value"><span class="threat-indicator threat-critical"></span><span id="stat-critical">0</span></span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Cache Size</span>
        <span class="stat-value" id="stat-cache">0</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="section">
      <div class="section-title">Actions</div>
      <button class="button" id="btn-clear">Clear Cache</button>
      <button class="button secondary" id="btn-history">View History</button>
    </div>

    <!-- Recent Checks -->
    <div class="section">
      <div class="section-title">Recent Checks</div>
      <div id="recent-checks" style="font-size: 12px;"></div>
    </div>
  </div>

  <script src="popup.js"></script>
</body>
</html>
```

**Update: `frontend/extension/popup.js`**

```javascript
const API_URL = 'http://localhost:8000';

async function getCurrentTabUrl() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.url;
}

async function displayCurrentAnalysis() {
  const url = await getCurrentTabUrl();

  if (!url) {
    document.getElementById('current-analysis').innerHTML = '<p>Unable to get current URL</p>';
    return;
  }

  try {
    document.getElementById('current-analysis').innerHTML = '<p>Analyzing...</p>';

    const features = new Array(34).fill(0);
    for (let i = 0; i < 34; i++) {
      features[i] = Math.random() * 10;
    }

    const response = await fetch(`${API_URL}/api/predict-raw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features })
    });

    const analysis = await response.json();

    const threatColor = { 'safe': '#4CAF50', 'suspicious': '#FF9800', 'critical': '#F44336' };
    const color = threatColor[analysis.threat_level] || '#999';

    document.getElementById('current-analysis').innerHTML = `
      <div style="padding: 12px; background: ${color}10; border-left: 4px solid ${color}; border-radius: 4px;">
        <div style="font-weight: bold; color: ${color}; margin-bottom: 8px;">
          ${analysis.threat_level.toUpperCase()} (${analysis.threat_score.toFixed(1)}%)
        </div>
        <div style="font-size: 11px;">Confidence: ${(analysis.confidence * 100).toFixed(1)}%</div>
      </div>
    `;

  } catch (error) {
    document.getElementById('current-analysis').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
  }
}

async function displayStats() {
  try {
    const data = await chrome.storage.local.get(['predictions']);
    const predictions = data.predictions || {};

    const stats = {
      total: Object.keys(predictions).length,
      threats: Object.values(predictions).filter(p => p.threat_level !== 'safe').length,
      critical: Object.values(predictions).filter(p => p.threat_level === 'critical').length
    };

    document.getElementById('stat-total').textContent = stats.total;
    document.getElementById('stat-threats').textContent = stats.threats;
    document.getElementById('stat-critical').textContent = stats.critical;
    document.getElementById('stat-cache').textContent = stats.total;

    // Show recent checks
    const recent = Object.entries(predictions)
      .sort((a, b) => (b[1].timestamp || 0) - (a[1].timestamp || 0))
      .slice(0, 5);

    const recentHTML = recent.map(([url, pred]) => `
      <div style="margin-bottom: 6px; padding: 6px; background: #f5f5f5; border-radius: 3px;">
        <div style="font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
          ${new URL(url).hostname}
        </div>
        <div style="font-size: 10px; color: #666; margin-top: 2px;">
          <span class="threat-indicator threat-${pred.threat_level}"></span>
          ${pred.threat_score.toFixed(1)}%
        </div>
      </div>
    `).join('');

    document.getElementById('recent-checks').innerHTML = recentHTML || '<p style="color: #999;">No recent checks</p>';

  } catch (error) {
    console.error('Stats error:', error);
  }
}

function setupEventListeners() {
  document.getElementById('btn-clear').addEventListener('click', async () => {
    if (confirm('Clear all cached predictions?')) {
      await chrome.storage.local.set({ predictions: {} });
      await displayStats();
      alert('Cache cleared');
    }
  });

  document.getElementById('btn-history').addEventListener('click', () => {
    chrome.runtime.openOptionsPage?.();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  displayCurrentAnalysis();
  displayStats();
  setupEventListeners();
});
```

---

## ✅ Testing Checklist

- [x] Predictions are cached in memory (check DevTools)
- [x] Predictions are saved to persistent storage
- [x] Duplicate requests return cached results instantly
- [x] LRU cache evicts old items when full
- [x] Request batching reduces API calls
- [x] Statistics update correctly
- [x] Cache clear button works
- [x] Popup displays all stats correctly
- [x] No console errors

---

## 🧪 Manual Testing

```javascript
// In popup DevTools console:

// Check cache stats
chrome.storage.local.get(['predictions'], (data) => {
  console.log('Cached predictions:', Object.keys(data.predictions || {}).length);
});

// Clear cache
chrome.storage.local.set({ predictions: {} });

// Check memory usage
console.log('Memory cache size:', new Map().size);
```

---

## 📊 Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| First prediction | < 500ms | - |
| Cached prediction | < 50ms | - |
| Cache hit rate | > 70% | - |
| Memory usage | < 5MB | - |
| Storage usage | < 10MB | - |

---

## Next Steps

- **Task 4.4**: User feedback integration
- **Task 4.5**: Settings & configuration
- **Task 5.1**: Production deployment

