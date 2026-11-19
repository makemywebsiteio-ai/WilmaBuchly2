/* Original implementation informed by the inspected animation principles.
   Reference inventory: research/animation-review.txt. No demo code or assets copied. */
(() => {
  const body = document.body;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const ease = 'cubic-bezier(.22,1,.36,1)';
  const button = document.querySelector('.motion-toggle');
  let savedPause = false;
  try { savedPause = localStorage.getItem('wilma-motion-paused') === 'true'; } catch {}
  let paused = savedPause || reduce.matches;
  const moving = new Set();
  function animate(el, frames, options, done) {
    if (paused || !el.animate) { done?.(); return null; }
    const a = el.animate(frames, { easing: ease, ...options });
    moving.add(a);
    a.finished.then(() => { moving.delete(a); done?.(); }, () => moving.delete(a));
    return a;
  }
  function applyMotion() {
    paused = savedPause || reduce.matches;
    body.classList.toggle('motion-paused', paused);
    body.classList.toggle('motion-on', !paused);
    if (paused) for (const a of [...moving]) { try { a.finish(); } catch { a.cancel(); } }
    button.textContent = reduce.matches ? 'Verminderde beweging actief' : paused ? 'Animaties hervatten' : 'Animaties pauzeren';
    button.setAttribute('aria-pressed', String(paused));
    button.disabled = reduce.matches;
  }
  button.hidden = false;
  button.addEventListener('click', () => {
    savedPause = !paused;
    try { localStorage.setItem('wilma-motion-paused', String(savedPause)); } catch {}
    applyMotion();
  });
  reduce.addEventListener('change', applyMotion);
  applyMotion();
  document.addEventListener('visibilitychange', () => body.classList.toggle('tab-hidden', document.hidden));
  if ('IntersectionObserver' in window) {
    const shapeObserver = new IntersectionObserver(entries => entries.forEach(e => e.target.classList.toggle('in-view', e.isIntersecting)));
    document.querySelectorAll('.petal-field,.calm-ambient').forEach(el => shapeObserver.observe(el));
    const revealSelector = [
      '.hero-copy > *', '.hero-visual', '.hero-bottom > span', '.page-intro .wrap > *',
      '.welcome > .eyebrow', '.welcome-grid > h2', '.prose > h2', '.prose > h3',
      '.prose > p', '.prose > ul', '.prose > ol', '.section-side > *', '.treatment',
      '.home-about-photo', '.shop-mosaic > img', '.section-heading', '.blog-card',
      '.product-card', '.chapter-photos > button', '.photo-strip > button',
      '.contact-info > *', '.form-panel', '.review', '.closing .wrap > *', '.footer-grid > div'
    ].join(',');
    const reveals = new IntersectionObserver(entries => {
      let stagger = 0;
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        reveals.unobserve(el);
        el.dataset.entered = 'true';
        const isPhoto = el.matches('.hero-visual,.home-about-photo,.photo-expand,img');
        const delay = Math.min(stagger++ * 75, 300);
        animate(el, [
          { opacity: 0, transform: isPhoto ? 'translateY(24px) scale(.98)' : 'translateY(22px)' },
          { opacity: 1, transform: 'none' }
        ], { duration: isPhoto ? 950 : 780, delay, fill: 'backwards' });
      });
    }, { threshold: .08, rootMargin: '0px 0px -20px 0px' });
    document.querySelectorAll(revealSelector).forEach(el => {
      // Do not animate a child separately when its whole panel is already entering.
      if (el.closest('.detail-body,.form-panel') && !el.matches('.form-panel')) return;
      reveals.observe(el);
    });
  }

  const nav = document.querySelector('#navigation');
  const menu = document.querySelector('.menu-toggle');
  const mobile = matchMedia('(max-width: 950px)');
  let navAnimation;
  let menuOpen = false;
  body.classList.add('js-nav');
  function setMenu(open, focusBack = false) {
    menuOpen = open;
    navAnimation?.cancel();
    menu.setAttribute('aria-expanded', String(open));
    menu.querySelector('.menu-label').textContent = open ? 'Sluiten' : 'Menu';
    if (open) {
      nav.hidden = false; nav.inert = false;
      navAnimation = animate(nav, [{ opacity: 0, transform: 'translateY(-8px)' }, { opacity: 1, transform: 'none' }], { duration: 250 });
    } else {
      nav.inert = mobile.matches;
      if (focusBack) menu.focus();
      navAnimation = animate(nav, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateY(-6px)' }], { duration: 180 }, () => { if (!menuOpen && mobile.matches) nav.hidden = true; });
    }
  }
  function resizeNav() {
    navAnimation?.cancel();menuOpen = false;
    menu.hidden = !mobile.matches;
    nav.hidden = mobile.matches;nav.inert = mobile.matches;
    menu.setAttribute('aria-expanded', 'false');
    menu.querySelector('.menu-label').textContent = 'Menu';
    if (mobile.matches && nav.contains(document.activeElement)) menu.focus();
  }
  menu.addEventListener('click', () => setMenu(!menuOpen));
  mobile.addEventListener('change', resizeNav);resizeNav();
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && menuOpen) setMenu(false, true); });
  document.addEventListener('click', e => { if (menuOpen && !nav.contains(e.target) && !menu.contains(e.target)) setMenu(false, nav.contains(document.activeElement)); });
  nav.addEventListener('click', e => { if (mobile.matches && e.target.closest('a')) setMenu(false); });
  // Native details retain keyboard semantics and work without JavaScript.
  document.querySelectorAll('.treatment').forEach(details => {
    const summary = details.querySelector('summary');
    const panel = details.querySelector('.detail-body');
    let animation, desired = details.open;
    summary.addEventListener('click', e => {
      e.preventDefault();desired = !desired;
      const from = details.getBoundingClientRect().height;
      animation?.cancel();details.style.height = '';details.style.overflow = '';
      if (paused) { details.open = desired; panel.inert = !desired; return; }
      const collapsed = summary.getBoundingClientRect().height + 1;
      details.open = true;panel.inert = !desired;
      const to = desired ? details.getBoundingClientRect().height : collapsed;
      details.style.overflow = 'hidden';
      animation = animate(details, [{ height: `${from}px` }, { height: `${to}px` }], { duration: 360 }, () => {
        details.open = desired;details.style.height = '';details.style.overflow = '';panel.inert = !desired;
      });
    });
  });
  // Full-size photographs, with native focus trapping and Escape handling.
  const dialog = document.querySelector('.lightbox');
  const largeImage = dialog.querySelector('img');
  let opener;
  document.querySelectorAll('.photo-expand').forEach(el => el.addEventListener('click', () => {
    const image = el.querySelector('img');opener = el;
    largeImage.src = image.src;largeImage.alt = image.alt;
    dialog.querySelector('p').textContent = image.alt;
    dialog.showModal();
    animate(dialog, [{ opacity: 0, transform: 'scale(.97)' }, { opacity: 1, transform: 'scale(1)' }], { duration: 300 });
  }));
  dialog.querySelector('button').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => { if (e.target === dialog) { const r = dialog.getBoundingClientRect();if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close(); } });
  dialog.addEventListener('close', () => opener?.focus());
  const filter = document.querySelector('#filter');
  const sorter = document.querySelector('#sort');
  if (filter) {
    const grid = document.querySelector('.filter-grid');
    const items = [...grid.children];
    function updateFilter() {
      const before = new Map(items.filter(el => !el.hidden).map(el => [el, el.getBoundingClientRect()]));
      const query = filter.value.toLocaleLowerCase('nl').trim();
      const ordered = [...items];
      if (sorter?.value === 'asc') ordered.sort((a,b) => +a.dataset.price - +b.dataset.price);
      if (sorter?.value === 'desc') ordered.sort((a,b) => +b.dataset.price - +a.dataset.price);
      if (sorter?.value === 'name') ordered.sort((a,b) => a.dataset.search.localeCompare(b.dataset.search,'nl'));
      let count=0;
      ordered.forEach(el => { el.hidden = !el.dataset.search.includes(query);if (!el.hidden) count++;grid.append(el); });
      if (!paused) ordered.filter(el => !el.hidden).forEach((el,index) => {
        const old = before.get(el), now = el.getBoundingClientRect();
        if (old) animate(el,[{transform:`translate(${old.left-now.left}px,${old.top-now.top}px)`},{transform:'none'}],{duration:430});
        else animate(el,[{opacity:0,transform:'translateY(14px)'},{opacity:1,transform:'none'}],{duration:480,delay:Math.min(index*35,180),fill:'backwards'});
      });
      document.querySelector('#result-count').textContent = `${count} ${sorter ? 'producten' : 'artikelen'}`;
      document.querySelector('.no-results').hidden = count > 0;
    }
    filter.addEventListener('input',updateFilter);sorter?.addEventListener('change',updateFilter);updateFilter();
  }
  document.querySelectorAll('.video-load').forEach(load => load.addEventListener('click', () => {
    const frame = document.createElement('iframe');
    const videoUrl = new URL(load.dataset.video);
    videoUrl.searchParams.delete('app_id');
    videoUrl.searchParams.set('dnt','1');
    videoUrl.searchParams.set('autoplay','0');
    videoUrl.searchParams.set('playsinline','1');
    frame.src = videoUrl.href;
    frame.title = 'Video over koperen producten uit het oorspronkelijke artikel';
    frame.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    load.replaceWith(frame);
    frame.tabIndex = 0;
    frame.focus();
    const retry = document.createElement('button');
    retry.type = 'button';
    retry.className = 'video-retry text-link';
    retry.textContent = 'Videospeler opnieuw laden';
    retry.addEventListener('click', () => {
      frame.src = videoUrl.href;
      frame.focus();
    });
    frame.parentElement.append(retry);
    frame.parentElement.querySelector('p').textContent = 'Start en pauzeer met de knop in de video. Geen beeld? Laad de speler opnieuw of open de video op Vimeo.';
  }));
  // No <form>, no named fields, no endpoint, no persistence. CSP blocks submission too.
  const test = document.querySelector('#test-form');
  if (test) {
    test.disabled = false;
    const email = document.querySelector('#email');
    const message = document.querySelector('#message');
    const error = document.querySelector('#email-error');
    const status = document.querySelector('#form-status');
    message.addEventListener('input', () => document.querySelector('#message-count').textContent = `${message.value.length} / 180 tekens`);
    test.addEventListener('click', () => {
      const valid = email.validity.valid;
      email.setAttribute('aria-invalid', String(!valid));error.hidden = valid;
      error.textContent = email.validity.valueMissing ? 'Vul een e-mailadres in om te testen.' : 'Vul een geldig e-mailadres in, bijvoorbeeld naam@voorbeeld.nl.';
      status.textContent = valid ? 'De invoer is geldig. Dit was alleen een lokale test; er is niets verzonden of opgeslagen.' : '';
      if (!valid) email.focus();
    });
    email.addEventListener('input', () => { email.removeAttribute('aria-invalid');error.hidden = true;status.textContent = ''; });
    document.querySelector('#preview-form').addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') { e.preventDefault();test.click(); } });
  }
})();
