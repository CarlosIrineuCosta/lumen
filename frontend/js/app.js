/* Main Application Coordinator
 * Initializes all modules and coordinates interactions
 * Uses Poor Man's Modules pattern with window.LumenApp global
 */

window.LumenApp = {
    // State
    initialized: false,
    modules: [],
    
    // Initialize the application
    async init() {
        if (this.initialized) {
            console.log('App already initialized');
            return;
        }
        
        console.log('Initializing Lumen PWA...');
        
        try {
            // Initialize modules in correct order
            await this.initializeModules();
            
            // Setup global event listeners
            this.setupGlobalEventListeners();
            
            // Setup navigation
            this.setupNavigation();
            
            // Initialize auth modal
            this.setupAuthModal();
            
            // Start the application
            await this.start();
            
            this.initialized = true;
            console.log('Lumen PWA initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize app:', error);
            this.showInitError(error);
        }
    },
    
    // Initialize all modules in order
    async initializeModules() {
        const moduleOrder = [
            'LumenUtils',
            'LumenAuth',
            'LumenAPI',
            'LumenRouter',
            'LumenGallery',
            'LumenUpload',
            'LumenSearch'
        ];
        
        for (const moduleName of moduleOrder) {
            if (window[moduleName] && typeof window[moduleName].init === 'function') {
                try {
                    console.log(`Initializing ${moduleName}...`);
                    await window[moduleName].init();
                    this.modules.push(moduleName);
                } catch (error) {
                    console.error(`Failed to initialize ${moduleName}:`, error);
                }
            } else {
                console.warn(`Module ${moduleName} not found or missing init method`);
            }
        }
    },
    
    // Setup global event listeners
    setupGlobalEventListeners() {
        // Auth state changes
        document.addEventListener('auth-changed', (e) => {
            this.handleAuthChange(e.detail);
        });
        
        // User needs onboarding
        document.addEventListener('user-needs-onboarding', (e) => {
            this.handleOnboarding(e.detail);
        });
        
        // Error handling
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            LumenUtils.showError('An unexpected error occurred');
        });
        
        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            LumenUtils.showError('An unexpected error occurred');
        });
        
        // Online/offline status
        window.addEventListener('online', () => {
            LumenUtils.showSuccess('Connection restored');
        });
        
        window.addEventListener('offline', () => {
            LumenUtils.showError('Connection lost. Some features may not work.');
        });
    },
    
    // Setup navigation
    setupNavigation() {
        // Mobile menu toggle
        document.addEventListener('click', (e) => {
            if (e.target.closest('#mobileMenuBtn')) {
                this.toggleMobileMenu();
            }
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            const mobileMenu = document.getElementById('mobileMenu');
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            
            if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
                if (!mobileMenu.contains(e.target) && !mobileMenuBtn?.contains(e.target)) {
                    this.closeMobileMenu();
                }
            }
        });
        
        // Auth button listeners
        document.addEventListener('click', (e) => {
            const loginTrigger = e.target.closest('#loginBtn, #mobileLoginBtn');
            if (loginTrigger) {
                e.preventDefault();
                this.handleLoginPrompt();
                return;
            }

            const googleButton = e.target.closest('#googleSignIn');
            if (googleButton) {
                e.preventDefault();
                this.handleGoogleSignIn(googleButton);
                return;
            }

            if (e.target.closest('#logoutBtn, #mobileLogoutBtn')) {
                this.handleLogout();
            }
        });
        
        // Profile button listener
        document.addEventListener('click', (e) => {
            if (e.target.closest('#profile-toggle')) {
                e.preventDefault();
                if (window.LumenRouter && typeof LumenRouter.navigate === 'function') {
                    LumenRouter.navigate('profile');
                } else if (window.LumenProfile && typeof LumenProfile.showProfile === 'function') {
                    const profileContainer = document.getElementById('profile-view');
                    LumenProfile.showProfile('me', { renderInView: true, container: profileContainer });
                } else {
                    console.error('Profile module not loaded');
                }
            }
        });

        // Search modal listeners
        document.addEventListener('click', (e) => {
            if (e.target.closest('#search-toggle')) {
                this.showSearchOverlay();
            } else if (e.target.closest('#search-close')) {
                this.hideSearchOverlay();
            }
        });

        // Close search overlay when clicking backdrop
        document.addEventListener('click', (e) => {
            const searchOverlay = document.getElementById('search-overlay');
            if (searchOverlay && e.target === searchOverlay) {
                this.hideSearchOverlay();
            }
        });

        // Close search overlay with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const searchOverlay = document.getElementById('search-overlay');
                if (searchOverlay && !searchOverlay.classList.contains('hidden')) {
                    this.hideSearchOverlay();
                }
            }
        });
    },
    
    // Setup auth modal
    setupAuthModal() {
        const authModal = document.getElementById('authModal');
        if (!authModal) {
            return;
        }

        authModal.innerHTML = LumenTemplates.authModal();
        this.bindAuthModalEvents(authModal);
    },

    // Start the application
    async start() {
        // Initialize authentication first
        if (window.LumenAuth) {
            LumenAuth.init();
        }
        
        // Start routing
        if (window.LumenRouter) {
            LumenRouter.init();
        }
        
        // Show initial navigation
        this.updateNavigation(null);
    },
    
    // Handle authentication state changes
    handleAuthChange(detail) {
        const { user, token } = detail;
        console.log('Auth state changed:', user ? 'signed in' : 'signed out');
        
        this.updateNavigation(user);
        
        if (user) {
            this.hideAuthModal();
        } else {
            this.showAuthModal();
        }
    },
    
    // Handle user onboarding
    handleOnboarding(detail) {
        console.log('User needs onboarding:', detail.profile);
        // Could show onboarding modal here
        LumenUtils.showSuccess('Welcome to Lumen! Complete your profile to get started.');
    },
    
    // Update navigation UI
    updateNavigation(user) {
        const profileToggle = document.getElementById('profile-toggle');
        
        if (profileToggle) {
            if (user) {
                // User is logged in - add visual indicators
                profileToggle.classList.add('logged-in');
                profileToggle.style.color = '#4CAF50';
                profileToggle.title = `Profile - ${user.display_name || user.email}`;
                
                // Add status dot if not already present
                if (!profileToggle.querySelector('.status-dot')) {
                    const statusDot = document.createElement('span');
                    statusDot.className = 'status-dot';
                    statusDot.style.cssText = `
                        position: absolute;
                        top: 2px;
                        right: 2px;
                        width: 8px;
                        height: 8px;
                        background: #4CAF50;
                        border-radius: 50%;
                        border: 2px solid var(--bg-primary);
                        pointer-events: none;
                    `;
                    profileToggle.style.position = 'relative';
                    profileToggle.appendChild(statusDot);
                }
            } else {
                // User is logged out - remove visual indicators
                profileToggle.classList.remove('logged-in');
                profileToggle.style.color = '';
                profileToggle.title = 'Profile';
                
                // Remove status dot
                const statusDot = profileToggle.querySelector('.status-dot');
                if (statusDot) {
                    statusDot.remove();
                }
            }
        }
        
        console.log('Navigation updated for user:', user?.display_name || 'Anonymous');
    },
    
    // Toggle mobile menu
    toggleMobileMenu() {
        const mobileMenu = document.getElementById('mobileMenu');
        const menuIcon = document.querySelector('#mobileMenuBtn svg path');
        
        if (mobileMenu) {
            const isHidden = mobileMenu.classList.contains('hidden');
            
            if (isHidden) {
                mobileMenu.classList.remove('hidden');
                if (menuIcon) {
                    menuIcon.setAttribute('d', 'M6 18L18 6M6 6l12 12');
                }
            } else {
                mobileMenu.classList.add('hidden');
                if (menuIcon) {
                    menuIcon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
                }
            }
        }
    },
    
    // Close mobile menu
    closeMobileMenu() {
        const mobileMenu = document.getElementById('mobileMenu');
        const menuIcon = document.querySelector('#mobileMenuBtn svg path');
        
        if (mobileMenu) {
            mobileMenu.classList.add('hidden');
            if (menuIcon) {
                menuIcon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
            }
        }
    },
    
    // Handle login prompt (opens auth modal)
    handleLoginPrompt() {
        if (window.LumenAuth?.isAuthenticated()) {
            this.hideAuthModal();
            return;
        }

        this.showAuthModal();
    },

    // Handle logout
    async handleLogout() {
        if (window.LumenAuth) {
            try {
                await LumenAuth.signOut();
                this.closeMobileMenu();
            } catch (error) {
                console.error('Logout failed:', error);
                LumenUtils.showError('Logout failed. Please try again.');
            }
        }
    },
    
    // Show authentication modal
    showAuthModal() {
        const authModal = document.getElementById('authModal');
        if (!authModal) {
            return;
        }

        if (window.LumenUI?.showModal) {
            LumenUI.showModal('authModal');
            return;
        }

        if (typeof authModal.showModal === 'function') {
            try {
                authModal.showModal();
                return;
            } catch (error) {
                console.error('Failed to open auth modal using showModal()', error);
            }
        }

        authModal.classList.remove('hidden');
    },

    // Hide authentication modal
    hideAuthModal() {
        const authModal = document.getElementById('authModal');
        if (!authModal) {
            return;
        }

        if (window.LumenUI?.hideModal) {
            LumenUI.hideModal('authModal');
            return;
        }

        if (typeof authModal.close === 'function') {
            try {
                authModal.close();
                return;
            } catch (error) {
                console.error('Failed to close auth modal using close()', error);
            }
        }

        authModal.classList.add('hidden');
    },

    // Bind auth modal specific events
    bindAuthModalEvents(modal) {
        const closeButton = modal.querySelector('.auth-modal-close');
        if (closeButton) {
            closeButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.hideAuthModal();
            });
        }

        modal.addEventListener('cancel', (event) => {
            event.preventDefault();
            this.hideAuthModal();
        });
    },

    // Handle the Google sign-in button inside the modal
    async handleGoogleSignIn(button) {
        if (!window.LumenAuth || button.dataset.loading === 'true') {
            return;
        }

        const originalLabel = button.textContent;
        button.dataset.loading = 'true';
        button.disabled = true;
        button.textContent = 'Signing in...';

        try {
            await LumenAuth.signIn();
            this.hideAuthModal();
        } catch (error) {
            console.error('Google sign-in failed:', error);
            if (window.LumenUtils?.showError) {
                LumenUtils.showError('Failed to sign in. Please try again.');
            }
        } finally {
            delete button.dataset.loading;
            button.disabled = false;
            button.textContent = originalLabel;
        }
    },

    // Show search overlay
    showSearchOverlay() {
        const searchOverlay = document.getElementById('search-overlay');
        if (searchOverlay) {
            searchOverlay.classList.remove('hidden');
            searchOverlay.classList.add('flex');
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
        }
    },

    // Hide search overlay
    hideSearchOverlay() {
        const searchOverlay = document.getElementById('search-overlay');
        if (searchOverlay) {
            searchOverlay.classList.add('hidden');
            searchOverlay.classList.remove('flex');
        }
    },
    
    // Show initialization error
    showInitError(error) {
        const app = document.getElementById('app');
        if (app) {
            app.innerHTML = `
                <div class="min-h-screen flex items-center justify-center p-4">
                    <div class="glass-card p-8 rounded-lg max-w-md text-center">
                        <h2 class="text-2xl font-bold mb-4 text-red-400">Initialization Error</h2>
                        <p class="text-gray-400 mb-4">Failed to initialize the application.</p>
                        <p class="text-sm text-gray-500 mb-6">${error.message}</p>
                        <button onclick="window.location.reload()" class="glass-light px-6 py-3 rounded-lg hover:glass-hover">
                            Reload Page
                        </button>
                    </div>
                </div>
            `;
        }
    },
    
    // Get application status
    getStatus() {
        return {
            initialized: this.initialized,
            modules: this.modules,
            currentRoute: window.LumenRouter ? LumenRouter.getCurrentRoute() : null,
            authenticated: window.LumenAuth ? LumenAuth.isAuthenticated() : false
        };
    },
    
    // Restart application
    async restart() {
        this.initialized = false;
        this.modules = [];
        
        // Clear existing state
        const nav = document.getElementById('main-nav');
        const gallery = document.getElementById('photo-gallery');
        const profile = document.getElementById('profile-view');
        const series = document.getElementById('series-view');

        if (nav) nav.innerHTML = '';
        [gallery, profile, series].forEach((section) => {
            if (section) {
                section.innerHTML = '';
            }
        });
        
        // Reinitialize
        await this.init();
    }
};
