/* system-map.js — SignalFoundry living system topology
   Zero dependencies. Vanilla JS + SVG + CSS animations.
   Renders a layered, animated, interactive system map. */

(function () {
  'use strict';

  // ── NODE DATA MODEL ──
  // x/y are percentages of container width/height
  var nodes = [
    // CORE
    { id: 'sf-core', label: 'SignalFoundry', icon: 'SF', x: 50, y: 42, size: 'core', color: 'c-core', delay: 2,
      panel: { title: 'SignalFoundry Core', role: 'Central Orchestration Engine',
        metrics: [['Cases processed', '49,774'], ['Auto-close rate', '~89%'], ['Escalated', '2,478'], ['Reconciliation', 'PASS (0)'], ['Heartbeat', 'SUCCESS']],
        desc: 'Policy-driven triage engine. Receives all ingested alerts, applies deterministic disposition logic, routes to evidence assembly or auto-close.' }},

    // INGESTION (left)
    { id: 'wazuh-mgr', label: 'Wazuh Manager', icon: 'WZ', x: 18, y: 38, size: 'major', color: 'c-edge', delay: 3,
      panel: { title: 'Wazuh Manager', role: 'SIEM / Alert Collection',
        metrics: [['Agents', '8/8 reporting'], ['Role', 'Alert ingestion + rule matching'], ['Custom rules', '100000+ range']],
        desc: 'Receives endpoint telemetry from all 8 lab hosts. Matches against Wazuh XML rules and forwards alerts to SignalFoundry for triage.' }},
    { id: 'ep-1', label: 'dc01', icon: 'DC', x: 5, y: 22, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-2', label: 'win10-01', icon: 'W1', x: 5, y: 34, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-3', label: 'win10-02', icon: 'W2', x: 5, y: 46, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-4', label: 'linux-web', icon: 'LW', x: 5, y: 58, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-5', label: 'linux-db', icon: 'DB', x: 10, y: 68, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-6', label: 'honeypot', icon: 'HP', x: 10, y: 16, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-7', label: 'splunk-fwd', icon: 'SF', x: 14, y: 58, size: 'cluster', color: 'c-edge', delay: 3 },
    { id: 'ep-8', label: 'wazuh-mgr-a', icon: 'WA', x: 14, y: 22, size: 'cluster', color: 'c-edge', delay: 3 },

    // DETECTION ENGINEERING (upper left)
    { id: 'sigma', label: 'Sigma Rules', icon: '103', x: 25, y: 12, size: 'major', color: 'c-detect', delay: 4,
      panel: { title: 'Sigma Detection Rules', role: 'Detection Engineering',
        metrics: [['Rules', '103'], ['Tactics', '9 MITRE ATT&CK'], ['Format', 'YAML portable']],
        desc: 'Behavioral detection rules organized by MITRE ATT&CK tactic. Process creation, lateral movement, credential access, persistence, and more.' }},
    { id: 'wazuh-xml', label: 'Wazuh XML', icon: '28', x: 18, y: 8, size: 'minor', color: 'c-detect', delay: 4 },
    { id: 'ir-playbooks', label: 'IR Playbooks', icon: '10', x: 32, y: 6, size: 'minor', color: 'c-detect', delay: 4 },
    { id: 'honeypot-intel', label: 'Honeypot Intel', icon: 'HI', x: 12, y: 6, size: 'cluster', color: 'c-detect', delay: 4 },

    // SIEM / ANALYSIS (upper right)
    { id: 'splunk', label: 'Splunk', icon: 'SPL', x: 75, y: 14, size: 'major', color: 'c-siem', delay: 4,
      panel: { title: 'Splunk (Lab)', role: 'Investigation / Analysis',
        metrics: [['Queries', '8 SPL'], ['Scope', 'Home lab'], ['Input', 'Wazuh-forwarded events']],
        desc: 'Investigation layer for threat hunting and signal-vs-noise analysis. EventID 4688 analysis reduced forwarder noise from 70% to 0%.' }},
    { id: 'grafana', label: 'Grafana', icon: 'GF', x: 82, y: 8, size: 'minor', color: 'c-siem', delay: 4 },

    // CLOSED-LOOP OUTPUT (right)
    { id: 'evidence', label: 'Evidence Packer', icon: 'EP', x: 72, y: 38, size: 'major', color: 'c-validate', delay: 5,
      panel: { title: 'Evidence Pack Assembly', role: 'Artifact Generation',
        metrics: [['Outputs', '5 per escalation'], ['Redaction', 'Mandatory gate'], ['Format', 'MD + CSV']],
        desc: 'Assembles 00_one_pager.md, 01_full_report.md, 02_timeline.csv, 03_queries.md, 04_closure_report.md. All pass redaction gate before publication.' }},
    { id: 'validation', label: 'Validation Gate', icon: 'VG', x: 82, y: 42, size: 'major', color: 'c-validate', delay: 5,
      panel: { title: 'Validation Gate', role: 'Pass/Fail Decision',
        metrics: [['Reconciliation', 'PASS (0 mismatches)'], ['Coverage', '8/8'], ['Heartbeat', 'SUCCESS']],
        desc: 'Ledger check comparing ingested cases against committed dispositions. Pass triggers documentation and governed release. Fail blocks publication and flags for review.' }},

    // PASS PATH
    { id: 'doc-gen', label: 'Doc Gen', icon: 'DG', x: 90, y: 34, size: 'minor', color: 'c-validate', delay: 6 },
    { id: 'git-commit', label: 'Commit', icon: 'GC', x: 93, y: 44, size: 'minor', color: 'c-validate', delay: 6 },
    { id: 'git-push', label: 'Push', icon: 'GP', x: 93, y: 54, size: 'minor', color: 'c-validate', delay: 6 },
    { id: 'publish', label: 'Publish', icon: 'PB', x: 90, y: 64, size: 'minor', color: 'c-validate', delay: 7,
      panel: { title: 'Governed Publish', role: 'Public Release',
        metrics: [['Target', 'hawkinsops.com'], ['Deploy', 'Cloudflare Pages'], ['Branch', 'main']],
        desc: 'Final output: proof artifacts deployed to public site. Only reached after validation PASS. Every published metric traces to current-authority.json.' }},

    // FAIL PATH
    { id: 'fail-retain', label: 'Retain', icon: 'RT', x: 90, y: 50, size: 'cluster', color: 'c-fail', delay: 6 },
    { id: 'fail-block', label: 'Block', icon: 'BK', x: 95, y: 46, size: 'cluster', color: 'c-fail', delay: 6 },
    { id: 'fail-flag', label: 'Flag Review', icon: 'FR', x: 95, y: 54, size: 'cluster', color: 'c-fail', delay: 6 },

    // GOVERNANCE (bottom right)
    { id: 'authority', label: 'Authority Engine', icon: 'AE', x: 68, y: 72, size: 'major', color: 'c-govern', delay: 7,
      panel: { title: 'Governance Layer', role: 'Trust Boundary',
        metrics: [['Source', 'current-authority.json'], ['Reconciliation', '0 mismatches'], ['Audit logs', 'Immutable']],
        desc: 'Controls what becomes public truth. current-authority.json is the single source of truth for all reviewer-facing metrics. Reconciliation gates enforce ledger integrity.' }},
    { id: 'reconciliation', label: 'Reconciliation', icon: 'RC', x: 58, y: 78, size: 'minor', color: 'c-govern', delay: 7 },
    { id: 'audit-logs', label: 'Audit Logs', icon: 'AL', x: 78, y: 78, size: 'minor', color: 'c-govern', delay: 7 },

    // INFRASTRUCTURE (bottom)
    { id: 'ho-sr-01', label: 'HO-SR-01', icon: 'SR', x: 38, y: 82, size: 'major', color: 'c-infra', delay: 1,
      panel: { title: 'HO-SR-01', role: 'Physical Host / Compute Substrate',
        metrics: [['Hypervisor', 'Proxmox VE'], ['Storage', 'ZFS + LVM-thin'], ['GPU', 'Dual Tesla V100'], ['Network', 'Tailscale mesh']],
        desc: 'Primary bare-metal host running all Proxmox VMs. Dual-socket, 72 logical CPUs, 2.0 TiB RAM. Foundation for the entire SignalFoundry stack.' }},
    { id: 'proxmox', label: 'Proxmox', icon: 'PX', x: 30, y: 88, size: 'minor', color: 'c-infra', delay: 1 },
    { id: 'zfs', label: 'ZFS', icon: 'ZF', x: 40, y: 92, size: 'cluster', color: 'c-infra', delay: 1 },
    { id: 'gpu', label: 'Tesla V100', icon: 'V1', x: 50, y: 90, size: 'cluster', color: 'c-infra', delay: 1 },
    { id: 'runner', label: 'CI Runner', icon: 'CI', x: 48, y: 82, size: 'cluster', color: 'c-infra', delay: 1 }
  ];

  // ── EDGE DATA MODEL ──
  var edges = [
    // Endpoint → Wazuh
    { from: 'ep-1', to: 'wazuh-mgr', particle: 'p-ingest' },
    { from: 'ep-2', to: 'wazuh-mgr', particle: 'p-ingest' },
    { from: 'ep-3', to: 'wazuh-mgr', particle: 'p-ingest' },
    { from: 'ep-4', to: 'wazuh-mgr', particle: 'p-ingest' },
    { from: 'ep-5', to: 'wazuh-mgr', particle: 'p-ingest' },
    { from: 'ep-6', to: 'wazuh-mgr', particle: 'p-ingest' },
    { from: 'ep-7', to: 'wazuh-mgr', particle: 'p-ingest' },
    { from: 'ep-8', to: 'wazuh-mgr', particle: 'p-ingest' },
    // Wazuh → Core
    { from: 'wazuh-mgr', to: 'sf-core', particle: 'p-core', thick: true },
    // Detection → Core (feedback)
    { from: 'sigma', to: 'sf-core', particle: 'p-detect' },
    { from: 'wazuh-xml', to: 'wazuh-mgr', particle: 'p-detect' },
    { from: 'ir-playbooks', to: 'sf-core', particle: 'p-detect' },
    { from: 'honeypot-intel', to: 'sigma', particle: 'p-detect' },
    // Core → SIEM
    { from: 'sf-core', to: 'splunk', particle: 'p-core' },
    { from: 'splunk', to: 'grafana' },
    // Core → Evidence → Validation
    { from: 'sf-core', to: 'evidence', particle: 'p-core', thick: true },
    { from: 'evidence', to: 'validation', particle: 'p-pass', thick: true },
    // Pass path
    { from: 'validation', to: 'doc-gen', particle: 'p-pass' },
    { from: 'doc-gen', to: 'git-commit', particle: 'p-pass' },
    { from: 'git-commit', to: 'git-push', particle: 'p-pass' },
    { from: 'git-push', to: 'publish', particle: 'p-pass' },
    // Fail path
    { from: 'validation', to: 'fail-retain', particle: 'p-fail' },
    { from: 'fail-retain', to: 'fail-block', particle: 'p-fail' },
    { from: 'fail-retain', to: 'fail-flag', particle: 'p-fail' },
    // Governance
    { from: 'authority', to: 'validation', particle: 'p-govern' },
    { from: 'reconciliation', to: 'authority', particle: 'p-govern' },
    { from: 'audit-logs', to: 'authority' },
    { from: 'sf-core', to: 'reconciliation', particle: 'p-govern' },
    // Feedback loop: governance → detections
    { from: 'authority', to: 'sigma', particle: 'p-govern', dashed: true },
    // Infrastructure connections
    { from: 'ho-sr-01', to: 'sf-core', dashed: true },
    { from: 'proxmox', to: 'ho-sr-01' },
    { from: 'zfs', to: 'ho-sr-01' },
    { from: 'gpu', to: 'ho-sr-01' },
    { from: 'runner', to: 'ho-sr-01' }
  ];

  // ── MESH CONNECTIONS (Tailscale) ──
  var meshNodes = ['sf-core', 'wazuh-mgr', 'splunk', 'evidence', 'ho-sr-01', 'authority', 'sigma'];

  // ── UTILITIES ──
  function nodeById(id) {
    for (var i = 0; i < nodes.length; i++) { if (nodes[i].id === id) return nodes[i]; }
    return null;
  }

  function getCenter(node, container) {
    var w = container.offsetWidth;
    var h = container.offsetHeight;
    return { x: (node.x / 100) * w, y: (node.y / 100) * h };
  }

  // ── RENDER ──
  function render() {
    var container = document.getElementById('system-map');
    if (!container) return;

    var canvas = container.querySelector('.sysmap-canvas');
    if (!canvas) return;

    // Clear previous render
    var oldSvg = canvas.querySelector('.sysmap-edges');
    if (oldSvg) oldSvg.remove();
    var oldMesh = canvas.querySelector('.sysmap-mesh');
    if (oldMesh) oldMesh.remove();
    canvas.querySelectorAll('.sysmap-node, .sysmap-particle').forEach(function(el) { el.remove(); });

    var w = canvas.offsetWidth;
    var h = canvas.offsetHeight;

    // Create edge SVG
    var svgNS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('class', 'sysmap-edges');
    svg.setAttribute('width', w);
    svg.setAttribute('height', h);
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    canvas.appendChild(svg);

    // Render mesh (Tailscale)
    var meshSvg = document.createElementNS(svgNS, 'svg');
    meshSvg.setAttribute('class', 'sysmap-mesh');
    meshSvg.setAttribute('width', w);
    meshSvg.setAttribute('height', h);
    meshSvg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    for (var mi = 0; mi < meshNodes.length; mi++) {
      for (var mj = mi + 1; mj < meshNodes.length; mj++) {
        var mn1 = nodeById(meshNodes[mi]);
        var mn2 = nodeById(meshNodes[mj]);
        if (!mn1 || !mn2) continue;
        var mc1 = getCenter(mn1, canvas);
        var mc2 = getCenter(mn2, canvas);
        var mline = document.createElementNS(svgNS, 'line');
        mline.setAttribute('x1', mc1.x);
        mline.setAttribute('y1', mc1.y);
        mline.setAttribute('x2', mc2.x);
        mline.setAttribute('y2', mc2.y);
        mline.setAttribute('stroke', 'rgba(167, 139, 250, 0.06)');
        mline.setAttribute('stroke-width', '1');
        mline.setAttribute('stroke-dasharray', '4 8');
        meshSvg.appendChild(mline);
      }
    }
    canvas.insertBefore(meshSvg, canvas.firstChild);

    // Render edges
    edges.forEach(function (edge) {
      var n1 = nodeById(edge.from);
      var n2 = nodeById(edge.to);
      if (!n1 || !n2) return;
      var c1 = getCenter(n1, canvas);
      var c2 = getCenter(n2, canvas);
      var line = document.createElementNS(svgNS, 'line');
      line.setAttribute('x1', c1.x);
      line.setAttribute('y1', c1.y);
      line.setAttribute('x2', c2.x);
      line.setAttribute('y2', c2.y);
      var color = edge.particle === 'p-pass' ? 'rgba(74, 222, 128, 0.15)' :
                  edge.particle === 'p-fail' ? 'rgba(248, 113, 113, 0.15)' :
                  edge.particle === 'p-ingest' ? 'rgba(251, 191, 36, 0.1)' :
                  edge.particle === 'p-govern' ? 'rgba(167, 139, 250, 0.12)' :
                  edge.particle === 'p-detect' ? 'rgba(59, 143, 217, 0.12)' :
                  edge.particle === 'p-core' ? 'rgba(0, 196, 212, 0.15)' :
                  'rgba(148, 163, 184, 0.08)';
      line.setAttribute('stroke', color);
      line.setAttribute('stroke-width', edge.thick ? '2' : '1');
      if (edge.dashed) line.setAttribute('stroke-dasharray', '6 4');
      svg.appendChild(line);
    });

    // Render governance arc
    var govArc = document.createElement('div');
    govArc.className = 'sysmap-governance';
    canvas.appendChild(govArc);

    // Render nodes
    nodes.forEach(function (node) {
      var el = document.createElement('div');
      el.className = 'sysmap-node ' + node.size + ' ' + node.color;
      el.setAttribute('data-delay', node.delay || 0);
      el.setAttribute('data-id', node.id);
      var c = getCenter(node, canvas);
      var sizeMap = { core: 140, major: 80, minor: 52, cluster: 36 };
      var s = sizeMap[node.size] || 52;
      el.style.left = (c.x - s / 2) + 'px';
      el.style.top = (c.y - s / 2) + 'px';

      var iconEl = document.createElement('div');
      iconEl.className = 'sysmap-icon';
      iconEl.textContent = node.icon;
      el.appendChild(iconEl);

      var labelEl = document.createElement('div');
      labelEl.className = 'sysmap-label';
      labelEl.textContent = node.label;
      el.appendChild(labelEl);

      // Hover panel
      if (node.panel) {
        el.addEventListener('mouseenter', function (e) {
          showPanel(node, el, canvas);
        });
        el.addEventListener('mouseleave', function () {
          hidePanel();
        });
      }

      canvas.appendChild(el);
    });

    // Particle animation system
    startParticles(canvas);
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
        var valColor = m[1] === 'SUCCESS' || m[1] === 'PASS (0)' ? 'color:#4ade80;' :
                       m[1].indexOf('FAIL') >= 0 ? 'color:#f87171;' : 'color:#7ab8ff;';
        html += '<div class="sysmap-panel-metric"><span>' + m[0] + '</span><span class="sysmap-panel-val" style="' + valColor + '">' + m[1] + '</span></div>';
      });
    }
    panelEl.innerHTML = html;
    panelEl.classList.add('visible');

    // Position panel near node
    var rect = nodeEl.getBoundingClientRect();
    var cRect = canvas.getBoundingClientRect();
    var left = rect.right - cRect.left + 12;
    var top = rect.top - cRect.top;
    if (left + 290 > canvas.offsetWidth) left = rect.left - cRect.left - 292;
    if (top + 200 > canvas.offsetHeight) top = canvas.offsetHeight - 220;
    panelEl.style.left = left + 'px';
    panelEl.style.top = Math.max(10, top) + 'px';
  }

  function hidePanel() {
    if (panelEl) panelEl.classList.remove('visible');
  }

  // ── PARTICLE FLOW ──
  var particlePool = [];
  var animating = false;

  function startParticles(canvas) {
    if (animating) return;
    animating = true;

    // Create particles for animated edges
    var animatedEdges = edges.filter(function (e) { return e.particle; });

    function spawnParticle() {
      if (!animating) return;
      var edge = animatedEdges[Math.floor(Math.random() * animatedEdges.length)];
      var n1 = nodeById(edge.from);
      var n2 = nodeById(edge.to);
      if (!n1 || !n2) return;
      var c1 = getCenter(n1, canvas);
      var c2 = getCenter(n2, canvas);

      var dot = document.createElement('div');
      dot.className = 'sysmap-particle ' + (edge.particle || 'p-core');
      dot.style.left = c1.x + 'px';
      dot.style.top = c1.y + 'px';
      canvas.appendChild(dot);

      var duration = 1500 + Math.random() * 1500;
      var start = performance.now();

      function tick(now) {
        var t = Math.min((now - start) / duration, 1);
        var ease = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
        dot.style.left = (c1.x + (c2.x - c1.x) * ease) + 'px';
        dot.style.top = (c1.y + (c2.y - c1.y) * ease) + 'px';
        dot.style.opacity = t < 0.1 ? t * 10 : t > 0.85 ? (1 - t) / 0.15 : 0.8;
        if (t < 1 && animating) {
          requestAnimationFrame(tick);
        } else {
          dot.remove();
        }
      }
      requestAnimationFrame(tick);
    }

    // Spawn particles at intervals
    var spawnInterval = setInterval(function () {
      if (!animating) { clearInterval(spawnInterval); return; }
      spawnParticle();
      if (Math.random() > 0.5) spawnParticle(); // sometimes 2 at once
    }, 400);
  }

  function stopParticles() {
    animating = false;
  }

  // ── SCROLL TRIGGER ──
  function init() {
    var container = document.getElementById('system-map');
    if (!container) return;

    render();

    // Handle resize
    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(render, 200);
    });

    // Intersection observer for activation
    if (typeof IntersectionObserver === 'function') {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            container.classList.add('active');
          }
        });
      }, { threshold: 0.15 });
      observer.observe(container);
    } else {
      // Fallback: activate immediately
      container.classList.add('active');
    }
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
