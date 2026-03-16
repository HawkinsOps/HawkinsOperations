#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const root = process.cwd();
const siteDir = path.join(root, "site");
const countsJsonPath = path.join(siteDir, "assets", "verified-counts.json");
const opsJsonPath = path.join(siteDir, "assets", "data", "ops-metrics.json");
const homePagePath = path.join(siteDir, "index.html");

function fail(message) {
  console.error(`Site runtime contract failed: ${message}`);
  process.exit(1);
}

function readJson(filePath) {
  if (!fs.existsSync(filePath)) fail(`missing required JSON artifact ${path.relative(root, filePath)}`);
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function readText(filePath) {
  if (!fs.existsSync(filePath)) fail(`missing required file ${path.relative(root, filePath)}`);
  return fs.readFileSync(filePath, "utf8");
}

function collectHtmlFiles(dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      collectHtmlFiles(full, out);
      continue;
    }
    if (entry.isFile() && entry.name.toLowerCase().endsWith(".html")) out.push(full);
  }
  return out;
}

function extractFallbackValue(html, attr) {
  const pattern = new RegExp(`data-ops="${attr}"[^>]*>([^<]+)<`, "i");
  const match = html.match(pattern);
  return match ? match[1].trim() : null;
}

function ensureHomeFallbacksMatchOps(homeHtml, opsMetrics) {
  const expected = {
    coverage_ratio: String(opsMetrics.coverage_ratio),
    reconciliation_mismatch: String(opsMetrics.reconciliation_mismatch),
    last_updated: String(opsMetrics.last_updated),
    total_cases: String(opsMetrics.total_cases),
    auto_closed_benign: String(opsMetrics.auto_closed_benign),
    known_fp: String(opsMetrics.known_fp),
    escalated: String(opsMetrics.escalated)
  };

  Object.entries(expected).forEach(([key, value]) => {
    const actual = extractFallbackValue(homeHtml, key);
    if (actual === null) fail(`homepage is missing data-ops="${key}"`);
    if (actual !== value) {
      fail(`homepage fallback for ${key} is ${JSON.stringify(actual)} but generated metrics require ${JSON.stringify(value)}`);
    }
  });
}

function ensureMetricPagesLoadRuntimeData(htmlFiles) {
  const errors = [];
  htmlFiles.forEach((filePath) => {
    const rel = path.relative(root, filePath).replaceAll("\\", "/");
    const html = readText(filePath);
    const usesVerified = html.includes("data-verified=");
    const usesOps = html.includes("data-ops=") || html.includes("data-ops-status=");
    if (!usesVerified && !usesOps) return;

    const hasAppJs = html.includes('/assets/app.js');
    if (!hasAppJs) errors.push(`${rel} uses runtime metrics but does not load /assets/app.js`);
    if (usesVerified && !html.includes('/data/counts.js')) {
      errors.push(`${rel} uses data-verified but does not load /data/counts.js`);
    }
    if (usesOps && !html.includes('/data/ops-metrics.js')) {
      errors.push(`${rel} uses data-ops but does not load /data/ops-metrics.js`);
    }
  });

  if (errors.length) fail(errors.join("\n"));
}

function ensureCountsIntegrity(countsPayload) {
  if (!countsPayload || typeof countsPayload !== "object" || !countsPayload.counts || typeof countsPayload.counts !== "object") {
    fail("verified counts payload is malformed");
  }
  const required = ["sigma", "splunk", "wazuh_xml_files", "wazuh", "ir", "detections"];
  required.forEach((key) => {
    if (!Number.isFinite(countsPayload.counts[key])) fail(`verified counts payload is missing numeric ${key}`);
  });
}

const countsPayload = readJson(countsJsonPath);
const opsPayload = readJson(opsJsonPath);
const homeHtml = readText(homePagePath);
const htmlFiles = collectHtmlFiles(siteDir);

ensureCountsIntegrity(countsPayload);
ensureHomeFallbacksMatchOps(homeHtml, opsPayload.metrics || {});
ensureMetricPagesLoadRuntimeData(htmlFiles);

console.log("Site runtime contract passed.");
