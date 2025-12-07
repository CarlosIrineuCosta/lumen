// Lumen Utils - Utility Functions
// Global namespace: window.LumenUtils

window.LumenUtils = {
    
    // DOM Utilities
    dom: {
        // Get element with error checking
        get: function(selector) {
            const element = document.querySelector(selector);
            if (!element) {
                console.warn(`Element not found: ${selector}`);
            }
            return element;
        },

        // Get multiple elements
        getAll: function(selector) {
            return Array.from(document.querySelectorAll(selector));
        },

        // Create element with attributes and children
        create: function(tag, attributes = {}, children = []) {
            const element = document.createElement(tag);
            
            // Set attributes
            Object.entries(attributes).forEach(([key, value]) => {
                if (key === 'className') {
                    element.className = value;
                } else if (key === 'innerHTML') {
                    element.innerHTML = value;
                } else if (key === 'textContent') {
                    element.textContent = value;
                } else {
                    element.setAttribute(key, value);
                }
            });
            
            // Append children
            children.forEach(child => {
                if (typeof child === 'string') {
                    element.appendChild(document.createTextNode(child));
                } else if (child instanceof Node) {
                    element.appendChild(child);
                }
            });
            
            return element;
        },

        // Show/hide elements with animation
        show: function(element, duration = 250) {
            if (!element) return;
            
            element.style.display = 'block';
            element.style.opacity = '0';
            element.style.transition = `opacity ${duration}ms ease`;
            
            requestAnimationFrame(() => {
                element.style.opacity = '1';
            });
            
            return new Promise(resolve => {
                setTimeout(resolve, duration);
            });
        },

        hide: function(element, duration = 250) {
            if (!element) return;
            
            element.style.transition = `opacity ${duration}ms ease`;
            element.style.opacity = '0';
            
            return new Promise(resolve => {
                setTimeout(() => {
                    element.style.display = 'none';
                    resolve();
                }, duration);
            });
        },

        // Toggle element visibility
        toggle: function(element, duration = 250) {
            if (!element) return;
            
            const isVisible = element.style.display !== 'none' && 
                             getComputedStyle(element).display !== 'none';
            
            return isVisible ? this.hide(element, duration) : this.show(element, duration);
        },

        // Add class with animation support
        addClass: function(element, className, animated = false) {
            if (!element) return;
            
            element.classList.add(className);
            
            if (animated) {
                element.style.transition = 'all 250ms ease';
            }
        },

        // Remove class
        removeClass: function(element, className) {
            if (!element) return;
            element.classList.remove(className);
        },

        // Toggle class
        toggleClass: function(element, className) {
            if (!element) return;
            return element.classList.toggle(className);
        }
    },

    // Event Utilities
    events: {
        // Event listener with cleanup
        on: function(element, event, handler, options = {}) {
            if (!element) return null;
            
            element.addEventListener(event, handler, options);
            
            // Return cleanup function
            return () => {
                element.removeEventListener(event, handler, options);
            };
        },

        // One-time event listener
        once: function(element, event, handler) {
            if (!element) return null;
            
            const onceHandler = (e) => {
                handler(e);
                element.removeEventListener(event, onceHandler);
            };
            
            element.addEventListener(event, onceHandler);
            return () => element.removeEventListener(event, onceHandler);
        },

        // Debounced event handler
        debounce: function(func, delay = 300) {
            let timeoutId;
            return (...args) => {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => func.apply(this, args), delay);
            };
        },

        // Throttled event handler
        throttle: function(func, limit = 100) {
            let inThrottle;
            return (...args) => {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    },

    // API Utilities
    api: {
        // Base fetch wrapper with error handling
        request: async function(url, options = {}) {
            const config = window.LumenConfig;
            const defaultOptions = {
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            };

            const finalOptions = { ...defaultOptions, ...options };
            const fullUrl = url.startsWith('http') ? url : config.api.baseUrl + url;

            try {
                const response = await fetch(fullUrl, finalOptions);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return await response.json();
                } else {
                    return await response.text();
                }
            } catch (error) {
                console.error('API Request failed:', error);
                throw error;
            }
        },

        // GET request
        get: function(url, options = {}) {
            return this.request(url, { ...options, method: 'GET' });
        },

        // POST request
        post: function(url, data, options = {}) {
            return this.request(url, {
                ...options,
                method: 'POST',
                body: JSON.stringify(data)
            });
        },

        // PUT request
        put: function(url, data, options = {}) {
            return this.request(url, {
                ...options,
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },

        // DELETE request
        delete: function(url, options = {}) {
            return this.request(url, { ...options, method: 'DELETE' });
        }
    },

    // Storage Utilities
    storage: {
        // Get from localStorage with JSON parsing
        get: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.warn('Failed to parse localStorage item:', key, error);
                return defaultValue;
            }
        },

        // Set to localStorage with JSON stringification
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                console.error('Failed to save to localStorage:', key, error);
                return false;
            }
        },

        // Remove from localStorage
        remove: function(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (error) {
                console.error('Failed to remove from localStorage:', key, error);
                return false;
            }
        },

        // Clear all localStorage
        clear: function() {
            try {
                localStorage.clear();
                return true;
            } catch (error) {
                console.error('Failed to clear localStorage:', error);
                return false;
            }
        }
    },

    // Image Utilities
    images: {
        // Preload image
        preload: function(src) {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.onload = () => resolve(img);
                img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
                img.src = src;
            });
        },

        // Get image dimensions
        getDimensions: function(src) {
            return this.preload(src).then(img => ({
                width: img.naturalWidth,
                height: img.naturalHeight,
                aspectRatio: img.naturalWidth / img.naturalHeight
            }));
        },

        // Generate responsive image URLs
        getResponsiveUrl: function(baseUrl, size = 'medium') {
            const sizes = window.LumenConfig.gallery.imageSizes;
            const width = sizes[size] || sizes.medium;
            
            if (!width) return baseUrl;
            
            // Assume API supports ?w= parameter for resizing
            return `${baseUrl}?w=${width}`;
        },

        // Create image element with lazy loading
        createLazy: function(src, alt = '', className = '') {
            const img = document.createElement('img');
            img.setAttribute('data-src', src);
            img.alt = alt;
            img.className = className;
            img.loading = 'lazy';
            
            // Intersection Observer for lazy loading
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            img.src = img.getAttribute('data-src');
                            img.removeAttribute('data-src');
                            observer.unobserve(img);
                        }
                    });
                });
                
                observer.observe(img);
            } else {
                // Fallback for older browsers
                img.src = src;
            }
            
            return img;
        }
    },

    // Validation Utilities
    validation: {
        // Email validation
        isEmail: function(email) {
            const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return pattern.test(email);
        },

        // URL validation
        isUrl: function(url) {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        },

        // Image file validation
        isImageFile: function(file) {
            const allowedTypes = window.LumenConfig.upload.acceptedFileTypes;
            return allowedTypes.includes(file.type);
        },

        // File size validation
        isValidFileSize: function(file) {
            const maxSize = this.parseFileSize(window.LumenConfig.upload.maxFileSize);
            return file.size <= maxSize;
        },

        // Parse file size string (e.g., "50MB" -> bytes)
        parseFileSize: function(sizeStr) {
            const match = sizeStr.match(/^(\d+)([KMGT]?)B?$/i);
            if (!match) return 0;
            
            const size = parseInt(match[1]);
            const unit = match[2].toUpperCase();
            
            const multipliers = { '': 1, K: 1024, M: 1024**2, G: 1024**3, T: 1024**4 };
            return size * (multipliers[unit] || 1);
        }
    },

    // URL Utilities
    url: {
        // Get URL parameters
        getParams: function() {
            return new URLSearchParams(window.location.search);
        },

        // Get single parameter
        getParam: function(name, defaultValue = null) {
            const params = this.getParams();
            return params.get(name) || defaultValue;
        },

        // Set URL parameter without page reload
        setParam: function(name, value) {
            const url = new URL(window.location);
            url.searchParams.set(name, value);
            window.history.replaceState({}, '', url);
        },

        // Remove URL parameter
        removeParam: function(name) {
            const url = new URL(window.location);
            url.searchParams.delete(name);
            window.history.replaceState({}, '', url);
        },

        // Build query string from object
        buildQuery: function(params) {
            return new URLSearchParams(params).toString();
        }
    },

    // Device Detection
    device: {
        // Check if mobile device
        isMobile: function() {
            return window.matchMedia('(max-width: 767px)').matches;
        },

        // Check if tablet
        isTablet: function() {
            return window.matchMedia('(min-width: 768px) and (max-width: 1023px)').matches;
        },

        // Check if desktop
        isDesktop: function() {
            return window.matchMedia('(min-width: 1024px)').matches;
        },

        // Check if touch device
        isTouch: function() {
            return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        },

        // Get viewport dimensions
        getViewport: function() {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            };
        }
    },

    // Performance Utilities
    performance: {
        // Measure function execution time
        measure: function(name, fn) {
            const start = performance.now();
            const result = fn();
            const end = performance.now();
            
            if (window.LumenConfig.app.debug) {
                console.log(`Performance: ${name} took ${(end - start).toFixed(2)}ms`);
            }
            
            return result;
        },

        // Async function measurement
        measureAsync: async function(name, fn) {
            const start = performance.now();
            const result = await fn();
            const end = performance.now();
            
            if (window.LumenConfig.app.debug) {
                console.log(`Performance: ${name} took ${(end - start).toFixed(2)}ms`);
            }
            
            return result;
        },

        // Request idle callback polyfill
        requestIdle: function(callback, options = {}) {
            if ('requestIdleCallback' in window) {
                return requestIdleCallback(callback, options);
            } else {
                return setTimeout(callback, 1);
            }
        }
    },

    // Error Handling
    errors: {
        // Handle and log errors
        handle: function(error, context = 'Unknown') {
            const config = window.LumenConfig;
            
            console.error(`Error in ${context}:`, error);
            
            // Send to analytics if enabled
            if (config.analytics.enabled) {
                // Analytics error tracking would go here
            }
            
            // Show user-friendly message
            const message = this.getUserMessage(error);
            this.showToast(message, 'error');
            
            return message;
        },

        // Get user-friendly error message
        getUserMessage: function(error) {
            const config = window.LumenConfig;
            
            if (error.name === 'NetworkError' || (error.message && error.message.includes('fetch'))) {
                return config.errors.messages.network;
            } else if (error.status === 401 || (error.message && error.message.includes('auth'))) {
                return config.errors.messages.auth;
            } else if (error.message && error.message.includes('upload')) {
                return config.errors.messages.upload;
            } else {
                return config.errors.messages.general;
            }
        },

        // Show error toast
        showToast: function(message, type = 'error') {
            // This will be implemented by the UI module
            if (window.LumenUI && window.LumenUI.toast) {
                window.LumenUI.toast(message, type);
            } else {
                console.log(`Toast: ${message}`);
            }
        }
    },

    // User feedback methods
    showError: function(message) {
        this.errors.showToast(message, 'error');
    },

    showSuccess: function(message) {
        this.errors.showToast(message, 'success');
    },

    showWarning: function(message) {
        this.errors.showToast(message, 'warning');
    },

    showInfo: function(message) {
        this.errors.showToast(message, 'info');
    },
    
    // Image file validation (shortcut method)
    validateImageFile: function(file) {
        return this.validation.isImageFile(file);
    },
    
    // File size validation (shortcut method)  
    validateFileSize: function(file) {
        return this.validation.isValidFileSize(file);
    },

    // Initialize utilities
    init: function() {
        // Set up global error handling
        window.addEventListener('error', (event) => {
            this.errors.handle(event.error, 'Global Error');
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.errors.handle(event.reason, 'Unhandled Promise');
        });

        if (window.LumenConfig.app.debug) {
            console.log('🔧 Lumen Utils initialized');
        }
    }
};

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.LumenUtils.init();
});

// Export for debugging
if (window.LumenConfig?.app?.debug) {
    window.DEBUG_UTILS = window.LumenUtils;
}