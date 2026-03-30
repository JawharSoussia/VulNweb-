
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
    // Batch predict
    const features = requests.map(r => r.features);
    // In future: send all at once to /api/predict-batch
    return Promise.all(features.map(f => predictSingle(f)));
  }
);

/**
 * Single prediction with timeout
 */
async function predictSingle(features) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000); // 5 second timeout

  try {
    const response = await fetch(`${CONFIG.API_URL}/api/predict-raw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features }),
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('API request timed out after 5 seconds');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
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

    // Generate deterministic features from URL (same URL = same features)
    const features = data.features || generateFeatures(url);

    // Use batcher for efficiency
    const prediction = await requestBatcher.add({ features });

    // Cache result (use standardized cache key)
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
 * Generate deterministic 34 features from URL (same URL = same features)
 */
function generateFeatures(url = '') {
  // Use URL hash to seed feature generation for consistency
  let hash = 0;
  const seed = url || Math.random().toString();

  for (let i = 0; i < seed.length; i++) {
    const char = seed.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }

  // Seeded random function for reproducibility
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