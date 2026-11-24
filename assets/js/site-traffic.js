(() => {
  'use strict';

  const loader = document.currentScript;
  const account = loader?.dataset.goatcounterAccount?.trim();

  if (!account) return;

  const dashboardUrl = `https://${account}.goatcounter.com/`;
  const counterBase = `https://${account}.goatcounter.com/counter/`;

  function pagePath() {
    const canonical = document.querySelector('link[rel="canonical"]');

    try {
      return canonical ? new URL(canonical.href).pathname : window.location.pathname;
    } catch (_error) {
      return window.location.pathname;
    }
  }

  async function loadCount(path, target) {
    try {
      const response = await fetch(`${counterBase}${encodeURIComponent(path)}.json`, {
        mode: 'cors',
        credentials: 'omit',
      });

      if (!response.ok) throw new Error(`Counter returned ${response.status}`);

      const data = await response.json();
      target.textContent = data.count || '0';
    } catch (_error) {
      target.textContent = '—';
      target.closest('.site-traffic__metric')?.classList.add('is-unavailable');
    }
  }

  function mountTrafficCard() {
    const sidebar = document.querySelector('#sidebar');
    const sidebarBottom = sidebar?.querySelector('.sidebar-bottom');

    if (!sidebar || !sidebarBottom || sidebar.querySelector('#site-traffic')) return;

    const card = document.createElement('section');
    card.id = 'site-traffic';
    card.className = 'site-traffic';
    card.setAttribute('aria-label', 'Site traffic');
    card.innerHTML = `
      <div class="site-traffic__title">
        <i class="fa-solid fa-chart-simple" aria-hidden="true"></i>
        <span>Site traffic</span>
      </div>
      <div class="site-traffic__metrics">
        <div class="site-traffic__metric">
          <strong id="site-total-views" aria-live="polite">…</strong>
          <span>Total views</span>
        </div>
        <div class="site-traffic__metric">
          <strong id="site-page-views" aria-live="polite">…</strong>
          <span>This page</span>
        </div>
      </div>
      <a class="site-traffic__sources" href="${dashboardUrl}" target="_blank" rel="noopener noreferrer">
        <span>Traffic sources</span>
        <i class="fa-solid fa-chart-pie" aria-hidden="true"></i>
      </a>
    `;

    sidebar.insertBefore(card, sidebarBottom);

    loadCount('TOTAL', card.querySelector('#site-total-views'));
    loadCount(pagePath(), card.querySelector('#site-page-views'));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountTrafficCard, { once: true });
  } else {
    mountTrafficCard();
  }
})();
