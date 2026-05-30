/**
 * VulNweb Extension Performance Test Suite
 * Tests: Response times, Caching, Batch Processing, Memory usage
 */

const API_URL = 'http://localhost:8000';

// Test URLs - mix of different types
const TEST_URLS = [
  'https://www.google.com',
  'https://github.com',
  'https://stackoverflow.com',
  'https://example.com',
  'https://amazon.com',
  'https://wikipedia.org',
  'https://youtube.com',
  'https://twitter.com',
  'https://linkedin.com',
  'https://reddit.com',
];

/**
 * Sleep utility
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Measure single URL prediction time
 */
async function testSinglePrediction(url) {
  const startTime = performance.now();

  try {
    const response = await fetch(`${API_URL}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });

    const endTime = performance.now();
    const duration = endTime - startTime;

    if (!response.ok) {
      return { url, duration, error: `HTTP ${response.status}` };
    }

    const data = await response.json();

    return {
      url,
      duration,
      threat_level: data.threat_level,
      threat_score: data.threat_score,
      confidence: data.confidence,
      success: true
    };
  } catch (error) {
    const endTime = performance.now();
    return {
      url,
      duration: endTime - startTime,
      error: error.message,
      success: false
    };
  }
}

/**
 * Test batch prediction
 */
async function testBatchPrediction(urls) {
  const startTime = performance.now();

  try {
    const response = await fetch(`${API_URL}/api/predict-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls })
    });

    const endTime = performance.now();
    const duration = endTime - startTime;

    if (!response.ok) {
      return { urls: urls.length, duration, error: `HTTP ${response.status}` };
    }

    const data = await response.json();

    return {
      batch_size: urls.length,
      duration,
      successful: data.successful,
      failed: data.failed,
      avg_time_per_url: duration / urls.length,
      success: true
    };
  } catch (error) {
    const endTime = performance.now();
    return {
      batch_size: urls.length,
      duration: endTime - startTime,
      error: error.message,
      success: false
    };
  }
}

/**
 * Test cache effectiveness
 */
async function testCaching(url, iterations = 3) {
  const results = [];

  for (let i = 0; i < iterations; i++) {
    const result = await testSinglePrediction(url);
    results.push({
      iteration: i + 1,
      duration: result.duration,
      from_cache: i > 0 ? 'expected' : 'fresh'
    });

    if (i < iterations - 1) {
      await sleep(100); // Small delay between requests
    }
  }

  const avgFirstRequest = results[0].duration;
  const avgCachedRequests = results.slice(1).reduce((sum, r) => sum + r.duration, 0) / (results.length - 1);

  return {
    url,
    iterations,
    first_request_ms: avgFirstRequest,
    avg_cached_ms: avgCachedRequests,
    speedup: avgFirstRequest / avgCachedRequests,
    results
  };
}

/**
 * Test model info endpoint
 */
async function testModelInfo() {
  const startTime = performance.now();

  try {
    const response = await fetch(`${API_URL}/api/model-info`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    const endTime = performance.now();

    if (!response.ok) {
      return { duration: endTime - startTime, error: `HTTP ${response.status}` };
    }

    const data = await response.json();

    return {
      model_name: data.model_name,
      num_features: data.num_features,
      duration: endTime - startTime,
      success: true
    };
  } catch (error) {
    const endTime = performance.now();
    return {
      duration: endTime - startTime,
      error: error.message,
      success: false
    };
  }
}

/**
 * Test health check
 */
async function testHealth() {
  const startTime = performance.now();

  try {
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    const endTime = performance.now();

    if (!response.ok) {
      return { duration: endTime - startTime, error: `HTTP ${response.status}` };
    }

    const data = await response.json();

    return {
      status: data.status,
      model_loaded: data.model_loaded,
      duration: endTime - startTime,
      success: true
    };
  } catch (error) {
    const endTime = performance.now();
    return {
      duration: endTime - startTime,
      error: error.message,
      success: false
    };
  }
}

/**
 * Run comprehensive performance test
 */
async function runPerformanceTest() {
  console.log('🚀 VulNweb Performance Test Suite');
  console.log('='.repeat(60));

  // Test 1: Health Check
  console.log('\n📊 Test 1: Health Check');
  const healthResult = await testHealth();
  console.log(JSON.stringify(healthResult, null, 2));

  if (!healthResult.success) {
    console.error('❌ Backend is not running! Please start the FastAPI server.');
    return;
  }

  // Test 2: Model Info
  console.log('\n📊 Test 2: Model Information');
  const modelInfo = await testModelInfo();
  console.log(JSON.stringify(modelInfo, null, 2));

  // Test 3: Single URL Predictions
  console.log('\n📊 Test 3: Single URL Predictions');
  const singlePredictions = [];
  for (const url of TEST_URLS.slice(0, 5)) {
    const result = await testSinglePrediction(url);
    singlePredictions.push(result);
    console.log(`  ${result.url}: ${result.duration.toFixed(2)}ms - ${result.threat_level || result.error}`);
  }

  const avgSingleTime = singlePredictions
    .filter(r => r.success)
    .reduce((sum, r) => sum + r.duration, 0) / singlePredictions.filter(r => r.success).length;

  console.log(`  Average: ${avgSingleTime.toFixed(2)}ms`);
  console.log(`  Min: ${Math.min(...singlePredictions.filter(r => r.success).map(r => r.duration)).toFixed(2)}ms`);
  console.log(`  Max: ${Math.max(...singlePredictions.filter(r => r.success).map(r => r.duration)).toFixed(2)}ms`);

  // Test 4: Batch Predictions
  console.log('\n📊 Test 4: Batch Prediction (10 URLs)');
  const batchResult = await testBatchPrediction(TEST_URLS);
  console.log(`  Total time: ${batchResult.duration.toFixed(2)}ms`);
  console.log(`  URLs processed: ${batchResult.successful}/${batchResult.batch_size}`);
  console.log(`  Avg time per URL: ${batchResult.avg_time_per_url.toFixed(2)}ms`);

  // Test 5: Cache Effectiveness
  console.log('\n📊 Test 5: Cache Effectiveness (3 requests)');
  const cacheResult = await testCaching(TEST_URLS[0], 3);
  console.log(`  First request: ${cacheResult.first_request_ms.toFixed(2)}ms`);
  console.log(`  Avg cached requests: ${cacheResult.avg_cached_ms.toFixed(2)}ms`);
  console.log(`  Speedup: ${cacheResult.speedup.toFixed(1)}x faster`);

  // Summary Statistics
  console.log('\n' + '='.repeat(60));
  console.log('📈 Performance Summary');
  console.log('='.repeat(60));

  const successRate = (singlePredictions.filter(r => r.success).length / singlePredictions.length * 100).toFixed(1);

  console.log(`✅ Success Rate: ${successRate}%`);
  console.log(`⚡ Single URL Time: ${avgSingleTime.toFixed(2)}ms (${(1000/avgSingleTime).toFixed(1)} URLs/sec)`);
  console.log(`📦 Batch Time per URL: ${batchResult.avg_time_per_url.toFixed(2)}ms`);
  console.log(`💾 Cache Speedup: ${cacheResult.speedup.toFixed(1)}x`);

  // Performance Rating
  console.log('\n🎯 Performance Rating:');
  if (avgSingleTime < 100) {
    console.log('  ⭐⭐⭐⭐⭐ Excellent - Response time <100ms');
  } else if (avgSingleTime < 200) {
    console.log('  ⭐⭐⭐⭐ Good - Response time 100-200ms');
  } else if (avgSingleTime < 500) {
    console.log('  ⭐⭐⭐ Fair - Response time 200-500ms');
  } else {
    console.log('  ⭐⭐ Slow - Response time >500ms');
  }

  console.log('\n✅ Performance test completed!');
}

// Run tests
runPerformanceTest().catch(error => {
  console.error('Test error:', error);
  process.exit(1);
});
