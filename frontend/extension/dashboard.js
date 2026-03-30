/**
 * VulNweb Dashboard - Threat Statistics & Activity Log
 */

// ============================================================================
// DATA LOADING
// ============================================================================

async function loadDashboardData() {
  try {
    document.querySelector('.container').innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
        <div class="spinner"></div>
        <p>Loading dashboard data...</p>
      </div>
    `;

    const data = await chrome.storage.local.get(['predictions']);
    const predictions = data.predictions || {};

    const lastUpdated = Math.max(
      ...Object.values(predictions).map(p => p.savedAt || 0)
    );

    // Calculate statistics
    const stats = calculateStats(predictions);

    // Render dashboard
    renderDashboard(stats, predictions, lastUpdated);

  } catch (error) {
    console.error('Dashboard error:', error);
    showError('Failed to load dashboard');
  }
}

function calculateStats(predictions) {
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
    safe: validPredictions.filter(p => p.threat_level === 'safe').length,
    suspicious: validPredictions.filter(p => p.threat_level === 'suspicious').length,
    critical: validPredictions.filter(p => p.threat_level === 'critical').length,
    avgScore: validPredictions.length > 0
      ? (validPredictions.reduce((sum, p) => sum + (p.threat_score || 0), 0) / validPredictions.length).toFixed(1)
      : 0
  };

  return stats;
}

// ============================================================================
// RENDERING
// ============================================================================

function renderDashboard(stats, predictions, lastUpdated) {
  const html = `
    <div class="header">
      <h1>📊 VulNweb Threat Dashboard</h1>
      <p>Real-time threat statistics and activity log</p>
    </div>

    <div class="info-box">
      Last updated: <strong id="last-updated">${formatTime(lastUpdated)}</strong> |
      Cache size: <strong id="cache-size">${Object.keys(predictions).length} URLs</strong> |
      API Status: <strong id="api-status" style="color: #4CAF50;">Connected</strong>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card safe">
        <div class="stat-value" id="stat-safe">${stats.safe}</div>
        <div class="stat-label">Safe URLs</div>
      </div>
      <div class="stat-card suspicious">
        <div class="stat-value" id="stat-suspicious">${stats.suspicious}</div>
        <div class="stat-label">Suspicious URLs</div>
      </div>
      <div class="stat-card critical">
        <div class="stat-value" id="stat-critical">${stats.critical}</div>
        <div class="stat-label">Critical Threats</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="stat-total">${stats.total}</div>
        <div class="stat-label">Total Checked</div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="charts-grid">
      <!-- Threat Distribution -->
      <div class="chart-card">
        <div class="chart-title">Threat Distribution</div>
        <div class="threat-distribution" id="threat-chart">
          ${renderChartBars(stats)}
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="chart-card">
        <div class="chart-title">Recent Activity (Last 10)</div>
        <div class="activity-list" id="activity-list">
          ${renderActivityList(predictions)}
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="actions" style="margin-bottom: 24px;">
      <button class="btn btn-primary" onclick="refreshDashboard()">↻ Refresh</button>
      <button class="btn btn-secondary" onclick="clearAllData()">🗑️ Clear All</button>
      <button class="btn btn-secondary" onclick="exportData()">📥 Export</button>
    </div>
  `;

  document.querySelector('.container').innerHTML = html;
}

function renderChartBars(stats) {
  const total = stats.total || 1;
  const safeHeight = (stats.safe / total) * 100 || 10;
  const susHeight = (stats.suspicious / total) * 100 || 10;
  const critHeight = (stats.critical / total) * 100 || 10;

  return `
    <div class="bar safe" style="height: ${safeHeight}%;">
      <div class="bar-value">${stats.safe}</div>
      <div class="bar-label">Safe</div>
    </div>
    <div class="bar suspicious" style="height: ${susHeight}%;">
      <div class="bar-value">${stats.suspicious}</div>
      <div class="bar-label">Suspicious</div>
    </div>
    <div class="bar critical" style="height: ${critHeight}%;">
      <div class="bar-value">${stats.critical}</div>
      <div class="bar-label">Critical</div>
    </div>
  `;
}

function renderActivityList(predictions) {
  const validPredictions = Object.entries(predictions)
    .filter(([url, pred]) => {
      try {
        return new URL(url) && pred && pred.threat_level;
      } catch {
        return false;
      }
    })
    .sort((a, b) => (b[1].savedAt || 0) - (a[1].savedAt || 0))
    .slice(0, 10);

  if (validPredictions.length === 0) {
    return '<div class="no-data">No activity yet. Visit websites to see threats detected here.</div>';
  }

  return validPredictions
    .map(([url, pred]) => `
      <div class="activity-item">
        <div class="activity-url" title="${url}">${truncateUrl(url, 40)}</div>
        <span class="activity-badge ${pred.threat_level}">
          ${pred.threat_level.toUpperCase()}
        </span>
      </div>
    `)
    .join('');
}

// ============================================================================
// ACTIONS
// ============================================================================

async function refreshDashboard() {
  await loadDashboardData();
}

async function clearAllData() {
  if (confirm('⚠️ Are you sure? This will clear all cached threat predictions. This cannot be undone.')) {
    try {
      await chrome.storage.local.set({ predictions: {} });
      await loadDashboardData();
      console.log('✓ All data cleared');
    } catch (error) {
      alert('Error clearing data: ' + error.message);
    }
  }
}

async function exportData() {
  try {
    const data = await chrome.storage.local.get(['predictions']);
    const json = JSON.stringify(data.predictions || {}, null, 2);

    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vulnweb-threats-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    console.log('✓ Data exported');
  } catch (error) {
    alert('Error exporting data: ' + error.message);
  }
}

function showError(message) {
  document.querySelector('.container').innerHTML = `
    <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px; color: #F44336;">
      <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
      <div style="font-size: 18px; margin-bottom: 8px;">Error</div>
      <div style="color: #999; font-size: 14px;">${message}</div>
      <button class="btn btn-primary" onclick="loadDashboardData()" style="margin-top: 16px; max-width: 200px;">Retry</button>
    </div>
  `;
}

// ============================================================================
// UTILITIES
// ============================================================================

function formatTime(timestamp) {
  if (!timestamp) return '--';
  const date = new Date(timestamp);
  return date.toLocaleString();
}

function truncateUrl(url, maxLength = 50) {
  if (url.length <= maxLength) return url;
  return url.substring(0, maxLength - 3) + '...';
}

// ============================================================================
// INITIALIZE
// ============================================================================

document.addEventListener('DOMContentLoaded', loadDashboardData);

// Auto-refresh every 30 seconds
setInterval(loadDashboardData, 30000);
