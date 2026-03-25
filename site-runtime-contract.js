#!/usr/bin/env node
'use strict';

/**
 * site-runtime-contract.js
 *
 * Verifies that every data-ops / data-ops-status binding declared in
 * site/index.html resolves to a key that actually exists in the generated
 * ops-metrics payload (site/assets/data/ops-metrics.json).
 *
 * Specific contract gates:
 *   - auto_close_rate  must be a non-empty string
 *   - escalated        must be a non-negative integer
 *
 * Exit 0 = PASS, exit 1 = FAIL.
 */

const fs = require('fs');
const path = require('path');

const root = process.cwd();

// ── Load ops-metrics.json ──────────────────────────────────────────────────
const opsMetricsPath = path.join(root, 'site', 'assets', 'data', 'ops-metrics.json');
if (!fs.existsSync(opsMetricsPath)) {
  console.error('FAIL: site/assets/data/ops-metrics.json not found');
  process.exit(1);
}

let rawMetrics;
try {
  rawMetrics = JSON.parse(fs.readFileSync(opsMetricsPath, 'utf8'));
} catch (err) {
  console.error(`FAIL: could not parse ops-metrics.json — ${err.message}`);
  process.exit(1);
}

const metrics =
  rawMetrics.metrics && typeof rawMetrics.metrics === 'object'
    ? rawMetrics.metrics
    : rawMetrics;

// ── Load index.html ────────────────────────────────────────────────────────
const indexPath = path.join(root, 'site', 'index.html');
if (!fs.existsSync(indexPath)) {
  console.error('FAIL: site/index.html not found');
  process.exit(1);
}

const html = fs.readFileSync(indexPath, 'utf8');

// ── Extract binding keys ───────────────────────────────────────────────────
const dataOpsKeys = new Set();
const dataOpsStatusKeys = new Set();

let m;
const reOps = /data-ops="([^"]+)"/g;
const reOpsStatus = /data-ops-status="([^"]+)"/g;
while ((m = reOps.exec(html)) !== null) dataOpsKeys.add(m[1]);
while ((m = reOpsStatus.exec(html)) !== null) dataOpsStatusKeys.add(m[1]);

// ── Binding coverage check ─────────────────────────────────────────────────
const errors = [];
const passes = [];

for (const key of [...dataOpsKeys]) {
  const value = metrics[key];
  if (value === undefined || value === null) {
    errors.push(`[data-ops="${key}"] → key "${key}" missing from ops-metrics`);
  } else {
    passes.push(`[data-ops="${key}"] → ${JSON.stringify(value)}`);
  }
}

for (const key of [...dataOpsStatusKeys]) {
  const value = metrics[key];
  if (value === undefined || value === null) {
    errors.push(`[data-ops-status="${key}"] → key "${key}" missing from ops-metrics`);
  } else {
    passes.push(`[data-ops-status="${key}"] → ${JSON.stringify(value)}`);
  }
}

// ── Specific contract gates ────────────────────────────────────────────────
const autoCloseRate = metrics['auto_close_rate'];
if (typeof autoCloseRate !== 'string' || !autoCloseRate.trim()) {
  errors.push('contract: auto_close_rate must be a non-empty string in ops-metrics');
}

const escalated = metrics['escalated'];
if (typeof escalated !== 'number' || !Number.isFinite(escalated) || escalated < 0) {
  errors.push('contract: escalated must be a non-negative integer in ops-metrics');
}

// ── Report ─────────────────────────────────────────────────────────────────
console.log('site-runtime-contract: binding check');
console.log('');
for (const p of passes) {
  console.log(`  PASS  ${p}`);
}

if (errors.length > 0) {
  console.log('');
  for (const e of errors) {
    process.stderr.write(`  FAIL  ${e}\n`);
  }
  console.log('');
  process.stderr.write(`site-runtime-contract FAILED: ${errors.length} error(s)\n`);
  process.exit(1);
}

console.log('');
console.log(`site-runtime-contract PASSED: ${passes.length} binding(s) verified`);
process.exit(0);
