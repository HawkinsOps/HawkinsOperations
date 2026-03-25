#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const root = process.cwd();
const now = new Date().toISOString();

const metricsPath = path.join(root, "data", "metrics.json");
const runMetricsPath = path.join(root, "proof", "autosoc", "latest", "run_metrics_latest.json");
const reconciliationPath = path.join(root, "proof", "autosoc", "latest", "reconciliation_latest.json");
const coveragePath = path.join(root, "proof", "autosoc", "latest", "coverage_latest.json");

const splunkProofPath = path.join(
  root,
  "content",
  "lab",
  "proxmox",
  "vms",
  "104",
  "splunk",
  "exports",
  "WAZUH_SPLUNK_PIPELINE_PROOF_2026-03-20.md"
);
const grafanaProofPath = path.join(root, "proof", "grafana", "latest.md");

const proofValidationJsonPath = path.join(root, "proof", "validation", "latest.json");
const proofValidationMdPath = path.join(root, "proof", "validation", "latest.md");
const siteValidationJsonPath = path.join(root, "site", "proof", "validation", "latest.json");
const siteValidationMdPath = path.join(root, "site", "proof", "validation", "latest.md");

const proofQualityJsonPath = path.join(root, "proof", "quality", "latest.json");
const proofQualityMdPath = path.join(root, "proof", "quality", "latest.md");
const siteQualityJsonPath = path.join(root, "site", "proof", "quality", "latest.json");
const siteQualityMdPath = path.join(root, "site", "proof", "quality", "latest.md");

function readJson(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Missing required input: ${path.relative(root, filePath)}`);
  }
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function pct(numerator, denominator) {
  if (!Number.isFinite(numerator) || !Number.isFinite(denominator) || denominator <= 0) return 0;
  return Number(((numerator / denominator) * 100).toFixed(2));
}

function parseRatio(value) {
  const match = String(value || "").trim().match(/^(\d+)\s*\/\s*(\d+)$/);
  if (!match) return { numerator: 0, denominator: 0 };
  return { numerator: Number(match[1]), denominator: Number(match[2]) };
}

function writeJson(filePath, payload) {
  ensureDir(filePath);
  fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function writeText(filePath, text) {
  ensureDir(filePath);
  fs.writeFileSync(filePath, text, "utf8");
}

function buildValidationLane() {
  const metrics = readJson(metricsPath);
  const runMetrics = readJson(runMetricsPath);
  const reconciliation = readJson(reconciliationPath);
  const coverage = readJson(coveragePath);

  const coverageRatio = String(metrics.host_coverage || `${Number(coverage.present_hosts)}/${Number(coverage.required_hosts)}`);
  const coverageParsed = parseRatio(coverageRatio);

  const checks = [
    {
      id: "heartbeat",
      status: metrics.heartbeat === "SUCCESS" ? "PASS" : "FAIL",
      value: String(metrics.heartbeat || "UNKNOWN"),
      source: "data/metrics.json"
    },
    {
      id: "reconciliation_mismatch",
      status: Number(reconciliation.mismatch_count) === 0 ? "PASS" : "FAIL",
      value: Number(reconciliation.mismatch_count),
      source: "proof/autosoc/latest/reconciliation_latest.json"
    },
    {
      id: "coverage_required_hosts",
      status: coverageParsed.denominator > 0 && coverageParsed.numerator >= coverageParsed.denominator ? "PASS" : "WATCH",
      value: coverageRatio,
      source: "data/metrics.json"
    },
    {
      id: "pipeline_last_status",
      status: String(runMetrics.status || "").toUpperCase() === "SUCCESS" ? "PASS" : "FAIL",
      value: String(runMetrics.status || "UNKNOWN"),
      source: "proof/autosoc/latest/run_metrics_latest.json"
    },
    {
      id: "splunk_ingest_proof_present",
      status: fs.existsSync(splunkProofPath) ? "PASS" : "FAIL",
      value: path.relative(root, splunkProofPath).replaceAll("\\", "/"),
      source: "filesystem"
    },
    {
      id: "grafana_proof_present",
      status: fs.existsSync(grafanaProofPath) ? "PASS" : "FAIL",
      value: path.relative(root, grafanaProofPath).replaceAll("\\", "/"),
      source: "filesystem"
    }
  ];

  const passCount = checks.filter((check) => check.status === "PASS").length;
  const failCount = checks.filter((check) => check.status === "FAIL").length;
  const watchCount = checks.filter((check) => check.status === "WATCH").length;
  const payload = {
    generated_utc: now,
    validation_window: "rolling_latest_artifacts",
    suite: "continuous-detection-validation",
    summary: {
      checks_total: checks.length,
      checks_passed: passCount,
      checks_watch: watchCount,
      checks_failed: failCount,
      pass_rate_pct: pct(passCount, checks.length),
      overall_status: failCount > 0 ? "FAIL" : watchCount > 0 ? "WATCH" : "PASS"
    },
    checks
  };

  const md = [
    "# Continuous Detection Validation",
    "",
    `- Generated (UTC): ${payload.generated_utc}`,
    `- Suite: ${payload.suite}`,
    `- Overall status: ${payload.summary.overall_status}`,
    `- Checks passed: ${payload.summary.checks_passed}/${payload.summary.checks_total} (${payload.summary.pass_rate_pct}%)`,
    "",
    "## Checks",
    "",
    "| Check | Status | Value | Source |",
    "|---|---|---|---|",
    ...checks.map((check) => `| ${check.id} | ${check.status} | ${check.value} | \`${check.source}\` |`)
  ].join("\n");

  return { payload, md };
}

function buildQualityLane() {
  const metrics = readJson(metricsPath);
  const totals = metrics.running_totals || {};
  const totalCases = Number(totals.total_cases || 0);
  const benign = Number(totals.auto_closed_benign || 0);
  const knownFp = Number(totals.known_fp || 0);
  const escalated = Number(totals.escalated || 0);
  const review = Number(totals.review || 0);
  const stagedPending = Number(totals.staged_pending || 0);
  const mismatch = Number(metrics.reconciliation_mismatch || 0);

  const metricsList = [
    { id: "auto_close_benign_pct", value: pct(benign, totalCases), target: ">= 35", status: pct(benign, totalCases) >= 35 ? "PASS" : "WATCH" },
    { id: "known_fp_pct", value: pct(knownFp, totalCases), target: "<= 45", status: pct(knownFp, totalCases) <= 45 ? "PASS" : "WATCH" },
    { id: "escalation_pct", value: pct(escalated, totalCases), target: ">= 3", status: pct(escalated, totalCases) >= 3 ? "PASS" : "WATCH" },
    { id: "review_backlog_pct", value: pct(review, totalCases), target: "<= 20", status: pct(review, totalCases) <= 20 ? "PASS" : "WATCH" },
    { id: "staged_pending_pct", value: pct(stagedPending, totalCases), target: "<= 1", status: pct(stagedPending, totalCases) <= 1 ? "PASS" : "WATCH" },
    { id: "reconciliation_mismatch_count", value: mismatch, target: "0", status: mismatch === 0 ? "PASS" : "FAIL" }
  ];

  const watchOrFail = metricsList.filter((metric) => metric.status !== "PASS").length;
  const payload = {
    generated_utc: now,
    scorecard_window: "lifetime_runtime_snapshot",
    source_metrics: "data/metrics.json",
    totals: {
      total_cases: totalCases,
      auto_closed_benign: benign,
      known_fp: knownFp,
      escalated,
      review,
      staged_pending: stagedPending
    },
    scorecard: {
      status: watchOrFail === 0 ? "PASS" : "WATCH",
      metrics: metricsList
    }
  };

  const md = [
    "# Alert Quality Scorecard",
    "",
    `- Generated (UTC): ${payload.generated_utc}`,
    `- Window: ${payload.scorecard_window}`,
    `- Overall status: ${payload.scorecard.status}`,
    `- Source: \`${payload.source_metrics}\``,
    "",
    "## Totals",
    "",
    `- Total cases: ${totalCases}`,
    `- Auto-closed benign: ${benign}`,
    `- Known false positive: ${knownFp}`,
    `- Escalated: ${escalated}`,
    `- Review backlog: ${review}`,
    `- Staged pending: ${stagedPending}`,
    "",
    "## Scorecard",
    "",
    "| Metric | Value | Target | Status |",
    "|---|---:|---|---|",
    ...metricsList.map((metric) => `| ${metric.id} | ${metric.value} | ${metric.target} | ${metric.status} |`)
  ].join("\n");

  return { payload, md };
}

function main() {
  const validation = buildValidationLane();
  writeJson(proofValidationJsonPath, validation.payload);
  writeJson(siteValidationJsonPath, validation.payload);
  writeText(proofValidationMdPath, `${validation.md}\n`);
  writeText(siteValidationMdPath, `${validation.md}\n`);

  const quality = buildQualityLane();
  writeJson(proofQualityJsonPath, quality.payload);
  writeJson(siteQualityJsonPath, quality.payload);
  writeText(proofQualityMdPath, `${quality.md}\n`);
  writeText(siteQualityMdPath, `${quality.md}\n`);

  console.log(`Generated ${path.relative(root, proofValidationJsonPath)}`);
  console.log(`Generated ${path.relative(root, proofValidationMdPath)}`);
  console.log(`Generated ${path.relative(root, siteValidationJsonPath)}`);
  console.log(`Generated ${path.relative(root, siteValidationMdPath)}`);
  console.log(`Generated ${path.relative(root, proofQualityJsonPath)}`);
  console.log(`Generated ${path.relative(root, proofQualityMdPath)}`);
  console.log(`Generated ${path.relative(root, siteQualityJsonPath)}`);
  console.log(`Generated ${path.relative(root, siteQualityMdPath)}`);
}

main();
