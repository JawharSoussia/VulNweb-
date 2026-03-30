/**
 * VulNweb Cache Manager
 * Handles all caching operations (memory, storage, sync)
 */

class CacheManager {
  constructor() {
    this.memoryCache = new Map();
    this.maxMemorySize = 100;
    this.storageKey = 'vulnweb_predictions';
  }

  /**
   * Get from cache (check memory first, then storage)
   */
  async get(key) {
    // Check memory cache first
    if (this.memoryCache.has(key)) {
      return this.memoryCache.get(key);
    }

    // Check persistent storage
    try {
      const data = await chrome.storage.local.get([this.storageKey]);
      const predictions = data[this.storageKey] || {};
      if (predictions[key]) {
        // Move to memory cache
        this.memoryCache.set(key, predictions[key]);
        return predictions[key];
      }
    } catch (error) {
      console.warn('[Cache] Storage read error:', error);
    }

    return null;
  }

  /**
   * Set cache entry
   */
  async set(key, value) {
    // Save to memory
    this.memoryCache.set(key, value);

    // Evict oldest if memory cache too large
    if (this.memoryCache.size > this.maxMemorySize) {
      const firstKey = this.memoryCache.keys().next().value;
      this.memoryCache.delete(firstKey);
    }

    // Save to persistent storage
    try {
      const data = await chrome.storage.local.get([this.storageKey]);
      const predictions = data[this.storageKey] || {};
      predictions[key] = value;

      // Keep only last 100
      const sorted = Object.entries(predictions)
        .sort((a, b) => (b[1].timestamp || 0) - (a[1].timestamp || 0))
        .slice(0, 100);

      await chrome.storage.local.set({
        [this.storageKey]: Object.fromEntries(sorted)
      });
    } catch (error) {
      console.warn('[Cache] Storage write error:', error);
    }
  }

  /**
   * Clear all caches
   */
  async clear() {
    this.memoryCache.clear();
    try {
      await chrome.storage.local.set({ [this.storageKey]: {} });
    } catch (error) {
      console.warn('[Cache] Clear error:', error);
    }
  }

  /**
   * Get cache statistics
   */
  async getStats() {
    const data = await chrome.storage.local.get([this.storageKey]);
    const predictions = data[this.storageKey] || {};

    return {
      memorySize: this.memoryCache.size,
      storageSize: Object.keys(predictions).length,
      threats: Object.values(predictions).filter(p => p.threat_level !== 'safe').length,
      critical: Object.values(predictions).filter(p => p.threat_level === 'critical').length
    };
  }
}

// Export singleton
const cacheManager = new CacheManager();