/* Fondo contextual: no interfiere con acciones o peticiones. */
(() => {
 const path = window.location.pathname.toLowerCase();
 let area = '';
 if (path.includes('/clientes/')) area = 'clientes';
 else if (path.includes('/usuarios/')) area = 'usuarios';
 else if (path.includes('/categorias/')) area = 'categorias';
 else if (path.includes('/proveedores/')) area = 'proveedores';
 else for (const name of ['compras','ventas','reportes','inventario','productos']) {
   if (path.includes('/' + name + '/')) { area = name; break; }
 }
 if (area) document.body.classList.add('sgi-' + area);
})();
/* Interacciones progresivas: respetan preferencias de movimiento reducido. */
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', event => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
  document.querySelectorAll('.nav-dropdown').forEach(details => {
    details.addEventListener('toggle', () => {
      if (!details.open) return;
      document.querySelectorAll('.nav-dropdown').forEach(other => {
        if (other !== details) other.open = false;
      });
    });
  });
  // Búsqueda local en tablas pequeñas: no cambia ni elimina datos.
  document.querySelectorAll('.table-responsive table').forEach((table, index) => {
    const rows = [...table.querySelectorAll('tbody tr')];
    if (rows.length < 4) return;
    const wrapper = table.closest('.table-responsive');
    const search = document.createElement('input');
    search.type = 'search';
    search.className = 'form-control table-search mb-2';
    search.placeholder = '🔎 Buscar en esta tabla…';
    search.setAttribute('aria-label', 'Buscar filas de la tabla');
    wrapper.parentNode.insertBefore(search, wrapper);
    search.addEventListener('input', () => {
      const term = search.value.toLocaleLowerCase().trim();
      rows.forEach(row => { row.hidden = !row.textContent.toLocaleLowerCase().includes(term); });
    });
  });
  if (!reduce) {
    document.querySelectorAll('.card, .table-responsive, .action-header').forEach((element, i) => {
      element.style.setProperty('--reveal-delay', `${Math.min(i * 35, 280)}ms`);
      element.classList.add('reveal-in');
    });
  }
  document.querySelectorAll('button[type="submit"]').forEach(button => {
    if (!button.closest('form')) return;
    button.closest('form').addEventListener('submit', event => {
      if (event.defaultPrevented) return;
      if (button.closest('form').checkValidity()) button.classList.add('submitting');
    });
  });
})();
