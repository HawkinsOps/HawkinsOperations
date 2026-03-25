#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const childProcess = require("child_process");

const root = process.cwd();
const srcPath = path.join(root, "PROOF_PACK", "verified_counts.json");
const metricsPath = path.join(root, "data", "metrics.json");
const canonicalOutPath = path.join(root, "PROOF_PACK", "verified_counts.json");
const siteOutPath = path.join(root, "site", "assets", "verified-counts.json");
const siteCountsJsOutPath = path.join(root, "site", "data", "counts.js");
const siteOpsJsonOutPath = path.join(root, "site", "assets", "data", "ops-metrics.json");
const siteOpsJsOutPath = path.join(root, "site", "data", "ops-metrics.js");
const detectionsDataPath = path.join(root, "site", "assets", "data", "detections.json");
const withProofPack = process.argv.includes("--with-proof-pack");
const regenerateMetricsFlag = process.argv.includes("--regenerate-metrics");

function regenerateMetrics() {
  const result = childProcess.spawnSync(process.execPath, [path.join(root, "scripts", "generate-metrics.js")], {
    cwd: root,
    stdio: "inherit"
  });
  if (result.status !== 0) {
    throw new Error("Failed to regenerate data/metrics.json from committed proof artifacts");
  }
}

function parseVerifiedCountsJson(rawJson) {
  const parsed = JSON.parse(rawJson);
  if (!parsed || typeof parsed !== "object" || !parsed.counts || typeof parsed.counts !== "object") {
    throw new Error("Missing counts object in PROOF_PACK/verified_counts.json");
  }

  const requiredKeys = ["sigma", "splunk", "wazuh_xml_files", "wazuh", "ir", "detections"];
  for (const key of requiredKeys) {
    if (!Number.isFinite(parsed.counts[key])) {
      throw new Error(`Missing or invalid numeric count '${key}' in PROOF_PACK/verified_counts.json`);
    }
  }

  const counts = {
    sigma: Number(parsed.counts.sigma),
    splunk: Number(parsed.counts.splunk),
    wazuh_xml_files: Number(parsed.counts.wazuh_xml_files),
    wazuh: Number(parsed.counts.wazuh),
    ir: Number(parsed.counts.ir),
    detections: Number(parsed.counts.detections)
  };

  return {
    source_path: "PROOF_PACK/verified_counts.json",
    generated_at_utc: parsed.generated_at_utc || new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    counts,
    source_refs: parsed.source_refs && typeof parsed.source_refs === "object" ? parsed.source_refs : {}
  };
}

function toMmDdYyyy(isoString) {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return isoString;
  const mm = String(date.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(date.getUTCDate()).padStart(2, "0");
  const yyyy = String(date.getUTCFullYear());
  return `${mm}-${dd}-${yyyy}`;
}

function parseLooseNumeric(value, label, options = {}) {
  const { totalForPercent = null, defaultValue = NaN } = options;
  if (Number.isFinite(value)) return Number(value);
  if (value === null || value === undefined) return defaultValue;

  const raw = String(value).trim();
  if (!raw) return defaultValue;
  if (/^n\/a$/i.test(raw)) return 0;

  const percentMatch = raw.match(/(-?\d+(?:\.\d+)?)\s*%/);
  if (percentMatch) {
    if (!Number.isFinite(totalForPercent)) return defaultValue;
    const ratio = Number(percentMatch[1]) / 100;
    return Math.round(Number(totalForPercent) * ratio);
  }

  const cleaned = raw.replace(/[~, +]/g, "").replace(/,/g, "");
  const parsed = Number(cleaned);
  if (Number.isFinite(parsed)) return parsed;

  return defaultValue;
}

function parseMetricsJson(rawJson) {
  const parsed = JSON.parse(rawJson);
  if (!parsed || typeof parsed !== "object") {
    throw new Error("Invalid data/metrics.json payload");
  }
  const stableBenchmark = parsed.stable_benchmark;
  const lifetimeRuntime = parsed.lifetime_runtime;
  const runningTotals = parsed.running_totals;
  const detectionInventory = parsed.detection_inventory;
  if (!stableBenchmark || typeof stableBenchmark !== "object") {
    throw new Error("Missing stable_benchmark object in data/metrics.json");
  }
  if (!lifetimeRuntime || typeof lifetimeRuntime !== "object") {
    throw new Error("Missing lifetime_runtime object in data/metrics.json");
  }
  if (!runningTotals || typeof runningTotals !== "object") {
    throw new Error("Missing running_totals object in data/metrics.json");
  }
  if (!detectionInventory || typeof detectionInventory !== "object") {
    throw new Error("Missing detection_inventory object in data/metrics.json");
  }

  const requiredNumericTotals = [
    "total_cases",
    "auto_closed_benign",
    "known_fp",
    "escalated",
    "review",
    "staged_pending"
  ];
  const parsedRunningTotals = {};
  for (const key of requiredNumericTotals) {
    const parsed = parseLooseNumeric(runningTotals[key], `running_totals.${key}`, {
      totalForPercent: parseLooseNumeric(runningTotals.total_cases, "running_totals.total_cases")
    });
    if (!Number.isFinite(parsed)) {
      throw new Error(`Missing or invalid numeric total '${key}' in data/metrics.json`);
    }
    parsedRunningTotals[key] = parsed;
  }

  const requiredInventoryKeys = ["sigma", "wazuh_files", "wazuh_rule_blocks", "splunk", "ir_playbooks"];
  for (const key of requiredInventoryKeys) {
    if (!Number.isFinite(detectionInventory[key])) {
      throw new Error(`Missing or invalid detection inventory '${key}' in data/metrics.json`);
    }
  }

  const totalCases = parsedRunningTotals.total_cases;
  const autoCloseCount = parsedRunningTotals.auto_closed_benign + parsedRunningTotals.known_fp;
  const autoCloseRate = totalCases > 0 ? `${((autoCloseCount / totalCases) * 100).toFixed(2)}%` : "0.00%";
  const stableTotalCases = parseLooseNumeric(stableBenchmark.total_cases, "stable_benchmark.total_cases");
  const stableAutoClosed = parseLooseNumeric(stableBenchmark.auto_closed_benign, "stable_benchmark.auto_closed_benign", {
    totalForPercent: stableTotalCases
  });
  const stableKnownFp = parseLooseNumeric(stableBenchmark.known_fp, "stable_benchmark.known_fp");
  const stableEscalated = parseLooseNumeric(stableBenchmark.escalated, "stable_benchmark.escalated");
  const stableAutoCloseCount = stableAutoClosed + stableKnownFp;
  const stableAutoCloseRate = stableTotalCases > 0
    ? `${((stableAutoCloseCount / stableTotalCases) * 100).toFixed(2)}%`
    : "0.00%";
  const reconciliationMismatch = Number(parsed.reconciliation_mismatch);
  const reconciliationBasisCount = parsedRunningTotals.escalated;
  const reconciliationReconciledCount = Math.max(reconciliationBasisCount - reconciliationMismatch, 0);
  const reconciliationMismatchRate = reconciliationBasisCount > 0
    ? `${((reconciliationMismatch / reconciliationBasisCount) * 100).toFixed(2)}%`
    : "0.00%";
  const reconciliationSuccessRate = reconciliationBasisCount > 0
    ? `${((reconciliationReconciledCount / reconciliationBasisCount) * 100).toFixed(2)}%`
    : "0.00%";

  return {
    generated_at_utc: parsed.last_updated,
    source_note: "Canonical SignalFoundry metrics generated from data/metrics.json.",
    display_policy: parsed.display_policy && typeof parsed.display_policy === "object"
      ? parsed.display_policy
      : {
          candidate_default: "stable_benchmark",
          runtime_label: "Lifetime processed (runtime snapshot)"
        },
    stable_benchmark: {
      total_cases: stableTotalCases,
      auto_closed_benign: String(stableBenchmark.auto_closed_benign || stableAutoCloseRate),
      known_fp: String(stableBenchmark.known_fp || "N/A"),
      escalated: String(stableBenchmark.escalated || String(stableEscalated)),
      coverage_ratio: String(stableBenchmark.coverage_ratio || ""),
      heartbeat: String(stableBenchmark.heartbeat || ""),
      locked_date: String(stableBenchmark.locked_date || toMmDdYyyy(String(parsed.last_updated || ""))),
      statement: String(stableBenchmark.statement || "")
    },
    lifetime_runtime: {
      total_cases: parseLooseNumeric(lifetimeRuntime.total_cases, "lifetime_runtime.total_cases"),
      auto_closed_benign: String(lifetimeRuntime.auto_closed_benign || autoCloseRate),
      known_fp: String(lifetimeRuntime.known_fp || "N/A"),
      escalated: String(lifetimeRuntime.escalated || String(parsedRunningTotals.escalated)),
      review: parseLooseNumeric(lifetimeRuntime.review, "lifetime_runtime.review", { defaultValue: 0 }),
      staged_pending: parseLooseNumeric(lifetimeRuntime.staged_pending, "lifetime_runtime.staged_pending", { defaultValue: 0 }),
      coverage_ratio: String(lifetimeRuntime.coverage_ratio || parsed.host_coverage || ""),
      heartbeat: String(lifetimeRuntime.heartbeat || parsed.heartbeat || ""),
      last_updated: toMmDdYyyy(String(lifetimeRuntime.last_updated || parsed.last_updated || ""))
    },
    metrics: {
      total_cases: stableTotalCases,
      auto_close_rate: stableAutoCloseRate,
      escalated: stableEscalated,
      review: parsedRunningTotals.review,
      staged_pending: parsedRunningTotals.staged_pending,
      known_fp: stableKnownFp,
      auto_closed_benign: stableAutoClosed,
      reconciliation: reconciliationMismatch === 0 ? "PASS" : "FAIL",
      reconciliation_mismatch: reconciliationMismatch,
      reconciliation_basis_count: reconciliationBasisCount,
      reconciliation_reconciled_count: reconciliationReconciledCount,
      reconciliation_mismatch_rate: reconciliationMismatchRate,
      reconciliation_success_rate: reconciliationSuccessRate,
      heartbeat: String(stableBenchmark.heartbeat || parsed.heartbeat || ""),
      coverage_ratio: String(stableBenchmark.coverage_ratio || parsed.host_coverage || ""),
      coverage_status: String(stableBenchmark.coverage_ratio || parsed.host_coverage || "").trim() === "8/8" ? "PASS" : "FAIL",
      stable_locked_date: String(stableBenchmark.locked_date || toMmDdYyyy(String(parsed.last_updated || ""))),
      last_updated: String(stableBenchmark.locked_date || toMmDdYyyy(String(parsed.last_updated || ""))),
      stable_total_cases: stableTotalCases,
      stable_auto_closed_benign: String(stableBenchmark.auto_closed_benign || stableAutoCloseRate),
      stable_known_fp: String(stableBenchmark.known_fp || "N/A"),
      stable_escalated: String(stableBenchmark.escalated || String(stableEscalated)),
      stable_coverage_ratio: String(stableBenchmark.coverage_ratio || ""),
      stable_heartbeat: String(stableBenchmark.heartbeat || ""),
      stable_statement: String(stableBenchmark.statement || ""),
      lifetime_total_cases: totalCases,
      lifetime_auto_closed_benign: String(lifetimeRuntime.auto_closed_benign || autoCloseRate),
      lifetime_known_fp: String(lifetimeRuntime.known_fp || "N/A"),
      lifetime_escalated: String(lifetimeRuntime.escalated || String(parsedRunningTotals.escalated)),
      lifetime_auto_close_rate: autoCloseRate,
      lifetime_label: "Lifetime processed (runtime snapshot)",
      lifetime_last_updated: toMmDdYyyy(parsed.last_updated),
      sigma: Number(detectionInventory.sigma),
      splunk: Number(detectionInventory.splunk),
      wazuh: Number(detectionInventory.wazuh_rule_blocks),
      ir: Number(detectionInventory.ir_playbooks)
    }
  };
}

function writeSiteCountsJs(payload) {
  const countsPayload = {
    generated_at_utc: payload.generated_at_utc,
    source_path: payload.source_path,
    last_verified_utc: payload.generated_at_utc,
    counts: payload.counts,
    detections: payload.counts.detections,
    sigma: payload.counts.sigma,
    wazuh: payload.counts.wazuh,
    splunk: payload.counts.splunk,
    playbooks: payload.counts.ir,
    ir: payload.counts.ir,
    wazuh_xml_files: payload.counts.wazuh_xml_files
  };
  const js = `window.HAWKINSOPS_COUNTS = ${JSON.stringify(countsPayload, null, 2)};\n`;
  fs.mkdirSync(path.dirname(siteCountsJsOutPath), { recursive: true });
  fs.writeFileSync(siteCountsJsOutPath, js, "utf8");
}

function syncDetectionsData(counts) {
  if (!fs.existsSync(detectionsDataPath)) return;
  const raw = fs.readFileSync(detectionsDataPath, "utf8");
  const parsed = JSON.parse(raw);
  if (!parsed || !Array.isArray(parsed.detections)) return;

  const map = {
    sigma: counts.sigma,
    wazuh: counts.wazuh,
    splunk: counts.splunk,
    "ir-playbooks": counts.ir
  };

  let changed = false;
  parsed.detections.forEach((entry) => {
    if (!entry || typeof entry !== "object") return;
    const next = map[entry.id];
    if (typeof next === "number" && entry.count !== next) {
      entry.count = next;
      changed = true;
    }
  });

  if (changed) {
    fs.writeFileSync(detectionsDataPath, `${JSON.stringify(parsed, null, 2)}\n`, "utf8");
  }
}

function writeSiteOpsMetrics(payload) {
  fs.mkdirSync(path.dirname(siteOpsJsonOutPath), { recursive: true });
  fs.mkdirSync(path.dirname(siteOpsJsOutPath), { recursive: true });
  fs.writeFileSync(siteOpsJsonOutPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  fs.writeFileSync(siteOpsJsOutPath, `window.HAWKINSOPS_OPS_METRICS = ${JSON.stringify(payload, null, 2)};\n`, "utf8");
}

if (!fs.existsSync(srcPath)) {
  console.error(`Missing source file: ${srcPath}`);
  process.exit(1);
}

if (regenerateMetricsFlag) {
  regenerateMetrics();
}

const src = fs.readFileSync(srcPath, "utf8");
const parsed = parseVerifiedCountsJson(src);
if (!fs.existsSync(metricsPath)) {
  console.error(`Missing metrics source file: ${metricsPath}`);
  process.exit(1);
}
const metricsRaw = fs.readFileSync(metricsPath, "utf8");
const metricsPayload = parseMetricsJson(metricsRaw);

const payload = {
  generated_at_utc: parsed.generated_at_utc,
  source_path: "PROOF_PACK/verified_counts.json",
  counts: parsed.counts,
  source_refs: parsed.source_refs
};

fs.mkdirSync(path.dirname(canonicalOutPath), { recursive: true });
fs.mkdirSync(path.dirname(siteOutPath), { recursive: true });
fs.writeFileSync(siteOutPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
writeSiteCountsJs(payload);
syncDetectionsData(parsed.counts);
writeSiteOpsMetrics(metricsPayload);

if (withProofPack) {
  fs.writeFileSync(canonicalOutPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  console.log(`Generated ${path.relative(root, canonicalOutPath)}`);
}
console.log(`Generated ${path.relative(root, siteOutPath)}`);
console.log(`Generated ${path.relative(root, siteCountsJsOutPath)}`);
console.log(`Generated ${path.relative(root, siteOpsJsonOutPath)}`);
console.log(`Generated ${path.relative(root, siteOpsJsOutPath)}`);
console.log(`Synced ${path.relative(root, detectionsDataPath)}`);
