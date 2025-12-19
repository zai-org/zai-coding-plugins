#!/usr/bin/env node

/**
 * Case feedback submission script.
 * Determines whether to call the Z.ai or ZHIPU endpoint based on ANTHROPIC_BASE_URL
 * and authenticates with ANTHROPIC_AUTH_TOKEN.
 */

import https from 'https';

// Parse command line arguments
const args = process.argv.slice(2);
let feedback = '';
let context = '';
let codeType = '';
let happenedTime = '';
let requestId = '';

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--feedback' && args[i + 1]) {
    feedback = args[i + 1];
    i++;
  } else if (args[i] === '--context' && args[i + 1]) {
    context = args[i + 1];
    i++;
  } else if (args[i] === '--code_type' && args[i + 1]) {
    codeType = args[i + 1];
    i++;
  } else if (args[i] === '--happened_time' && args[i + 1]) {
    happenedTime = args[i + 1];
    i++;
  } else if (args[i] === '--request_id' && args[i + 1]) {
    requestId = args[i + 1];
    i++;
  }
}

if (!feedback) {
  console.error('Error: --feedback argument is required');
  console.error('');
  console.error('Usage:');
  console.error('  node submit-feedback.mjs --feedback "your feedback" --context "context info"');
  process.exit(1);
}

if (!context) {
  console.error('Error: --context argument is required');
  console.error('');
  console.error('Usage:');
  console.error('  node submit-feedback.mjs --feedback "your feedback" --context "context info"');
  process.exit(1);
}

// Read environment variables
const baseUrl = process.env.ANTHROPIC_BASE_URL || '';
const authToken = process.env.ANTHROPIC_AUTH_TOKEN || '';

if (!authToken) {
  console.error('Error: ANTHROPIC_AUTH_TOKEN is not set');
  console.error('');
  console.error('Set the environment variable and retry:');
  console.error('  export ANTHROPIC_AUTH_TOKEN="your-token-here"');
  process.exit(1);
}

// Validate ANTHROPIC_BASE_URL
if (!baseUrl) {
  console.error('Error: ANTHROPIC_BASE_URL is not set');
  console.error('');
  console.error('Set the environment variable and retry:');
  console.error('  export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"');
  console.error('  or');
  console.error('  export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"');
  process.exit(1);
}

// Determine which platform to use
let platform;
let feedbackUrl;

// Extract the base domain from ANTHROPIC_BASE_URL
const parsedBaseUrl = new URL(baseUrl);
const baseDomain = `${parsedBaseUrl.protocol}//${parsedBaseUrl.host}`;

if (baseUrl.includes('api.z.ai')) {
  platform = 'ZAI';
  feedbackUrl = `${baseDomain}/api/monitor/feedback/case`;
} else if (baseUrl.includes('open.bigmodel.cn') || baseUrl.includes('dev.bigmodel.cn')) {
  platform = 'ZHIPU';
  feedbackUrl = `${baseDomain}/api/monitor/feedback/case`;
} else {
  console.error('Error: Unrecognized ANTHROPIC_BASE_URL:', baseUrl);
  console.error('');
  console.error('Supported values:');
  console.error('  - https://api.z.ai/api/anthropic');
  console.error('  - https://open.bigmodel.cn/api/anthropic');
  process.exit(1);
}

console.log(`Platform: ${platform}`);
console.log('');

const submitFeedback = () => {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(feedbackUrl);
    const postData = JSON.stringify({
      feedback: feedback,
      context: context,
      codeType: codeType,
      happenedTime: happenedTime,
      requestId: requestId
    });

    const options = {
      hostname: parsedUrl.hostname,
      port: 443,
      path: parsedUrl.pathname,
      method: 'POST',
      headers: {
        'Authorization': authToken,
        'Content-Type': 'application/json',
        'Accept-Language': 'en-US,en',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        if (res.statusCode !== 200) {
          return reject(new Error(`HTTP ${res.statusCode}\n${data}`));
        }

        console.log('Feedback submitted successfully!');
        console.log('');

        try {
          const json = JSON.parse(data);
          console.log('Response:');
          console.log(JSON.stringify(json, null, 2));
        } catch (e) {
          console.log('Response body:');
          console.log(data);
        }

        console.log('');
        resolve();
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.write(postData);
    req.end();
  });
};

const run = async () => {
  console.log('Submitting feedback...');
  console.log('Feedback:', feedback);
  console.log('Context:', context.substring(0, 200) + (context.length > 200 ? '...' : ''));
  console.log('');
  await submitFeedback();
};

run().catch((error) => {
  console.error('Request failed:', error.message);
  process.exit(1);
});
