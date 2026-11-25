const planner = document.getElementById('quote-planner');

if (planner) {
  const dateField = planner.querySelector('.planner-date');
  const shortcuts = [...document.querySelectorAll('button[form="quote-planner"]')].map(button => {
    // The original submit button also works without JavaScript.
    const link = document.createElement('a');
    link.className = button.className;
    link.append(...button.childNodes);
    button.replaceWith(link);
    return link;
  });

  function syncShortcuts() {
    if (dateField) {
      const moving = planner.elements.motif.value === 'demenagement';
      dateField.hidden = !moving;
      planner.elements.date_cles.disabled = !moving;
    }
    const url = new URL(planner.action);
    for (const [name, value] of new FormData(planner)) {
      if (value) url.searchParams.append(name, value);
    }
    const href = url.pathname + url.search + url.hash;
    for (const link of shortcuts) link.setAttribute('href', href);
    return url.search;
  }

  function rememberChoices() {
    const selection = syncShortcuts();
    if (history.state?.quotePlanner !== selection) {
      history.replaceState({...history.state, quotePlanner: selection}, '');
    }
  }

  function restoreChoices() {
    // Save only this history entry's selections, so other visits and services start fresh.
    const selection = new URLSearchParams(history.state?.quotePlanner);
    if (selection.get('service') === planner.elements.service.value) {
      for (const field of planner.elements) {
        if (!field.name || field.name === 'service') continue;
        if (field.type === 'checkbox' || field.type === 'radio') {
          field.checked = selection.getAll(field.name).includes(field.value);
        } else {
          field.value = selection.get(field.name) || '';
        }
      }
    }
    syncShortcuts();
  }

  planner.addEventListener('input', rememberChoices);
  planner.addEventListener('change', rememberChoices);
  planner.addEventListener('reset', () => queueMicrotask(rememberChoices));
  window.addEventListener('pageshow', restoreChoices);
  restoreChoices();
}
