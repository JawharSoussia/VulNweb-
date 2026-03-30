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