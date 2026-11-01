import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const scripts = [
  ['usage', '../plugins/glm-plan-usage/skills/usage-query-skill/scripts/query-usage.mjs'],
  ['feedback', '../plugins/glm-plan-bug/skills/case-feedback-skill/scripts/submit-feedback.mjs'],
];

// Observe the actual scripts' HTTPS options and feedback bytes without sending
// requests, loading user configuration, or using a real credential.
const harness = `
import https from 'node:https';
import { EventEmitter } from 'node:events';
import { pathToFileURL } from 'node:url';
const script = process.argv[1];
process.argv = [process.execPath, script, ...process.argv.slice(2)];
https.request = (options, onResponse) => {
  const request = new EventEmitter();
  const chunks = [];
  request.write = (chunk) => chunks.push(Buffer.from(chunk));
  request.end = () => {
    process.stderr.write('REQUEST ' + JSON.stringify({
      ...options, body: Buffer.concat(chunks).toString('utf8'),
    }) + '\\n');
    queueMicrotask(() => {
      const response = new EventEmitter();
      response.statusCode = 200;
      onResponse(response);
      response.emit('data', Buffer.from(JSON.stringify({ data: { limits: [] } })));
      response.emit('end');
    });
  };
  return request;
};
await import(pathToFileURL(script).href);
`;

function runScript(kind, relativePath, baseUrl) {
  const script = fileURLToPath(new URL(relativePath, import.meta.url));
  const args = kind === 'feedback'
    ? ['--feedback', 'synthetic feedback', '--context', 'synthetic context']
    : [];
  const result = spawnSync(
    process.execPath,
    ['--input-type=module', '--eval', harness, script, ...args],
    {
      env: {
        ...process.env,
        ANTHROPIC_BASE_URL: baseUrl,
        ANTHROPIC_AUTH_TOKEN: 'synthetic-test-token',
      },
      encoding: 'utf8',
      timeout: 5000,
    },
  );
  assert.ifError(result.error);
  const requests = result.stderr.split('\n')
    .filter((line) => line.startsWith('REQUEST '))
    .map((line) => JSON.parse(line.slice('REQUEST '.length)));
  return { ...result, requests };
}

for (const [kind, script] of scripts) {
  for (const [url, platform] of [
    ['https://api.z.ai/api/anthropic', 'ZAI'],
    ['https://open.bigmodel.cn/api/anthropic', 'ZHIPU'],
    ['https://dev.bigmodel.cn/api/anthropic', 'ZHIPU'],
    ['https://API.Z.AI/api/anthropic', 'ZAI'],
    ['https://open.bigmodel.cn/api/anthropic?upstream=api.z.ai', 'ZHIPU'],
  ]) {
    test(`${kind} routes a supported parsed URL: ${url}`, () => {
      const result = runScript(kind, script, url);
      assert.equal(result.status, 0, result.stderr);
      assert.match(result.stdout, new RegExp('Platform: ' + platform));
      const expectedPaths = kind === 'usage'
        ? ['/api/monitor/usage/model-usage', '/api/monitor/usage/tool-usage', '/api/monitor/usage/quota/limit']
        : ['/api/monitor/feedback/case'];
      assert.equal(result.requests.length, expectedPaths.length);
      for (const [index, request] of result.requests.entries()) {
        assert.equal(request.hostname, new URL(url).hostname);
        assert.equal(request.port, 443);
        assert.equal(request.method, kind === 'usage' ? 'GET' : 'POST');
        assert.equal(request.path.split('?')[0], expectedPaths[index]);
        assert.equal(request.headers.Authorization, 'synthetic-test-token');
        if (kind === 'feedback') {
          assert.equal(request.headers['Content-Length'], Buffer.byteLength(request.body));
          assert.deepEqual(JSON.parse(request.body), {
            feedback: 'synthetic feedback', context: 'synthetic context',
            codeType: '', happenedTime: '', requestId: '',
          });
        }
      }
    });
  }

  for (const url of [
    'https://api.z.ai.example.invalid/api/anthropic',
    'https://example.invalid/api.z.ai/api/anthropic',
    'https://example.invalid/?upstream=open.bigmodel.cn',
    'https://open.bigmodel.cn@example.invalid/api/anthropic',
    'https://example.invalid/#dev.bigmodel.cn',
    'https://example.invalid/api/anthropic',
    'http://api.z.ai/api/anthropic',
  ]) {
    test(`${kind} rejects an unsupported destination before HTTPS: ${url}`, () => {
      const result = runScript(kind, script, url);
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.equal(result.requests.length, 0, 'must reject before assembling an authenticated request');
      assert.match(result.stderr, /Unrecognized ANTHROPIC_BASE_URL/);
    });
  }
}
