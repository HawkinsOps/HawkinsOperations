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

function extractStatusFallbackValue(html, attr) {
  const pattern = new RegExp(`data-ops-status="${attr}"[^>]*>([^<]+)<`, "i");
  const match = html.match(pattern);
  return match ? match[1].trim() : null;
}

function normalizeComparable(value) {
  return String(value ?? "").trim().replaceAll(",", "");
}

const allowedMetricPlaceholders = new Set(["0", "-", "—", "--", "N/A", "n/a"]);
const allowedStatusPlaceholders = new Set(["UNKNOWN", "-", "—", "--", "N/A"]);

function ensureHomeFallbacksMatchOps(homeHtml, opsMetrics) {
  const requiredAttrs = [
    "stable_coverage_ratio",
    "stable_total_cases",
    "stable_known_fp",
    "stable_escalated",
    "lifetime_total_cases",
    "lifetime_known_fp",
    "lifetime_escalated",
    "reconciliation_mismatch",
    "last_updated",
    "lifetime_last_updated"
  ];

  requiredAttrs.forEach((key) => {
    const actual = extractFallbackValue(homeHtml, key);
    if (actual === null) return;
    if (!String(actual).trim()) {
      fail(`homepage fallback for ${key} is empty`);
    }
  });
}

function ensurePageFallbacksMatchOps(pagePath, opsMetrics) {
  if (!fs.existsSync(pagePath)) return;
  const html = readText(pagePath);
  const rel = path.relative(root, pagePath).replaceAll("\\", "/");
  const metricKeys = [
    "stable_total_cases",
    "stable_auto_closed_benign",
    "stable_known_fp",
    "stable_escalated",
    "stable_coverage_ratio",
    "last_updated",
    "lifetime_total_cases",
    "lifetime_auto_closed_benign",
    "lifetime_known_fp",
    "lifetime_escalated",
    "lifetime_last_updated",
    "coverage_ratio"
  ];
  const statusKeys = ["stable_heartbeat", "heartbeat", "reconciliation"];

  metricKeys.forEach((key) => {
    const actual = extractFallbackValue(html, key);
    if (actual === null) return;
    if (allowedMetricPlaceholders.has(String(actual).trim())) return;
    if (!(key in opsMetrics)) {
      fail(`${rel} uses data-ops="${key}" but ops-metrics payload does not define it`);
    }
    const expected = normalizeComparable(opsMetrics[key]);
    const observed = normalizeComparable(actual);
    if (observed !== expected) {
      fail(`${rel} fallback for ${key} mismatches ops-metrics payload (expected ${opsMetrics[key]}, got ${actual})`);
    }
  });

  statusKeys.forEach((key) => {
    const actual = extractStatusFallbackValue(html, key);
    if (actual === null) return;
    if (allowedStatusPlaceholders.has(String(actual).trim().toUpperCase())) return;
    if (!(key in opsMetrics)) {
      fail(`${rel} uses data-ops-status="${key}" but ops-metrics payload does not define it`);
    }
    const expected = normalizeComparable(opsMetrics[key]).toUpperCase();
    const observed = normalizeComparable(actual).toUpperCase();
    if (observed !== expected) {
      fail(`${rel} fallback status for ${key} mismatches ops-metrics payload (expected ${opsMetrics[key]}, got ${actual})`);
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

function ensureCandidatePagesUseLabeledRuntimeTotals() {
  const candidatePages = [
    path.join(siteDir, "index.html"),
    path.join(siteDir, "proof.html"),
    path.join(siteDir, "resume.html"),
    path.join(siteDir, "start-here.html")
  ];
  const runtimeLabel = "Lifetime processed (runtime snapshot)";

  const errors = [];
  candidatePages.forEach((filePath) => {
    if (!fs.existsSync(filePath)) return;
    const rel = path.relative(root, filePath).replaceAll("\\", "/");
    const html = readText(filePath);

    if (html.includes('data-ops="total_cases"')) {
      errors.push(`${rel} uses legacy data-ops=\"total_cases\" on a candidate-facing page; use stable_total_cases for default display.`);
    }

    const usesRuntimeTotal = html.includes('data-ops="lifetime_total_cases"');
    if (usesRuntimeTotal && !html.includes(runtimeLabel)) {
      errors.push(`${rel} shows lifetime runtime totals without the exact required label: "${runtimeLabel}".`);
    }
  });

  if (errors.length) fail(errors.join("\n"));
}

function ensureProvenanceLabels() {
  const required = ["Public benchmark snapshot", "Runtime snapshot", "Generated at", "Source artifact"];
  const targets = [
    path.join(siteDir, "index.html"),
    path.join(siteDir, "proof.html")
  ];
  const errors = [];

  targets.forEach((filePath) => {
    if (!fs.existsSync(filePath)) return;
    const rel = path.relative(root, filePath).replaceAll("\\", "/");
    const html = readText(filePath);
    required.forEach((label) => {
      if (!html.includes(label)) {
        errors.push(`${rel} is missing provenance label "${label}"`);
      }
    });
  });

  if (errors.length) fail(errors.join("\n"));
}

function ensureCriticalNamingContract() {
  const rules = [
    {
      path: path.join(root, "README.md"),
      require: ["SignalFoundry", "AutoSOC engine"],
      forbid: ["AutoSOC pipeline"]
    },
    {
      path: path.join(siteDir, "index.html"),
      require: ["SignalFoundry"],
      forbid: ["AutoSOC pipeline"]
    },
    {
      path: path.join(siteDir, "resume.html"),
      require: ["SignalFoundry"],
      forbid: ["AutoSOC pipeline"]
    }
  ];
  const errors = [];

  rules.forEach((rule) => {
    if (!fs.existsSync(rule.path)) return;
    const rel = path.relative(root, rule.path).replaceAll("\\", "/");
    const text = readText(rule.path);
    rule.require.forEach((token) => {
      if (!text.includes(token)) errors.push(`${rel} is missing required naming token "${token}"`);
    });
    rule.forbid.forEach((token) => {
      if (text.includes(token)) errors.push(`${rel} still contains disallowed stale naming token "${token}"`);
    });
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
const opsMetrics = opsPayload.metrics || {};

ensureCountsIntegrity(countsPayload);
ensureHomeFallbacksMatchOps(homeHtml, opsMetrics);
ensurePageFallbacksMatchOps(path.join(siteDir, "index.html"), opsMetrics);
ensurePageFallbacksMatchOps(path.join(siteDir, "proof.html"), opsMetrics);
ensurePageFallbacksMatchOps(path.join(siteDir, "case-study-autosoc.html"), opsMetrics);
ensurePageFallbacksMatchOps(path.join(siteDir, "start-here.html"), opsMetrics);
ensureMetricPagesLoadRuntimeData(htmlFiles);
ensureCandidatePagesUseLabeledRuntimeTotals();
ensureProvenanceLabels();
ensureCriticalNamingContract();

console.log("Site runtime contract passed.");
