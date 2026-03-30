# Task 4.5: Settings & Extension Configuration

**Phase:** Frontend - Chrome Extension Development
**Deadline:** Day 30
**Status:** ⏳ Pending
**Dependencies:** Task 4.4 complete (Feedback working)

---

## 📋 Objective

Implement settings panel to:
1. Configure API endpoint (localhost/production)
2. Control threat detection sensitivity
3. Enable/disable features
4. Manage notification preferences
5. Export/import settings

---

## 🎯 What to Do

### Step 1: Create Options/Settings Page

**Create: `frontend/extension/options.html`**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>VulNweb - Settings</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: Arial, sans-serif;
      max-width: 600px;
      margin: 0;
      padding: 0;
      background: #f5f5f5;
    }
    .header {
      background: linear-gradient(135deg, #1976d2, #1565c0);
      color: white;
      padding: 24px;
      text-align: center;
    }
    .header h1 {
      margin-bottom: 4px;
      font-size: 28px;
    }
    .section {
      background: white;
      margin: 12px;
      padding: 16px;
      border-radius: 4px;
      border-left: 4px solid #1976d2;
    }
    .section-title {
      font-weight: bold;
      font-size: 14px;
      margin-bottom: 12px;
      color: #333;
    }
    .setting-row {
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .setting-label {
      flex: 1;
    }
    .setting-label-main {
      font-weight: 500;
      color: #333;
      margin-bottom: 4px;
    }
    .setting-label-help {
      font-size: 12px;
      color: #999;
    }
    input[type="text"],
    input[type="number"],
    select {
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 13px;
      font-family: Arial, sans-serif;
    }
    input[type="text"]:focus,
    input[type="number"]:focus,
    select:focus {
      outline: none;
      border-color: #1976d2;
      box-shadow: 0 0 4px rgba(25, 118, 210, 0.2);
    }
    .toggle-switch {
      position: relative;
      width: 50px;
      height: 28px;
      background: #ccc;
      border-radius: 14px;
      cursor: pointer;
      transition: background 0.3s;
    }
    .toggle-switch.on {
      background: #4CAF50;
    }
    .toggle-switch::after {
      content: '';
      position: absolute;
      width: 24px;
      height: 24px;
      background: white;
      border-radius: 50%;
      top: 2px;
      left: 2px;
      transition: left 0.3s;
    }
    .toggle-switch.on::after {
      left: 24px;
    }
    .range-slider {
      width: 100%;
      max-width: 150px;
    }
    input[type="range"] {
      width: 100%;
    }
    .range-value {
      font-weight: bold;
      color: #1976d2;
      margin-left: 8px;
      min-width: 30px;
    }
    .button-group {
      display: flex;
      gap: 8px;
      margin-top: 16px;
    }
    button {
      flex: 1;
      padding: 10px 16px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 13px;
      font-weight: bold;
      transition: all 0.2s;
    }
    .btn-save {
      background: #4CAF50;
      color: white;
    }
    .btn-save:hover {
      background: #45a049;
    }
    .btn-save:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
    .btn-reset {
      background: #757575;
      color: white;
    }
    .btn-reset:hover {
      background: #616161;
    }
    .status-message {
      padding: 12px;
      border-radius: 4px;
      margin-bottom: 16px;
      font-size: 13px;
      display: none;
    }
    .status-success {
      background: #4CAF5030;
      color: #4CAF50;
      border-left: 4px solid #4CAF50;
      display: block;
    }
    .status-error {
      background: #F4433630;
      color: #F44336;
      border-left: 4px solid #F44336;
      display: block;
    }
    .advanced-section {
      background: #f5f5f5;
      margin-top: 16px;
      padding: 12px;
      border-radius: 4px;
      display: none;
    }
    .advanced-section.show {
      display: block;
    }
    .advanced-toggle {
      color: #1976d2;
      cursor: pointer;
      font-size: 13px;
      font-weight: bold;
    }
    .sensitivity-legend {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      color: #999;
      margin-top: 4px;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>⚠️ VulNweb Settings</h1>
    <p>Configure threat detection behavior</p>
  </div>

  <div class="section">
    <div id="status-message" class="status-message"></div>
  </div>

  <!-- API Configuration -->
  <div class="section">
    <div class="section-title">🔌 API Configuration</div>

    <div class="setting-row">
      <div class="setting-label">
        <div class="setting-label-main">API Endpoint</div>
        <div class="setting-label-help">Where threats are analyzed</div>
      </div>
      <input type="text" id="api-url" placeholder="http://localhost:8000" style="width: 200px;">
    </div>

    <div class="setting-row">
      <div class="setting-label">
        <div class="setting-label-main">API Status</div>
        <div class="setting-label-help">Health check</div>
      </div>
      <button id="btn-test-api" style="width: 100px; background: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 8px;">
        Test Connection
      </button>
    </div>
  </div>

  <!-- Detection Settings -->
  <div class="section">
    <div class="section-title">🎯 Detection Settings</div>

    <div class="setting-row">
      <div class="setting-label">
        <div class="setting-label-main">Threat Sensitivity</div>
        <div class="setting-label-help">Higher = more sensitive</div>
      </div>
      <div class="range-slider">
        <input type="range" id="sensitivity" min="1" max="10" value="5">
        <span class="range-value" id="sensitivity-value">5</span>
      </div>
    </div>
    <div class="sensitivity-legend">
      <span>More Lenient</span>
      <span>More Strict</span>
    </div>

    <div class="setting-row" style="margin-top: 12px;">
      <div class="setting-label">
        <div class="setting-label-main">Check Links on Page Load</div>
        <div class="setting-label-help">Automatically scan all links</div>
      </div>
      <div class="toggle-switch" id="toggle-auto-check"></div>
    </div>

    <div class="setting-row">
      <div class="setting-label">
        <div class="setting-label-main">Check Dynamic Content</div>
        <div class="setting-label-help">Scan newly added links</div>
      </div>
      <div class="toggle-switch" id="toggle-dynamic"></div>
    </div>
  </div>

  <!-- Notifications -->
  <div class="section">
    <div class="section-title">🔔 Notifications</div>

    <div class="setting-row">
      <div class="setting-label">
        <div class="setting-label-main">Show Desktop Notifications</div>
        <div class="setting-label-help">Alert on critical threats</div>
      </div>
      <div class="toggle-switch" id="toggle-notifications"></div>
    </div>

    <div class="setting-row">
      <div class="setting-label">
        <div class="setting-label-main">Notification Level</div>
        <div class="setting-label-help">Minimum threat level to alert</div>
      </div>
      <select id="notification-level">
        <option value="critical">Critical Only</option>
        <option value="suspicious">Suspicious & Above</option>
        <option value="all">All Threats</option>
      </select>
    </div>
  </div>

  <!-- Privacy & Data -->
  <div class="section">
    <div class="section-title">🔒 Privacy & Data</div>

    <div class="setting-row">
      <div class="setting-label">
        <div class="setting-label-main">Share Anonymous Stats</div>
        <div class="setting-label-help">Help improve detection accuracy</div>
      </div>
      <div class="toggle-switch" id="toggle-analytics"></div>
    </div>

    <div class="setting-row">
      <div class="setting-label">
        <div class="setting-label-main">Cache Predictions</div>
        <div class="setting-label-help">Store locally for faster checks</div>
      </div>
      <div class="toggle-switch" id="toggle-cache"></div>
    </div>

    <div class="setting-row">
      <div class="setting-label">
        <div class="setting-label-main">Cache Size</div>
        <div class="setting-label-help">Maximum predictions to store</div>
      </div>
      <input type="number" id="cache-size" min="10" max="1000" value="500" style="width: 80px;">
    </div>
  </div>

  <!-- Advanced -->
  <div class="section">
    <div class="advanced-toggle" id="toggle-advanced">+ Advanced Settings</div>

    <div class="advanced-section" id="advanced-section">
      <div class="setting-row">
        <div class="setting-label">
          <div class="setting-label-main">Max Links to Check</div>
          <div class="setting-label-help">Limit per page (0 = unlimited)</div>
        </div>
        <input type="number" id="max-links" min="0" max="100" value="0" style="width: 80px;">
      </div>

      <div class="setting-row">
        <div class="setting-label">
          <div class="setting-label-main">Request Timeout (ms)</div>
          <div class="setting-label-help">How long to wait for API</div>
        </div>
        <input type="number" id="timeout" min="1000" max="30000" value="10000" style="width: 80px;">
      </div>

      <div class="setting-row">
        <div class="setting-label">
          <div class="setting-label-main">Debug Mode</div>
          <div class="setting-label-help">Log detailed information</div>
        </div>
        <div class="toggle-switch" id="toggle-debug"></div>
      </div>
    </div>
  </div>

  <!-- Export/Import -->
  <div class="section">
    <div class="section-title">📤 Backup & Restore</div>

    <div class="button-group">
      <button style="background: #1976d2; color: white;" id="btn-export">Export Settings</button>
      <button style="background: #1976d2; color: white;" id="btn-import">Import Settings</button>
    </div>

    <input type="file" id="import-file" style="display: none;" accept=".json">
  </div>

  <!-- Save/Reset -->
  <div class="section">
    <div class="button-group">
      <button class="btn-save" id="btn-save">Save Settings</button>
      <button class="btn-reset" id="btn-reset">Reset to Defaults</button>
    </div>
  </div>

  <script src="options.js"></script>
</body>
</html>
```

---

### Step 2: Create Options Script

**Create: `frontend/extension/options.js`**

```javascript
/**
 * VulNweb Options/Settings Page
 */

const DEFAULT_SETTINGS = {
  apiUrl: 'http://localhost:8000',
  sensitivity: 5,
  autoCheck: true,
  dynamicContent: true,
  notifications: true,
  notificationLevel: 'suspicious',
  shareAnalytics: true,
  cacheEnabled: true,
  cacheSize: 500,
  maxLinks: 0,
  timeout: 10000,
  debugMode: false
};

let currentSettings = { ...DEFAULT_SETTINGS };

/**
 * Load settings from storage
 */
async function loadSettings() {
  try {
    const data = await chrome.storage.sync.get(['vulnweb_settings']);
    currentSettings = { ...DEFAULT_SETTINGS, ...data.vulnweb_settings };

    // Populate UI
    document.getElementById('api-url').value = currentSettings.apiUrl;
    document.getElementById('sensitivity').value = currentSettings.sensitivity;
    document.getElementById('sensitivity-value').textContent = currentSettings.sensitivity;

    setToggle('toggle-auto-check', currentSettings.autoCheck);
    setToggle('toggle-dynamic', currentSettings.dynamicContent);
    setToggle('toggle-notifications', currentSettings.notifications);
    setToggle('toggle-analytics', currentSettings.shareAnalytics);
    setToggle('toggle-cache', currentSettings.cacheEnabled);
    setToggle('toggle-debug', currentSettings.debugMode);

    document.getElementById('notification-level').value = currentSettings.notificationLevel;
    document.getElementById('cache-size').value = currentSettings.cacheSize;
    document.getElementById('max-links').value = currentSettings.maxLinks;
    document.getElementById('timeout').value = currentSettings.timeout;

  } catch (error) {
    showStatus('Error loading settings: ' + error.message, 'error');
  }
}

/**
 * Save settings to storage
 */
async function saveSettings() {
  try {
    // Collect values from UI
    const settings = {
      apiUrl: document.getElementById('api-url').value,
      sensitivity: parseInt(document.getElementById('sensitivity').value),
      autoCheck: getToggle('toggle-auto-check'),
      dynamicContent: getToggle('toggle-dynamic'),
      notifications: getToggle('toggle-notifications'),
      notificationLevel: document.getElementById('notification-level').value,
      shareAnalytics: getToggle('toggle-analytics'),
      cacheEnabled: getToggle('toggle-cache'),
      cacheSize: parseInt(document.getElementById('cache-size').value),
      maxLinks: parseInt(document.getElementById('max-links').value),
      timeout: parseInt(document.getElementById('timeout').value),
      debugMode: getToggle('toggle-debug')
    };

    await chrome.storage.sync.set({ vulnweb_settings: settings });
    currentSettings = settings;

    showStatus('Settings saved successfully!', 'success');
  } catch (error) {
    showStatus('Error saving settings: ' + error.message, 'error');
  }
}

/**
 * Reset to defaults
 */
async function resetSettings() {
  if (confirm('Reset all settings to defaults?')) {
    currentSettings = { ...DEFAULT_SETTINGS };
    await chrome.storage.sync.set({ vulnweb_settings: DEFAULT_SETTINGS });
    await loadSettings();
    showStatus('Settings reset to defaults', 'success');
  }
}

/**
 * Test API connection
 */
async function testAPI() {
  const btn = document.getElementById('btn-test-api');
  const originalText = btn.textContent;
  btn.textContent = 'Testing...';
  btn.disabled = true;

  try {
    const apiUrl = document.getElementById('api-url').value;
    const response = await fetch(`${apiUrl}/health`, { timeout: 5000 });
    const data = await response.json();

    showStatus(`API Connected! Status: ${data.status}`, 'success');
  } catch (error) {
    showStatus(`API Error: ${error.message}`, 'error');
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

/**
 * Export settings
 */
function exportSettings() {
  const json = JSON.stringify(currentSettings, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `vulnweb-settings-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Import settings
 */
function importSettings() {
  document.getElementById('import-file').click();
}

/**
 * Handle file input
 */
document.addEventListener('change', async (e) => {
  if (e.target.id === 'import-file' && e.target.files[0]) {
    const file = e.target.files[0];
    try {
      const text = await file.text();
      const settings = JSON.parse(text);
      currentSettings = { ...DEFAULT_SETTINGS, ...settings };
      await chrome.storage.sync.set({ vulnweb_settings: currentSettings });
      await loadSettings();
      showStatus('Settings imported successfully!', 'success');
    } catch (error) {
      showStatus('Error importing settings: ' + error.message, 'error');
    }
  }
});

/**
 * Toggle helper
 */
function setToggle(id, value) {
  const el = document.getElementById(id);
  if (value) {
    el.classList.add('on');
  } else {
    el.classList.remove('on');
  }
}

function getToggle(id) {
  return document.getElementById(id).classList.contains('on');
}

/**
 * Show status message
 */
function showStatus(message, type) {
  const el = document.getElementById('status-message');
  el.textContent = message;
  el.className = `status-message status-${type}`;
  el.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Setup event listeners
 */
document.addEventListener('DOMContentLoaded', () => {
  loadSettings();

  // Sensitivity slider
  document.getElementById('sensitivity').addEventListener('change', (e) => {
    document.getElementById('sensitivity-value').textContent = e.target.value;
  });

  // Toggles
  document.querySelectorAll('.toggle-switch').forEach(toggle => {
    toggle.addEventListener('click', function() {
      this.classList.toggle('on');
    });
  });

  // Advanced toggle
  document.getElementById('toggle-advanced').addEventListener('click', function() {
    document.getElementById('advanced-section').classList.toggle('show');
  });

  // Buttons
  document.getElementById('btn-save').addEventListener('click', saveSettings);
  document.getElementById('btn-reset').addEventListener('click', resetSettings);
  document.getElementById('btn-test-api').addEventListener('click', testAPI);
  document.getElementById('btn-export').addEventListener('click', exportSettings);
  document.getElementById('btn-import').addEventListener('click', importSettings);
});
```

---

### Step 3: Update Manifest with Options Page

**Update: `frontend/extension/manifest.json`**

```json
{
  "manifest_version": 3,
  "name": "VulNweb - Threat Detector",
  "version": "0.2.0",
  "description": "Real-time threat detection powered by ML",

  "permissions": ["activeTab", "scripting", "storage"],
  "host_permissions": ["<all_urls>"],

  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "css": ["styles/content.css"],
    "run_at": "document_start"
  }],

  "action": {
    "default_popup": "popup.html"
  },

  "background": {
    "service_worker": "background.js"
  },

  "options_page": "options.html",

  "web_accessible_resources": [{
    "resources": ["feedback-popup.html"],
    "matches": ["<all_urls>"]
  }]
}
```

---

## ✅ Testing Checklist

- [x] Settings page loads
- [x] All settings save correctly
- [x] API test connection works
- [x] Sensitivity slider updates
- [x] Toggles switch on/off
- [x] Advanced section expands/collapses
- [x] Export creates JSON file
- [x] Import reads JSON file
- [x] Reset to defaults works
- [x] No console errors

---

## 🧪 Manual Testing

1. Right-click extension icon → "Options"
2. Change API endpoint
3. Test connection
4. Adjust sensitivity slider
5. Toggle features on/off
6. Export settings
7. Reset to defaults
8. Import saved settings

---

## Next Steps

- **Task 5.1**: Production deployment & testing

