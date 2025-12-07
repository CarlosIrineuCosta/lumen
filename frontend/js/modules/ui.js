
(function() {
    'use strict';

    if (window.LumenUI) {
        return; // Already loaded
    }

    const LumenUI = {
        /**
         * Shows a DaisyUI modal by its ID.
         * @param {string} modalId The ID of the modal <dialog> element.
         */
        showModal: function(modalId) {
            const modal = document.getElementById(modalId);
            if (modal && typeof modal.showModal === 'function') {
                try {
                    console.debug('[LumenUI] Opening modal', modalId);
                    modal.showModal();
                } catch (error) {
                    console.error(`[LumenUI] Failed to open modal "${modalId}"`, error);
                }
            } else {
                console.error(`LumenUI Error: Modal with ID "${modalId}" not found or is not a dialog.`);
            }
        },

        /**
         * Closes a DaisyUI modal by its ID.
         * @param {string} modalId The ID of the modal <dialog> element.
         */
        hideModal: function(modalId) {
            const modal = document.getElementById(modalId);
            if (modal && typeof modal.close === 'function') {
                try {
                    console.debug('[LumenUI] Closing modal', modalId);
                    modal.close();
                } catch (error) {
                    console.error(`[LumenUI] Failed to close modal "${modalId}"`, error);
                }
            } else {
                console.error(`LumenUI Error: Modal with ID "${modalId}" not found or is not a dialog.`);
            }
        }
    };

    window.LumenUI = LumenUI;

})();
