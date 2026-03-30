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

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    try {
      const response = await fetch(`${apiUrl}/health`, {
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      showStatus(`✓ API Connected! Status: ${data.status}`, 'success');
    } catch (error) {
      clearTimeout(timeoutId);

      if (error.name === 'AbortError') {
        showStatus('API Error: Request timeout (5 seconds)', 'error');
      } else {
        showStatus(`API Error: ${error.message}`, 'error');
      }
    }
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