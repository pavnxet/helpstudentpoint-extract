const MANIFEST_URL = 'downloaded.json';
const SOURCE_BASE = 'https://file.helpstudentpoint.com/wp-content/uploads/2026/06/';

let allFiles = [];
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', init);

async function init() {
  setupSpotlight();
  setupScrollProgress();
  setupFAB();
  setupReveal();

  await loadFiles();
  document.getElementById('loading').style.display = 'none';

  document.getElementById('searchInput').addEventListener('input', renderFiles);

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderFiles();
    });
  });
}

async function loadFiles() {
  try {
    const resp = await fetch(MANIFEST_URL + '?t=' + Date.now());
    if (!resp.ok) throw new Error('Manifest not found');
    const manifest = await resp.json();

    allFiles = Object.entries(manifest).map(([name, info]) => ({
      name,
      url: info.url || (SOURCE_BASE + encodeURIComponent(name)),
      discovered_at: info.discovered_at || info.downloaded_at || '',
      type: getFileType(name),
    }));

    allFiles.sort((a, b) => {
      if (a.discovered_at && b.discovered_at) {
        return new Date(b.discovered_at) - new Date(a.discovered_at);
      }
      return a.name.localeCompare(b.name);
    });

    updateStats();
    renderFiles();
  } catch (e) {
    document.getElementById('loading').innerHTML =
      '<div class="empty-state"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg><h3>No files yet</h3><p>The GitHub Action hasn\'t downloaded any files yet. Check back soon!</p></div>';
  }
}

function getFileType(name) {
  const ext = name.split('.').pop().toLowerCase();
  if (['pdf'].includes(ext)) return 'pdf';
  if (['jpeg', 'jpg', 'png', 'gif', 'webp'].includes(ext)) return 'image';
  return 'other';
}

function updateStats() {
  const pdfCount = allFiles.filter(f => f.type === 'pdf').length;
  const imageCount = allFiles.filter(f => f.type === 'image').length;
  document.getElementById('statTotal').textContent = allFiles.length;
  document.getElementById('statPdfs').textContent = pdfCount;
  document.getElementById('statImages').textContent = imageCount;
}

function renderFiles() {
  const query = document.getElementById('searchInput').value.toLowerCase().trim();
  const grid = document.getElementById('fileGrid');

  let filtered = allFiles;

  if (currentFilter !== 'all') {
    filtered = filtered.filter(f => f.type === currentFilter);
  }

  if (query) {
    filtered = filtered.filter(f => f.name.toLowerCase().includes(query));
  }

  if (filtered.length === 0) {
    grid.innerHTML =
      '<div class="empty-state" style="grid-column:1/-1;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><h3>No files found</h3><p>Try a different search term or filter.</p></div>';
    return;
  }

  grid.innerHTML = filtered.map((f, i) => `
    <div class="file-card" style="animation-delay:${Math.min(i * 30, 500)}ms">
      <div class="file-card-icon ${f.type}">
        ${f.type === 'pdf'
          ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>'
          : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>'
        }
      </div>
      <div class="file-card-body">
        <div class="file-card-name">${escapeHtml(f.name)}</div>
        <div class="file-card-meta">
          <span class="tag ${f.type}">${f.type.toUpperCase()}</span>
        </div>
        <div class="file-card-actions">
          <a href="${f.url}" class="btn btn-primary" target="_blank" rel="noopener">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Open
          </a>
        </div>
      </div>
    </div>
  `).join('');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/* ── Dynamic UI: Spotlight, Scroll Progress, FAB, Reveal ── */

function setupSpotlight() {
  const spotlight = document.getElementById('spotlight');
  let visible = false, raf = null, x = 0, y = 0;

  document.addEventListener('mousemove', (e) => {
    x = e.clientX; y = e.clientY;
    if (!visible) { spotlight.style.opacity = '1'; visible = true; }
    if (!raf) raf = requestAnimationFrame(update);
  });

  function update() {
    spotlight.style.transform = `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%)`;
    raf = null;
  }

  document.addEventListener('mouseleave', () => {
    spotlight.style.opacity = '0'; visible = false;
  });
}

function setupScrollProgress() {
  const bar = document.getElementById('scrollProgress');
  let raf = null;
  window.addEventListener('scroll', () => {
    if (!raf) raf = requestAnimationFrame(() => {
      const ratio = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight || 1);
      bar.style.transform = `scaleX(${ratio})`;
      raf = null;
    });
  }, { passive: true });
}

function setupFAB() {
  const fab = document.getElementById('fab');
  let raf = null;
  window.addEventListener('scroll', () => {
    if (!raf) raf = requestAnimationFrame(() => {
      fab.classList.toggle('visible', window.scrollY > 400);
      raf = null;
    });
  }, { passive: true });
}

function setupReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el));
}
