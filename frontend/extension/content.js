/**
 * VulNweb Content Script
 * Extracts URLs and IPs from web pages for threat analysis
 */

// Configuration
const CONFIG = {
  API_URL: 'http://localhost:8000',
  CACHE_DURATION: 60000, // 1 minute
  CHECK_INTERVAL: 2000   // Check DOM every 2 seconds
};

// Cache for predictions to avoid repeated API calls
const predictionCache = new Map();

/**
 * Extract all links from current page
 */
function extractLinks() {
  const links = [];

  // Get all anchor tags
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');

    // Skip javascript: and mailto: links
    if (href && !href.startsWith('javascript:') && !href.startsWith('mailto:')) {
      try {
        const url = new URL(href, window.location.origin);
        links.push({
          url: url.href,
          text: link.textContent.trim().substring(0, 100),
          element: link
        });
      } catch (e) {
        // Invalid URL, skip
      }
    }
  });

  return links;
}

/**
 * Extract IP addresses from page content (basic extraction)
 */
function extractIPs() {
  const ips = [];
  const ipRegex = /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g;

  const pageText = document.body.innerText;
  const matches = pageText.match(ipRegex);

  if (matches) {
    // Remove duplicates
    const unique = [...new Set(matches)];
    unique.slice(0, 10).forEach(ip => {
      ips.push({ ip });
    });
  }

  return ips;
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
 * Create threat indicator element
 */
function createThreatIndicator(threat) {
  const indicator = document.createElement('div');
  indicator.className = 'vulnweb-threat-indicator';

  // Color based on threat level
  const colors = {
    'safe': '#4CAF50',
    'suspicious': '#FF9800',
    'critical': '#F44336'
  };

  const bgColor = colors[threat.threat_level] || '#9E9E9E';

  indicator.style.cssText = `
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: ${bgColor};
    margin-left: 8px;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  `;

  // Add tooltip with threat info
  indicator.title = `[${threat.threat_level.toUpperCase()}] Threat Score: ${threat.threat_score.toFixed(1)}%`;

  // Add hover details
  indicator.addEventListener('mouseenter', (e) => {
    showThreatPopup(e, threat);
  });

  return indicator;
}

/**
 * Show threat details popup
 */
function showThreatPopup(event, threat) {
  // Remove existing popup
  const existing = document.querySelector('.vulnweb-popup');
  if (existing) existing.remove();

  const popup = document.createElement('div');
  popup.className = 'vulnweb-popup';

  popup.innerHTML = `
    <div style="padding: 12px; background: white; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); max-width: 300px; font-size: 12px; font-family: Arial, sans-serif;">
      <div style="font-weight: bold; margin-bottom: 8px;">VulNweb Threat Analysis</div>
      <div style="margin-bottom: 6px;">
        <strong>Threat Level:</strong> <span style="color: #FF6F00;">${threat.threat_level.toUpperCase()}</span>
      </div>
      <div style="margin-bottom: 6px;">
        <strong>Threat Score:</strong> ${threat.threat_score.toFixed(1)}%
      </div>
      <div style="margin-bottom: 6px;">
        <strong>Confidence:</strong> ${typeof threat.confidence === 'number' ? (threat.confidence > 1 ? threat.confidence : threat.confidence * 100).toFixed(1) : 'N/A'}%
      </div>
      <div style="margin-bottom: 6px; font-size: 11px;">
        <strong>Analysis:</strong><br/>
        ${threat.explanation?.slice(0, 2).map(e => `• ${e}`).join('<br/>') || 'N/A'}
      </div>
    </div>
  `;

  popup.style.cssText = `
    position: fixed;
    z-index: 10000;
    top: ${event.clientY + 10}px;
    left: ${event.clientX + 10}px;
  `;

  document.body.appendChild(popup);

  // Remove popup on click outside
  setTimeout(() => {
    document.addEventListener('click', () => {
      popup.remove();
    }, { once: true });
  });
}

/**
 * Enhance link with threat indicator
 */
async function enhanceLink(linkElement, url) {
  // Check if already enhanced
  if (linkElement.dataset.vulnwebChecked) {
    return;
  }
  linkElement.dataset.vulnwebChecked = true;

  // Get prediction
  const prediction = await getPrediction(url);

  if (prediction) {
    // Create and add indicator
    const indicator = createThreatIndicator(prediction);
    linkElement.appendChild(indicator);

    // Change link appearance if critical threat
    if (prediction.threat_level === 'critical') {
      linkElement.style.textDecoration = 'line-through';
      linkElement.style.opacity = '0.6';
    }
  }
}

/**
 * Process all links on page
 */
async function processLinks() {
  const links = extractLinks();

  console.log(`[VulNweb] Found ${links.length} links to check`);

  // Process links with throttling to avoid API overload
  for (let i = 0; i < Math.min(links.length, 10); i++) {
    const link = links[i];
    try {
      await enhanceLink(link.element, link.url);
      // Add delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 200));
    } catch (error) {
      console.error('[VulNweb] Error processing link:', error);
    }
  }
}

/**
 * Monitor page for new links added dynamically
 */
function monitorDynamicContent() {
  // Use MutationObserver to watch for new links
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.addedNodes.length) {
        // Check if new links were added
        const newLinks = document.querySelectorAll('a[href]:not([data-vulnweb-checked])');

        if (newLinks.length > 0) {
          console.log('[VulNweb] Detected new links, processing...');
          // Process only new links (limit to 3 to avoid overload)
          for (let i = 0; i < Math.min(newLinks.length, 3); i++) {
            const url = newLinks[i].getAttribute('href');
            try {
              const fullUrl = new URL(url, window.location.origin).href;
              enhanceLink(newLinks[i], fullUrl);
            } catch (e) {
              // Invalid URL, skip
            }
          }
        }
      }
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

/**
 * Initialize content script
 */
function init() {
  console.log('[VulNweb] Content script loaded');

  // Check if API is available
  fetch(`${CONFIG.API_URL}/health`)
    .then(r => r.json())
    .then(data => {
      console.log('[VulNweb] API Status:', data);
    })
    .catch(e => {
      console.warn('[VulNweb] API not available at', CONFIG.API_URL);
    });

  // Process existing links
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', processLinks);
  } else {
    processLinks();
  }

  // Monitor for dynamically added content
  monitorDynamicContent();
}
// Add helper function to work with background worker
function sendToBackground(type, data) {
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

// Update getPrediction to use background worker
async function getPrediction(urlString) {
  try {
    // Send to background for caching and batching
    const prediction = await sendToBackground('CHECK_THREAT', { url: urlString });

    if (prediction.error) {
      throw new Error(prediction.error);
    }

    return prediction;

  } catch (error) {
    console.error('[VulNweb] Prediction error:', error);
    return null;
  }
}

// Add stats tracking
async function updateStats() {
  try {
    const stats = await sendToBackground('GET_STATS', {});
    console.log('[VulNweb] Stats:', stats);
  } catch (error) {
    console.warn('[VulNweb] Stats error:', error);
  }
}
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

// Start when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}