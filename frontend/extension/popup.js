const API_URL = 'http://localhost:8000';

async function getCurrentTabUrl() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.url;
}


async function displayCurrentAnalysis() {
  const url = await getCurrentTabUrl();

  if (!url) {
    document.getElementById('current-analysis').innerHTML = '<div>Unable to get current URL</div>';
    return;
  }

  try {
    document.getElementById('current-analysis').innerHTML = '<div>Analyzing...</div>';

    // Check unified storage pattern from background.js
    const data = await chrome.storage.local.get(['predictions']);
    const predictions = data.predictions || {};

    if (predictions[url]) {
      const analysis = predictions[url];
      const confidence = analysis.confidence > 1 ? analysis.confidence : analysis.confidence * 100;

      document.getElementById('current-analysis').innerHTML = `
        <div class="threat-level ${analysis.threat_level}">
          ${(analysis.threat_level || 'unknown').toUpperCase()} (${confidence.toFixed(1)}%)
        </div>
      `;
      return;
    }

    // Use background worker for prediction (handles caching, batching)
    const analysis = await chrome.runtime.sendMessage({ type: 'CHECK_THREAT', data: { url } });

    if (analysis.error) {
      throw new Error(analysis.error);
    }

    if (!analysis.threat_level) {
      throw new Error('Invalid response: missing threat_level');
    }

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

    // Filter out invalid predictions safely
    const validPredictions = Object.entries(predictions)
      .filter(([url, pred]) => {
        try {
          return new URL(url) && pred && pred.threat_level;
        } catch {
          return false;
        }
      })
      .map(([, pred]) => pred);

    const stats = {
      total: validPredictions.length,
      threats: validPredictions.filter(p => p.threat_level !== 'safe').length,
      critical: validPredictions.filter(p => p.threat_level === 'critical').length
    };

    document.getElementById('stat-total').textContent = stats.total;
    document.getElementById('stat-threats').textContent = stats.threats;
    document.getElementById('stat-critical').textContent = stats.critical;

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

  document.getElementById('btn-dashboard').addEventListener('click', () => {
    chrome.tabs.create({ url: chrome.runtime.getURL('dashboard.html') });
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