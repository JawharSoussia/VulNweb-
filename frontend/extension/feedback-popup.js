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