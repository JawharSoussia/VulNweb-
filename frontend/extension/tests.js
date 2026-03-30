/**
 * VulNweb Extension - Comprehensive Test Suite
 *
 * Usage in Chrome Console:
 * 1. Open chrome://extensions
 * 2. Find VulNweb and click "Details"
 * 3. Open any website
 * 4. Open Chrome DevTools (F12)
 * 5. Go to "Sources" tab, find this file or paste code
 * 6. Run individual tests like: await testFeatureGeneration()
 */

// Configuration
const TEST_CONFIG = {
  API_URL: 'http://localhost:8000',
  TEST_URLS: [
    'https://www.google.com',
    'https://www.example.com',
    'https://amazon.com/search?q=laptop',
    'https://suspicious-chars.com/page?file=test.exe',
    'http://192.168.1.1:8080/admin'
  ],
  TIMEOUT: 10000
};

// Test results storage
const testResults = {
  passed: 0,
  failed: 0,
  errors: [],
  logs: []
};

// ============================================================================
// TEST UTILITIES
// ============================================================================

async function log(message, type = 'info') {
  const timestamp = new Date().toISOString().split('T')[1];
  const prefix = type === 'error' ? '❌' : type === 'pass' ? '✅' : 'ℹ️';
  const logEntry = `[${timestamp}] ${prefix} ${message}`;
  console.log(logEntry);
  testResults.logs.push(logEntry);
}

async function assert(condition, message) {
  if (condition) {
    testResults.passed++;
    await log(`PASS: ${message}`, 'pass');
    return true;
  } else {
    testResults.failed++;
    const errorMsg = `FAIL: ${message}`;
    testResults.errors.push(errorMsg);
    await log(errorMsg, 'error');
    return false;
  }
}

function sendMessage(type, data) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type, data }, (response) => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve(response);
      }
    });
  });
}

function getStorage(keys) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get(keys, (result) => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        resolve(result);
      }
    });
  });
}

// ============================================================================
// TEST SUITE
// ============================================================================

async function testFeatureGeneration() {
  await log('=== TEST: Feature Generation ===', 'info');

  const testUrl = 'https://example.com/test?param=value';

  // Feature generation is in background.js, so we'll verify indirectly via API
  try {
    const response = await fetch(`${TEST_CONFIG.API_URL}/api/features`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      await assert(false, 'Failed to fetch feature list');
      return;
    }

    const data = await response.json();
    await assert(data.feature_count === 34, `Feature count is 34 (got ${data.feature_count})`);
    await assert(Array.isArray(data.features), 'Features is an array');
    await log(`Feature names: ${data.features.slice(0, 3).join(', ')}...`, 'info');

  } catch (error) {
    await assert(false, `Feature generation test: ${error.message}`);
  }
}

async function testAPIHealthCheck() {
  await log('=== TEST: API Health Check ===', 'info');

  try {
    const response = await fetch(`${TEST_CONFIG.API_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(TEST_CONFIG.TIMEOUT)
    });

    await assert(response.ok, 'Health check endpoint responds');

    const data = await response.json();
    await assert(data.status !== undefined, 'Health response contains status field');
    await assert(data.model_loaded !== undefined, 'Health response contains model_loaded field');

    if (data.model_loaded) {
      await log('✓ Model is loaded and ready', 'pass');
    } else {
      await log('⚠ Model is not loaded', 'info');
    }

  } catch (error) {
    await assert(false, `API health check: ${error.message}`);
  }
}

async function testRawPredictionEndpoint() {
  await log('=== TEST: Raw Prediction Endpoint ===', 'info');

  try {
    // Generate sample features (simplified)
    const features = Array(34).fill(0).map((_, i) => Math.sin(i) * 10);

    const response = await fetch(`${TEST_CONFIG.API_URL}/api/predict-raw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features }),
      signal: AbortSignal.timeout(TEST_CONFIG.TIMEOUT)
    });

    await assert(response.status === 200 || response.ok, 'Raw prediction endpoint responds');

    if (response.ok) {
      const data = await response.json();

      await assert(data.threat_score !== undefined, 'Response contains threat_score');
      await assert(data.threat_level !== undefined, 'Response contains threat_level');
      await assert(data.confidence !== undefined, 'Response contains confidence');
      await assert(data.explanation !== undefined, 'Response contains explanation');
      await assert(Array.isArray(data.explanation), 'Explanation is an array');

      // Validate ranges
      await assert(data.threat_score >= 0 && data.threat_score <= 100, 'Threat score is 0-100');
      await assert(data.confidence >= 0 && data.confidence <= 1, 'Confidence is 0-1');
      await assert(['safe', 'suspicious', 'critical'].includes(data.threat_level), 'Threat level is valid');

      await log(`Sample prediction: ${data.threat_level} (${data.threat_score.toFixed(1)}%)`, 'pass');
    }

  } catch (error) {
    await assert(false, `Raw prediction test: ${error.message}`);
  }
}

async function testCacheStorage() {
  await log('=== TEST: Cache Storage ===', 'info');

  try {
    // Clear cache
    await new Promise(resolve => {
      chrome.storage.local.set({ predictions: {} }, resolve);
    });

    // Store test prediction
    const testPrediction = {
      'https://test1.com': {
        threat_level: 'safe',
        threat_score: 10,
        confidence: 0.95,
        explanation: ['test'],
        savedAt: Date.now()
      },
      'https://test2.com': {
        threat_level: 'critical',
        threat_score: 90,
        confidence: 0.98,
        explanation: ['test'],
        savedAt: Date.now()
      }
    };

    await new Promise(resolve => {
      chrome.storage.local.set({ predictions: testPrediction }, resolve);
    });

    // Verify storage
    const stored = await getStorage(['predictions']);
    await assert(stored.predictions !== undefined, 'Predictions stored in chrome.storage');
    await assert(Object.keys(stored.predictions).length === 2, 'Correct number of predictions stored');
    await assert(stored.predictions['https://test1.com'] !== undefined, 'First prediction accessible');

    // Verify data integrity
    await assert(
      stored.predictions['https://test1.com'].threat_level === 'safe',
      'Threat level preserved correctly'
    );

    await log(`Stored ${Object.keys(stored.predictions).length} test predictions`, 'pass');

  } catch (error) {
    await assert(false, `Cache storage test: ${error.message}`);
  }
}

async function testStatisticsCalculation() {
  await log('=== TEST: Statistics Calculation ===', 'info');

  try {
    // Set up test data
    const testData = {
      predictions: {
        'https://safe1.com': { threat_level: 'safe', savedAt: Date.now() },
        'https://safe2.com': { threat_level: 'safe', savedAt: Date.now() },
        'https://suspicious1.com': { threat_level: 'suspicious', savedAt: Date.now() },
        'https://critical1.com': { threat_level: 'critical', savedAt: Date.now() },
      }
    };

    await new Promise(resolve => {
      chrome.storage.local.set(testData, resolve);
    });

    // Get stats via background worker
    const stats = await sendMessage('GET_STATS', {});

    await assert(stats.totalChecked === 4, `Total checked is 4 (got ${stats.totalChecked})`);
    await assert(stats.threatsFound === 2, `Threats found is 2 (got ${stats.threatsFound})`);
    await assert(stats.criticalThreats === 1, `Critical threats is 1 (got ${stats.criticalThreats})`);

    await log(`Stats: ${stats.totalChecked} checked, ${stats.threatsFound} threats, ${stats.criticalThreats} critical`, 'pass');

  } catch (error) {
    await assert(false, `Statistics calculation test: ${error.message}`);
  }
}

async function testMessagePassing() {
  await log('=== TEST: Message Passing ===', 'info');

  try {
    // Test GET_STATS message
    const stats = await sendMessage('GET_STATS', {});
    await assert(stats !== undefined, 'GET_STATS message returns response');
    await assert(stats.totalChecked !== undefined, 'Stats response contains totalChecked');

    // Test CLEAR_CACHE message
    const clearResponse = await sendMessage('CLEAR_CACHE', {});
    await assert(clearResponse.status === 'cleared', 'CLEAR_CACHE message works');

    await log('Message passing functional', 'pass');

  } catch (error) {
    await assert(false, `Message passing test: ${error.message}`);
  }
}

async function testErrorHandling() {
  await log('=== TEST: Error Handling ===', 'info');

  try {
    // Test 1: Invalid feature count (should fail gracefully)
    try {
      const response = await fetch(`${TEST_CONFIG.API_URL}/api/predict-raw`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features: [1, 2, 3] }), // Only 3 instead of 34
        signal: AbortSignal.timeout(5000)
      });

      await assert(response.status === 400, 'Invalid feature count returns 400');
    } catch (e) {
      await assert(false, `Invalid feature test failed: ${e.message}`);
    }

    // Test 2: Timeout handling
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 100); // Very short timeout

      const response = await fetch(`${TEST_CONFIG.API_URL}/api/predict-raw`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features: Array(34).fill(1) }),
        signal: controller.signal
      });

      clearTimeout(timeout);
      await assert(false, 'Should have timed out');
    } catch (error) {
      await assert(error.name === 'AbortError', 'Timeout is handled as AbortError');
    }

    await log('Error handling verified', 'pass');

  } catch (error) {
    await assert(false, `Error handling test: ${error.message}`);
  }
}

async function testContentScriptIntegration() {
  await log('=== TEST: Content Script Integration ===', 'info');

  try {
    // Verify content script is running
    const links = document.querySelectorAll('a[href]');
    await assert(links.length > 0, `Found ${links.length} links on page`);

    // Check if any links have threat indicators
    const indicators = document.querySelectorAll('.vulnweb-threat-indicator');
    await log(`Found ${indicators.length} threat indicators on page`, 'info');

    if (indicators.length > 0) {
      // Check indicator styling
      const firstIndicator = indicators[0];
      const bgColor = window.getComputedStyle(firstIndicator).backgroundColor;
      await assert(bgColor !== '', 'Threat indicator has background color');
    }

    await log('Content script integration verified', 'pass');

  } catch (error) {
    await assert(false, `Content script integration test: ${error.message}`);
  }
}

// ============================================================================
// TEST RUNNER
// ============================================================================

async function runAllTests() {
  console.clear();
  console.log('🧪 VulNweb Extension Test Suite');
  console.log('================================\n');

  testResults.passed = 0;
  testResults.failed = 0;
  testResults.errors = [];
  testResults.logs = [];

  const startTime = performance.now();

  try {
    // Run all tests
    await testAPIHealthCheck();
    console.log('');
    await testFeatureGeneration();
    console.log('');
    await testRawPredictionEndpoint();
    console.log('');
    await testCacheStorage();
    console.log('');
    await testStatisticsCalculation();
    console.log('');
    await testMessagePassing();
    console.log('');
    await testErrorHandling();
    console.log('');
    await testContentScriptIntegration();

  } catch (error) {
    await log(`Test suite error: ${error.message}`, 'error');
  }

  const endTime = performance.now();
  const duration = (endTime - startTime) / 1000;

  // Print summary
  console.log('\n================================');
  console.log('📊 TEST SUMMARY');
  console.log('================================');
  console.log(`✅ Passed: ${testResults.passed}`);
  console.log(`❌ Failed: ${testResults.failed}`);
  console.log(`⏱️  Duration: ${duration.toFixed(2)}s`);
  console.log(`📝 Total Tests: ${testResults.passed + testResults.failed}`);

  if (testResults.failed === 0) {
    console.log('\n🎉 All tests passed!');
  } else {
    console.log('\n⚠️  Some tests failed:');
    testResults.errors.forEach(error => console.log(`  - ${error}`));
  }

  // Export results
  return {
    passed: testResults.passed,
    failed: testResults.failed,
    errors: testResults.errors,
    duration: duration.toFixed(2),
    timestamp: new Date().toISOString()
  };
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { runAllTests };
}

console.log('✅ Test suite loaded. Run: await runAllTests()');
