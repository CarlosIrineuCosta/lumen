/* Authentication Module
 * Firebase auth logic extracted from frontend-deprecated/js/app.js
 * Uses Poor Man's Modules pattern with window.LumenAuth global
 */

window.LumenAuth = {
    // State
    user: null,
    token: null,
    initialized: false,
    authReady: false,
    authReadyPromise: null,
    
    // Initialize Firebase authentication
    init() {
        if (this.initialized) return;
        
        if (typeof firebase === 'undefined') {
            console.error('Firebase not loaded');
            return;
        }
        
        try {
            firebase.initializeApp(LumenConfig.firebase);
            this.setupAuthStateListener();
            this.initialized = true;
            console.log('Firebase auth initialized');
        } catch (error) {
            console.error('Firebase initialization failed:', error);
        }
    },

    // Check if auth is ready (Promise-based)
    isAuthReady() {
        if (!this.authReadyPromise) {
            this.authReadyPromise = new Promise((resolve) => {
                if (this.authReady) {
                    resolve(true);
                    return;
                }

                // Check every 100ms for auth readiness
                const checkAuth = () => {
                    if (this.authReady) {
                        resolve(true);
                    } else {
                        setTimeout(checkAuth, 100);
                    }
                };
                checkAuth();
            });
        }
        return this.authReadyPromise;
    },

    // Setup Firebase auth state listener
    setupAuthStateListener() {
        firebase.auth().onAuthStateChanged(async (user) => {
            // Mark auth as ready after first state check
            this.authReady = true;
            if (user) {
                // User is signed in
                try {
                    const token = await user.getIdToken();
                    this.token = token;
                    this.user = {
                        uid: user.uid,
                        email: user.email,
                        display_name: user.displayName,
                        profile_image_url: user.photoURL
                    };
                    
                    // Store token for API requests
                    localStorage.setItem('authToken', token);
                    
                    // Try to get user profile from backend
                    await this.syncUserProfile();
                    
                    this.onSignIn(this.user);
                } catch (error) {
                    console.error('Auth token error:', error);
                }
            } else {
                // No user signed in
                this.user = null;
                this.token = null;
                localStorage.removeItem('authToken');
                this.onSignOut();
            }
            
            // Dispatch custom event for other modules
            document.dispatchEvent(new CustomEvent('auth-changed', { 
                detail: { user: this.user, token: this.token } 
            }));
        });
    },
    
    // Sign in with Google
    async signIn() {
        if (typeof firebase === 'undefined') {
            console.error('Firebase not loaded');
            throw new Error('Firebase not available');
        }
        
        const provider = new firebase.auth.GoogleAuthProvider();
        try {
            const result = await firebase.auth().signInWithPopup(provider);
            console.log('Sign in successful:', result.user.displayName);
            
            // Show welcome message
            if (window.LumenUtils) {
                const name = result.user.displayName || result.user.email.split('@')[0];
                LumenUtils.showSuccess(`Welcome back, ${name}!`);
            }
            
            return result.user;
        } catch (error) {
            console.error('Sign in failed:', error);
            if (window.LumenUtils) {
                LumenUtils.showError('Failed to sign in. Please try again.');
            }
            throw error;
        }
    },
    
    // Sign out
    async signOut() {
        try {
            if (firebase.auth().currentUser) {
                await firebase.auth().signOut();
            }
            
            // Clear local data
            this.user = null;
            this.token = null;
            localStorage.removeItem('authToken');
            
            console.log('Sign out successful');
        } catch (error) {
            console.error('Sign out failed:', error);
            throw error;
        }
    },
    
    // Get current auth token
    getToken() {
        return this.token;
    },
    
    // Check if user is authenticated
    isAuthenticated() {
        return !!this.user;
    },
    
    // Require authentication for protected actions
    requireAuth() {
        if (!this.isAuthenticated()) {
            if (window.LumenUtils) {
                LumenUtils.showError('Please sign in to continue');
            }
            if (window.LumenApp?.showAuthModal) {
                LumenApp.showAuthModal();
            } else if (window.LumenUI?.showModal) {
                LumenUI.showModal('authModal');
            }
            return false;
        }
        return true;
    },
    
    // Sync user profile with backend
    async syncUserProfile() {
        if (!this.token || !window.LumenAPI) return;
        
        try {
            const response = await LumenAPI.getUserProfile();
            if (response) {
                // Update user data with backend profile
                this.user.display_name = response.display_name || this.user.display_name;
                console.log('Backend profile synced successfully:', response);
                
                // Check if profile needs onboarding
                if (response.needs_onboarding) {
                    this.handleOnboarding(response);
                }
            }
        } catch (error) {
            console.log('Backend profile sync failed, using Firebase data only:', error);
        }
    },
    
    // Handle onboarding for new users
    handleOnboarding(profile) {
        // Dispatch event for other modules to handle onboarding
        document.dispatchEvent(new CustomEvent('user-needs-onboarding', { 
            detail: { profile } 
        }));
    },
    
    // Called when user signs in
    onSignIn(user) {
        // TODO: Add a "Welcome back, [user.display_name]!" toast message for better user feedback.
        console.log('User signed in:', user.display_name);
        
        // Navigation is static - no need to update
        
        // Navigate to gallery
        if (window.LumenRouter) {
            LumenRouter.navigate('gallery');
        }
        
        // Hide auth modal if visible
        if (window.LumenApp?.hideAuthModal) {
            LumenApp.hideAuthModal();
        } else if (window.LumenUI?.hideModal) {
            LumenUI.hideModal('authModal');
        }
    },
    
    // Called when user signs out
    onSignOut() {
        console.log('User signed out');
        
        // Navigation is static - no need to update
        
        // Show auth modal
        if (window.LumenApp?.showAuthModal) {
            LumenApp.showAuthModal();
        } else if (window.LumenUI?.showModal) {
            LumenUI.showModal('authModal');
        }
        
        // Clear other module states
        if (window.LumenGallery) {
            LumenGallery.clear();
        }
    },
    
    // Get user avatar URL
    getAvatarUrl() {
        if (!this.user) return null;
        
        return this.user.profile_image_url || 
               `https://ui-avatars.com/api/?name=${encodeURIComponent(this.user.display_name || 'U')}&background=4a90e2&color=fff`;
    }
};
