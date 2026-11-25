const header = document.querySelector('.site-header');
const menuButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('#main-nav');
const serviceMenu = document.querySelector('.nav-services');

function setMenuOpen(open) {
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
  menu.dataset.open = String(open);
  if (!open) serviceMenu.open = false;
}

menuButton.addEventListener('click', () => {
  setMenuOpen(menuButton.getAttribute('aria-expanded') !== 'true');
});
header.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  if (serviceMenu.open) {
    serviceMenu.open = false;
    serviceMenu.querySelector('summary').focus();
  } else if (menuButton.getAttribute('aria-expanded') === 'true') {
    setMenuOpen(false);
    menuButton.focus();
  }
});
header.addEventListener('focusout', event => {
  if (!event.relatedTarget) return;
  if (!header.contains(event.relatedTarget)) setMenuOpen(false);
  else if (!serviceMenu.contains(event.relatedTarget)) serviceMenu.open = false;
});
document.addEventListener('click', event => {
  if (!header.contains(event.target)) setMenuOpen(false);
  else if (!serviceMenu.contains(event.target)) serviceMenu.open = false;
});
menu.addEventListener('click', event => {
  if (event.target.closest('a')) setMenuOpen(false);
});
matchMedia('(min-width: 961px)').addEventListener('change', () => setMenuOpen(false));
header.setAttribute('data-menu-ready', '');

// Some touch browsers defer :active on links until the tap ends.
let pressedAction;
function releaseAction() {
  pressedAction?.removeAttribute('data-touch-pressed');
  pressedAction = null;
}
document.addEventListener('pointerdown', event => {
  if (event.pointerType !== 'touch' || !event.isPrimary) return;
  releaseAction();
  pressedAction = event.target.closest('.button:not(:disabled), .mobile-quote:not(:disabled)');
  pressedAction?.setAttribute('data-touch-pressed', '');
}, {passive: true});
for (const type of ['pointerup', 'pointercancel', 'blur', 'pagehide']) {
  window.addEventListener(type, releaseAction, {passive: true});
}

const backToTop = document.querySelector('.back-to-top');
if (backToTop) {
  const updateBackToTop = () => {
    const nearTop = window.scrollY < window.innerHeight;
    if (backToTop.hidden !== nearTop) backToTop.hidden = nearTop;
  };
  backToTop.dataset.floating = '';
  updateBackToTop();
  window.addEventListener('scroll', updateBackToTop, {passive: true});
  window.addEventListener('resize', updateBackToTop);
  window.addEventListener('pageshow', updateBackToTop);
}

const footerInvitation = document.querySelector('.signature-invitation');
if (footerInvitation && 'IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const observer = new IntersectionObserver(entries => {
    if (!entries.some(entry => entry.isIntersecting)) return;
    footerInvitation.dataset.arrived = '';
    observer.disconnect();
  }, {threshold: .2});
  observer.observe(footerInvitation);
}

const query = new URLSearchParams(location.search);
const service = query.get('service');
const serviceSelect = document.querySelector('select[name=service]');
const initialOption = serviceSelect && [...serviceSelect.options].find(option => option.value === service);
if (initialOption) initialOption.defaultSelected = true;

const genericError = 'Votre demande n’a pas pu être confirmée. Les renseignements saisis sont conservés.';

async function deliveryMode() {
  const response = await fetch('/api/health', {cache: 'no-store', signal: AbortSignal.timeout(7000)});
  if (!response.ok) throw new Error('Service indisponible');
  const health = await response.json();
  if (health.ok === true && (health.delivery === 'local' || health.delivery === 'email')) return health.delivery;
  if (health.ok === true && health.delivery === undefined) return 'local';
  throw new Error('Mode inconnu');
}

document.querySelectorAll('[data-request-form]').forEach(async form => {
  const shell = form.closest('.form-shell');
  const success = shell.querySelector('.form-success');
  const status = form.querySelector('.form-status');
  const submit = form.querySelector('[type=submit]');
  const preparesEmail = form.dataset.delivery === 'mailto';
  let mode;
  try {
    mode = preparesEmail ? 'mailto' : await deliveryMode();
  } catch {
    return; // The direct email link remains available while the server is offline.
  }
  const isApplication = form.dataset.kind === 'application';
  const sendsEmail = mode === 'email';
  if (sendsEmail) {
    form.querySelector('.form-intro').textContent = 'Votre message sera envoyé directement à info@ketuvi.com.';
    submit.textContent = isApplication ? 'Envoyer ma candidature' : 'Envoyer ma demande';
  }
  const originalLabel = submit.textContent;
  let previousBody;
  let requestKey;
  const receipt = success.querySelector('[data-receipt]');
  const emailCopy = success.querySelector('[data-email-copy]');
  const recipient = emailCopy.getAttribute('href');
  const recap = success.querySelector('[data-quote-recap]');
  const brief = recap?.querySelector('[data-quote-brief]');
  const quoteDocument = recap?.querySelector('[data-quote-document]');
  const copyStatus = success.querySelector('[data-copy-status]');
  success.querySelector('[data-copy-quote]')?.addEventListener('click', async () => {
    const text = quoteDocument.value;
    if (!text || success.hidden) return;
    try {
      await navigator.clipboard.writeText(text);
      if (text === quoteDocument.value) copyStatus.textContent = preparesEmail ? 'Courriel copié.' : 'Demande et référence copiées.';
    } catch {
      if (text !== quoteDocument.value) return;
      recap.open = true;
      quoteDocument.focus();
      quoteDocument.select();
      copyStatus.textContent = 'Le texte est sélectionné. Utilisez la commande Copier de votre appareil.';
    }
  });
  const detailGroups = [...form.querySelectorAll('[data-quote-service]')];
  const note = form.elements.namedItem('message');

  function selectedDetails(group) {
    if (group.hidden) return [];
    return [...group.querySelectorAll('input, select')].filter(input =>
      input.type === 'checkbox' ? input.checked : Boolean(input.value)
    );
  }

  function detailLabel(input) {
    if (input.type === 'checkbox') return document.getElementById(input.getAttribute('aria-labelledby')).textContent;
    if (input.tagName === 'SELECT') return input.selectedOptions[0].textContent;
    return input.value;
  }

  if (detailGroups.length) {
    for (const group of detailGroups) {
      if (group.dataset.quoteService !== service) continue;
      for (const input of group.querySelectorAll('input, select')) {
        const initial = query.get(input.name);
        if (input.type === 'checkbox') {
          input.defaultChecked = query.getAll(input.name).includes(input.value);
        } else if (input.tagName === 'SELECT') {
          const option = [...input.options].find(item => item.value === initial);
          if (option) option.defaultSelected = true;
        } else if (query.get('motif') === 'demenagement' && /^\d{4}-\d{2}-\d{2}$/.test(initial)) {
          input.defaultValue = initial;
          if (!input.value) input.defaultValue = ''; // The date input rejects impossible dates.
        }
      }
    }
    const optionalNote = form.querySelector('[data-note-optional]');
    const preview = form.querySelector('[data-selection-preview]');
    const editor = form.querySelector('#quote-selection-fields');
    const editSelection = preview.querySelector('[data-edit-selection]');
    const applySelection = editor.querySelector('[data-apply-selection]');
    const listFormat = new Intl.ListFormat('fr-CA', {type: 'conjunction'});

    function refreshPreview() {
      const parts = detailGroups.map(group => {
        const labels = selectedDetails(group).map((input, index) => {
          if (input.type === 'date') {
            return input.valueAsDate.toLocaleDateString('fr-CA', {dateStyle: 'long', timeZone: 'UTC'});
          }
          const label = detailLabel(input);
          return index ? label.toLocaleLowerCase('fr-CA') : label;
        });
        return listFormat.format(labels);
      }).filter(Boolean);
      preview.querySelector('[data-selection-service]').textContent = serviceSelect.selectedOptions[0].textContent;
      preview.querySelector('[data-selection-details]').textContent = parts.length ? ' · ' + parts.join(' · ') : '';
      return parts.length > 0;
    }

    function showEditor(open) {
      editor.hidden = !open;
      preview.hidden = open;
      editSelection.setAttribute('aria-expanded', String(open));
    }
    editSelection.addEventListener('click', () => {
      preview.parentElement.dataset.edited = '';
      showEditor(true);
      serviceSelect.focus();
    });
    applySelection.addEventListener('click', () => {
      if (!serviceSelect.reportValidity()) return;
      refreshPreview();
      showEditor(false);
      editSelection.focus();
    });
    editor.addEventListener('invalid', () => showEditor(true), true);

    function updateDetails() {
      for (const group of detailGroups) {
        const isRelevant = group.dataset.quoteService === serviceSelect.value &&
          (!group.hasAttribute('data-moving-date') || form.elements.motif.value === 'demenagement');
        group.hidden = !isRelevant;
        const control = group.tagName === 'FIELDSET' ? group : group.querySelector('input, select');
        control.disabled = !isRelevant;
      }
      const hasDetail = detailGroups.some(group => selectedDetails(group).some(input => input.value !== 'a-discuter'));
      note.required = !hasDetail;
      note.minLength = hasDetail ? 0 : 10;
      optionalNote.hidden = !hasDetail;
      note.setCustomValidity('');
    }
    form.addEventListener('change', event => {
      if (event.target === serviceSelect || event.target.closest('[data-quote-service]')) {
        updateDetails();
        refreshPreview();
      }
    });
    function restoreSelection() {
      delete preview.parentElement.dataset.edited;
      updateDetails();
      const prepared = Boolean(initialOption) && refreshPreview();
      applySelection.hidden = !prepared;
      showEditor(!prepared);
    }
    form.addEventListener('reset', () => queueMicrotask(restoreSelection));
    restoreSelection();
  }

  form.addEventListener('input', event => {
    if (event.target.validity?.customError) event.target.setCustomValidity('');
    if (status.dataset.error === 'true') {
      status.textContent = '';
      status.dataset.error = 'false';
    }
  });

  function showConfirmation(value, serviceLabel, highlights, reference) {
    const subject = isApplication ? 'Candidature spontanée — Ketuvi' : 'Demande de soumission — Ketuvi';
    const context = isApplication ? `Disponibilités : ${value.availability || 'Non précisées'}` : `Service : ${serviceLabel || 'Non précisé'}`;
    let message = `${subject}\n\nNom : ${value.name.trim()}\nCourriel : ${value.email.trim()}\nTéléphone : ${value.phone.trim() || 'Non précisé'}\nVille : ${value.location.trim() || 'Non précisée'}\n${context}\n\n${value.message.trim()}`;
    if (reference) {
      receipt.textContent = reference;
      message += `\n\n${sendsEmail ? 'Référence' : 'Référence locale'} : ${reference}`;
    } else {
      message += '\n\n' + form.querySelector('.consent span').textContent;
    }
    if (recap) {
      brief.textContent = [serviceLabel, ...highlights].filter(Boolean).join(' · ');
      quoteDocument.value = message;
      if (!preparesEmail) {
        const deliveryStatus = sendsEmail ? 'Envoi accepté par le service de messagerie.' : 'Enregistrée sur le serveur de l’aperçu. À envoyer à Ketuvi par courriel.';
        quoteDocument.value += '\nStatut : ' + deliveryStatus;
      }
    }
    if (sendsEmail) {
      success.querySelector('h2').textContent = isApplication ? 'Candidature transmise.' : 'Demande transmise.';
      success.querySelector('.delivery-note').textContent = 'Le service de messagerie a accepté votre message à destination de info@ketuvi.com.';
      emailCopy.hidden = true;
    } else {
      emailCopy.href = recipient + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(message.replace(/\r?\n/g, '\r\n'));
    }
    form.hidden = true;
    success.hidden = false;
    success.focus();
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (form.hidden || submit.disabled || !form.reportValidity()) return;
    const fields = new FormData(form);
    const detailLines = [];
    const highlights = [];
    for (const group of detailGroups) {
      for (const input of group.querySelectorAll('[name]')) fields.delete(input.name);
      const labels = selectedDetails(group).map(detailLabel);
      if (labels.length) {
        const selection = labels.join(', ');
        detailLines.push(group.dataset.summary + ' : ' + selection + '.');
        highlights.push(selection);
      }
    }
    const value = Object.fromEntries(fields);
    value.consent = fields.has('consent');
    if (detailLines.length) {
      const summary = detailLines.join('\n');
      const detail = value.message.trim();
      value.message = detail ? summary + '\n\n' + detail : summary;
      if (value.message.length > note.maxLength) {
        const maxDetail = note.maxLength - summary.length - 2;
        note.setCustomValidity('Limitez vos précisions à ' + maxDetail + ' caractères pour cette sélection.');
        note.reportValidity();
        return;
      }
    }
    const serviceLabel = serviceSelect?.selectedOptions[0]?.textContent;
    if (preparesEmail) {
      showConfirmation(value, serviceLabel, highlights);
      return;
    }
    value.expectedDelivery = mode;
    const body = JSON.stringify(value);
    if (body !== previousBody) {
      requestKey = crypto.randomUUID();
      previousBody = body;
    }
    submit.disabled = true;
    submit.textContent = sendsEmail ? 'Envoi…' : 'Enregistrement…';
    form.setAttribute('aria-busy', 'true');
    status.textContent = '';
    status.dataset.error = 'false';
    const abort = new AbortController();
    const timer = setTimeout(() => abort.abort(), 12000);
    try {
      const response = await fetch('/api/requests', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'Idempotency-Key': requestKey},
        body,
        signal: abort.signal
      });
      const result = await response.json().catch(() => null);
      if (!response.ok) {
        const field = result?.field && form.elements.namedItem(result.field);
        const message = result?.error || genericError;
        if (field && field.value === value[result.field]) {
          field.setCustomValidity(message);
          field.reportValidity();
        }
        throw new Error(message);
      }
      if (result?.ok !== true || typeof result.receipt !== 'string' || !result.receipt || (result.delivery ?? 'local') !== mode) {
        throw new Error(genericError);
      }
      showConfirmation(value, serviceLabel, highlights, result.receipt);
    } catch (error) {
      status.dataset.error = 'true';
      if (error.name === 'AbortError') status.textContent = 'Le serveur tarde à confirmer la réception. Les renseignements saisis sont conservés.';
      else if (error instanceof TypeError) status.textContent = 'La connexion est interrompue. Les renseignements saisis sont conservés.';
      else status.textContent = error.message;
    } finally {
      clearTimeout(timer);
      submit.disabled = false;
      submit.textContent = originalLabel;
      form.removeAttribute('aria-busy');
    }
  });

  shell.querySelector('[data-new-request]').addEventListener('click', () => {
    form.reset();
    previousBody = undefined;
    status.textContent = '';
    if (receipt) receipt.textContent = '';
    if (recap) {
      recap.open = false;
      brief.textContent = '';
      quoteDocument.value = '';
      copyStatus.textContent = '';
    }
    emailCopy.href = recipient;
    success.hidden = true;
    form.hidden = false;
    form.elements.name.focus();
  });
  submit.disabled = false;
  form.hidden = false;
  const fallback = shell.querySelector('.form-fallback');
  if (fallback) fallback.hidden = true;
});
