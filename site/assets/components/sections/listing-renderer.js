function esc(text) {
  return String(text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderTags(tags) {
  return (tags || [])
    .map((tag) => `<span>${esc(tag)}</span>`)
    .join("");
}

function renderEvidence(evidence) {
  return (evidence || [])
    .map((entry) => `<a href="${esc(entry.url)}" target="_blank" rel="noreferrer">${esc(entry.label)}</a>`)
    .join("");
}

export function renderListing(container, items, kind = "projects") {
  if (!container) return;
  if (!items.length) {
    container.innerHTML = '<article class="listing-item"><h3>No results</h3><p>Try a different filter or search term.</p></article>';
    return;
  }

  container.innerHTML = items
    .map((item) => {
      const primaryLink = kind === "detections"
        ? `https://github.com/raylee-hawkins/HawkinsOperations/tree/main/${esc(item.location || "")}`
        : esc(item.page_url || item.repo_url || "#");
      const title = esc(item.title || item.platform || "Untitled");
      const summary = esc(item.summary || `${item.count || ""} ${item.format || ""}`.trim());
      const countPart = typeof item.count === "number" ? `<span>count ${item.count}</span>` : "";
      const typePart = item.type ? `<span>${esc(item.type)}</span>` : "";
      const formatPart = item.format ? `<span>${esc(item.format)}</span>` : "";
      return `<article class="listing-item">
  <h3><a href="${primaryLink}">${title}</a></h3>
  <p>${summary}</p>
  <div class="listing-meta">${countPart}${typePart}${formatPart}${renderTags(item.tags)}</div>
  <div class="listing-evidence">${renderEvidence(item.evidence)}</div>
</article>`;
    })
    .join("");
}
