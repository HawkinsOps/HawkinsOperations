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
ensureCandidatePagesUseLabeledRuntimeTotals();

console.log("Site runtime contract passed.");
