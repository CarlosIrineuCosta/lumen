/**
 * Glassmorphism Theme Configuration
 * Customizable values for the entire UI system
 * Designers can modify these values without touching CSS
 */

const GlassTheme = {
    // Base Colors (RGBA values for transparency control)
    colors: {
        primary: {
            r: 17, g: 25, b: 40,           // Dark blue-gray base
            light: 'rgba(17, 25, 40, 0.6)',
            medium: 'rgba(17, 25, 40, 0.75)',
            strong: 'rgba(17, 25, 40, 0.9)',
            solid: 'rgba(17, 25, 40, 1)'
        },
        secondary: {
            r: 25, g: 25, b: 25,           // Dark gray
            light: 'rgba(25, 25, 25, 0.6)',
            medium: 'rgba(25, 25, 25, 0.8)',
            strong: 'rgba(25, 25, 25, 0.9)',
            solid: 'rgba(25, 25, 25, 1)'
        },
        background: {
            r: 10, g: 10, b: 10,           // Very dark background
            light: 'rgba(10, 10, 10, 0.7)',
            medium: 'rgba(10, 10, 10, 0.85)',
            strong: 'rgba(10, 10, 10, 0.95)',
            solid: 'rgba(10, 10, 10, 1)'
        },
        accent: {
            r: 64, g: 149, b: 255,         // Blue accent
            light: 'rgba(64, 149, 255, 0.4)',
            medium: 'rgba(64, 149, 255, 0.6)',
            strong: 'rgba(64, 149, 255, 0.8)',
            solid: 'rgba(64, 149, 255, 1)'
        },
        border: {
            light: 'rgba(255, 255, 255, 0.1)',
            medium: 'rgba(255, 255, 255, 0.15)',
            strong: 'rgba(255, 255, 255, 0.2)',
            accent: 'rgba(64, 149, 255, 0.3)'
        },
        text: {
            primary: 'rgba(255, 255, 255, 0.9)',
            secondary: 'rgba(255, 255, 255, 0.7)',
            muted: 'rgba(255, 255, 255, 0.5)',
            disabled: 'rgba(255, 255, 255, 0.3)'
        }
    },

    // Blur Levels
    blur: {
        none: '0px',
        subtle: '6px',
        light: '8px',
        medium: '12px',
        strong: '16px',
        intense: '20px',
        extreme: '24px'
    },

    // Border Radius
    radius: {
        none: '0px',
        small: '6px',
        medium: '10px',
        large: '16px',
        xl: '20px',
        full: '50%'
    },

    // Spacing
    spacing: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '20px',
        '2xl': '24px',
        '3xl': '32px'
    },

    // Transitions
    transitions: {
        fast: '0.15s ease',
        normal: '0.3s ease',
        slow: '0.5s ease',
        spring: '0.3s cubic-bezier(0.25, 0.8, 0.25, 1)'
    },

    // Component Specific Settings
    components: {
        navbar: {
            background: 'var(--glass-bg-strong)',
            blur: 'var(--glass-blur-strong)',
            border: 'var(--glass-border-medium)',
            height: '60px'
        },
        button: {
            background: {
                default: 'var(--glass-primary-medium)',
                hover: 'var(--glass-primary-strong)',
                active: 'var(--glass-primary-solid)'
            },
            blur: 'var(--glass-blur-medium)',
            border: 'var(--glass-border-light)',
            padding: 'var(--glass-spacing-md) var(--glass-spacing-lg)'
        },
        card: {
            background: 'var(--glass-primary-light)',
            blur: 'var(--glass-blur-medium)',
            border: 'var(--glass-border-light)',
            padding: 'var(--glass-spacing-xl)'
        },
        modal: {
            backdrop: 'var(--glass-bg-medium)',
            background: 'var(--glass-bg-strong)',
            blur: 'var(--glass-blur-intense)',
            border: 'var(--glass-border-medium)'
        },
        input: {
            background: 'var(--glass-secondary-light)',
            blur: 'var(--glass-blur-light)',
            border: 'var(--glass-border-light)',
            focus: 'var(--glass-border-accent)'
        }
    },

    // Theme Presets
    presets: {
        dark: {
            name: 'Dark Glass',
            description: 'Deep dark theme with subtle glass effects'
        },
        light: {
            name: 'Light Glass',
            description: 'Bright theme with enhanced transparency',
            colors: {
                primary: { r: 240, g: 245, b: 250 },
                secondary: { r: 230, g: 235, b: 240 },
                background: { r: 250, g: 250, b: 250 },
                text: {
                    primary: 'rgba(20, 20, 20, 0.9)',
                    secondary: 'rgba(20, 20, 20, 0.7)',
                    muted: 'rgba(20, 20, 20, 0.5)'
                }
            }
        },
        midnight: {
            name: 'Midnight Blue',
            description: 'Deep blue theme with enhanced contrast',
            colors: {
                primary: { r: 15, g: 23, b: 42 },
                accent: { r: 96, g: 165, b: 250 }
            }
        }
    }
};

// Generate CSS Variables from Configuration
function generateCSSVariables(theme = GlassTheme) {
    const variables = {};

    // Color Variables
    Object.entries(theme.colors).forEach(([category, colors]) => {
        if (typeof colors === 'object' && colors.r !== undefined) {
            // RGB color object
            variables[`--glass-${category}-rgb`] = `${colors.r}, ${colors.g}, ${colors.b}`;
            Object.entries(colors).forEach(([variant, value]) => {
                if (variant !== 'r' && variant !== 'g' && variant !== 'b') {
                    variables[`--glass-${category}-${variant}`] = value;
                }
            });
        } else if (typeof colors === 'object') {
            // Nested color object
            Object.entries(colors).forEach(([variant, value]) => {
                variables[`--glass-${category}-${variant}`] = value;
            });
        }
    });

    // Other Properties
    ['blur', 'radius', 'spacing', 'transitions'].forEach(category => {
        Object.entries(theme[category]).forEach(([size, value]) => {
            variables[`--glass-${category}-${size}`] = value;
        });
    });

    return variables;
}

// Apply Theme Preset
function applyPreset(presetName) {
    const preset = GlassTheme.presets[presetName];
    if (!preset) return GlassTheme;

    // Deep merge preset with base theme
    const mergedTheme = JSON.parse(JSON.stringify(GlassTheme));
    if (preset.colors) {
        Object.assign(mergedTheme.colors, preset.colors);
    }

    return mergedTheme;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GlassTheme, generateCSSVariables, applyPreset };
} else if (typeof window !== 'undefined') {
    window.GlassTheme = { GlassTheme, generateCSSVariables, applyPreset };
}