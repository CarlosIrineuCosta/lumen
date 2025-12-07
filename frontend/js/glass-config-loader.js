/**
 * Glassmorphism Theme Configuration Loader
 * Injects theme variables from config/glass-theme.js into the CSS root
 */

document.addEventListener('DOMContentLoaded', () => {
    // Ensure GlassTheme and its functions are available
    if (typeof window.GlassTheme === 'undefined' || typeof window.GlassTheme.generateCSSVariables === 'undefined') {
        console.error('GlassTheme or generateCSSVariables function not found. Make sure config/glass-theme.js is loaded before this script.');
        return;
    }

    const { generateCSSVariables } = window.GlassTheme;
    const variables = generateCSSVariables();
    const root = document.documentElement;

    // Apply variables to the :root element
    Object.entries(variables).forEach(([key, value]) => {
        root.style.setProperty(key, value);
    });

    console.log('Glassmorphism theme variables loaded.');
});
