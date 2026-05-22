#!/usr/bin/env node

/**
 * Usage query script for GLM Coding Plan.
 * Reads config from ~/.glm-config (no env vars needed).
 *
 * ~/.glm-config format:
 *   ANTHROPIC_AUTH_TOKEN=***
 *   ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
 */

import https from 'https';
import fs from 'fs';
import path from 'path';
import os from 'os';

// Force Asia/Shanghai timezone — all API responses use Beijing time.
process.env.TZ = 'Asia/Shanghai';

// Read config from ~/.glm-config
const configPath = path.join(os.homedir(), '.glm-config');

let authToken = '';
let baseUrl = '';

try {
  const configContent = fs.readFileSync(configPath, 'utf-8');
  for (const line of configContent.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eqIndex = trimmed.indexOf('=');
    if (eqIndex === -1) continue;
    const key = trimmed.slice(0, eqIndex).trim();
    const value = trimmed.slice(eqIndex + 1).trim();
    if (key === 'ANTHROPIC_AUTH_TOKEN') authToken = value;
    if (key === 'ANTHROPIC_BASE_URL') baseUrl = value;
  }
} catch (err) {
  console.error('Error: Cannot read config file:', configPath);
  console.error(err.message);
  process.exit(1);
}

// Also allow env vars to override config file
authToken = process.env.ANTHROPIC_AUTH_TOKEN || authToken;
baseUrl = process.env.ANTHROPIC_BASE_URL || baseUrl;

if (!authToken) {
  console.error('Error: ANTHROPIC_AUTH_TOKEN is not set in ~/.glm-config or environment');
  process.exit(1);
}

if (!baseUrl) {
  console.error('Error: ANTHROPIC_BASE_URL is not set in ~/.glm-config or environment');
  process.exit(1);
}

// Determine which platform to use
let platform;
let modelUsageUrl;
let toolUsageUrl;
let quotaLimitUrl;

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

const queryUsage = (apiUrl, label, appendQueryParams = true) => {
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
          const outputData = json.data || json;
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
  await queryUsage(quotaLimitUrl, 'Quota limit', false);
};

run().catch((error) => {
  console.error('Request failed:', error.message);
  process.exit(1);
});
