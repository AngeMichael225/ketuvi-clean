const gallery = document.querySelector('.cover-window');

if (gallery) {
  const frames = [...gallery.querySelectorAll('.cover-shot')];
  const controls = gallery.querySelector('.cover-controls');
  const linkLabel = gallery.querySelector('[data-scene-link-label]');
  const counter = gallery.querySelector('[data-count]');
  const sceneLink = gallery.querySelector('.cover-scene-link');
  const announcement = controls.querySelector('[role=status]');
  const pad = number => String(number).padStart(2, '0');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let current = 0;
  let requested = 0;
  let revision = 0;
  let fade;
  let transitionDone = Promise.resolve();

  reducedMotion.addEventListener('change', () => {
    if (reducedMotion.matches) fade?.finish();
  });

  async function move(step) {
    requested = (requested + step + frames.length) % frames.length;
    const next = requested;
    const version = ++revision;
    controls.dataset.pending = String(next !== current);
    if (next === current) return;
    const target = frames[next];
    const template = target.querySelector('template');
    if (template) template.replaceWith(template.content.cloneNode(true));
    const image = target.querySelector('img');
    try {
      await image.decode();
    } catch {
      if (revision === version) {
        requested = current;
        controls.dataset.pending = 'false';
        announcement.textContent = 'Impossible de charger cette photo.';
      }
      return;
    }
    // Finish the visible dissolve before applying the latest decoded request.
    await transitionDone;
    if (revision !== version) return;
    controls.dataset.pending = 'false';
    const previous = frames[current];
    previous.dataset.underlay = '';
    previous.dataset.current = 'false';
    previous.setAttribute('aria-hidden', 'true');
    target.dataset.enter = step > 0 ? 'next' : 'previous';
    target.dataset.current = 'true';
    target.setAttribute('aria-hidden', 'false');
    if (!reducedMotion.matches && target.animate) {
      fade = target.animate([{opacity: 0}, {opacity: 1}], {duration: 380, easing: 'ease-out'});
      transitionDone = fade.finished.finally(() => {
        previous.removeAttribute('data-underlay');
        fade = undefined;
      });
    } else {
      previous.removeAttribute('data-underlay');
    }
    current = next;
    counter.textContent = pad(current + 1) + ' / ' + pad(frames.length);
    linkLabel.textContent = target.dataset.destination;
    sceneLink.setAttribute('href', target.dataset.url);
    announcement.textContent = 'Photo ' + (current + 1) + ' sur ' + frames.length + '. ' + target.dataset.caption + '.';
  }

  for (const button of controls.querySelectorAll('[data-direction]')) {
    button.addEventListener('click', () => move(Number(button.dataset.direction)));
    button.hidden = false;
  }
  controls.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const step = { ArrowLeft: -1, ArrowRight: 1 }[event.key];
    if (!step) return;
    event.preventDefault();
    move(step);
  });
  let start;
  gallery.addEventListener('touchstart', event => {
    if (event.touches.length !== 1 || event.target.closest('a, button')) {
      start = null;
      return;
    }
    const { clientX: x, clientY: y } = event.touches[0];
    start = { x, y };
  }, { passive: true });
  gallery.addEventListener('touchcancel', () => { start = null; });
  gallery.addEventListener('touchend', event => {
    if (!start) return;
    const dx = event.changedTouches[0].clientX - start.x;
    const dy = event.changedTouches[0].clientY - start.y;
    start = null;
    if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy) * 1.7) {
      move(dx < 0 ? 1 : -1);
    }
  }, { passive: true });
  controls.hidden = false;
}
