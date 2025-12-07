/**
 * Language Registry and Detection System
 * Manages available languages and user preferences
 */

const LanguageRegistry = {
    // Available languages
    available: {
        en: {
            code: 'en',
            name: 'English',
            nativeName: 'English',
            flag: '🇺🇸',
            rtl: false,
            dateFormat: 'MM/DD/YYYY',
            timeFormat: '12h'
        },
        es: {
            code: 'es',
            name: 'Spanish',
            nativeName: 'Español',
            flag: '🇪🇸',
            rtl: false,
            dateFormat: 'DD/MM/YYYY',
            timeFormat: '24h'
        },
        fr: {
            code: 'fr',
            name: 'French',
            nativeName: 'Français',
            flag: '🇫🇷',
            rtl: false,
            dateFormat: 'DD/MM/YYYY',
            timeFormat: '24h'
        },
        de: {
            code: 'de',
            name: 'German',
            nativeName: 'Deutsch',
            flag: '🇩🇪',
            rtl: false,
            dateFormat: 'DD.MM.YYYY',
            timeFormat: '24h'
        },
        it: {
            code: 'it',
            name: 'Italian',
            nativeName: 'Italiano',
            flag: '🇮🇹',
            rtl: false,
            dateFormat: 'DD/MM/YYYY',
            timeFormat: '24h'
        },
        pt: {
            code: 'pt',
            name: 'Portuguese',
            nativeName: 'Português',
            flag: '🇵🇹',
            rtl: false,
            dateFormat: 'DD/MM/YYYY',
            timeFormat: '24h'
        },
        ru: {
            code: 'ru',
            name: 'Russian',
            nativeName: 'Русский',
            flag: '🇷🇺',
            rtl: false,
            dateFormat: 'DD.MM.YYYY',
            timeFormat: '24h'
        },
        ja: {
            code: 'ja',
            name: 'Japanese',
            nativeName: '日本語',
            flag: '🇯🇵',
            rtl: false,
            dateFormat: 'YYYY/MM/DD',
            timeFormat: '24h'
        },
        zh: {
            code: 'zh',
            name: 'Chinese',
            nativeName: '中文',
            flag: '🇨🇳',
            rtl: false,
            dateFormat: 'YYYY/MM/DD',
            timeFormat: '24h'
        },
        ar: {
            code: 'ar',
            name: 'Arabic',
            nativeName: 'العربية',
            flag: '🇸🇦',
            rtl: true,
            dateFormat: 'DD/MM/YYYY',
            timeFormat: '12h'
        }
    },

    // Default language
    default: 'en',

    // Storage key for user preference
    storageKey: 'lumen-language',

    /**
     * Get user's preferred language
     * Priority: localStorage > browser setting > default
     */
    getUserLanguage() {
        try {
            // Check localStorage first
            const saved = localStorage.getItem(this.storageKey);
            if (saved && this.available[saved]) {
                return saved;
            }
        } catch (error) {
            console.warn('Could not access localStorage for language preference');
        }

        // Check browser language
        const browserLang = this.detectBrowserLanguage();
        if (browserLang && this.available[browserLang]) {
            return browserLang;
        }

        // Fallback to default
        return this.default;
    },

    /**
     * Detect browser language
     */
    detectBrowserLanguage() {
        if (typeof navigator === 'undefined') return null;

        const languages = [
            navigator.language,
            ...(navigator.languages || [])
        ];

        for (const lang of languages) {
            // Extract language code (e.g., 'en-US' -> 'en')
            const code = lang.split('-')[0].toLowerCase();
            if (this.available[code]) {
                return code;
            }
        }

        return null;
    },

    /**
     * Set user language preference
     */
    setUserLanguage(languageCode) {
        if (!this.available[languageCode]) {
            console.warn(`Language "${languageCode}" not available`);
            return false;
        }

        try {
            localStorage.setItem(this.storageKey, languageCode);
            return true;
        } catch (error) {
            console.warn('Could not save language preference:', error);
            return false;
        }
    },

    /**
     * Get language information
     */
    getLanguageInfo(code) {
        return this.available[code] || this.available[this.default];
    },

    /**
     * Get all available languages as array
     */
    getAvailableLanguages() {
        return Object.values(this.available);
    },

    /**
     * Check if language is RTL
     */
    isRTL(code) {
        const lang = this.available[code];
        return lang ? lang.rtl : false;
    },

    /**
     * Get language direction
     */
    getDirection(code) {
        return this.isRTL(code) ? 'rtl' : 'ltr';
    },

    /**
     * Format date according to language preference
     */
    formatDate(date, languageCode) {
        const lang = this.getLanguageInfo(languageCode);
        const locale = lang.code;

        try {
            return new Intl.DateTimeFormat(locale).format(date);
        } catch (error) {
            // Fallback to basic formatting
            return date.toLocaleDateString();
        }
    },

    /**
     * Format time according to language preference
     */
    formatTime(date, languageCode) {
        const lang = this.getLanguageInfo(languageCode);
        const locale = lang.code;
        const hour12 = lang.timeFormat === '12h';

        try {
            return new Intl.DateTimeFormat(locale, {
                hour: '2-digit',
                minute: '2-digit',
                hour12: hour12
            }).format(date);
        } catch (error) {
            // Fallback to basic formatting
            return date.toLocaleTimeString();
        }
    },

    /**
     * Format number according to language preference
     */
    formatNumber(number, languageCode) {
        const lang = this.getLanguageInfo(languageCode);
        const locale = lang.code;

        try {
            return new Intl.NumberFormat(locale).format(number);
        } catch (error) {
            // Fallback to basic formatting
            return number.toString();
        }
    },

    /**
     * Get currency formatter for language
     */
    getCurrencyFormatter(languageCode, currency = 'USD') {
        const lang = this.getLanguageInfo(languageCode);
        const locale = lang.code;

        try {
            return new Intl.NumberFormat(locale, {
                style: 'currency',
                currency: currency
            });
        } catch (error) {
            // Fallback formatter
            return {
                format: (amount) => `${currency} ${amount}`
            };
        }
    },

    /**
     * Add new language to registry
     */
    addLanguage(code, config) {
        if (this.available[code]) {
            console.warn(`Language "${code}" already exists`);
            return false;
        }

        this.available[code] = {
            code,
            name: config.name || code.toUpperCase(),
            nativeName: config.nativeName || config.name || code.toUpperCase(),
            flag: config.flag || '',
            rtl: config.rtl || false,
            dateFormat: config.dateFormat || 'DD/MM/YYYY',
            timeFormat: config.timeFormat || '24h',
            ...config
        };

        return true;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageRegistry;
} else if (typeof window !== 'undefined') {
    window.LanguageRegistry = LanguageRegistry;
}