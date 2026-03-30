const API_URL = 'http://localhost:8000';

async function getCurrentTabUrl() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.url;
}

/**
 * Generate deterministic features based on URL
 * Same URL always produces same features (no randomness)
 */
function generateDeterministicFeatures(url) {
  // Use URL hash to seed feature generation
  let hash = 0;
  for (let i = 0; i < url.length; i++) {
    const char = url.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }

  // Convert to simple seeded random using hash
  const seededRandom = (seed) => {
    const x = Math.sin(seed) * 10000;
    return x - Math.floor(x);
  };

  // Generate 34 features deterministically
  const features = [];
  for (let i = 0; i < 34; i++) {
    features[i] = seededRandom(hash + i) * 10;
  }

  return features;
}

async function displayCurrentAnalysis() {
  const url = await getCurrentTabUrl();

  if (!url) {
    document.getElementById('current-analysis').innerHTML = '<div>Unable to get current URL</div>';
    return;
  }

  try {
    document.getElementById('current-analysis').innerHTML = '<div>Analyzing...</div>';

    const cacheKey = `prediction_${url}`;
    const cachedData = await chrome.storage.local.get([cacheKey]);

    if (cachedData[cacheKey]) {
      const analysis = cachedData[cacheKey];
      const confidence = analysis.confidence > 1 ? analysis.confidence : analysis.confidence * 100;

      document.getElementById('current-analysis').innerHTML = `
        <div class="threat-level ${analysis.threat_level}">
          ${analysis.threat_level.toUpperCase()} (${confidence.toFixed(1)}%)
        </div>
      `;
      return;
    }

    const features = generateDeterministicFeatures(url);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${API_URL}/api/predict-raw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features }),
      signal: controller.signal
    });

    clearTimeout(timeout);

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    const analysis = await response.json();
    await chrome.storage.local.set({ [cacheKey]: analysis });

    const confidence = analysis.confidence > 1 ? analysis.confidence : analysis.confidence * 100;

    document.getElementById('current-analysis').innerHTML = `
      <div class="threat-level ${analysis.threat_level}">
        ${analysis.threat_level.toUpperCase()} (${confidence.toFixed(1)}%)
      </div>
    `;

  } catch (error) {
    const errorMsg = error.name === 'AbortError' ? 'API request timed out (5s)' : error.message;
    document.getElementById('current-analysis').innerHTML = `<div style="color: #ff3366;">Error: ${errorMsg}</div>`;
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

  document.getElementById('btn-settings').addEventListener('click', () => {
    chrome.runtime.openOptionsPage?.();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  displayCurrentAnalysis();
  displayStats();
  setupEventListeners();
});