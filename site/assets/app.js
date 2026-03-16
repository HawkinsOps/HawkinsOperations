/* HawkinsOps v3: tiny JS to enhance (not power) the site.
   - Modal open/close for expandable cards
   - Copy buttons for terminal blocks
   - Mobile nav toggle
*/
(function () {
  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));
  const html = document.documentElement;
  const VERIFIED_TIMEOUT_MS = 1500;
  const OPS_TIMEOUT_MS = 1500;
  const isLocalDebugHost = /^(localhost|127\.0\.0\.1)$/.test(window.location.hostname);

  html.setAttribute('data-theme', 'dark');

  // Mobile nav
  const mobBtn = $('#mobBtn');
  const mobMenu = $('#mobMenu');
  if (mobBtn && mobMenu) {
    mobBtn.setAttribute('aria-expanded', 'false');
    mobBtn.setAttribute('aria-controls', 'mobMenu');
    mobBtn.addEventListener('click', () => {
      const open = mobMenu.getAttribute('data-open') === 'true';
      mobMenu.setAttribute('data-open', String(!open));
      mobMenu.style.display = open ? 'none' : 'block';
      mobBtn.setAttribute('aria-expanded', String(!open));
    });
  }

  // Active link highlight
  function normalizeNavPath(value) {
    const raw = String(value || '').trim();
    const noQuery = raw.split('#')[0].split('?')[0];
    const trimmed = noQuery.replace(/^https?:\/\/[^/]+/i, '').replace(/\\/g, '/').replace(/\/+$/, '');
    const leaf = (trimmed.split('/').pop() || '').trim();
    if (!leaf) return '';
    return leaf.toLowerCase().replace(/\.html$/, '');
  }

  const activePath = normalizeNavPath(location.pathname || '/');
  const navLinks = Array.from(
    new Set([
      ...$$('.nav-l a'),
      ...$$('#mobMenu a'),
      ...$$('.mob-menu a')
    ])
  );
  navLinks.forEach(a => {
    const hrefPath = normalizeNavPath(a.getAttribute('href') || '');
    const isActive = hrefPath === activePath;
    a.classList.toggle('act', isActive);
    if (isActive) {
      a.setAttribute('aria-current', 'page');
    } else {
      a.removeAttribute('aria-current');
    }
  });

  function applyVerifiedPayload(payload) {
    if (!payload || typeof payload !== 'object') return;
    const counts = payload.counts && typeof payload.counts === 'object' ? payload.counts : payload;
    $$('[data-verified]').forEach((node) => {
      const key = node.getAttribute('data-verified');
      const value = key ? counts[key] : null;
      if (typeof value === 'number' && Number.isFinite(value)) {
        node.textContent = String(value);
      }
    });
    $$('[data-verified-date]').forEach((node) => {
      const sourceDate = payload.generated_at_utc || payload.last_verified_utc;
      if (typeof sourceDate === 'string') {
        node.textContent = formatMmDdYyyy(sourceDate) || sourceDate;
      }
    });
  }

  function formatMetricValue(value) {
    if (typeof value === 'number' && Number.isFinite(value)) {
      return new Intl.NumberFormat('en-US').format(value);
    }
    return value;
  }

  function applyOpsMetricsPayload(payload) {
    if (!payload || typeof payload !== 'object') return;
    var metrics = payload.metrics && typeof payload.metrics === 'object' ? payload.metrics : payload;
    $$('[data-ops]').forEach(function (node) {
      var key = node.getAttribute('data-ops');
      var value = key ? metrics[key] : null;
      if ((typeof value === 'number' && Number.isFinite(value)) || (typeof value === 'string' && value.trim())) {
        node.textContent = String(formatMetricValue(value));
      }
    });
    $$('[data-ops-status]').forEach(function (node) {
      var key = node.getAttribute('data-ops-status');
      var value = key ? metrics[key] : null;
      if (typeof value === 'string' && value.trim()) {
        node.textContent = value;
        node.setAttribute('data-status', value.toLowerCase());
      }
    });
  }

  async function loadVerifiedCounts() {
    if (window.HAWKINSOPS_COUNTS && typeof window.HAWKINSOPS_COUNTS === 'object') {
      applyVerifiedPayload(window.HAWKINSOPS_COUNTS);
    }
    if (typeof window.fetchJsonWithTimeout !== 'function') return;
    try {
      const payload = await window.fetchJsonWithTimeout('/assets/verified-counts.json', {
        timeoutMs: VERIFIED_TIMEOUT_MS
      });
      applyVerifiedPayload(payload);
    } catch {
      // keep existing values if the payload is unavailable
    }
  }

  async function loadOpsMetrics() {
    if (window.HAWKINSOPS_OPS_METRICS && typeof window.HAWKINSOPS_OPS_METRICS === 'object') {
      applyOpsMetricsPayload(window.HAWKINSOPS_OPS_METRICS);
    }
    if (typeof window.fetchJsonWithTimeout !== 'function') return;
    try {
      const payload = await window.fetchJsonWithTimeout('/assets/data/ops-metrics.json', {
        timeoutMs: OPS_TIMEOUT_MS
      });
      applyOpsMetricsPayload(payload);
    } catch {
      // keep existing values if the payload is unavailable
    }
  }

  async function imageExists(src) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = () => resolve(false);
      img.src = src;
    });
  }

  async function hydrateLabScreenshots() {
    const cards = $$('[data-screenshot-card]');
    if (!cards.length) return;
    let shown = 0;
    for (const card of cards) {
      const src = card.getAttribute('data-src');
      if (!src) continue;
      const ok = await imageExists(src);
      if (!ok) continue;
      const img = $('[data-screenshot-img]', card);
      if (img) img.setAttribute('src', src);
      card.hidden = false;
      shown += 1;
    }
    const fallback = $('[data-screenshot-fallback]');
    if (fallback) fallback.hidden = shown > 0;
  }

  // Copy wiring (supports dynamically injected modal content too)
  function wireCopy(root=document) {
    $$('button[data-copy]', root).forEach(btn => {
      if (btn.__wired) return;
      btn.__wired = true;

      btn.addEventListener('click', async () => {
        const targetId = btn.getAttribute('data-copy');
        const pre = targetId ? document.getElementById(targetId) : null;
        if (!pre) return;

        const text = pre.innerText || pre.textContent || '';
        try {
          await navigator.clipboard.writeText(text);
          const old = btn.textContent;
          btn.textContent = 'Copied';
          setTimeout(() => (btn.textContent = old), 900);
        } catch {
          // fallback: select text for manual copy
          const range = document.createRange();
          range.selectNodeContents(pre);
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
        }
      });
    });
  }
  wireCopy();

  // Modal
  const modalBg = $('#modalBg');
  const modalTitle = $('#modalTitle');
  const modalBody = $('#modalBody');
  const modalClose = $('#modalClose');
  let lastFocused = null;

  function getFocusable(container) {
    return $$('a[href],button:not([disabled]),textarea,input,select,[tabindex]:not([tabindex="-1"])', container)
      .filter(el => !el.hasAttribute('hidden'));
  }

  function trapFocus(e) {
    if (!modalBg || !modalBg.classList.contains('open') || e.key !== 'Tab') return;
    const focusable = getFocusable(modalBg);
    if (!focusable.length) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function closeModal() {
    if (!modalBg) return;
    modalBg.classList.remove('open');
    modalBg.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (lastFocused && typeof lastFocused.focus === 'function') {
      lastFocused.focus();
    }
  }

  function openModal(title, html) {
    if (!modalBg || !modalTitle || !modalBody) return;
    lastFocused = document.activeElement;
    modalTitle.textContent = title || 'DETAILS';
    modalBody.innerHTML = html || '';
    wireCopy(modalBody);
    modalBg.classList.add('open');
    modalBg.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    if (modalClose) {
      modalClose.focus();
    }
  }

  if (modalClose) modalClose.addEventListener('click', closeModal);
  if (modalBg) {
    modalBg.addEventListener('click', (e) => {
      if (e.target === modalBg) closeModal();
    });
  }
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
    trapFocus(e);
  });

  // Expandable cards: data-modal points to a <template> id
  $$('[data-modal]').forEach(el => {
    const tid = el.getAttribute('data-modal');
    const t = tid ? document.getElementById(tid) : null;
    if (!t) return;

    const title = el.getAttribute('data-modal-title') || el.textContent.trim().slice(0, 60);
    const html = t.innerHTML;

    el.addEventListener('click', () => openModal(title, html));

    // keyboard support if it's not a button
    if (el.tagName !== 'BUTTON' && el.tagName !== 'A') {
      el.setAttribute('role', 'button');
      el.setAttribute('tabindex', '0');
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openModal(title, html);
        }
      });
    }
  });

  // Inline "See all work" toggle on homepage documented work section.
  const workExpandBtn = $('#workExpandBtn');
  const workMore = $('#workMore');
  if (workExpandBtn && workMore) {
    workMore.hidden = false;
    workMore.style.maxHeight = '0px';
    workMore.style.opacity = '0';
    workExpandBtn.addEventListener('click', () => {
      const expanded = workExpandBtn.getAttribute('aria-expanded') === 'true';
      workExpandBtn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      if (expanded) {
        workMore.style.maxHeight = '0px';
        workMore.style.opacity = '0';
      } else {
        workMore.style.maxHeight = `${workMore.scrollHeight}px`;
        workMore.style.opacity = '1';
      }
      const label = workExpandBtn.querySelector('span');
      if (label) label.textContent = expanded ? 'See all work' : 'Show less';
    });
  }

  loadVerifiedCounts();
  loadOpsMetrics();
  hydrateLabScreenshots();

  // DEV-only overflow detector: local hosts only.
  if (isLocalDebugHost) {
    const scanOverflow = () => {
      const viewport = Math.ceil(window.innerWidth);
      const offenders = $$("body *").filter((el) => {
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && (Math.ceil(rect.right) > viewport + 1 || Math.floor(rect.left) < -1);
      });
      if (offenders.length) {
        console.warn("[overflow-debug] possible offenders:", offenders.slice(0, 20));
      }
    };
    window.addEventListener("load", scanOverflow, { once: true });
    window.addEventListener("resize", scanOverflow);
  }
})();
  function formatMmDdYyyy(iso) {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return "";
    const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
    const dd = String(d.getUTCDate()).padStart(2, "0");
    const yyyy = String(d.getUTCFullYear());
    return `${mm}-${dd}-${yyyy}`;
  }
