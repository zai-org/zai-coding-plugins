#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const repoRoot = process.cwd();
const pluginsDir = path.join(repoRoot, 'plugins');

const errors = [];
const builtScripts = [];

function walk(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    if (e.name === 'node_modules' || e.name === '.git') continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walk(full);
    else if (e.isFile() && e.name === 'SKILL.md') buildSkillScripts(full);
  }
}

function parseFrontmatter(md) {
  const lines = md.split(/\r?\n/);
  if (lines[0] !== '---') return null;

  let end = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i] === '---') {
      end = i;
      break;
    }
  }
  if (end === -1) return null;

  const fm = {};
  for (const l of lines.slice(1, end)) {
    const idx = l.indexOf(':');
    if (idx === -1) continue;
    const key = l.slice(0, idx).trim();
    const val = l.slice(idx + 1).trim();
    fm[key] = val;
  }

  const body = lines.slice(end + 1).join('\n');
  return { frontmatter: fm, body };
}

function buildSkillScripts(skillMdPath) {
  const rel = path.relative(repoRoot, skillMdPath);
  const content = fs.readFileSync(skillMdPath, 'utf8');

  const parsed = parseFrontmatter(content);
  if (!parsed) {
    errors.push(`${rel}: missing or invalid frontmatter (expected '---' block)`);
    return;
  }

  const { body } = parsed;
  const skillDir = path.dirname(skillMdPath);

  const scriptRefs = new Set();
  const re = /\bnode\s+scripts\/([^\s"'`]+)\b/g;
  let m;
  while ((m = re.exec(body)) !== null) {
    scriptRefs.add(m[1]);
  }

  for (const scriptRel of scriptRefs) {
    const scriptPath = path.join(skillDir, 'scripts', scriptRel);
    const scriptRepoRel = path.relative(repoRoot, scriptPath);

    if (!fs.existsSync(scriptPath) || !fs.statSync(scriptPath).isFile()) {
      errors.push(`${rel}: referenced script missing: ${scriptRepoRel}`);
      continue;
    }

    // Check if it's a JavaScript file (.js, .mjs)
    if (!scriptRel.match(/\.(js|mjs)$/)) {
      console.log(`Skipping non-JS script: ${scriptRepoRel}`);
      continue;
    }

    // Build/compile the JavaScript script
    console.log(`Building script: ${scriptRepoRel}`);
    
    // Use node --check first for syntax validation
    const checkResult = spawnSync(process.execPath, ['--check', scriptPath], { 
      encoding: 'utf8',
      stdio: 'pipe'
    });
    
    if (checkResult.status !== 0) {
      const out = (checkResult.stderr || checkResult.stdout || '').trim();
      errors.push(`${scriptRepoRel}: syntax check failed${out ? `\n${out}` : ''}`);
      continue;
    }

    // For ES modules (.mjs), we can try to load them to ensure they work
    if (scriptRel.endsWith('.mjs')) {
      // For .mjs files, just ensure they pass syntax check
      // Loading them dynamically might cause side effects during build
      builtScripts.push(scriptRepoRel);
    } else {
      // For .js files, just ensure they can be parsed
      builtScripts.push(scriptRepoRel);
    }
  }
}

if (!fs.existsSync(pluginsDir) || !fs.statSync(pluginsDir).isDirectory()) {
  console.error(`Skill build failed:\n- plugins directory not found at ${path.relative(repoRoot, pluginsDir)}`);
  process.exit(1);
}

walk(pluginsDir);

if (errors.length) {
  console.error('Skill build failed:');
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}

if (builtScripts.length) {
  console.log(`Successfully built ${builtScripts.length} script(s):`);
  for (const script of builtScripts) {
    console.log(`- ${script}`);
  }
} else {
  console.log('No JavaScript scripts found to build.');
}

console.log('Skill build completed.');
