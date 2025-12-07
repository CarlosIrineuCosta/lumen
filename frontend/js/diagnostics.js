(function () {
  'use strict';
  if (!window.LumenConfig?.app?.debug) return;

  function check(selector, label) {
    const el = document.querySelector(selector);
    console.debug('[Diag] node', label, selector, !!el);
    return el;
  }

  function runOnce() {
    check('#profile-toggle', 'profile-toggle');
    check('#settings-modal', 'settings-modal');
    check('#settings-modal-content-wrapper', 'settings-modal-content-wrapper');
    check('#photo-gallery', 'photo-gallery');
  }

  document.addEventListener('DOMContentLoaded', runOnce);

  // re-check after app init
  setTimeout(runOnce, 1500);
})();

