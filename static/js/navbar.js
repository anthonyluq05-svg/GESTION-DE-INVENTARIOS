document.addEventListener('DOMContentLoaded', () => {
  const button = document.querySelector('[data-sgi-navbar-toggle]');
  const menu = document.getElementById('menuSgi');
  if (!button || !menu) return;
  button.addEventListener('click', () => {
    const visible = menu.classList.toggle('show');
    button.setAttribute('aria-expanded', String(visible));
  });
});
