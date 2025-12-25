#!/usr/bin/env node

/**
 * Usage query script.
 * Determines whether to call the Z.ai or ZHIPU endpoint based on ANTHROPIC_BASE_URL
 * and authenticates with ANTHROPIC_AUTH_TOKEN.
 */

import https from 'https';

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
let modelUsageUrl;
let toolUsageUrl;
let quotaLimitUrl;

// Extract the base domain from ANTHROPIC_BASE_URL
const parsedBaseUrl = new URL(baseUrl);
const baseDomain = `${parsedBaseUrl.protocol}//${parsedBaseUrl.host}`;

if (baseUrl.includes('api.z.ai')) {
  platform = 'ZAI';
  modelUsageUrl = `${baseDomain}/api/monitor/usage/model-usage`;
  toolUsageUrl = `${baseDomain}/api/monitor/usage/tool-usage`;
  quotaLimitUrl = `${baseDomain}/api/monitor/usage/quota/limit`;
} else if (baseUrl.includes('open.bigmodel.cn') || baseUrl.includes('dev.bigmodel.cn')) {
  platform = 'ZHIPU';
  modelUsageUrl = `${baseDomain}/api/monitor/usage/model-usage`;
  toolUsageUrl = `${baseDomain}/api/monitor/usage/tool-usage`;
  quotaLimitUrl = `${baseDomain}/api/monitor/usage/quota/limit`;
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
// Time window: from yesterday at the current hour (HH:00:00) to today at the current hour end (HH:59:59).
const now = new Date();
const startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, now.getHours(), 0, 0, 0);
const endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), 59, 59, 999);

// Format dates as yyyy-MM-dd HH:mm:ss
const formatDateTime = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

const startTime = formatDateTime(startDate);
const endtime = formatDateTime(endDate);

// Properly encode query parameters
const queryParams = `?startTime=${encodeURIComponent(startTime)}&endTime=${encodeURIComponent(endtime)}`;

const processQuotaLimit = (data) => {
  if (!data || !data.limits) return data;
  
  data.limits = data.limits.map(item => {
    if (item.type === 'TOKENS_LIMIT') {
      return {
        type: 'Token usage(5 Hour)',
        percentage: item.percentage
      };
    }
    if (item.type === 'TIME_LIMIT') {
      return {
        type: 'MCP usage(1 Month)',
        percentage: item.percentage,
        currentUsage: item.currentValue,
        totol: item.usage,
        usageDetails: item.usageDetails
      };
    }
    return item;
  });
  return data;
};

const queryUsage = (apiUrl, label, appendQueryParams = true, postProcessor = null) => {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(apiUrl);
    const options = {
      hostname: parsedUrl.hostname,
      port: 443,
      path: parsedUrl.pathname + (appendQueryParams ? queryParams : ''),
      method: 'GET',
      headers: {
        'Authorization': authToken,
        'Accept-Language': 'en-US,en',
        'Content-Type': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        if (res.statusCode !== 200) {
          return reject(new Error(`[${label}] HTTP ${res.statusCode}\n${data}`));
        }

        console.log(`${label} data:`);
        console.log('');

        try {
          const json = JSON.parse(data);
          let outputData = json.data || json;
          if (postProcessor && json.data) {
            outputData = postProcessor(json.data);
          }
          console.log(JSON.stringify(outputData));
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

    req.end();
  });
};

const run = async () => {
  await queryUsage(modelUsageUrl, 'Model usage');
  await queryUsage(toolUsageUrl, 'Tool usage');
  await queryUsage(quotaLimitUrl, 'Quota limit', false, processQuotaLimit);
};

run().catch((error) => {
  console.error('Request failed:', error.message);
  process.exit(1);
});
