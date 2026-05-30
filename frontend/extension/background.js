
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

    // If there are more items in queue, set timer for next batch
    if (this.queue.length > 0 && !this.timer) {
      this.timer = setTimeout(() => this.flush(), this.timeout);
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
    // Batch predict with URLs
    const urls = requests.map(r => r.url);
    return Promise.all(urls.map(u => predictSingle(u)));
  }
);

/**
 * Single prediction with timeout and enhanced error handling
 */
async function predictSingle(url, retryCount = 0) {
  const MAX_RETRIES = 2;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000); // 5 second timeout

  try {
    const response = await fetch(`${CONFIG.API_URL}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
      signal: controller.signal
    });

    clearTimeout(timeout);

    // Handle HTTP status codes
    if (response.status === 429) {
      // Rate limited - retry with backoff
      if (retryCount < MAX_RETRIES) {
        const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff: 1s, 2s, 4s
        console.warn(`[VulNweb BG] Rate limited (429). Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return predictSingle(url, retryCount + 1);
      }
      throw new Error('API rate limited - too many requests');
    }

    if (response.status === 503) {
      throw new Error('API service unavailable (model loading/error)');
    }

    if (response.status === 502 || response.status === 503 || response.status === 504) {
      throw new Error('API server error - service temporarily unavailable');
    }

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`API returned ${response.status}: ${errorBody.substring(0, 100)}`);
    }

    return response.json();

  } catch (error) {
    clearTimeout(timeout);

    // Handle specific error types
    if (error.name === 'AbortError') {
      throw new Error('API request timed out after 5 seconds');
    }

    if (error instanceof TypeError) {
      // Network error (DNS resolution failed, connection refused, etc.)
      if (error.message.includes('fetch')) {
        throw new Error(`Network error: Cannot reach API at ${CONFIG.API_URL}. Is the backend running?`);
      }
      throw new Error(`Network error: ${error.message}`);
    }

    // Re-throw other errors
    throw error;
  }
}

/**
 * Check threat with caching
 */
async function checkThreat(data, sender) {
  const url = data.url || sender.url;
  const cacheKey = `prediction_${url}`;

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

    // Use batcher for efficiency (let backend extract features from URL)
    let prediction;
    try {
      prediction = await requestBatcher.add({ url });
    } catch (batchError) {
      // If batching fails, try direct prediction with user feedback
      console.warn('[VulNweb BG] Batch processing failed, attempting direct prediction:', batchError.message);
      prediction = await predictSingle(url);
    }

    // Cache result (use standardized cache key)
    predictionCache.set(cacheKey, {
      data: prediction,
      timestamp: Date.now()
    });

    // Persist to storage
    await saveToStorage(url, prediction);

    // Send notification if enabled
    await sendNotification(prediction, url);

    console.log('[VulNweb BG] Prediction:', url, prediction.threat_level);
    return prediction;

  } catch (error) {
    console.error('[VulNweb BG] Error:', error);

    // Return a safe default error response instead of throwing
    // This prevents the content script from breaking
    const errorResponse = {
      threat_level: 'unknown',
      threat_score: 0,
      confidence: 0,
      explanation: [error.message],
      predicted_class: -1,
      probabilities: {},
      model_version: 'error',
      request_id: 'error',
      timestamp: new Date().toISOString(),
      error: error.message
    };

    throw errorResponse;
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
 * Send browser notification for threats
 */
async function sendNotification(prediction, url) {
  try {
    // Get notification settings from options
    const settings = await chrome.storage.sync.get(['enableNotifications', 'notificationLevel']);

    if (settings.enableNotifications === false) {
      return; // Notifications disabled
    }

    // Determine if we should notify based on threat level
    const notificationLevel = settings.notificationLevel || 'critical'; // 'safe', 'suspicious', 'critical'

    const shouldNotify =
      (notificationLevel === 'critical' && prediction.threat_level === 'critical') ||
      (notificationLevel === 'suspicious' && ['suspicious', 'critical'].includes(prediction.threat_level)) ||
      (notificationLevel === 'all' && prediction.threat_level !== 'safe');

    if (!shouldNotify) {
      return;
    }

    // Create notification
    const notification = {
      type: 'basic',
      title: `🚨 VulNweb: ${prediction.threat_level.toUpperCase()} Threat Detected`,
      message: `Threat Score: ${prediction.threat_score.toFixed(0)}%`,
      iconUrl: '/icons/icon-128.png',
      priority: prediction.threat_level === 'critical' ? 2 : 1,
      silent: false
    };

    // Send notification
    const notificationId = `vulnweb_${Date.now()}`;
    chrome.notifications.create(notificationId, notification, (id) => {
      console.log(`[VulNweb BG] Notification sent: ${id}`);
    });

    // Auto-clear notification after 10 seconds
    setTimeout(() => {
      chrome.notifications.clear(notificationId);
    }, 10000);

  } catch (error) {
    console.warn('[VulNweb BG] Notification error:', error);
  }
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
      .catch(error => {
        const errorMsg = error?.message || error?.error || String(error);
        sendResponse({ error: errorMsg, threat_level: 'unknown', threat_score: 0, confidence: 0 });
      });
    return true;
  }

  if (request.type === 'GET_STATS') {
    getStats()
      .then(stats => sendResponse(stats))
      .catch(error => {
        const errorMsg = error?.message || String(error);
        sendResponse({ error: errorMsg });
      });
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