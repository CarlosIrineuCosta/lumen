/**
 * Internationalization (i18n) Helper
 * Manages language translations for the Lumen UI
 */

const i18n = {
    translations: {},

    /**
     * Loads a language pack.
     * @param {string} lang - The language code (e.g., 'en').
     * @param {object} translations - The translation object.
     */
    load(lang, translations) {
        this.translations[lang] = translations;
        console.log(`Language pack for '${lang}' loaded.`);
    },

    /**
     * Translates a key path into the currently set language.
     * @param {string} keyPath - The key path (e.g., 'nav.explore').
     * @returns {string} The translated string or the key path if not found.
     */
    t(keyPath) {
        const lang = document.documentElement.lang || 'en';
        const keys = keyPath.split('.');
        let result = this.translations[lang];

        try {
            for (const key of keys) {
                result = result[key];
            }
            return result || keyPath;
        } catch (error) {
            console.warn(`Translation not found for key: ${keyPath}`);
            return keyPath;
        }
    },

    /**
     * Scans the DOM for elements with `data-i18n` attributes and applies translations.
     */
    applyTranslations() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const keyPath = element.getAttribute('data-i18n');
            const translation = this.t(keyPath);
            if (translation) {
                // Also check for placeholder attributes
                if (element.hasAttribute('placeholder')) {
                    element.placeholder = translation;
                } else {
                    element.textContent = translation;
                }
            }
        });
        console.log('UI translations applied.');
    },

    /**
     * Initializes the i18n system.
     */
    init() {
        // Load the default English translations if available
        if (typeof window.i18n_en !== 'undefined') {
            this.load('en', window.i18n_en);
        }

        // Set the default language on the HTML element
        if (!document.documentElement.lang) {
            document.documentElement.lang = 'en';
        }

        // Apply translations on initial load
        this.applyTranslations();
    }
};

// Initialize on script load
document.addEventListener('DOMContentLoaded', () => {
    i18n.init();
});
