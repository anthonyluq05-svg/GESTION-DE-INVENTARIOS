document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-formset]').forEach(container => {
    const prefix = container.dataset.formset;
    const total = document.querySelector(`[name="${prefix}-TOTAL_FORMS"]`);
    const maximum = document.querySelector(`[name="${prefix}-MAX_NUM_FORMS"]`);
    const area = container.querySelector('[data-formset-rows]');
    const template = container.querySelector('template[data-formset-empty]');
    const addButton = container.querySelector('[data-formset-add]');
    if (!total || !area || !template || !addButton) return;

    const updateCount = () => {
      const active = [...area.querySelectorAll('[data-formset-row]')]
        .filter(row => row.style.display !== 'none').length;
      const max = Number(maximum?.value || 50);
      addButton.disabled = Number(total.value) >= max;
      const count = container.querySelector('[data-formset-count]');
      if (count) count.textContent = `${active} producto(s) en la operación`;
    };

    addButton.addEventListener('click', () => {
      const i = Number(total.value);
      const max = Number(maximum?.value || 50);
      if (i >= max) return;
      const wrapper = document.createElement('div');
      wrapper.innerHTML = template.innerHTML.replaceAll('__prefix__', String(i)).trim();
      const newRow = wrapper.firstElementChild;
      if (!newRow) return;
      area.appendChild(newRow);
      total.value = String(i + 1);
      updateCount();
      newRow.querySelector('select')?.focus();
    });

    area.addEventListener('click', event => {
      const button = event.target.closest('[data-formset-remove]');
      if (!button) return;
      const row = button.closest('[data-formset-row]');
      if (!row) return;
      const deletion = row.querySelector('input[name$="-DELETE"]');
      if (deletion) {
        deletion.checked = true;
        row.style.display = 'none';
      }
      updateCount();
    });
    updateCount();
  });
});
