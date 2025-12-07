/* Router Module
 * Simple hash-based routing for single page application
 * Uses Poor Man's Modules pattern with window.LumenRouter global
 */

window.LumenRouter = {
    // State
    currentRoute: 'gallery',
    routes: {},
    sections: {},
    loadingIndicator: null,

    // Initialize router
    init() {
        this.setupRoutes();
        this.cacheSections();
        this.setupEventListeners();
        this.handleHashChange();
    },

    // Setup available routes
    setupRoutes() {
        this.routes = {
            'gallery': {
                title: 'Gallery',
                section: 'gallery',
                render: () => this.renderGallery(),
                requireAuth: false
            },
            'upload': {
                title: 'Upload',
                section: 'gallery',
                render: () => this.renderUpload(),
                requireAuth: true
            },
            'profile': {
                title: 'Profile',
                section: 'profile',
                render: () => this.renderProfile(),
                requireAuth: true
            },
            'series': {
                title: 'Series',
                section: 'series',
                render: () => this.renderSeries(),
                requireAuth: false
            }
        };
    },

    // Cache key DOM sections for quicker access
    cacheSections() {
        this.sections = {
            gallery: document.getElementById('photo-gallery'),
            profile: document.getElementById('profile-view'),
            series: document.getElementById('series-view')
        };
    },

    // Setup event listeners
    setupEventListeners() {
        // Hash change listener
        window.addEventListener('hashchange', () => {
            this.handleHashChange();
        });

        // Navigation link listeners (delegated)
        document.addEventListener('click', (e) => {
            const navLink = e.target.closest('[data-route]');
            if (navLink) {
                e.preventDefault();
                const route = navLink.dataset.route;
                this.navigate(route);

                // Close mobile menu if open
                const mobileMenu = document.getElementById('mobileMenu');
                if (mobileMenu) {
                    mobileMenu.classList.add('hidden');
                }
            }
        });
    },

    // Handle hash change
    handleHashChange() {
        const hash = window.location.hash.substring(1); // Remove #
        const route = hash || 'gallery'; // Default to gallery
        this.loadRoute(route);
    },

    // Navigate to a route
    navigate(route) {
        if (!this.routes[route]) {
            console.error(`Route '${route}' not found`);
            route = 'gallery';
        }

        window.location.hash = route;
    },

    // Load and render a route
    async loadRoute(route) {
        const routeConfig = this.routes[route];
        if (!routeConfig) {
            console.error(`Route '${route}' not found`);
            return;
        }

        // Check authentication requirement
        if (routeConfig.requireAuth && !this.isAuthenticated()) {
            console.log(`Route '${route}' requires authentication`);
            this.showAuthRequired();
            return;
        }

        // Update current route
        this.currentRoute = route;

        // Update page title
        document.title = `${routeConfig.title} - Lumen Photography`;

        // Update navigation UI
        this.updateNavigationUI(route);

        // Show the proper section before rendering
        this.showSection(routeConfig.section);

        // Render the route
        this.showRouteLoading(routeConfig);
        try {
            await routeConfig.render();
        } catch (error) {
            console.error(`Error rendering route '${route}':`, error);
            this.renderError(error);
        } finally {
            this.hideRouteLoading();
        }
    },

    // Check if user is authenticated
    isAuthenticated() {
        return window.LumenAuth && LumenAuth.isAuthenticated();
    },

    // Show authentication required message
    showAuthRequired() {
        if (window.LumenApp?.showAuthModal) {
            LumenApp.showAuthModal();
        } else if (window.LumenUI) {
            LumenUI.showModal('authModal');
        }

        if (window.LumenUtils?.showError) {
            LumenUtils.showError('Please sign in to access this area.');
        }

        // Redirect back to gallery so the UI stays consistent
        if (this.currentRoute !== 'gallery') {
            this.navigate('gallery');
        }
    },

    // Update navigation UI to show active route
    updateNavigationUI(route) {
        document.querySelectorAll('[data-route]').forEach(link => {
            link.classList.remove('active');

            if (link.dataset.route === route) {
                link.classList.add('active');
            }
        });
    },

    // Toggle main sections based on the active route
    showSection(sectionKey) {
        if (!this.sections || Object.keys(this.sections).length === 0) {
            this.cacheSections();
        }

        Object.entries(this.sections).forEach(([key, element]) => {
            if (!element) return;

            if (key === sectionKey) {
                element.classList.remove('glass-hidden');
            } else if (!element.classList.contains('glass-hidden')) {
                element.classList.add('glass-hidden');
            }
        });
    },

    showRouteLoading(routeConfig) {
        const activeSection = this.sections?.[routeConfig?.section];
        if (!activeSection) return;

        // Add fade-out class to current content
        activeSection.classList.add('route-transitioning');

        // Show skeleton content based on route type
        if (window.LumenTemplates?.gallery?.loadingSkeleton && routeConfig?.section === 'gallery') {
            activeSection.innerHTML = window.LumenTemplates.gallery.loadingSkeleton(12);
        } else if (routeConfig?.section === 'profile') {
            activeSection.innerHTML = this.renderProfileSkeleton();
        } else if (routeConfig?.section === 'series') {
            activeSection.innerHTML = this.renderSeriesSkeleton();
        } else {
            // Fallback to generic loading indicator
            activeSection.innerHTML = this.renderGenericSkeleton();
        }

        // Remove transition class after a brief delay
        setTimeout(() => {
            activeSection.classList.remove('route-transitioning');
        }, 50);
    },

    hideRouteLoading() {
        if (!this.loadingIndicator) return;

        this.loadingIndicator.classList.remove('visible');
    },

    // Render error page
    renderError(error) {
        const activeSection = this.routes[this.currentRoute]?.section;
        const container = activeSection ? this.sections?.[activeSection] : null;

        if (container) {
            container.innerHTML = `
                <div class="container mx-auto px-4 py-16 text-center">
                    <h2 class="text-3xl font-bold mb-4 text-red-400">Error</h2>
                    <p class="text-gray-400 mb-8">Something went wrong loading this page.</p>
                    <p class="text-sm text-gray-500 mb-8">${error.message}</p>
                    <button onclick="LumenRouter.navigate('gallery')" class="glass-btn glass-btn-primary">
                        Go to Gallery
                    </button>
                </div>
            `;
        } else if (window.LumenUtils?.showError) {
            LumenUtils.showError(error.message || 'Something went wrong');
        }
    },

    // === ROUTE RENDERERS ===

    // Render gallery view
    async renderGallery() {
        const gallerySection = this.sections.gallery || document.getElementById('photo-gallery');
        if (!gallerySection) return;

        // Ensure gallery section is clear when first rendering
        if (gallerySection.children.length === 0 && window.LumenGallery?.renderSkeleton) {
            gallerySection.innerHTML = window.LumenGallery.renderSkeleton();
        }

        if (window.LumenGallery) {
            if (typeof LumenGallery.init === 'function') {
                LumenGallery.init(gallerySection);
            }

            if (typeof LumenGallery.renderGallery === 'function') {
                LumenGallery.renderGallery(gallerySection);
            }
        }
    },

    // Render upload view
    async renderUpload() {
        if (window.LumenUpload?.showUploadModal) {
            LumenUpload.showUploadModal();
        }
    },

    // Render profile view
    async renderProfile() {
        const profileSection = this.sections.profile || document.getElementById('profile-view');
        if (!profileSection) return;

        if (window.LumenProfile && typeof LumenProfile.showProfile === 'function') {
            await LumenProfile.showProfile('me', { renderInView: true, container: profileSection });
        }
    },

    // Render series view
    async renderSeries() {
        const seriesSection = this.sections.series || document.getElementById('series-view');
        if (!seriesSection) return;

        if (window.LumenSeries && typeof LumenSeries.show === 'function') {
            await LumenSeries.show(seriesSection);
        } else {
            // Fallback if series module not loaded
            seriesSection.innerHTML = `
                <div class="container mx-auto px-4 pt-20">
                    <div class="text-center">
                        <h2 class="text-3xl font-bold mb-4">Series</h2>
                        <p class="text-gray-400">Series module not loaded.</p>
                    </div>
                </div>
            `;
        }
    },

    // Get current route
    getCurrentRoute() {
        return this.currentRoute;
    },

    // Register a new route
    registerRoute(path, config) {
        this.routes[path] = config;
    },

    // Remove a route
    removeRoute(path) {
        delete this.routes[path];
    },

    // Skeleton rendering methods
    renderProfileSkeleton() {
        return `
            <div class="profile-shell">
                <div class="profile-header">
                    <div class="skeleton skeleton-avatar"></div>
                    <div class="profile-info">
                        <div class="skeleton skeleton-title"></div>
                        <div class="skeleton skeleton-text"></div>
                        <div class="skeleton skeleton-text short"></div>
                        <div class="profile-stats">
                            <div class="skeleton skeleton-stat"></div>
                            <div class="skeleton skeleton-stat"></div>
                            <div class="skeleton skeleton-stat"></div>
                        </div>
                    </div>
                </div>
                <div class="profile-tabs">
                    <div class="skeleton skeleton-tab"></div>
                    <div class="skeleton skeleton-tab"></div>
                    <div class="skeleton skeleton-tab"></div>
                </div>
                <div class="photos-section">
                    <div class="skeleton skeleton-section-title"></div>
                    <div class="user-photos-grid">
                        <div class="skeleton skeleton-photo"></div>
                        <div class="skeleton skeleton-photo"></div>
                        <div class="skeleton skeleton-photo"></div>
                        <div class="skeleton skeleton-photo"></div>
                    </div>
                </div>
            </div>
        `;
    },

    renderSeriesSkeleton() {
        return `
            <div class="container mx-auto px-4 pt-20">
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="series-grid">
                    <div class="skeleton skeleton-series-card"></div>
                    <div class="skeleton skeleton-series-card"></div>
                    <div class="skeleton skeleton-series-card"></div>
                </div>
            </div>
        `;
    },

    renderGenericSkeleton() {
        return `
            <div class="container mx-auto px-4 pt-20">
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text short"></div>
                <div class="skeleton-paragraph">
                    <div class="skeleton skeleton-line"></div>
                    <div class="skeleton skeleton-line"></div>
                    <div class="skeleton skeleton-line short"></div>
                </div>
            </div>
        `;
    }
};
