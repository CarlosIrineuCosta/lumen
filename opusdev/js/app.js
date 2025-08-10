// Lumen PWA - Main Application
// Glass-inspired photography platform

import PhotoViewer from './photo-viewer.js';

const API_BASE_URL = 'http://100.106.201.33:8080/api/v1';

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBJvE7-sY_IxF5i0EaKvwJIGkF8L8XqW0E",
    authDomain: "lumen-photo-app-20250731.firebaseapp.com",
    projectId: "lumen-photo-app-20250731"
};

class LumenApp {
    constructor() {
        this.user = null;
        this.authToken = null;
        this.photos = [];
        this.currentView = 'discover';
        this.page = 1;
        this.loading = false;
        this.hasMore = true;
        this.deferredPrompt = null;
        this.photoViewer = new PhotoViewer();
        
        // Initialize Firebase
        if (typeof firebase !== 'undefined') {
            firebase.initializeApp(firebaseConfig);
        }
        
        this.init();
    }
    
    async init() {
        console.log('Initializing Lumen PWA...');
        
        // Register service worker for PWA
        this.registerServiceWorker();
        
        // Check authentication
        await this.checkAuth();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial photos
        if (this.user) {
            this.loadPhotos();
        }
    }
    
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/service-worker.js');
                console.log('Service Worker registered:', registration);
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }
    
    async checkAuth() {
        // Check Firebase Auth state
        if (typeof firebase !== 'undefined') {
            firebase.auth().onAuthStateChanged(async (user) => {
                if (user) {
                    // User is signed in
                    const token = await user.getIdToken();
                    localStorage.setItem('authToken', token);
                    this.authToken = token;
                    this.user = {
                        uid: user.uid,
                        email: user.email,
                        display_name: user.displayName,
                        profile_image_url: user.photoURL
                    };
                    
                    // Verify with backend
                    try {
                        const response = await fetch(`${API_BASE_URL}/auth/status`, {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        
                        if (response.ok) {
                            this.hideAuthModal();
                            this.updateUserUI();
                            this.loadPhotos();
                        } else {
                            this.showAuthModal();
                        }
                    } catch (error) {
                        console.error('Backend auth check failed:', error);
                        // Continue anyway if Firebase auth is valid
                        this.hideAuthModal();
                        this.updateUserUI();
                        this.loadPhotos();
                    }
                } else {
                    // No user signed in
                    this.showAuthModal();
                }
            });
        } else {
            // Firebase not loaded, show auth modal
            this.showAuthModal();
        }
    }
    
    showAuthModal() {
        document.getElementById('authModal')?.classList.remove('hidden');
    }
    
    hideAuthModal() {
        document.getElementById('authModal')?.classList.add('hidden');
    }
    
    updateUserUI() {
        if (this.user) {
            const avatar = document.getElementById('userAvatar');
            if (avatar) {
                avatar.src = this.user.profile_image_url || 
                    `https://ui-avatars.com/api/?name=${encodeURIComponent(this.user.display_name || 'U')}&background=4a90e2&color=fff`;
            }
        }
    }
    
    setupEventListeners() {
        // Navigation tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.dataset.view);
            });
        });
        
        // Upload button
        document.getElementById('uploadBtn')?.addEventListener('click', () => {
            this.showUploadModal();
        });
        
        // Google Sign In
        document.getElementById('googleSignIn')?.addEventListener('click', () => {
            this.signInWithGoogle();
        });
        
        // Close buttons
        document.getElementById('viewerClose')?.addEventListener('click', () => {
            document.getElementById('photoViewer')?.classList.add('hidden');
        });
        
        document.getElementById('uploadClose')?.addEventListener('click', () => {
            document.getElementById('uploadModal')?.classList.add('hidden');
        });
        
        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea?.addEventListener('click', () => {
            fileInput?.click();
        });
        
        fileInput?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });
        
        // Infinite scroll
        window.addEventListener('scroll', () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
                if (!this.loading && this.hasMore) {
                    this.loadPhotos();
                }
            }
        });
    }
    
    switchView(view) {
        this.currentView = view;
        this.page = 1;
        this.photos = [];
        this.hasMore = true;
        
        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });
        
        // Clear grid
        const grid = document.getElementById('photoGrid');
        if (grid) grid.innerHTML = '';
        
        // Load new content
        this.loadPhotos();
    }
    
    async loadPhotos() {
        if (this.loading) return;
        
        this.loading = true;
        document.getElementById('loadingIndicator')?.classList.remove('hidden');
        
        try {
            let endpoint = '/photos/recent';
            
            switch(this.currentView) {
                case 'photographers':
                    endpoint = '/users/photographers';
                    break;
                case 'nearby':
                    endpoint = '/photos/nearby?radius=30';
                    break;
                case 'portfolio':
                    endpoint = `/photos/user/${this.user?.id}`;
                    break;
            }
            
            const response = await fetch(`${API_BASE_URL}${endpoint}?page=${this.page}&limit=20`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.photos = [...this.photos, ...data.photos || data];
                this.hasMore = data.has_more !== false;
                this.renderPhotos(data.photos || data);
                this.page++;
            }
        } catch (error) {
            console.error('Failed to load photos:', error);
            document.getElementById('emptyState')?.classList.remove('hidden');
        } finally {
            this.loading = false;
            document.getElementById('loadingIndicator')?.classList.add('hidden');
        }
    }
    
    renderPhotos(photos) {
        const grid = document.getElementById('photoGrid');
        if (!grid) return;
        
        if (photos.length === 0 && this.photos.length === 0) {
            document.getElementById('emptyState')?.classList.remove('hidden');
            return;
        }
        
        photos.forEach(photo => {
            const item = this.createPhotoElement(photo);
            grid.appendChild(item);
        });
        
        // Apply masonry layout
        this.applyMasonryLayout();
    }
    
    createPhotoElement(photo) {
        const div = document.createElement('div');
        div.className = 'photo-item';
        div.dataset.photoId = photo.id;
        
        // Calculate grid row span based on aspect ratio
        const aspectRatio = photo.height / photo.width || 1.5;
        const rowSpan = Math.ceil(aspectRatio * 20);
        div.style.gridRowEnd = `span ${rowSpan}`;
        
        // Check if photo is part of a series
        const isSeries = photo.series && photo.series.length > 1;
        
        div.innerHTML = `
            <img src="${photo.thumbnail_url || photo.url}" 
                 alt="${photo.title || 'Photo'}" 
                 loading="lazy">
            ${isSeries ? `<div class="series-indicator">${photo.series.length} photos</div>` : ''}
            <div class="photo-overlay">
                <div class="photo-photographer">${photo.photographer_name || photo.username || 'Unknown'}</div>
                <div class="photo-location">${photo.location || ''}</div>
            </div>
        `;
        
        div.addEventListener('click', () => {
            this.showPhotoViewer(photo, isSeries);
        });
        
        return div;
    }
    
    applyMasonryLayout() {
        // For browsers without native masonry support
        if (!CSS.supports('grid-template-rows', 'masonry')) {
            const grid = document.getElementById('photoGrid');
            const items = grid.querySelectorAll('.photo-item');
            
            items.forEach(item => {
                const img = item.querySelector('img');
                img.onload = () => {
                    const rowSpan = Math.ceil(img.offsetHeight / 10);
                    item.style.gridRowEnd = `span ${rowSpan}`;
                };
            });
        }
    }
    
    showPhotoViewer(photo, isSeries = false) {
        // Use the new enhanced photo viewer
        this.photoViewer.open(photo, this.photos, isSeries);
    }
    
    showUploadModal() {
        document.getElementById('uploadModal')?.classList.remove('hidden');
    }
    
    handleFileSelect(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('previewImage').src = e.target.result;
            document.getElementById('uploadArea')?.classList.add('hidden');
            document.getElementById('uploadPreview')?.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
        
        this.selectedFile = file;
    }
    
    async signInWithGoogle() {
        // Use Firebase Auth for Google sign-in
        if (typeof firebase === 'undefined') {
            console.error('Firebase not loaded');
            return;
        }
        
        const provider = new firebase.auth.GoogleAuthProvider();
        try {
            const result = await firebase.auth().signInWithPopup(provider);
            const token = await result.user.getIdToken();
            
            // Store token and user info
            localStorage.setItem('authToken', token);
            this.authToken = token;
            this.user = {
                uid: result.user.uid,
                email: result.user.email,
                display_name: result.user.displayName,
                profile_image_url: result.user.photoURL
            };
            
            // Update UI
            this.hideAuthModal();
            this.updateUserUI();
            this.loadPhotos();
        } catch (error) {
            console.error('Auth error:', error);
            alert('Sign in failed. Please try again.');
        }
    }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.lumenApp = new LumenApp();
    });
} else {
    window.lumenApp = new LumenApp();
}