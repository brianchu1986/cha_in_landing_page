const mobileMenu = document.querySelector('.mobile-menu');

if (mobileMenu) {
  const menuButton = mobileMenu.querySelector('summary');
  const menuLinks = mobileMenu.querySelectorAll('nav a');

  const syncMenuState = () => {
    const isOpen = mobileMenu.open;
    menuButton.setAttribute('aria-expanded', String(isOpen));
    menuButton.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
  };

  menuButton.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      mobileMenu.open = !mobileMenu.open;
    }
  });

  menuLinks.forEach((link) => {
    link.addEventListener('click', () => {
      mobileMenu.open = false;
    });
  });

  mobileMenu.addEventListener('toggle', syncMenuState);
  syncMenuState();
}
