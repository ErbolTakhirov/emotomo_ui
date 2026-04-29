// emotomo-ui/static/utils.js

/**
 * Handles clicks on the main logo to redirect logged-in users to the catalog
 * and logged-out users to the landing page.
 */
function logoClick() {
  const token = localStorage.getItem('auth_token');
  window.location.href = token ? 'catalog.html' : 'index.html';
}
