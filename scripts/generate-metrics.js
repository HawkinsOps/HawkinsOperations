#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const root = process.cwd();
const pipelineRoot = path.resolve("C:\\", "RH", "OPS", "30_Projects", "Active", "AutoSOC", "Output");
const heartbeatPath = path.join(pipelineRoot, "heartbeat.json");
const coveragePath = path.join(pipelineRoot, "coverage_latest.json");
const reconciliationPath = path.join(pipelineRoot, "reconciliation_latest.json");
const ledgerPath = path.join(pipelineRoot, "ledger.json");
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

function expectObject(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`Missing or invalid object field: ${label}`);
  }
  return value;
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

function buildMetricsPayload() {
  const heartbeat = readJson(heartbeatPath);
  const coverage = readJson(coveragePath);
  const reconciliation = readJson(reconciliationPath);
  const ledger = readJson(ledgerPath);
  const verifiedCounts = readJson(verifiedCountsPath);

  const heartbeatCounts = expectObject(heartbeat.counts, "heartbeat.counts");
  const reconciliationCounts = expectObject(reconciliation.counts, "reconciliation.counts");
  const verifiedCountValues = expectObject(verifiedCounts.counts, "verified_counts.counts");
  const ledgerMetrics = expectObject(ledger.metrics, "ledger.metrics");

  const presentHosts = expectFinite(coverage.present_hosts, "coverage.present_hosts");
  const requiredHosts = expectFinite(coverage.required_hosts, "coverage.required_hosts");
  const runtimeCoverageRatio = `${presentHosts}/${requiredHosts}`;
  const runtimeHeartbeat = String(heartbeat.status || "").trim();
  const runtimeLastUpdated = String(heartbeat.end_utc || coverage.generated_utc || heartbeat.generated_utc || "").trim();
  const runtimeLockedDate = formatMmDdYyyy(runtimeLastUpdated);
  const stableTotalCases = expectFinite(ledgerMetrics.total_cases, "ledger.metrics.total_cases");
  const stableAutoClosedBenign = expectFinite(ledgerMetrics.auto_closed_benign, "ledger.metrics.auto_closed_benign");
  const stableKnownFp = expectFinite(ledgerMetrics.auto_closed_known_fp, "ledger.metrics.auto_closed_known_fp");
  const stableEscalated = expectFinite(reconciliationCounts.ledger_escalated_status_ids, "reconciliation.counts.ledger_escalated_status_ids");
  const stableStatement = `Validated active benchmark: ${withCommas(stableTotalCases)}-case corpus with ${withCommas(stableEscalated)} escalation artifacts, ${runtimeCoverageRatio} host coverage, and heartbeat ${runtimeHeartbeat}.`;

  return {
    display_policy: {
      candidate_default: "stable_benchmark",
      runtime_label: "Lifetime processed (runtime snapshot)"
    },
    stable_benchmark: {
      total_cases: stableTotalCases,
      auto_closed_benign: stableAutoClosedBenign,
      known_fp: stableKnownFp,
      escalated: stableEscalated,
      coverage_ratio: runtimeCoverageRatio,
      heartbeat: runtimeHeartbeat,
      locked_date: runtimeLockedDate,
      statement: stableStatement
    },
    lifetime_runtime: {
      total_cases: expectFinite(ledgerMetrics.total_cases, "ledger.metrics.total_cases"),
      auto_closed_benign: expectFinite(ledgerMetrics.auto_closed_benign, "ledger.metrics.auto_closed_benign"),
      known_fp: expectFinite(ledgerMetrics.auto_closed_known_fp, "ledger.metrics.auto_closed_known_fp"),
      escalated: expectFinite(reconciliationCounts.ledger_escalated_status_ids, "reconciliation.counts.ledger_escalated_status_ids"),
      review: expectFinite(ledgerMetrics.review, "ledger.metrics.review"),
      staged_pending: expectFinite(reconciliationCounts.ledger_pending_escalate_ids_staged, "reconciliation.counts.ledger_pending_escalate_ids_staged"),
      coverage_ratio: runtimeCoverageRatio,
      heartbeat: runtimeHeartbeat,
      last_updated: runtimeLastUpdated
    },
    running_totals: {
      total_cases: expectFinite(ledgerMetrics.total_cases, "ledger.metrics.total_cases"),
      auto_closed_benign: expectFinite(ledgerMetrics.auto_closed_benign, "ledger.metrics.auto_closed_benign"),
      known_fp: expectFinite(ledgerMetrics.auto_closed_known_fp, "ledger.metrics.auto_closed_known_fp"),
      escalated: expectFinite(reconciliationCounts.ledger_escalated_status_ids, "reconciliation.counts.ledger_escalated_status_ids"),
      review: expectFinite(ledgerMetrics.review, "ledger.metrics.review"),
      staged_pending: expectFinite(reconciliationCounts.ledger_pending_escalate_ids_staged, "reconciliation.counts.ledger_pending_escalate_ids_staged")
    },
    host_coverage: runtimeCoverageRatio,
    reconciliation_mismatch: expectFinite(reconciliation.mismatch_count, "reconciliation.mismatch_count"),
    heartbeat: runtimeHeartbeat,
    last_updated: runtimeLastUpdated,
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
    }
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
