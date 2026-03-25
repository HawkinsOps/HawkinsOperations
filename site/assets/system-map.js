/* system-map.js v2 — SignalFoundry living system topology
   Clarity pass: strict hierarchy, layer separation, directional flow,
   explicit pass/fail fork, mesh overlay, governance boundary. */

(function () {
  'use strict';

  // ── NODE DATA ──
  // Positions are % of container. Grouped by layer with clear spatial separation.
  var nodes = [
    // === LAYER: CORE (center, dominant) ===
    { id: 'sf-core', label: 'SignalFoundry', icon: 'SF\nCORE', x: 48, y: 44, size: 'core', color: 'c-core', delay: 2,
      panel: { title: 'SignalFoundry Core', role: 'Central Orchestration Engine',
        metrics: [['Cases processed', '49,774'], ['Auto-close rate', '~89%'], ['Escalated', '2,478'], ['Reconciliation', 'PASS (0)'], ['Heartbeat', 'SUCCESS']],
        desc: 'Policy-driven triage engine. Receives all ingested alerts, applies deterministic disposition logic, routes to evidence assembly or auto-close. Every case gets a disposition. No alert is silently dropped.' }},

    // === LAYER: INGESTION (far left) ===
    { id: 'wazuh-mgr', label: 'Wazuh Manager', icon: 'WZ', x: 22, y: 44, size: 'major', color: 'c-edge', delay: 3,
      panel: { title: 'Wazuh Manager', role: 'SIEM / Alert Ingestion',
        metrics: [['Agents', '8/8 reporting'], ['Custom rules', '100000+ range'], ['Role', 'Alert collection + rule matching']],
        desc: 'Central collection point for all endpoint telemetry. Matches against Wazuh XML rules and forwards structured alerts to SignalFoundry.' }},
    { id: 'ep-1', label: 'dc01',      x: 4, y: 20, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-2', label: 'win10-01',  x: 4, y: 32, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-3', label: 'win10-02',  x: 4, y: 44, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-4', label: 'linux-web', x: 4, y: 56, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-5', label: 'linux-db',  x: 4, y: 68, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-6', label: 'honeypot',  x: 8, y: 14, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-7', label: 'splunk-fwd',x: 8, y: 74, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-8', label: 'wazuh-agt', x: 8, y: 26, size: 'cluster', color: 'c-edge', delay: 3 },

    // === LAYER: DETECTION ENGINEERING (upper-left, distinct from ingestion) ===
    { id: 'sigma', label: 'Sigma Rules', icon: '103', x: 28, y: 14, size: 'major', color: 'c-detect', delay: 4,
      panel: { title: 'Sigma Detection Rules', role: 'Detection Engineering Layer',
        metrics: [['Rules', '103'], ['Tactics', '9 MITRE ATT&CK'], ['Format', 'YAML portable']],
        desc: 'Behavioral detection rules mapped to MITRE ATT&CK. Process creation, lateral movement, credential access, persistence. These are the brain of the detection layer.' }},
    { id: 'wazuh-xml', label: 'Wazuh XML', icon: '28', x: 18, y: 10, size: 'minor', color: 'c-detect', delay: 4 },
    { id: 'ir-playbooks', label: 'IR Playbooks', icon: '10', x: 38, y: 8, size: 'minor', color: 'c-detect', delay: 4 },
    { id: 'honeypot-intel', label: 'Honeypot Intel', icon: 'HI', x: 14, y: 4, size: 'cluster', color: 'c-detect', delay: 4 },

    // === LAYER: SIEM / ANALYSIS (upper-right) ===
    { id: 'splunk', label: 'Splunk', icon: 'SPL', x: 72, y: 14, size: 'major', color: 'c-siem', delay: 4,
      panel: { title: 'Splunk (Lab)', role: 'Investigation / Threat Hunting',
        metrics: [['Queries', '8 SPL'], ['Scope', 'Home lab'], ['Achievement', '70%→0% noise reduction']],
        desc: 'Investigation layer. EventID 4688 analysis reduced forwarder noise from 70% to 0%. Correctly classified 375 process instances as expected tool behavior.' }},
    { id: 'grafana', label: 'Grafana', icon: 'GF', x: 82, y: 10, size: 'minor', color: 'c-siem', delay: 4 },

    // === LAYER: CLOSED-LOOP OUTPUT (right of core) ===
    { id: 'evidence', label: 'Evidence Packer', icon: 'EP', x: 68, y: 40, size: 'major', color: 'c-validate', delay: 5,
      panel: { title: 'Evidence Pack Assembly', role: 'Artifact Generation',
        metrics: [['Per escalation', '5 artifacts'], ['Redaction', 'Mandatory gate'], ['Format', 'MD + CSV']],
        desc: 'Generates one_pager, full_report, timeline, queries, closure_report. Every pack passes mandatory redaction before any output becomes visible.' }},

    // === LAYER: VALIDATION FORK (the critical decision point) ===
    { id: 'validation', label: 'VALIDATION', icon: '✓✗', x: 80, y: 40, size: 'major', color: 'c-validate', delay: 5,
      panel: { title: 'Validation Gate', role: 'Pass/Fail Decision Point',
        metrics: [['Reconciliation', 'PASS (0 mismatches)'], ['Coverage', '8/8'], ['Heartbeat', 'SUCCESS']],
        desc: 'The critical fork. Compares ingested cases against committed dispositions. PASS triggers documentation and governed release. FAIL blocks publication and flags for human review. No silent failures.' }},

    // === PASS PATH (upper-right, green) ===
    { id: 'doc-gen',    label: 'Doc Gen',  x: 90, y: 28, size: 'minor', color: 'c-validate', delay: 6 },
    { id: 'git-commit', label: 'Commit',   x: 93, y: 34, size: 'minor', color: 'c-validate', delay: 6 },
    { id: 'git-push',   label: 'Push',     x: 93, y: 42, size: 'minor', color: 'c-validate', delay: 6 },
    { id: 'publish',    label: 'PUBLISH',  icon: '▶', x: 93, y: 50, size: 'minor', color: 'c-validate', delay: 7,
      panel: { title: 'Governed Publish', role: 'Public Release Gate',
        metrics: [['Target', 'hawkinsops.com'], ['Deploy', 'Cloudflare Pages'], ['Condition', 'Validation PASS only']],
        desc: 'Final output. Proof artifacts deployed to public site. Only reachable after validation PASS. Every published metric traces to current-authority.json.' }},

    // === FAIL PATH (lower-right, red) ===
    { id: 'fail-retain', label: 'RETAIN',    x: 90, y: 52, size: 'minor', color: 'c-fail', delay: 6 },
    { id: 'fail-block',  label: 'BLOCK PUB', x: 93, y: 58, size: 'minor', color: 'c-fail', delay: 6 },
    { id: 'fail-flag',   label: 'FLAG REVIEW',x: 93, y: 66, size: 'minor', color: 'c-fail', delay: 6 },

    // === LAYER: GOVERNANCE (bottom-right, violet, trust boundary) ===
    { id: 'authority', label: 'Authority Engine', icon: 'AE', x: 62, y: 74, size: 'major', color: 'c-govern', delay: 7,
      panel: { title: 'Governance Layer', role: 'Trust Boundary & Auditability',
        metrics: [['Source of truth', 'current-authority.json'], ['Mismatches', '0'], ['Audit logs', 'Immutable']],
        desc: 'Controls what becomes public truth. All reviewer-facing metrics must trace here. Reconciliation enforces ledger integrity. No metric is published without governance approval.' }},
    { id: 'reconciliation', label: 'Reconciliation', icon: 'RC', x: 52, y: 80, size: 'minor', color: 'c-govern', delay: 7 },
    { id: 'audit-logs', label: 'Audit Logs', icon: 'AL', x: 72, y: 80, size: 'minor', color: 'c-govern', delay: 7 },

    // === LAYER: INFRASTRUCTURE SUBSTRATE (bottom, muted, foundational) ===
    { id: 'ho-sr-01', label: 'HO-SR-01', icon: 'SR', x: 34, y: 88, size: 'major', color: 'c-infra', delay: 1,
      panel: { title: 'HO-SR-01', role: 'Physical Host / Compute Substrate',
        metrics: [['Hypervisor', 'Proxmox VE'], ['Storage', 'ZFS + LVM-thin'], ['GPU', 'Dual Tesla V100'], ['CPUs', '72 logical'], ['RAM', '2.0 TiB']],
        desc: 'Primary bare-metal host. Everything runs on this machine. Dual-socket server with enterprise storage and GPU compute. Foundation of the entire stack.' }},
    { id: 'proxmox', label: 'Proxmox', x: 24, y: 92, size: 'cluster', color: 'c-infra', delay: 1 },
    { id: 'zfs',     label: 'ZFS',     x: 34, y: 96, size: 'cluster', color: 'c-infra', delay: 1 },
    { id: 'gpu',     label: 'V100',    x: 44, y: 94, size: 'cluster', color: 'c-infra', delay: 1 },
    { id: 'runner',  label: 'CI Run',  x: 50, y: 88, size: 'cluster', color: 'c-infra', delay: 1 }
  ];

  // ── EDGES ──
  // primary: thicker, more particles. secondary: thinner.
  var edges = [
    // Endpoints → Wazuh (ingestion fan-in)
    { from: 'ep-1', to: 'wazuh-mgr', type: 'ingest' },
    { from: 'ep-2', to: 'wazuh-mgr', type: 'ingest' },
    { from: 'ep-3', to: 'wazuh-mgr', type: 'ingest' },
    { from: 'ep-4', to: 'wazuh-mgr', type: 'ingest' },
    { from: 'ep-5', to: 'wazuh-mgr', type: 'ingest' },
    { from: 'ep-6', to: 'wazuh-mgr', type: 'ingest' },
    { from: 'ep-7', to: 'wazuh-mgr', type: 'ingest' },
    { from: 'ep-8', to: 'wazuh-mgr', type: 'ingest' },
    // Wazuh → Core (PRIMARY)
    { from: 'wazuh-mgr', to: 'sf-core', type: 'primary' },
    // Detection → Core / Wazuh
    { from: 'sigma', to: 'sf-core', type: 'detect' },
    { from: 'wazuh-xml', to: 'wazuh-mgr', type: 'detect' },
    { from: 'ir-playbooks', to: 'sf-core', type: 'detect' },
    { from: 'honeypot-intel', to: 'sigma', type: 'detect' },
    // Core → SIEM (analysis feed)
    { from: 'sf-core', to: 'splunk', type: 'primary' },
    { from: 'splunk', to: 'grafana', type: 'secondary' },
    // Core → Evidence → Validation (PRIMARY output)
    { from: 'sf-core', to: 'evidence', type: 'primary' },
    { from: 'evidence', to: 'validation', type: 'primary' },
    // PASS PATH (green)
    { from: 'validation', to: 'doc-gen', type: 'pass' },
    { from: 'doc-gen', to: 'git-commit', type: 'pass' },
    { from: 'git-commit', to: 'git-push', type: 'pass' },
    { from: 'git-push', to: 'publish', type: 'pass' },
    // FAIL PATH (red)
    { from: 'validation', to: 'fail-retain', type: 'fail' },
    { from: 'fail-retain', to: 'fail-block', type: 'fail' },
    { from: 'fail-retain', to: 'fail-flag', type: 'fail' },
    // Governance
    { from: 'authority', to: 'validation', type: 'govern' },
    { from: 'reconciliation', to: 'authority', type: 'govern' },
    { from: 'audit-logs', to: 'authority', type: 'secondary' },
    { from: 'sf-core', to: 'reconciliation', type: 'govern' },
    // Feedback: governance → detection tuning
    { from: 'authority', to: 'sigma', type: 'feedback' },
    // Infra (muted)
    { from: 'ho-sr-01', to: 'sf-core', type: 'infra' },
    { from: 'proxmox', to: 'ho-sr-01', type: 'infra' },
    { from: 'zfs', to: 'ho-sr-01', type: 'infra' },
    { from: 'gpu', to: 'ho-sr-01', type: 'infra' },
    { from: 'runner', to: 'ho-sr-01', type: 'infra' }
  ];

  // Edge visual config by type
  var edgeStyles = {
    primary:   { color: 'rgba(0,196,212,0.25)',   width: 2.5, particle: 'p-core',   rate: 3 },
    ingest:    { color: 'rgba(251,191,36,0.12)',   width: 1,   particle: 'p-ingest', rate: 1 },
    detect:    { color: 'rgba(59,143,217,0.15)',   width: 1.5, particle: 'p-detect', rate: 1.5 },
    pass:      { color: 'rgba(74,222,128,0.2)',    width: 2,   particle: 'p-pass',   rate: 2 },
    fail:      { color: 'rgba(248,113,113,0.2)',   width: 2,   particle: 'p-fail',   rate: 1.5 },
    govern:    { color: 'rgba(167,139,250,0.15)',  width: 1.5, particle: 'p-govern', rate: 1 },
    feedback:  { color: 'rgba(167,139,250,0.1)',   width: 1,   particle: 'p-govern', rate: 0.5, dash: '8 6' },
    secondary: { color: 'rgba(148,163,184,0.08)',  width: 1,   particle: null,       rate: 0 },
    infra:     { color: 'rgba(148,163,184,0.06)',  width: 1,   particle: null,       rate: 0, dash: '4 6' }
  };

  // Tailscale mesh connections
  var meshNodes = ['sf-core', 'wazuh-mgr', 'splunk', 'evidence', 'ho-sr-01', 'authority', 'sigma', 'validation'];

  // ── UTILITIES ──
  function nodeById(id) {
    for (var i = 0; i < nodes.length; i++) { if (nodes[i].id === id) return nodes[i]; }
    return null;
  }

  function getPos(node, w, h) {
    return { x: (node.x / 100) * w, y: (node.y / 100) * h };
  }

  var sizeMap = { core: 160, major: 80, minor: 48, cluster: 30 };

  // ── RENDER ──
  function render() {
    var container = document.getElementById('system-map');
    if (!container) return;
    var canvas = container.querySelector('.sysmap-canvas');
    if (!canvas) return;

    // Clear
    canvas.innerHTML = '';
    var w = canvas.offsetWidth;
    var h = canvas.offsetHeight;
    var svgNS = 'http://www.w3.org/2000/svg';

    // --- Layer 1: Tailscale mesh ---
    var meshSvg = document.createElementNS(svgNS, 'svg');
    meshSvg.setAttribute('class', 'sysmap-mesh');
    meshSvg.setAttribute('width', w); meshSvg.setAttribute('height', h);
    meshSvg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    for (var mi = 0; mi < meshNodes.length; mi++) {
      for (var mj = mi + 1; mj < meshNodes.length; mj++) {
        var mn1 = nodeById(meshNodes[mi]), mn2 = nodeById(meshNodes[mj]);
        if (!mn1 || !mn2) continue;
        var mc1 = getPos(mn1, w, h), mc2 = getPos(mn2, w, h);
        var mline = document.createElementNS(svgNS, 'line');
        mline.setAttribute('x1', mc1.x); mline.setAttribute('y1', mc1.y);
        mline.setAttribute('x2', mc2.x); mline.setAttribute('y2', mc2.y);
        mline.setAttribute('stroke', 'rgba(167,139,250,0.04)');
        mline.setAttribute('stroke-width', '1');
        mline.setAttribute('stroke-dasharray', '6 12');
        meshSvg.appendChild(mline);
      }
    }
    // Mesh label
    var meshLabel = document.createElementNS(svgNS, 'text');
    meshLabel.setAttribute('x', w * 0.5); meshLabel.setAttribute('y', h * 0.02 + 14);
    meshLabel.setAttribute('text-anchor', 'middle');
    meshLabel.setAttribute('fill', 'rgba(167,139,250,0.2)');
    meshLabel.setAttribute('style', 'font:500 0.6rem "JetBrains Mono",monospace;letter-spacing:0.15em;text-transform:uppercase;');
    meshLabel.textContent = 'TAILSCALE SECURE MESH';
    meshSvg.appendChild(meshLabel);
    canvas.appendChild(meshSvg);

    // --- Layer 2: Edges ---
    var edgeSvg = document.createElementNS(svgNS, 'svg');
    edgeSvg.setAttribute('class', 'sysmap-edges');
    edgeSvg.setAttribute('width', w); edgeSvg.setAttribute('height', h);
    edgeSvg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);

    // Arrow markers
    var defs = document.createElementNS(svgNS, 'defs');
    ['core','pass','fail','govern','detect','ingest'].forEach(function(t) {
      var colors = { core:'0,196,212', pass:'74,222,128', fail:'248,113,113', govern:'167,139,250', detect:'59,143,217', ingest:'251,191,36' };
      var marker = document.createElementNS(svgNS, 'marker');
      marker.setAttribute('id', 'arrow-' + t); marker.setAttribute('markerWidth', '8'); marker.setAttribute('markerHeight', '6');
      marker.setAttribute('refX', '8'); marker.setAttribute('refY', '3'); marker.setAttribute('orient', 'auto');
      var poly = document.createElementNS(svgNS, 'polygon');
      poly.setAttribute('points', '0 0, 8 3, 0 6');
      poly.setAttribute('fill', 'rgba(' + (colors[t] || '148,163,184') + ',0.4)');
      marker.appendChild(poly); defs.appendChild(marker);
    });
    edgeSvg.appendChild(defs);

    edges.forEach(function (edge) {
      var n1 = nodeById(edge.from), n2 = nodeById(edge.to);
      if (!n1 || !n2) return;
      var c1 = getPos(n1, w, h), c2 = getPos(n2, w, h);
      var style = edgeStyles[edge.type] || edgeStyles.secondary;
      var line = document.createElementNS(svgNS, 'line');
      line.setAttribute('x1', c1.x); line.setAttribute('y1', c1.y);
      line.setAttribute('x2', c2.x); line.setAttribute('y2', c2.y);
      line.setAttribute('stroke', style.color);
      line.setAttribute('stroke-width', style.width);
      if (style.dash) line.setAttribute('stroke-dasharray', style.dash);
      // Arrow on primary/pass/fail edges
      if (edge.type === 'primary' || edge.type === 'pass' || edge.type === 'fail') {
        var arrowType = edge.type === 'primary' ? 'core' : edge.type;
        line.setAttribute('marker-end', 'url(#arrow-' + arrowType + ')');
      }
      edgeSvg.appendChild(line);
    });
    canvas.appendChild(edgeSvg);

    // --- Layer 3: Governance boundary ---
    var govArc = document.createElement('div');
    govArc.className = 'sysmap-governance';
    canvas.appendChild(govArc);

    // --- Layer 4: PASS/FAIL labels ---
    var passLabel = document.createElement('div');
    passLabel.className = 'sysmap-zone-label';
    passLabel.style.cssText = 'position:absolute;left:87%;top:22%;color:rgba(74,222,128,0.35);font:700 0.65rem "JetBrains Mono",monospace;letter-spacing:0.12em;text-transform:uppercase;';
    passLabel.textContent = 'PASS';
    canvas.appendChild(passLabel);

    var failLabel = document.createElement('div');
    failLabel.className = 'sysmap-zone-label';
    failLabel.style.cssText = 'position:absolute;left:87%;top:55%;color:rgba(248,113,113,0.35);font:700 0.65rem "JetBrains Mono",monospace;letter-spacing:0.12em;text-transform:uppercase;';
    failLabel.textContent = 'FAIL';
    canvas.appendChild(failLabel);

    // --- Layer 5: Nodes ---
    nodes.forEach(function (node) {
      var el = document.createElement('div');
      var s = sizeMap[node.size] || 48;
      el.className = 'sysmap-node ' + node.size + ' ' + node.color;
      el.setAttribute('data-delay', node.delay || 0);
      el.setAttribute('data-id', node.id);
      var pos = getPos(node, w, h);
      el.style.left = (pos.x - s / 2) + 'px';
      el.style.top = (pos.y - s / 2) + 'px';

      if (node.icon) {
        var iconEl = document.createElement('div');
        iconEl.className = 'sysmap-icon';
        iconEl.textContent = node.icon.replace('\\n', '\n');
        el.appendChild(iconEl);
      }

      // Only show labels for major+ nodes to reduce clutter
      if (node.size !== 'cluster') {
        var labelEl = document.createElement('div');
        labelEl.className = 'sysmap-label';
        labelEl.textContent = node.label;
        el.appendChild(labelEl);
      }

      if (node.panel) {
        el.addEventListener('mouseenter', function () { showPanel(node, el, canvas); });
        el.addEventListener('mouseleave', hidePanel);
        el.addEventListener('click', function () { showPanel(node, el, canvas); });
      }

      canvas.appendChild(el);
    });

    // Start particles
    startParticles(canvas, w, h);
  }

  // ── HOVER PANELS ──
  var panelEl = null;

  function showPanel(node, nodeEl, canvas) {
    if (!panelEl) {
      panelEl = document.createElement('div');
      panelEl.className = 'sysmap-panel';
      canvas.appendChild(panelEl);
    }
    var p = node.panel;
    var html = '<div class="sysmap-panel-title">' + p.title + '</div>';
    html += '<div class="sysmap-panel-role">' + p.role + '</div>';
    html += '<div style="margin-bottom:10px;font-size:0.78rem;color:#9eb4d8;">' + p.desc + '</div>';
    if (p.metrics) {
      p.metrics.forEach(function (m) {
        var vc = m[1] === 'SUCCESS' || m[1].indexOf('PASS') >= 0 ? '#4ade80' :
                 m[1].indexOf('FAIL') >= 0 ? '#f87171' : '#7ab8ff';
        html += '<div class="sysmap-panel-metric"><span>' + m[0] + '</span><span class="sysmap-panel-val" style="color:' + vc + ';">' + m[1] + '</span></div>';
      });
    }
    panelEl.innerHTML = html;
    panelEl.classList.add('visible');
    var r = nodeEl.getBoundingClientRect(), cr = canvas.getBoundingClientRect();
    var left = r.right - cr.left + 14, top = r.top - cr.top - 20;
    if (left + 290 > canvas.offsetWidth) left = r.left - cr.left - 296;
    if (top < 10) top = 10;
    if (top + 240 > canvas.offsetHeight) top = canvas.offsetHeight - 250;
    panelEl.style.left = left + 'px';
    panelEl.style.top = top + 'px';
  }

  function hidePanel() { if (panelEl) panelEl.classList.remove('visible'); }

  // ── PARTICLE SYSTEM ──
  var animating = false;

  function startParticles(canvas, w, h) {
    if (animating) return;
    animating = true;

    var animEdges = edges.filter(function (e) {
      var s = edgeStyles[e.type];
      return s && s.particle && s.rate > 0;
    });

    function spawn() {
      if (!animating) return;
      // Pick edge weighted by rate
      var totalRate = 0;
      animEdges.forEach(function(e) { totalRate += (edgeStyles[e.type] || {}).rate || 0; });
      var pick = Math.random() * totalRate, acc = 0, edge = animEdges[0];
      for (var i = 0; i < animEdges.length; i++) {
        acc += (edgeStyles[animEdges[i].type] || {}).rate || 0;
        if (acc >= pick) { edge = animEdges[i]; break; }
      }

      var n1 = nodeById(edge.from), n2 = nodeById(edge.to);
      if (!n1 || !n2) return;
      var c1 = getPos(n1, w, h), c2 = getPos(n2, w, h);
      var style = edgeStyles[edge.type] || {};

      var dot = document.createElement('div');
      dot.className = 'sysmap-particle ' + (style.particle || 'p-core');
      canvas.appendChild(dot);

      var dur = 1200 + Math.random() * 1200;
      var st = performance.now();
      (function tick(now) {
        var t = Math.min((now - st) / dur, 1);
        var ease = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
        dot.style.left = (c1.x + (c2.x - c1.x) * ease) + 'px';
        dot.style.top = (c1.y + (c2.y - c1.y) * ease) + 'px';
        dot.style.opacity = t < 0.08 ? t * 12 : t > 0.88 ? (1 - t) / 0.12 : 0.9;
        if (t < 1 && animating) requestAnimationFrame(tick);
        else dot.remove();
      })(performance.now());
    }

    setInterval(function () {
      if (!animating) return;
      spawn();
      if (Math.random() > 0.4) spawn();
      if (Math.random() > 0.7) spawn();
    }, 300);
  }

  // ── INIT ──
  function init() {
    var container = document.getElementById('system-map');
    if (!container) return;
    render();
    var rt;
    window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(render, 250); });
    if (typeof IntersectionObserver === 'function') {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) container.classList.add('active'); });
      }, { threshold: 0.12 }).observe(container);
    } else {
      container.classList.add('active');
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
