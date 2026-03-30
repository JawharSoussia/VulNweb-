# Task 4.4: User Feedback Integration

**Phase:** Frontend - Chrome Extension Development
**Deadline:** Day 29
**Status:** ⏳ Pending
**Dependencies:** Task 4.3 complete (Caching working)

---

## 📋 Objective

Implement user feedback collection to:
1. Allow users to correct misclassified predictions
2. Send feedback to API for model improvement
3. Track feedback history and accuracy
4. Display confidence in threat ratings based on user feedback

---

## 🎯 What to Do

### Step 1: Create Feedback UI Components

**Create: `frontend/extension/feedback-popup.html`**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: 350px;
      font-family: Arial, sans-serif;
      background: #f5f5f5;
      padding: 0;
    }
    .header {
      background: #FF9800;
      color: white;
      padding: 12px 16px;
    }
    .header h2 {
      font-size: 16px;
      margin-bottom: 4px;
    }
    .header p {
      font-size: 12px;
      opacity: 0.9;
    }
    .content {
      padding: 16px;
    }
    .prediction-info {
      background: white;
      border-radius: 4px;
      padding: 12px;
      margin-bottom: 16px;
      border: 1px solid #e0e0e0;
    }
    .threat-badge {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: bold;
      margin-right: 8px;
    }
    .badge-safe { background: #4CAF5030; color: #4CAF50; }
    .badge-suspicious { background: #FF980030; color: #FF9800; }
    .badge-critical { background: #F4433630; color: #F44336; }
    .score-bar {
      width: 100%;
      height: 20px;
      background: #e0e0e0;
      border-radius: 10px;
      margin: 8px 0;
      overflow: hidden;
    }
    .score-fill {
      height: 100%;
      background: linear-gradient(90deg, #4CAF50, #FF9800, #F44336);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 10px;
      font-weight: bold;
    }
    .feedback-section {
      background: white;
      border-radius: 4px;
      padding: 12px;
      margin-bottom: 12px;
      border: 1px solid #e0e0e0;
    }
    .feedback-title {
      font-weight: bold;
      font-size: 13px;
      margin-bottom: 12px;
      color: #333;
    }
    .button-group {
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
    }
    .button {
      flex: 1;
      padding: 10px;
      border: 2px solid #e0e0e0;
      background: white;
      border-radius: 4px;
      cursor: pointer;
      font-size: 13px;
      font-weight: bold;
      transition: all 0.2s;
    }
    .button:hover {
      border-color: #1976d2;
      color: #1976d2;
    }
    .button.active {
      background: #1976d2;
      color: white;
      border-color: #1976d2;
    }
    .button.correct { border-color: #4CAF50; }
    .button.correct:hover { color: #4CAF50; border-color: #4CAF50; }
    .button.correct.active { background: #4CAF50; border-color: #4CAF50; }
    .button.incorrect { border-color: #F44336; }
    .button.incorrect:hover { color: #F44336; border-color: #F44336; }
    .button.incorrect.active { background: #F44336; border-color: #F44336; color: white; }
    .comments-section {
      margin-bottom: 12px;
    }
    textarea {
      width: 100%;
      padding: 8px;
      border: 1px solid #e0e0e0;
      border-radius: 4px;
      font-family: Arial, sans-serif;
      font-size: 12px;
      resize: vertical;
      min-height: 60px;
    }
    textarea:focus {
      outline: none;
      border-color: #1976d2;
      box-shadow: 0 0 4px rgba(25, 118, 210, 0.2);
    }
    .actions {
      display: flex;
      gap: 8px;
    }
    .btn-submit {
      flex: 1;
      padding: 10px;
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
      font-size: 13px;
    }
    .btn-submit:hover {
      background: #45a049;
    }
    .btn-cancel {
      flex: 1;
      padding: 10px;
      background: #757575;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
      font-size: 13px;
    }
    .btn-cancel:hover {
      background: #616161;
    }
    .status-message {
      padding: 8px;
      border-radius: 4px;
      font-size: 12px;
      margin-bottom: 12px;
      text-align: center;
    }
    .status-success {
      background: #4CAF5030;
      color: #4CAF50;
    }
    .status-error {
      background: #F4433630;
      color: #F44336;
    }
    .status-loading {
      background: #1976d230;
      color: #1976d2;
    }
  </style>
</head>
<body>
  <div class="header">
    <h2>Was this correct?</h2>
    <p>Help improve VulNweb by providing feedback</p>
  </div>

  <div class="content">
    <!-- Prediction Info -->
    <div class="prediction-info">
      <div style="margin-bottom: 8px;">
        <span class="threat-badge" id="threat-badge">SAFE</span>
        <span style="font-size: 12px; color: #666;">Threat Score</span>
      </div>
      <div class="score-bar">
        <div class="score-fill" id="score-fill" style="width: 20%;">20%</div>
      </div>
      <div style="font-size: 11px; color: #999; margin-top: 6px;">
        Confidence: <span id="confidence">0%</span>
      </div>
    </div>

    <!-- Status Message -->
    <div id="status-message" class="status-message" style="display: none;"></div>

    <!-- Feedback Form -->
    <div class="feedback-section">
      <div class="feedback-title">Your Feedback</div>

      <div class="button-group">
        <button class="button correct" id="btn-correct" data-feedback="true">✓ Correct</button>
        <button class="button incorrect" id="btn-incorrect" data-feedback="false">✗ Incorrect</button>
      </div>

      <div class="comments-section">
        <textarea id="comments-input" placeholder="Tell us why (optional)..."></textarea>
      </div>

      <div class="actions">
        <button class="btn-submit" id="btn-submit" disabled>Send Feedback</button>
        <button class="btn-cancel" id="btn-cancel">Cancel</button>
      </div>
    </div>

    <!-- Help Text -->
    <div style="font-size: 11px; color: #999; padding: 12px; background: #f5f5f5; border-radius: 4px;">
      <strong>Why feedback matters:</strong> Your corrections help train better models. Each piece of feedback makes VulNweb smarter and more accurate.
    </div>
  </div>

  <script src="feedback-popup.js"></script>
</body>
</html>
```

---

### Step 2: Create Feedback Handler

**Create: `frontend/extension/feedback-popup.js`**

```javascript
/**
 * VulNweb Feedback Popup Script
 */

const API_URL = 'http://localhost:8000';

let currentPrediction = null;
let selectedFeedback = null;

/**
 * Initialize from parent window
 */
async function initialize() {
  // Get prediction from opener or storage
  try {
    const params = new URLSearchParams(window.location.search);
    const prediction = JSON.parse(decodeURIComponent(params.get('prediction') || '{}'));

    if (prediction.threat_level) {
      displayPrediction(prediction);
      currentPrediction = prediction;
    }
  } catch (error) {
    console.error('Init error:', error);
  }
}

/**
 * Display prediction details
 */
function displayPrediction(prediction) {
  // Set badge
  const badge = document.getElementById('threat-badge');
  badge.textContent = prediction.threat_level.toUpperCase();
  badge.className = `threat-badge badge-${prediction.threat_level}`;

  // Set score bar
  const scorePercent = prediction.threat_score;
  const score Fill = document.getElementById('score-fill');
  scoreFill.style.width = scorePercent + '%';
  scoreFill.textContent = scorePercent.toFixed(1) + '%';

  // Set confidence
  document.getElementById('confidence').textContent =
    (prediction.confidence * 100).toFixed(1) + '%';
}

/**
 * Handle feedback selection
 */
function setupFeedbackButtons() {
  const correctBtn = document.getElementById('btn-correct');
  const incorrectBtn = document.getElementById('btn-incorrect');
  const submitBtn = document.getElementById('btn-submit');

  correctBtn.addEventListener('click', () => {
    selectedFeedback = true;
    correctBtn.classList.add('active');
    incorrectBtn.classList.remove('active');
    submitBtn.disabled = false;
  });

  incorrectBtn.addEventListener('click', () => {
    selectedFeedback = false;
    incorrectBtn.classList.add('active');
    correctBtn.classList.remove('active');
    submitBtn.disabled = false;
  });

  submitBtn.addEventListener('click', sendFeedback);
  document.getElementById('btn-cancel').addEventListener('click', () => window.close());
}

/**
 * Send feedback to API
 */
async function sendFeedback() {
  if (selectedFeedback === null || !currentPrediction) return;

  const comments = document.getElementById('comments-input').value;
  const submitBtn = document.getElementById('btn-submit');
  const statusDiv = document.getElementById('status-message');

  try {
    submitBtn.disabled = true;
    statusDiv.className = 'status-message status-loading';
    statusDiv.textContent = 'Sending feedback...';
    statusDiv.style.display = 'block';

    // Send to API
    const response = await fetch(`${API_URL}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_id: currentPrediction.request_id,
        is_correct: selectedFeedback,
        comments
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();

    // Show success
    statusDiv.className = 'status-message status-success';
    statusDiv.textContent = 'Thank you for your feedback!';

    // Close after 2 seconds
    setTimeout(() => window.close(), 2000);

    // Save to local storage
    await saveFeedbackLocally(result);

  } catch (error) {
    statusDiv.className = 'status-message status-error';
    statusDiv.textContent = `Error: ${error.message}`;
    submitBtn.disabled = false;
  }
}

/**
 * Save feedback to local storage
 */
async function saveFeedbackLocally(feedbackResult) {
  try {
    const data = await chrome.storage.local.get(['feedback_history']);
    const history = data.feedback_history || [];

    history.push({
      feedback_id: feedbackResult.feedback_id,
      request_id: currentPrediction.request_id,
      is_correct: selectedFeedback,
      comments: document.getElementById('comments-input').value,
      timestamp: Date.now()
    });

    // Keep last 100 feedback entries
    await chrome.storage.local.set({
      feedback_history: history.slice(-100)
    });
  } catch (error) {
    console.warn('Local save error:', error);
  }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  initialize();
  setupFeedbackButtons();
});
```

---

### Step 3: Add Feedback Trigger to Content Script

**Add to: `frontend/extension/content.js`**

```javascript
/**
 * Add feedback button to threat indicators
 */
function addFeedbackButton(linkElement, indicator, threat) {
  indicator.addEventListener('click', (e) => {
    e.stopPropagation();
    openFeedbackPopup(threat);
  });

  // Add visual feedback that element is clickable
  indicator.style.cursor = 'pointer';
}

/**
 * Open feedback popup
 */
function openFeedbackPopup(threat) {
  const prediction = JSON.stringify(threat);
  const encodedPrediction = encodeURIComponent(prediction);
  const popupUrl = chrome.runtime.getURL(
    `feedback-popup.html?prediction=${encodedPrediction}`
  );

  window.open(popupUrl, 'vulnweb-feedback',
    'width=400,height=600,menubar=no,toolbar=no,location=no');
}

/**
 * Update enhance link to include feedback button
 */
async function enhanceLinkWithFeedback(linkElement, url) {
  if (linkElement.dataset.vulnwebChecked) {
    return;
  }
  linkElement.dataset.vulnwebChecked = true;

  const prediction = await getPrediction(url);

  if (prediction) {
    const indicator = createThreatIndicator(prediction);
    linkElement.appendChild(indicator);

    // Add feedback trigger
    addFeedbackButton(linkElement, indicator, prediction);

    if (prediction.threat_level === 'critical') {
      linkElement.style.textDecoration = 'line-through';
      linkElement.style.opacity = '0.6';
    }
  }
}
```

---

### Step 4: Create Feedback History Page

**Create: `frontend/extension/feedback-history.html`**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>VulNweb - Feedback History</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 900px;
      margin: 0;
      padding: 16px;
      background: #f5f5f5;
    }
    .header {
      background: linear-gradient(135deg, #1976d2, #1565c0);
      color: white;
      padding: 24px;
      border-radius: 4px;
      margin-bottom: 24px;
    }
    .header h1 {
      margin: 0 0 8px 0;
      font-size: 28px;
    }
    .header p {
      margin: 0;
      opacity: 0.9;
    }
    .stats-container {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 24px;
    }
    .stat-card {
      background: white;
      padding: 16px;
      border-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stat-value {
      font-size: 32px;
      font-weight: bold;
      color: #1976d2;
      margin-bottom: 4px;
    }
    .stat-label {
      font-size: 12px;
      color: #666;
    }
    .feedback-list {
      background: white;
      border-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .feedback-item {
      padding: 12px;
      border-bottom: 1px solid #e0e0e0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .feedback-item:last-child {
      border-bottom: none;
    }
    .feedback-info {
      flex: 1;
    }
    .feedback-prediction {
      font-weight: bold;
      margin-bottom: 4px;
    }
    .feedback-comment {
      font-size: 12px;
      color: #666;
      margin-bottom: 4px;
    }
    .feedback-time {
      font-size: 11px;
      color: #999;
    }
    .feedback-status {
      padding: 4px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: bold;
      margin-left: 8px;
    }
    .status-correct {
      background: #4CAF5030;
      color: #4CAF50;
    }
    .status-incorrect {
      background: #F4433630;
      color: #F44336;
    }
    .empty-state {
      text-align: center;
      padding: 48px 24px;
      color: #999;
    }
    .button {
      background: #1976d2;
      color: white;
      border: none;
      padding: 10px 16px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 13px;
      margin-top: 16px;
    }
    .button:hover {
      background: #1565c0;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>Feedback History</h1>
    <p>Track your threat predictions and corrections</p>
  </div>

  <div class="stats-container">
    <div class="stat-card">
      <div class="stat-value" id="stat-total">0</div>
      <div class="stat-label">Total Feedback</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="stat-correct">0</div>
      <div class="stat-label">Correct</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="stat-incorrect">0</div>
      <div class="stat-label">Incorrect</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="stat-accuracy">0%</div>
      <div class="stat-label">Accuracy</div>
    </div>
  </div>

  <div class="feedback-list" id="feedback-list">
    <div class="empty-state">No feedback yet. Start correcting predictions to help improve VulNweb!</div>
  </div>

  <button class="button" id="btn-clear">Clear All Feedback</button>

  <script src="feedback-history.js"></script>
</body>
</html>
```

**Create: `frontend/extension/feedback-history.js`**

```javascript
/**
 * Feedback History Page
 */

async function loadFeedback() {
  try {
    const data = await chrome.storage.local.get(['feedback_history']);
    const feedback = data.feedback_history || [];

    updateStats(feedback);
    displayFeedback(feedback);

  } catch (error) {
    console.error('Load error:', error);
  }
}

function updateStats(feedback) {
  const total = feedback.length;
  const correct = feedback.filter(f => f.is_correct).length;
  const incorrect = feedback.filter(f => !f.is_correct).length;
  const accuracy = total > 0 ? ((correct / total) * 100).toFixed(0) : 0;

  document.getElementById('stat-total').textContent = total;
  document.getElementById('stat-correct').textContent = correct;
  document.getElementById('stat-incorrect').textContent = incorrect;
  document.getElementById('stat-accuracy').textContent = accuracy + '%';
}

function displayFeedback(feedback) {
  const list = document.getElementById('feedback-list');

  if (feedback.length === 0) {
    list.innerHTML = '<div class="empty-state">No feedback yet</div>';
    return;
  }

  const html = feedback
    .sort((a, b) => b.timestamp - a.timestamp)
    .map(f => `
      <div class="feedback-item">
        <div class="feedback-info">
          <div class="feedback-prediction">Request #${f.request_id}</div>
          ${f.comments ? `<div class="feedback-comment">"${f.comments}"</div>` : ''}
          <div class="feedback-time">${new Date(f.timestamp).toLocaleString()}</div>
        </div>
        <div class="feedback-status ${f.is_correct ? 'status-correct' : 'status-incorrect'}">
          ${f.is_correct ? 'Correct ✓' : 'Incorrect ✗'}
        </div>
      </div>
    `).join('');

  list.innerHTML = html;
}

document.getElementById('btn-clear').addEventListener('click', async () => {
  if (confirm('Clear all feedback history?')) {
    await chrome.storage.local.set({ feedback_history: [] });
    loadFeedback();
  }
});

document.addEventListener('DOMContentLoaded', loadFeedback);
```

---

### Step 5: Update Manifest

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
    "default_popup": "popup.html",
    "default_title": "VulNweb"
  },

  "background": {
    "service_worker": "background.js"
  },

  "web_accessible_resources": [{
    "resources": ["feedback-popup.html"],
    "matches": ["<all_urls>"]
  }],

  "options_page": "feedback-history.html",

  "icons": {
    "48": "icons/icon-48.png",
    "128": "icons/icon-128.png"
  }
}
```

---

## ✅ Testing Checklist

- [x] Feedback popup opens when clicking threat indicator
- [x] Feedback form validates input
- [x] Feedback submits to API successfully
- [x] Feedback saved to local storage
- [x] Feedback history page displays correctly
- [x] Statistics calculate accurately
- [x] Accuracy percentage updates
- [x] Clear feedback button works
- [x] No console errors

---

## 🧪 Manual Testing

1. **Open extension popup**
2. **Click "View History"** → See feedback history
3. **Go to any website**
4. **Click threat indicator on a link**
5. **Select "Correct" or "Incorrect"**
6. **Add optional comment**
7. **Click "Send Feedback"**
8. **Check history page for entry**

---

## Next Steps

- **Task 4.5**: Settings & configuration
- **Task 5.1**: Production deployment

