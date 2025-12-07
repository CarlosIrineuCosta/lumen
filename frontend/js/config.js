// Lumen Configuration - Poor Man's Modules
// Global namespace: window.LumenConfig

const lumenApiOrigin = (() => {
    if (typeof window !== 'undefined' && window.location) {
        const protocol = window.location.protocol;
        const host = window.location.hostname;
        return `${protocol}//${host}:8080`;
    }
    return 'http://localhost:8080';
})();

window.LumenConfig = {
    // Application Info
    app: {
        name: 'Lumen',
        version: '2.0.0',
        environment: 'development', // development | production
        debug: true
    },

    // API Configuration
    api: {
        baseURL: lumenApiOrigin,
        endpoints: {
            auth: '/api/v1/auth/',
            photos: '/api/v1/photos/',
            albums: '/api/v1/albums/',
            users: '/api/v1/users/',
            upload: '/api/v1/upload/',
            search: '/api/v1/search/'
        },
        timeout: 30000,
        retries: 3
    },

    // Firebase Configuration
    firebase: {
        apiKey: "AIzaSyCt8ERvmCTaV5obZHBTqOAOSCMTq-v16nE",
        authDomain: "lumen-photo-app-20250731.firebaseapp.com",
        projectId: "lumen-photo-app-20250731",
        storageBucket: "lumen-photo-app-20250731.firebasestorage.app",
        messagingSenderId: "316971929294",
        appId: "1:316971929294:web:2163c5676bdeabe30e8a9f",
        measurementId: "G-9KNBNQWSDG"
    },

    // Gallery Configuration
    gallery: {
        // justifiedGallery settings
        rowHeight: 200,
        maxRowHeight: 400,
        margins: 4,
        border: 0,
        lastRow: 'justify',
        fixedHeight: false,
        captions: false,
        randomize: false,
        
        // Image sizes for responsive loading
        imageSizes: {
            thumb: 150,
            small: 400,
            medium: 800,
            large: 1200,
            original: null
        },
        
        // lightGallery settings
        lightbox: {
            speed: 400,
            hideBarsDelay: 2000,
            enableDrag: true,
            enableSwipe: true,
            download: false,
            zoom: true,
            thumbnail: true,
            animateThumb: false,
            showThumbByDefault: false,
            // Feature toggle: owner-only actions in lightbox toolbar
            ownerActions: false
        },
        
        // Loading behavior
        loading: {
            lazy: true,
            preloadNext: 3,
            fadeIn: true,
            skeleton: true
        }
    },

    // Upload Configuration
    upload: {
        // FilePond settings
        maxFileSize: '50MB',
        maxFiles: 20,
        acceptedFileTypes: [
            'image/jpeg',
            'image/jpg', 
            'image/png',
            'image/webp',
            'image/tiff',
            'image/raw'
        ],
        
        // Image processing
        imageResize: {
            enabled: true,
            targetWidth: 2048,
            targetHeight: 2048,
            mode: 'contain',
            quality: 0.85
        },
        
        // Upload behavior
        allowMultiple: true,
        instantUpload: false,
        allowReorder: true,
        allowRemove: true
    },

    // UI Configuration
    ui: {
        // Animation settings
        animations: {
            enabled: true,
            duration: 250,
            easing: 'ease-out'
        },
        
        // Theme settings
        theme: {
            mode: 'dark', // Only dark mode
            primaryColor: '#007AFF',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        },
        
        // Layout settings
        layout: {
            maxWidth: '1400px',
            headerHeight: '60px',
            categoryHeight: '50px',
            sidebarWidth: '300px'
        },
        
        // Modal settings
        modals: {
            overlay: true,
            closeOnOverlayClick: true,
            closeOnEscape: true,
            preventScroll: true
        }
    },

    // Storage Configuration
    storage: {
        // Local storage keys
        keys: {
            authToken: 'lumen_auth_token',
            userId: 'lumen_user_id',
            preferences: 'lumen_preferences',
            recentSearches: 'lumen_recent_searches',
            galleryView: 'lumen_gallery_view'
        },
        
        // Cache settings
        cache: {
            photos: 100,      // Number of photos to cache
            searches: 10,     // Number of search results to cache
            ttl: 3600000     // Cache TTL in milliseconds (1 hour)
        }
    },

    // Error Handling
    errors: {
        // Error types
        types: {
            NETWORK: 'network',
            AUTH: 'authentication',
            VALIDATION: 'validation',
            UPLOAD: 'upload',
            GALLERY: 'gallery'
        },
        
        // Retry settings
        retry: {
            attempts: 3,
            delay: 1000,
            backoff: 2
        },
        
        // User messages
        messages: {
            network: 'Connection error. Please check your internet.',
            auth: 'Authentication failed. Please sign in again.',
            upload: 'Upload failed. Please try again.',
            general: 'Something went wrong. Please try again.'
        }
    },

    // Feature Flags
    features: {
        geotagging: false,      // Location features
        comments: false,        // Photo comments
        likes: true,           // Photo appreciation
        sharing: false,        // Social sharing
        collections: true,     // Photo collections/albums
        search: true,          // Search functionality
        filters: false,        // Photo filters
        editing: false,        // Basic photo editing
        analytics: false,      // Usage analytics
        notifications: true    // Push notifications
    },

    // Performance Settings
    performance: {
        // Image optimization
        images: {
            lazyLoad: true,
            progressive: true,
            webpSupport: true,
            placeholder: 'blur'
        },
        
        // Network optimization
        network: {
            enableCompression: true,
            batchRequests: true,
            requestTimeout: 10000,
            maxConcurrent: 6
        },
        
        // Memory management
        memory: {
            maxCachedImages: 50,
            clearCacheOnLowMemory: true,
            preloadDistance: 3
        }
    },

    // Development Settings
    development: {
        // Mock data
        useMockData: false,
        mockDelay: 500,
        
        // Debug settings
        verbose: true,
        logLevel: 'debug', // error | warn | info | debug
        showPerformance: true,
        
        // Hot reload
        hotReload: false,
        
        // Test mode
        testMode: false
    },

    // Security Settings
    security: {
        // CORS settings
        cors: {
            credentials: 'include',
            allowedOrigins: ['http://localhost:8000', 'https://lumen.photos']
        },
        
        // Token settings
        tokens: {
            refreshThreshold: 300000, // 5 minutes
            autoRefresh: true
        },
        
        // Content Security
        csp: {
            enforceHttps: false, // Set true in production
            allowedImageSources: ['*'],
            allowedScriptSources: ['self', 'https://cdnjs.cloudflare.com']
        }
    },

    // Analytics Configuration (if enabled)
    analytics: {
        enabled: false,
        provider: null,
        trackingId: null,
        
        // Events to track
        events: {
            photoView: true,
            photoUpload: true,
            search: true,
            profileView: false
        }
    }
};

// Initialize configuration
window.LumenConfig.init = function() {
    // Merge with localStorage preferences if they exist
    const savedPrefs = localStorage.getItem(this.storage.keys.preferences);
    if (savedPrefs) {
        try {
            const prefs = JSON.parse(savedPrefs);
            this.ui = Object.assign(this.ui, prefs.ui || {});
            this.gallery = Object.assign(this.gallery, prefs.gallery || {});
        } catch (e) {
            console.warn('Failed to parse saved preferences:', e);
        }
    }

    // Set environment-specific overrides
    if (this.app.environment === 'production') {
        this.app.debug = false;
        this.development.verbose = false;
        this.development.logLevel = 'error';
        this.security.csp.enforceHttps = true;
        this.api.baseURL = 'https://api.lumen.photos';
    }

    // Initialize Firebase if not already done
    if (typeof firebase !== 'undefined' && !firebase.apps.length) {
        firebase.initializeApp(this.firebase);
    }

    // Log successful initialization
    if (this.app.debug) {
        console.log('🎨 Lumen Config initialized:', {
            version: this.app.version,
            environment: this.app.environment,
            features: Object.keys(this.features).filter(key => this.features[key])
        });
    }

    return this;
};

// Save preferences to localStorage
window.LumenConfig.savePreferences = function() {
    const prefs = {
        ui: this.ui,
        gallery: this.gallery,
        timestamp: Date.now()
    };
    
    try {
        localStorage.setItem(this.storage.keys.preferences, JSON.stringify(prefs));
        if (this.app.debug) {
            console.log('📱 Preferences saved');
        }
    } catch (e) {
        console.error('Failed to save preferences:', e);
    }
};

// Get configuration value by path (e.g., 'api.baseUrl')
window.LumenConfig.get = function(path, defaultValue = null) {
    const keys = path.split('.');
    let value = this;
    
    for (const key of keys) {
        if (value && typeof value === 'object' && key in value) {
            value = value[key];
        } else {
            return defaultValue;
        }
    }
    
    return value;
};

// Set configuration value by path
window.LumenConfig.set = function(path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    let target = this;
    
    for (const key of keys) {
        if (!(key in target) || typeof target[key] !== 'object') {
            target[key] = {};
        }
        target = target[key];
    }
    
    target[lastKey] = value;
    
    if (this.app.debug) {
        console.log(`⚙️ Config updated: ${path} =`, value);
    }
};

// Validate configuration
window.LumenConfig.validate = function() {
    const errors = [];
    
    // Check required API settings
    if (!this.api.baseURL) {
        errors.push('API base URL is required');
    }
    
    // Check Firebase configuration
    if (!this.firebase.apiKey) {
        errors.push('Firebase API key is required');
    }
    
    // Check upload settings
    if (this.upload.maxFileSize && !this.upload.maxFileSize.match(/^\d+[KMGT]?B$/i)) {
        errors.push('Invalid maxFileSize format');
    }
    
    if (errors.length > 0) {
        console.error('❌ Configuration validation failed:', errors);
        return false;
    }
    
    if (this.app.debug) {
        console.log('✅ Configuration validation passed');
    }
    
    return true;
};

// Export for debugging
if (window.LumenConfig.app.debug) {
    window.DEBUG_CONFIG = window.LumenConfig;
}
