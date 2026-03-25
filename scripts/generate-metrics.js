#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const root = process.cwd();
const runtimePipelineRoot = path.resolve("C:\\", "RH", "OPS", "30_Projects", "Active", "AutoSOC", "Output");
const repoProofRoot = path.join(root, "proof", "autosoc", "latest");
const verifiedCountsPath = path.join(root, "PROOF_PACK", "verified_counts.json");
const metricsOutPath = path.join(root, "data", "metrics.json");
const metricsShaPath = path.join(root, "data", "metrics.json.sha256");

function readJson(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Missing required JSON file: ${path.relative(root, filePath)}`);
  }
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function expectFinite(value, label) {
  if (!Number.isFinite(value)) {
    throw new Error(`Missing or invalid numeric field: ${label}`);
  }
  return Number(value);
}

function parseLooseNumber(value) {
  if (Number.isFinite(value)) return Number(value);
  if (typeof value !== "string") return NaN;
  const raw = value.trim();
  if (!raw) return NaN;
  if (/^n\/a$/i.test(raw)) return 0;

  const percentMatch = raw.match(/(-?\d+(?:\.\d+)?)\s*%/);
  if (percentMatch) return Number(percentMatch[1]) / 100;

  const cleaned = raw.replace(/[~, +]/g, "").replace(/,/g, "");
  const parsed = Number(cleaned);
  return Number.isFinite(parsed) ? parsed : NaN;
}

function expectFiniteLoose(value, label) {
  const parsed = parseLooseNumber(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(`Missing or invalid numeric field: ${label}`);
  }
  return parsed;
}

function expectObject(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`Missing or invalid object field: ${label}`);
  }
  return value;
}

function resolveInputPath(primaryRoot, fallbackRoot, fileName) {
  const primary = path.join(primaryRoot, fileName);
  if (fs.existsSync(primary)) return primary;
  const fallback = path.join(fallbackRoot, fileName);
  if (fs.existsSync(fallback)) return fallback;
  throw new Error(`Missing required JSON file: ${path.relative(root, primary)}`);
}

function formatMmDdYyyy(isoValue) {
  const date = new Date(isoValue);
  if (Number.isNaN(date.getTime())) return String(isoValue || "");
  const mm = String(date.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(date.getUTCDate()).padStart(2, "0");
  const yyyy = String(date.getUTCFullYear());
  return `${mm}-${dd}-${yyyy}`;
}

function withCommas(value) {
  return new Intl.NumberFormat("en-US").format(Number(value));
}

function toApproxCountString(value) {
  const rounded = Math.round(Number(value) / 100) * 100;
  return `~${withCommas(rounded)}+`;
}

function resolveCanonicalMetricsPath(previousMetrics) {
  if (previousMetrics && typeof previousMetrics.canonical_source === "string") {
    const fromPrevious = path.join(root, previousMetrics.canonical_source.replaceAll("/", path.sep));
    if (fs.existsSync(fromPrevious)) return fromPrevious;
  }
  const sourceOfTruthDir = path.join(root, "source_of_truth");
  if (!fs.existsSync(sourceOfTruthDir)) return "";
  const candidates = fs.readdirSync(sourceOfTruthDir)
    .filter((name) => /^metrics_canonical_\d{4}-\d{2}-\d{2}\.json$/i.test(name))
    .sort();
  if (!candidates.length) return "";
  return path.join(sourceOfTruthDir, candidates[candidates.length - 1]);
}

function buildMetricsPayload() {
  const heartbeatPath = resolveInputPath(runtimePipelineRoot, repoProofRoot, "heartbeat.json");
  const coveragePath = resolveInputPath(runtimePipelineRoot, repoProofRoot, "coverage_latest.json");
  const reconciliationPath = resolveInputPath(runtimePipelineRoot, repoProofRoot, "reconciliation_latest.json");
  const ledgerPath = path.join(runtimePipelineRoot, "ledger.json");

  const heartbeat = readJson(heartbeatPath);
  const coverage = readJson(coveragePath);
  const reconciliation = readJson(reconciliationPath);
  const verifiedCounts = readJson(verifiedCountsPath);
  const previousMetrics = fs.existsSync(metricsOutPath) ? readJson(metricsOutPath) : {};
  const previousRunningTotals = previousMetrics && previousMetrics.running_totals && typeof previousMetrics.running_totals === "object"
    ? previousMetrics.running_totals
    : {};
  const previousStableBenchmark = previousMetrics && previousMetrics.stable_benchmark && typeof previousMetrics.stable_benchmark === "object"
    ? previousMetrics.stable_benchmark
    : {};
  const canonicalSourcePath = resolveCanonicalMetricsPath(previousMetrics);
  const canonicalMetrics = canonicalSourcePath && fs.existsSync(canonicalSourcePath)
    ? readJson(canonicalSourcePath)
    : {};

  const heartbeatCounts = expectObject(heartbeat.counts, "heartbeat.counts");
  const reconciliationCounts = expectObject(reconciliation.counts, "reconciliation.counts");
  const verifiedCountValues = expectObject(verifiedCounts.counts, "verified_counts.counts");
  const ledgerMetrics = fs.existsSync(ledgerPath)
    ? expectObject(readJson(ledgerPath).metrics, "ledger.metrics")
    : previousRunningTotals;

  const presentHosts = expectFinite(coverage.present_hosts, "coverage.present_hosts");
  const requiredHosts = expectFinite(coverage.required_hosts, "coverage.required_hosts");
  const runtimeCoverageRatio = `${presentHosts}/${requiredHosts}`;
  const runtimeHeartbeat = String(heartbeat.status || "").trim();
  const runtimeLastUpdated = String(heartbeat.end_utc || coverage.generated_utc || heartbeat.generated_utc || previousMetrics.last_updated || "").trim();
  const runtimeLockedDate = formatMmDdYyyy(runtimeLastUpdated);
  const stableCoverageRatio = String(canonicalMetrics.hosts_reporting || previousStableBenchmark.coverage_ratio || previousMetrics.host_coverage || runtimeCoverageRatio || "").trim() || runtimeCoverageRatio;
  const stableHeartbeat = String(canonicalMetrics.heartbeat || previousStableBenchmark.heartbeat || previousMetrics.heartbeat || runtimeHeartbeat || "").trim() || runtimeHeartbeat;
  const stableLastUpdatedIso = String(
    (canonicalMetrics.date ? `${canonicalMetrics.date}T00:00:00Z` : "")
      || previousMetrics.last_updated
      || runtimeLastUpdated
      || ""
  ).trim() || runtimeLastUpdated;
  const stableLockedDate = String(previousStableBenchmark.locked_date || formatMmDdYyyy(stableLastUpdatedIso) || runtimeLockedDate).trim() || runtimeLockedDate;
  const stableTotalCases = expectFiniteLoose(
    Number.isFinite(canonicalMetrics.total_cases) ? canonicalMetrics.total_cases : ledgerMetrics.total_cases,
    "ledger.metrics.total_cases"
  );
  const autoClosedRaw = ledgerMetrics.auto_closed_benign;
  let stableAutoClosedBenign = parseLooseNumber(autoClosedRaw);
  if (Number.isFinite(stableAutoClosedBenign) && stableAutoClosedBenign > 0 && stableAutoClosedBenign < 1) {
    stableAutoClosedBenign = Math.round(stableTotalCases * stableAutoClosedBenign);
  }
  stableAutoClosedBenign = expectFinite(stableAutoClosedBenign, "ledger.metrics.auto_closed_benign");
  const stableKnownFp = expectFiniteLoose(
    Number.isFinite(ledgerMetrics.auto_closed_known_fp) ? ledgerMetrics.auto_closed_known_fp : ledgerMetrics.known_fp,
    "ledger.metrics.auto_closed_known_fp"
  );
  const stableEscalated = expectFinite(reconciliationCounts.ledger_escalated_status_ids, "reconciliation.counts.ledger_escalated_status_ids");
  const runtimeReview = expectFinite(
    expectFiniteLoose(Number.isFinite(ledgerMetrics.review) ? ledgerMetrics.review : previousRunningTotals.review, "ledger.metrics.review"),
    "ledger.metrics.review"
  );
  const runtimeStagedPending = expectFinite(
    Number.isFinite(reconciliationCounts.ledger_pending_escalate_ids_staged)
      ? reconciliationCounts.ledger_pending_escalate_ids_staged
      : expectFiniteLoose(previousRunningTotals.staged_pending, "reconciliation.counts.ledger_pending_escalate_ids_staged"),
    "reconciliation.counts.ledger_pending_escalate_ids_staged"
  );
  const stableAutoCloseDisplay = String(canonicalMetrics.auto_close_rate_label || `~${Math.round((stableAutoClosedBenign / Math.max(stableTotalCases, 1)) * 100)}%`);
  const stableEscalatedDisplay = String(canonicalMetrics.escalations_label || toApproxCountString(stableEscalated));
  const stableStatement = String(previousStableBenchmark.statement || "").trim()
    || `Validated active benchmark: ${withCommas(stableTotalCases)}-case corpus with ${stableEscalatedDisplay} escalation artifacts, ${stableCoverageRatio} host coverage, and heartbeat ${stableHeartbeat}.`;

  return {
    display_policy: {
      candidate_default: "stable_benchmark",
      runtime_label: "Lifetime processed (runtime snapshot)"
    },
    stable_benchmark: {
      total_cases: stableTotalCases,
      auto_closed_benign: stableAutoCloseDisplay,
      known_fp: stableKnownFp === 0 ? "N/A" : withCommas(stableKnownFp),
      escalated: stableEscalatedDisplay,
      coverage_ratio: stableCoverageRatio,
      heartbeat: stableHeartbeat,
      locked_date: stableLockedDate,
      statement: stableStatement
    },
    lifetime_runtime: {
      total_cases: stableTotalCases,
      auto_closed_benign: stableAutoCloseDisplay,
      known_fp: stableKnownFp === 0 ? "N/A" : withCommas(stableKnownFp),
      escalated: stableEscalatedDisplay,
      review: runtimeReview === 0 ? "N/A" : runtimeReview,
      staged_pending: runtimeStagedPending === 0 ? "N/A" : runtimeStagedPending,
      coverage_ratio: stableCoverageRatio,
      heartbeat: stableHeartbeat,
      last_updated: stableLastUpdatedIso
    },
    running_totals: {
      total_cases: stableTotalCases,
      auto_closed_benign: stableAutoClosedBenign,
      known_fp: stableKnownFp,
      escalated: expectFinite(reconciliationCounts.ledger_escalated_status_ids, "reconciliation.counts.ledger_escalated_status_ids"),
      review: runtimeReview,
      staged_pending: runtimeStagedPending
    },
    host_coverage: stableCoverageRatio,
    reconciliation_mismatch: expectFinite(reconciliation.mismatch_count, "reconciliation.mismatch_count"),
    heartbeat: stableHeartbeat,
    last_updated: stableLastUpdatedIso,
    stress_test_window: {
      profile: "active_pipeline_snapshot",
      baseline_window: "C:/RH/OPS/30_Projects/Active/AutoSOC/Output",
      queue_backlog_target: 10000,
      latency_targets_ms: {
        per_event_under_load: 200,
        with_backlog: 500
      },
      simulated_rule_pressure: {
        rule_60227_pct_increase: 200,
        rule_92151_pct_increase: 100,
        sysmon_module_load_noise_pct_increase: 300
      }
    },
    detection_inventory: {
      sigma: expectFinite(verifiedCountValues.sigma, "verified_counts.counts.sigma"),
      wazuh_files: expectFinite(verifiedCountValues.wazuh_xml_files, "verified_counts.counts.wazuh_xml_files"),
      wazuh_rule_blocks: expectFinite(verifiedCountValues.wazuh, "verified_counts.counts.wazuh"),
      splunk: expectFinite(verifiedCountValues.splunk, "verified_counts.counts.splunk"),
      ir_playbooks: expectFinite(verifiedCountValues.ir, "verified_counts.counts.ir")
    },
    canonical_source: canonicalSourcePath ? path.relative(root, canonicalSourcePath).replaceAll("\\", "/") : undefined
  };
}

function sha256Hex(input) {
  return crypto.createHash("sha256").update(input).digest("hex");
}

const payload = buildMetricsPayload();
const json = `${JSON.stringify(payload, null, 2)}\n`;
fs.mkdirSync(path.dirname(metricsOutPath), { recursive: true });
fs.writeFileSync(metricsOutPath, json, "utf8");
fs.writeFileSync(metricsShaPath, `${sha256Hex(json)}  data/metrics.json\n`, "utf8");

console.log(`Generated ${path.relative(root, metricsOutPath)}`);
console.log(`Generated ${path.relative(root, metricsShaPath)}`);
