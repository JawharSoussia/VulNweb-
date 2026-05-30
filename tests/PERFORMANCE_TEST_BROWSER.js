/**
 * VulNweb Browser Console Performance Test
 * Run this in the browser console (F12 → Console tab)
 * Copy and paste the entire code block and press Enter
 */

(async function() {
  const API_URL = 'http://localhost:8000';

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

  console.clear();
  console.log('%c🚀 VulNweb Performance Test Suite', 'font-size: 20px; font-weight: bold; color: #7b68ee;');
  console.log('%c' + '='.repeat(60), 'font-weight: bold;');

  // Test health
  console.log('\n%c📊 Test 1: System Health Check', 'font-weight: bold; color: #00aaff;');
  try {
    const healthRes = await fetch(`${API_URL}/health`);
    const health = await healthRes.json();
    console.log('✅ API Status:', health.status);
    console.log('📦 Model Loaded:', health.model_loaded);

    if (!health.model_loaded) {
      console.error('❌ Model not loaded! Tests will fail.');
      return;
    }
  } catch (error) {
    console.error('❌ Backend not running:', error.message);
    return;
  }

  // Get model info
  console.log('\n%c📊 Test 2: Model Information', 'font-weight: bold; color: #00aaff;');
  try {
    const modelRes = await fetch(`${API_URL}/api/model-info`);
    const model = await modelRes.json();
    console.log('Model:', model.model_name);
    console.log('Features:', model.num_features);
    console.log('Classes:', model.class_names?.join(', '));
  } catch (error) {
    console.error('❌ Failed to get model info:', error.message);
  }

  // Single URL tests
  console.log('\n%c📊 Test 3: Single URL Performance (5 URLs)', 'font-weight: bold; color: #00aaff;');
  const singleResults = [];

  for (let i = 0; i < 5; i++) {
    const url = TEST_URLS[i];
    const startTime = performance.now();

    try {
      const res = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      const endTime = performance.now();
      const duration = endTime - startTime;

      if (res.ok) {
        const data = await res.json();
        singleResults.push({ url, duration, threat_level: data.threat_level, success: true });
        console.log(`  ✅ ${url.substring(0, 40)}: ${duration.toFixed(2)}ms → ${data.threat_level}`);
      } else {
        console.log(`  ❌ ${url.substring(0, 40)}: HTTP ${res.status}`);
      }
    } catch (error) {
      console.error(`  ❌ ${url}: ${error.message}`);
    }
  }

  const validResults = singleResults.filter(r => r.success);
  if (validResults.length > 0) {
    const avgTime = validResults.reduce((sum, r) => sum + r.duration, 0) / validResults.length;
    const minTime = Math.min(...validResults.map(r => r.duration));
    const maxTime = Math.max(...validResults.map(r => r.duration));

    console.log(`\n  📈 Average: ${avgTime.toFixed(2)}ms`);
    console.log(`  ⚡ Min: ${minTime.toFixed(2)}ms`);
    console.log(`  🐢 Max: ${maxTime.toFixed(2)}ms`);
    console.log(`  🚀 Throughput: ${(1000 / avgTime).toFixed(1)} URLs/sec`);
  }

  // Batch test
  console.log('\n%c📊 Test 4: Batch Prediction Performance', 'font-weight: bold; color: #00aaff;');
  const batchStart = performance.now();

  try {
    const batchRes = await fetch(`${API_URL}/api/predict-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls: TEST_URLS })
    });

    const batchEnd = performance.now();
    const batchDuration = batchEnd - batchStart;

    if (batchRes.ok) {
      const batch = await batchRes.json();
      console.log(`  ✅ Batch Size: ${batch.total}`);
      console.log(`  ✅ Successful: ${batch.successful}/${batch.total}`);
      console.log(`  ⏱️  Total Time: ${batchDuration.toFixed(2)}ms`);
      console.log(`  ⚡ Time/URL: ${(batchDuration / batch.total).toFixed(2)}ms`);
    }
  } catch (error) {
    console.error(`  ❌ Batch failed: ${error.message}`);
  }

  // Cache test
  console.log('\n%c📊 Test 5: Cache Effectiveness', 'font-weight: bold; color: #00aaff;');
  const testUrl = TEST_URLS[0];
  const cacheTimes = [];

  for (let i = 0; i < 3; i++) {
    const start = performance.now();

    try {
      const res = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: testUrl })
      });

      const end = performance.now();
      const duration = end - start;
      cacheTimes.push(duration);

      const cacheType = i === 0 ? '(fresh)' : '(cached)';
      console.log(`  Request ${i + 1} ${cacheType}: ${duration.toFixed(2)}ms`);
    } catch (error) {
      console.error(`  ❌ Request ${i + 1} failed:`, error.message);
    }
  }

  if (cacheTimes.length >= 2) {
    const speedup = cacheTimes[0] / (cacheTimes.slice(1).reduce((sum, t) => sum + t) / (cacheTimes.length - 1));
    console.log(`\n  💾 Cache Speedup: ${speedup.toFixed(1)}x faster`);
  }

  // Stress test
  console.log('\n%c📊 Test 6: Stress Test (Rapid Requests)', 'font-weight: bold; color: #00aaff;');
  const stressStart = performance.now();
  let stressSuccess = 0;
  let stressFailed = 0;

  const stressPromises = [];
  for (let i = 0; i < 10; i++) {
    const url = TEST_URLS[i % TEST_URLS.length];
    const promise = fetch(`${API_URL}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    })
      .then(res => {
        if (res.ok) {
          stressSuccess++;
        } else {
          stressFailed++;
        }
      })
      .catch(() => {
        stressFailed++;
      });

    stressPromises.push(promise);
  }

  await Promise.all(stressPromises);
  const stressEnd = performance.now();
  const stressDuration = stressEnd - stressStart;

  console.log(`  ✅ Success: ${stressSuccess}/10`);
  console.log(`  ❌ Failed: ${stressFailed}/10`);
  console.log(`  ⏱️  Duration: ${stressDuration.toFixed(2)}ms`);
  console.log(`  🚀 Throughput: ${(10000 / stressDuration).toFixed(1)} requests/sec`);

  // Summary
  console.log('\n%c' + '='.repeat(60), 'font-weight: bold;');
  console.log('%c🎯 Performance Summary', 'font-size: 16px; font-weight: bold; color: #7b68ee;');
  console.log('%c' + '='.repeat(60), 'font-weight: bold;');

  if (validResults.length > 0) {
    const avgTime = validResults.reduce((sum, r) => sum + r.duration, 0) / validResults.length;

    let rating = '⭐⭐⭐⭐⭐ Excellent (<100ms)';
    if (avgTime >= 100 && avgTime < 200) rating = '⭐⭐⭐⭐ Good (100-200ms)';
    else if (avgTime >= 200 && avgTime < 500) rating = '⭐⭐⭐ Fair (200-500ms)';
    else if (avgTime >= 500) rating = '⭐⭐ Slow (>500ms)';

    console.log(`%c${rating}`, 'font-weight: bold; font-size: 14px;');
    console.log(`Success Rate: ${((validResults.length / singleResults.length) * 100).toFixed(1)}%`);
    console.log(`Avg Response: ${avgTime.toFixed(2)}ms`);
    console.log(`Throughput: ${(1000 / avgTime).toFixed(1)} URLs/sec`);
  }

  console.log('\n%c✅ Performance test completed!', 'color: #00dd00; font-weight: bold;');
})();
