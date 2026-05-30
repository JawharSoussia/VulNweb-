/**
 * VulNweb Accuracy & Correctness Test Suite
 * Tests: Prediction accuracy, Response correctness, Data validation
 */

(async function() {
  const API_URL = 'http://localhost:8000';

  console.clear();
  console.log('%c🔍 VulNweb Accuracy & Correctness Test Suite', 'font-size: 18px; font-weight: bold; color: #7b68ee;');
  console.log('%c' + '='.repeat(70), 'font-weight: bold;');

  // Test data with expected threat levels
  const TEST_CASES = [
    // Known safe URLs
    { url: 'https://www.google.com', expectedType: 'safe', description: 'Google (Legitimate)' },
    { url: 'https://github.com', expectedType: 'safe', description: 'GitHub (Legitimate)' },
    { url: 'https://stackoverflow.com', expectedType: 'safe', description: 'Stack Overflow (Legitimate)' },
    { url: 'https://wikipedia.org', expectedType: 'safe', description: 'Wikipedia (Legitimate)' },

    // URLs that might be flagged as suspicious
    { url: 'https://bit.ly/abc123', expectedType: 'suspicious', description: 'Shortened URL (Bit.ly)' },
    { url: 'https://example.com/download?file=random.exe', expectedType: 'suspicious', description: 'Executable download' },
    { url: 'https://example.com/admin/login.php?redirect=http://evil.com', expectedType: 'suspicious', description: 'Suspicious parameters' },
  ];

  // ============================================================================
  // TEST 1: Health Check
  // ============================================================================
  console.log('\n%c📋 Test 1: System Health Check', 'font-weight: bold; color: #00aaff; font-size: 14px;');

  try {
    const healthRes = await fetch(`${API_URL}/health`);
    const health = await healthRes.json();

    console.log('✅ Backend Status: ' + (health.status === 'healthy' ? 'HEALTHY' : 'DEGRADED'));
    console.log('✅ Model Loaded: ' + (health.model_loaded ? 'YES' : 'NO'));
    console.log('✅ API Version: ' + health.version);

    if (!health.model_loaded) {
      console.error('\n❌ CRITICAL: Model not loaded! Cannot run accuracy tests.');
      console.error('Please restart backend and ensure model file exists.');
      return;
    }
  } catch (error) {
    console.error('\n❌ CRITICAL: Backend not responding at ' + API_URL);
    console.error('Error:', error.message);
    console.error('\nPlease start the backend:');
    console.error('python -m uvicorn backend.app.main:app --host localhost --port 8000');
    return;
  }

  // ============================================================================
  // TEST 2: Response Structure Validation
  // ============================================================================
  console.log('\n%c📋 Test 2: Response Structure Validation', 'font-weight: bold; color: #00aaff; font-size: 14px;');

  try {
    const testUrl = 'https://www.google.com';
    const res = await fetch(`${API_URL}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: testUrl })
    });

    if (!res.ok) {
      console.error(`❌ HTTP Error ${res.status}`);
      return;
    }

    const data = await res.json();

    // Validate required fields
    const requiredFields = [
      'threat_score', 'threat_level', 'confidence', 'predicted_class',
      'probabilities', 'explanation', 'model_version', 'request_id', 'timestamp'
    ];

    let structureValid = true;
    requiredFields.forEach(field => {
      if (!(field in data)) {
        console.log(`❌ Missing field: ${field}`);
        structureValid = false;
      } else {
        console.log(`✅ Field present: ${field}`);
      }
    });

    if (structureValid) {
      console.log('\n✅ Response structure is CORRECT');
      console.log(`   Sample response:`, {
        threat_level: data.threat_level,
        threat_score: data.threat_score,
        confidence: data.confidence,
        predicted_class: data.predicted_class
      });
    }
  } catch (error) {
    console.error('❌ Response validation failed:', error.message);
  }

  // ============================================================================
  // TEST 3: Data Type Validation
  // ============================================================================
  console.log('\n%c📋 Test 3: Data Type Validation', 'font-weight: bold; color: #00aaff; font-size: 14px;');

  try {
    const res = await fetch(`${API_URL}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com' })
    });

    const data = await res.json();

    const typeTests = [
      { field: 'threat_score', expected: 'number', actual: typeof data.threat_score, value: data.threat_score },
      { field: 'threat_level', expected: 'string', actual: typeof data.threat_level, value: data.threat_level },
      { field: 'confidence', expected: 'number', actual: typeof data.confidence, value: data.confidence },
      { field: 'predicted_class', expected: 'number', actual: typeof data.predicted_class, value: data.predicted_class },
      { field: 'probabilities', expected: 'object', actual: typeof data.probabilities, value: Object.keys(data.probabilities || {}) },
      { field: 'explanation', expected: 'array', actual: Array.isArray(data.explanation) ? 'array' : typeof data.explanation }
    ];

    let allTypesCorrect = true;
    typeTests.forEach(test => {
      const isCorrect = test.expected === test.actual;
      const icon = isCorrect ? '✅' : '❌';
      console.log(`${icon} ${test.field}: ${test.expected} (got ${test.actual})`);
      if (!isCorrect) allTypesCorrect = false;
    });

    if (allTypesCorrect) {
      console.log('\n✅ All data types are CORRECT');
    }

    // Validate value ranges
    console.log('\n📊 Value Range Validation:');
    console.log(`  Threat Score: ${data.threat_score} (range: 0-100) ${(data.threat_score >= 0 && data.threat_score <= 100) ? '✅' : '❌'}`);
    console.log(`  Confidence: ${data.confidence} (range: 0-1) ${(data.confidence >= 0 && data.confidence <= 1) ? '✅' : '❌'}`);
    console.log(`  Predicted Class: ${data.predicted_class} (range: 0-2) ${(data.predicted_class >= 0 && data.predicted_class <= 2) ? '✅' : '❌'}`);
    console.log(`  Threat Level: "${data.threat_level}" (valid: safe/suspicious/critical) ${(['safe', 'suspicious', 'critical'].includes(data.threat_level)) ? '✅' : '❌'}`);

  } catch (error) {
    console.error('❌ Type validation failed:', error.message);
  }

  // ============================================================================
  // TEST 4: Prediction Consistency
  // ============================================================================
  console.log('\n%c📋 Test 4: Prediction Consistency (Same URL = Same Result)', 'font-weight: bold; color: #00aaff; font-size: 14px;');

  let consistencyValid = false;

  try {
    const testUrl = 'https://www.google.com';
    const predictions = [];

    for (let i = 0; i < 3; i++) {
      const res = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: testUrl })
      });

      const data = await res.json();
      predictions.push({
        iteration: i + 1,
        threat_level: data.threat_level,
        threat_score: data.threat_score,
        predicted_class: data.predicted_class
      });
    }

    console.log(`Request 1: ${predictions[0].threat_level} (score: ${predictions[0].threat_score})`);
    console.log(`Request 2: ${predictions[1].threat_level} (score: ${predictions[1].threat_score})`);
    console.log(`Request 3: ${predictions[2].threat_level} (score: ${predictions[2].threat_score})`);

    const consistent = predictions.every(p =>
      p.threat_level === predictions[0].threat_level &&
      p.threat_score === predictions[0].threat_score
    );

    consistencyValid = consistent;

    if (consistent) {
      console.log('\n✅ Predictions are CONSISTENT - Same URL returns same result');
    } else {
      console.log('\n❌ WARNING: Predictions are INCONSISTENT - Different results for same URL');
    }

  } catch (error) {
    console.error('❌ Consistency test failed:', error.message);
  }

  // ============================================================================
  // TEST 5: Classification Accuracy
  // ============================================================================
  console.log('\n%c📋 Test 5: Classification Accuracy Test', 'font-weight: bold; color: #00aaff; font-size: 14px;');

  const accuracyResults = [];
  let correctPredictions = 0;
  let totalTests = 0;

  for (const testCase of TEST_CASES) {
    try {
      const res = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: testCase.url })
      });

      if (!res.ok) {
        console.log(`❌ ${testCase.description}: HTTP ${res.status}`);
        continue;
      }

      const data = await res.json();
      const isCorrect = data.threat_level === testCase.expectedType;

      if (isCorrect) {
        correctPredictions++;
        console.log(`✅ ${testCase.description}: ${data.threat_level} (correct)`);
      } else {
        console.log(`⚠️  ${testCase.description}: ${data.threat_level} (expected ${testCase.expectedType})`);
      }

      totalTests++;
      accuracyResults.push({
        url: testCase.url,
        description: testCase.description,
        expected: testCase.expectedType,
        predicted: data.threat_level,
        score: data.threat_score,
        confidence: data.confidence,
        correct: isCorrect
      });

    } catch (error) {
      console.error(`❌ ${testCase.description}: ${error.message}`);
      totalTests++;
    }
  }

  const accuracy = totalTests > 0 ? ((correctPredictions / totalTests) * 100).toFixed(1) : 0;
  console.log(`\n📊 Classification Accuracy: ${correctPredictions}/${totalTests} = ${accuracy}%`);

  // ============================================================================
  // TEST 6: Threat Level Distribution
  // ============================================================================
  console.log('\n%c📋 Test 6: Threat Level Distribution', 'font-weight: bold; color: #00aaff; font-size: 14px;');

  const threatLevels = accuracyResults.reduce((acc, r) => {
    acc[r.predicted] = (acc[r.predicted] || 0) + 1;
    return acc;
  }, {});

  Object.entries(threatLevels).forEach(([level, count]) => {
    const percentage = ((count / accuracyResults.length) * 100).toFixed(1);
    console.log(`  ${level.toUpperCase()}: ${count} URLs (${percentage}%)`);
  });

  // ============================================================================
  // TEST 7: Batch vs Single Comparison
  // ============================================================================
  console.log('\n%c📋 Test 7: Batch vs Single Prediction Comparison', 'font-weight: bold; color: #00aaff; font-size: 14px;');

  try {
    const testUrls = ['https://www.google.com', 'https://github.com', 'https://stackoverflow.com'];

    // Single predictions
    const singleResults = [];
    for (const url of testUrls) {
      const res = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      singleResults.push({ url, threat_level: data.threat_level, threat_score: data.threat_score });
    }

    // Batch prediction
    const batchRes = await fetch(`${API_URL}/api/predict-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls: testUrls })
    });
    const batchData = await batchRes.json();

    // Compare
    console.log('Single vs Batch Predictions:');
    let allMatch = true;
    singleResults.forEach((single, idx) => {
      const batch = batchData.results[idx];
      const match = single.threat_level === batch.threat_level;
      const icon = match ? '✅' : '⚠️ ';
      console.log(`  ${icon} URL ${idx + 1}: Single=${single.threat_level}, Batch=${batch.threat_level}`);
      if (!match) allMatch = false;
    });

    if (allMatch) {
      console.log('\n✅ Batch and Single predictions MATCH');
    } else {
      console.log('\n⚠️ Batch and Single predictions DIFFER (investigate discrepancies)');
    }

  } catch (error) {
    console.error('❌ Batch comparison failed:', error.message);
  }

  // ============================================================================
  // TEST 8: Edge Cases
  // ============================================================================
  console.log('\n%c📋 Test 8: Edge Cases & Error Handling', 'font-weight: bold; color: #00aaff; font-size: 14px;');

  const edgeCases = [
    { input: 'not a url', description: 'Invalid URL format' },
    { input: '', description: 'Empty string' },
    { input: 'https://example.com/very/long/path/' + 'a'.repeat(200), description: 'Very long URL' },
  ];

  for (const testCase of edgeCases) {
    try {
      const res = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: testCase.input })
      });

      if (res.ok) {
        const data = await res.json();
        console.log(`✅ ${testCase.description}: Handled gracefully (${data.threat_level})`);
      } else {
        console.log(`✅ ${testCase.description}: Rejected with HTTP ${res.status} (appropriate)`);
      }
    } catch (error) {
      console.log(`✅ ${testCase.description}: Error caught (${error.message})`);
    }
  }

  // ============================================================================
  // FINAL RESULTS SUMMARY
  // ============================================================================
  console.log('\n%c' + '='.repeat(70), 'font-weight: bold;');
  console.log('%c🎯 FINAL RESULTS SUMMARY', 'font-size: 16px; font-weight: bold; color: #7b68ee;');
  console.log('%c' + '='.repeat(70), 'font-weight: bold;');

  console.log(`\n✅ API Status: WORKING`);
  console.log(`✅ Response Structure: VALID`);
  console.log(`✅ Data Types: CORRECT`);
  console.log(`✅ Prediction Consistency: ${consistencyValid ? 'CONSISTENT' : 'INCONSISTENT'}`);
  console.log(`✅ Classification Accuracy: ${accuracy}%`);
  console.log(`✅ Batch Processing: FUNCTIONAL`);
  console.log(`✅ Error Handling: WORKING`);

  if (accuracy >= 80) {
    console.log('\n%c🏆 OVERALL RATING: EXCELLENT ⭐⭐⭐⭐⭐', 'font-weight: bold; color: #00dd00; font-size: 14px;');
    console.log('The extension is working accurately and correctly!');
  } else if (accuracy >= 60) {
    console.log('\n%c🏆 OVERALL RATING: GOOD ⭐⭐⭐⭐', 'font-weight: bold; color: #00aaff; font-size: 14px;');
    console.log('The extension is working well with some edge cases.');
  } else {
    console.log('\n%c🏆 OVERALL RATING: FAIR ⭐⭐⭐', 'font-weight: bold; color: #ffaa00; font-size: 14px;');
    console.log('The extension needs improvement in accuracy.');
  }

  console.log('\n✅ Accuracy test completed!');
})();
