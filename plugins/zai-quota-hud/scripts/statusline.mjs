#!/usr/bin/env node

import https from 'https';
import fs from 'fs';
import { URL } from 'url';

const CACHE_PATH = '/tmp/zai-quota-cache.json';
const CACHE_TTL_MS = 60_000;

const RESET = '\x1b[0m';
const DIM = '\x1b[2m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RED = '\x1b[31m';

function colorForPercent(pct) {
  if (pct >= 80) return RED;
  if (pct >= 50) return YELLOW;
  return GREEN;
}

function bar(pct, width = 10) {
  const filled = Math.round((pct / 100) * width);
  const empty = width - filled;
  return '█'.repeat(filled) + '░'.repeat(empty);
}

function formatCountdown(nextResetTime) {
  const ms = new Date(nextResetTime).getTime() - Date.now();
  if (ms <= 0) return null;
  const totalMin = Math.floor(ms / 60_000);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  const s = Math.floor((ms % 60_000) / 1000);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m`;
  return `${s}s`;
}

function readCache() {
  try {
    const stat = fs.statSync(CACHE_PATH);
    if (Date.now() - stat.mtimeMs < CACHE_TTL_MS) {
      const raw = fs.readFileSync(CACHE_PATH, 'utf8');
      return JSON.parse(raw);
    }
  } catch {}
  return null;
}

function writeCache(data) {
  try {
    fs.writeFileSync(CACHE_PATH, JSON.stringify(data));
  } catch {}
}

function fetchQuota(baseUrl, authToken) {
  return new Promise((resolve, reject) => {
    let parsed;
    try {
      parsed = new URL(baseUrl);
    } catch {
      return reject(new Error('Invalid ANTHROPIC_BASE_URL'));
    }

    const baseDomain = `${parsed.protocol}//${parsed.host}`;
    const apiUrl = `${baseDomain}/api/monitor/usage/quota/limit`;
    const url = new URL(apiUrl);

    const options = {
      hostname: url.hostname,
      port: url.port || 443,
      path: url.pathname,
      method: 'GET',
      headers: {
        'Authorization': authToken,
        'Accept-Language': 'en-US,en',
        'Content-Type': 'application/json',
      },
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode !== 200) {
          return reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
        try {
          const json = JSON.parse(data);
          if (json.success && json.data) {
            resolve(json.data);
          } else {
            reject(new Error(json.msg || 'API returned unsuccessful response'));
          }
        } catch (e) {
          reject(new Error(`Parse error: ${e.message}`));
        }
      });
    });

    req.on('error', reject);
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    req.end();
  });
}

function formatOutput(data) {
  const tokensLimit = (data.limits || []).find((l) => l.type === 'TOKENS_LIMIT');
  if (!tokensLimit) return `${DIM}ZAI: no data${RESET}`;
  const pct = tokensLimit.percentage || 0;
  let suffix = '';
  if (pct >= 100 && tokensLimit.nextResetTime) {
    const cd = formatCountdown(tokensLimit.nextResetTime);
    if (cd) suffix = ` ⏳ ${cd}`;
  }
  return `${colorForPercent(pct)}ZAI ${bar(pct, 5)} ${pct}%${suffix}${RESET}`;
}

function readStdin() {
  return new Promise((resolve) => {
    if (process.stdin.isTTY) {
      resolve(null);
      return;
    }
    let data = '';
    process.stdin.setEncoding('utf8');
    const timer = setTimeout(() => {
      resolve(null);
    }, 250);
    process.stdin.on('data', (chunk) => { data += chunk; });
    process.stdin.on('end', () => {
      clearTimeout(timer);
      try {
        resolve(JSON.parse(data.trim()));
      } catch {
        resolve(null);
      }
    });
  });
}

async function main() {
  const baseUrl = process.env.ANTHROPIC_BASE_URL || '';
  const authToken = process.env.ANTHROPIC_AUTH_TOKEN || '';

  if (!authToken || !baseUrl) {
    console.log(`${DIM}ZAI: not configured (set ANTHROPIC_BASE_URL & ANTHROPIC_AUTH_TOKEN)${RESET}`);
    return;
  }

  let isZai = baseUrl.includes('api.z.ai');
  let isZhipu = baseUrl.includes('open.bigmodel.cn') || baseUrl.includes('dev.bigmodel.cn');
  if (!isZai && !isZhipu) {
    console.log(`${DIM}ZAI: unsupported base URL${RESET}`);
    return;
  }

  await readStdin();

  let data = readCache();

  if (!data) {
    try {
      data = await fetchQuota(baseUrl, authToken);
      writeCache(data);
    } catch (e) {
      const stale = readCache();
      if (stale) {
        console.log(formatOutput(stale) + ` ${DIM}(stale)${RESET}`);
      } else {
        console.log(`${DIM}ZAI: unavailable (${e.message})${RESET}`);
      }
      return;
    }
  }

  console.log(formatOutput(data));
}

main().catch((e) => {
  console.log(`${DIM}ZAI: error (${e.message})${RESET}`);
});
