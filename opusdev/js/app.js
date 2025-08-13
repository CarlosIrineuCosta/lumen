// Lumen PWA - Main Application
// Glass-inspired photography platform

import PhotoViewer from './photo-viewer.js';
import SimpleMasonry from './simple-masonry.js';
import PhotoDisplay from './photo-display.js';

const API_BASE_URL = 'http://100.106.201.33:8080/api/v1';

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyCt8ERvmCTaV5obZHBTqOAOSCMTq-v16nE",
    authDomain: "lumen-photo-app-20250731.firebaseapp.com",
    projectId: "lumen-photo-app-20250731",
    storageBucket: "lumen-photo-app-20250731.firebasestorage.app",
    messagingSenderId: "316971929294"
};

class LumenApp {
    constructor() {
        this.user = null;
        this.authToken = null;
        this.photos = [];
        this.currentView = 'home'; // Changed from 'discover' to 'home'
        this.page = 1;
        this.loading = false;
        this.hasMore = true;
        
        // Global navigation context system
        this.navigationContext = {
            type: 'home', // home, discover, photographers, nearby, portfolio, user_photos, tag_photos
            userId: null, // for user-specific contexts
            tag: null, // for tag-specific contexts
            searchQuery: null, // for search contexts
            returnView: 'home' // what view to return to when closing viewer
        };
        this.deferredPrompt = null;
        this.photoViewer = new PhotoViewer();
        this.masonry = null;
        this.photoDisplay = new PhotoDisplay();
        
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
        this.setupPhotoDisplayEvents();
        
        // Load initial photos
        if (this.user) {
            this.loadPhotos();
        }
    }
    
    async registerServiceWorker() {
        // Temporarily disabled to fix upload issues
        // Service worker can interfere with file uploads and Firebase auth
        console.log('Service Worker registration temporarily disabled');
        return;
        
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
        // Check Firebase Auth state first
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
                    
                    // Try to get user profile from backend (non-blocking)
                    try {
                        const response = await fetch(`${API_BASE_URL}/users/me`, {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        
                        if (response.ok) {
                            const profile = await response.json();
                            // Update user data with backend profile if available
                            this.user.display_name = profile.display_name || this.user.display_name;
                            console.log('Backend profile loaded successfully');
                        } else {
                            console.log('Backend profile not available, using Firebase data');
                        }
                    } catch (error) {
                        console.log('Backend auth check failed, using Firebase data only:', error);
                    }
                    
                    // Always continue with Firebase auth - don't block on backend
                    this.hideAuthModal();
                    this.updateUserUI();
                    this.loadPhotos();
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
        const modal = document.getElementById('authModal');
        if (modal) {
            modal.classList.remove('hidden');
            console.log('Auth modal shown');
        } else {
            console.error('Auth modal element not found');
        }
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
        
        // Profile dropdown
        document.getElementById('profileBtn')?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleProfileDropdown();
        });
        
        document.getElementById('editProfileBtn')?.addEventListener('click', () => {
            this.hideProfileDropdown();
            this.showProfileModal();
        });
        
        document.getElementById('viewProfileBtn')?.addEventListener('click', () => {
            this.hideProfileDropdown();
            this.showProfileView(); // Show dedicated profile view modal
        });
        
        document.getElementById('logoutBtn')?.addEventListener('click', () => {
            this.logout();
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            this.hideProfileDropdown();
        });
        
        // Close buttons
        document.getElementById('viewerClose')?.addEventListener('click', () => {
            document.getElementById('photoViewer')?.classList.add('hidden');
        });
        
        document.getElementById('uploadClose')?.addEventListener('click', () => {
            document.getElementById('uploadModal')?.classList.add('hidden');
        });
        
        // Profile modal close buttons
        document.getElementById('profileClose')?.addEventListener('click', () => {
            this.hideProfileModal();
        });
        
        document.getElementById('cancelProfileEdit')?.addEventListener('click', () => {
            this.hideProfileModal();
        });
        
        // Profile view modal
        document.getElementById('profileViewClose')?.addEventListener('click', () => {
            this.hideProfileView();
        });
        
        document.getElementById('editFromView')?.addEventListener('click', () => {
            this.hideProfileView();
            this.showProfileModal();
        });
        
        // File upload with drag & drop support
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        // Click to browse files
        uploadArea?.addEventListener('click', () => {
            fileInput?.click();
        });
        
        // Drag & drop functionality
        uploadArea?.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea?.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea?.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
        
        // File input change
        fileInput?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });
        
        // Upload submission
        document.getElementById('submitUpload')?.addEventListener('click', () => {
            this.uploadPhoto();
        });
        
        // Profile editing
        document.getElementById('changeImageBtn')?.addEventListener('click', () => {
            document.getElementById('profileImageInput')?.click();
        });
        
        document.getElementById('profileImageInput')?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleProfileImageSelect(e.target.files[0]);
            }
        });
        
        document.getElementById('saveProfile')?.addEventListener('click', () => {
            this.saveProfile();
        });
        
        document.getElementById('profileUserType')?.addEventListener('change', (e) => {
            this.toggleUserTypeFields(e.target.value);
        });
        
        // Infinite scroll
        window.addEventListener('scroll', () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
                if (!this.loading && this.hasMore) {
                    this.loadPhotos();
                }
            }
        });
        
        // Window resize handling for responsive masonry
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (this.masonry) {
                    this.masonry.refresh();
                } else if (this.photoDisplay && this.photoDisplay.masonry) {
                    this.photoDisplay.masonry.refresh();
                }
            }, 250);
        });
    }
    
    switchView(view) {
        this.currentView = view;
        this.page = 1;
        this.photos = [];
        this.hasMore = true;
        
        // Update navigation context
        this.updateNavigationContext(view);
        
        // Update active tab
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });
        
        // Clear grid and masonry
        const grid = document.getElementById('photoGrid');
        if (grid) {
            grid.innerHTML = '';
            if (this.masonry) {
                this.masonry.destroy();
                this.masonry = null;
            }
        }
        
        // Update photo display context
        this.photoDisplay.setContext(view);
        this.photoDisplay.masonry = null; // Reset masonry reference
        
        // Load new content
        this.loadPhotos();
    }
    
    async loadPhotos() {
        if (this.loading) return;
        
        this.loading = true;
        document.getElementById('loadingIndicator')?.classList.remove('hidden');
        
        try {
            // Handle different view types with different request patterns
            if (this.currentView === 'photographers') {
                await this.loadPhotographers();
            } else {
                let endpoint = this.getEndpointForView(this.currentView);
                
                // Check if we need authentication for this endpoint
                const needsAuth = ['portfolio'].includes(this.currentView);
                if (needsAuth && !this.authToken) {
                    console.log('Authentication required for', this.currentView, 'but no token available');
                    this.showAuthModal();
                    return;
                }
                
                // Check if endpoint already has query parameters
                const separator = endpoint.includes('?') ? '&' : '?';
                const headers = {};
                if (this.authToken) {
                    headers['Authorization'] = `Bearer ${this.authToken}`;
                }
                
                const response = await fetch(`${API_BASE_URL}${endpoint}${separator}page=${this.page}&limit=20`, {
                    headers
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const newPhotos = data.photos || data; // Handle different response formats
                    
                    this.photos = [...this.photos, ...newPhotos];
                    this.hasMore = data.has_more !== false;
                    
                    // Set display context and render
                    this.photoDisplay.setContext(this.currentView);
                    this.photoDisplay.renderPhotos(newPhotos, this.user, document.getElementById('photoGrid'));
                    
                    this.page++;
                } else if (response.status === 401) {
                    console.log('Authentication failed, clearing auth state');
                    this.clearAuthState();
                    this.showAuthModal();
                } else {
                    console.error('API request failed:', response.status, response.statusText);
                    this.photoDisplay.showEmptyState();
                }
            }
        } catch (error) {
            console.error('Failed to load photos (network/CORS error):', error);
            // If it's a network error and we were trying to authenticate, show auth modal
            if (this.currentView === 'portfolio' || this.authToken) {
                console.log('Network error during authenticated request, may need re-authentication');
                this.clearAuthState();
                this.showAuthModal();
            } else {
                this.photoDisplay.showEmptyState();
            }
        } finally {
            this.loading = false;
            document.getElementById('loadingIndicator')?.classList.add('hidden');
        }
    }
    
    async loadPhotographers() {
        try {
            const searchQuery = {
                user_type: 'photographer',
                page: this.page,
                limit: 20
            };
            
            const response = await fetch(`${API_BASE_URL}/users/search`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(searchQuery)
            });
            
            if (response.ok) {
                const photographers = await response.json();
                
                this.photos = [...this.photos, ...photographers];
                this.hasMore = photographers.length === 20; // Assume more if we got a full page
                
                // Set display context and render
                this.photoDisplay.setContext(this.currentView);
                this.photoDisplay.renderPhotos(photographers, this.user, document.getElementById('photoGrid'));
                
                this.page++;
            } else {
                console.error('Failed to load photographers:', response.status, response.statusText);
                this.photoDisplay.showEmptyState();
            }
        } catch (error) {
            console.error('Error loading photographers:', error);
            this.photoDisplay.showEmptyState();
        }
    }
    
    /**
     * Get API endpoint based on current view
     * @param {string} view - Current view name
     * @returns {string} API endpoint
     */
    getEndpointForView(view) {
        switch(view) {
            case 'home':
                // Home feed: For now using recent photos until follow system is built
                return '/photos/recent'; // Using existing endpoint
                
            case 'discover':
                // Discovery: All public photos for exploration
                return '/photos/recent'; // Using same endpoint until discover is built
                
            case 'nearby':
                // Geographic discovery (temporarily using recent until nearby is implemented)
                return '/photos/recent';                
            
            case 'portfolio':
                // User's portfolio photos only
                return '/photos/my-photos?portfolio_only=true';

            default:
                return '/photos/recent';
        }
    }
    
    /**
     * Setup event listeners for photo display interactions
     */
    setupPhotoDisplayEvents() {
        // Listen for photo clicks
        document.addEventListener('photoClicked', (e) => {
            const { photo, isSeries } = e.detail;
            this.showPhotoViewer(photo, isSeries);
        });
        
        // Listen for photo context menu (right-click for edit/delete)
        document.addEventListener('photoContextMenu', (e) => {
            const { photo, x, y } = e.detail;
            this.showPhotoContextMenu(photo, x, y);
        });
    }
    
    /**
     * Show photo viewer for a photo or series
     */
    updateNavigationContext(view, options = {}) {
        this.navigationContext = {
            type: view,
            userId: options.userId || null,
            tag: options.tag || null,
            searchQuery: options.searchQuery || null,
            returnView: this.currentView // Store current view to return to
        };
    }

    showPhotoViewer(photo, isSeries) {
        // Get all photos from current view for navigation
        const allPhotos = this.photos || [];
        
        // Open the photo viewer with navigation context
        this.photoViewer.open(photo, allPhotos, isSeries, this.navigationContext);
    }
    
    /**
     * Show context menu for photo actions
     * @param {Object} photo - Photo data
     * @param {number} x - Click X coordinate
     * @param {number} y - Click Y coordinate
     */
    showPhotoContextMenu(photo, x, y) {
        // Remove existing context menu
        const existingMenu = document.querySelector('.photo-context-menu');
        if (existingMenu) existingMenu.remove();
        
        // Create context menu
        const menu = document.createElement('div');
        menu.className = 'photo-context-menu';
        menu.style.left = `${x}px`;
        menu.style.top = `${y}px`;
        menu.innerHTML = `
            <div class="context-menu-item" data-action="edit">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="m18.5 2.5 a2.121 2.121 0 0 1 3 3l-2.5 2.5-3-3 2.5-2.5z"/>
                    <path d="m15 5 3 3"/>
                </svg>
                Edit Photo
            </div>
            <div class="context-menu-item" data-action="delete">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3,6 5,6 21,6"/>
                    <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1 2-2h4a2,2 0 0,1 2,2v2"/>
                </svg>
                Delete Photo
            </div>
        `;
        
        // Add click handlers
        menu.addEventListener('click', (e) => {
            const action = e.target.closest('.context-menu-item')?.dataset.action;
            if (action === 'edit') {
                this.editPhoto(photo);
            } else if (action === 'delete') {
                this.deletePhoto(photo);
            }
            menu.remove();
        });
        
        // Add to body and show
        document.body.appendChild(menu);
        
        // Remove on outside click
        setTimeout(() => {
            document.addEventListener('click', () => menu.remove(), { once: true });
        }, 100);
    }
    
    showGridLoading(show) {
        const loading = document.getElementById('loadingIndicator');
        const grid = document.getElementById('photoGrid');
        
        if (show) {
            loading?.classList.remove('hidden');
            if (grid) grid.classList.add('grid-loading');
        } else {
            loading?.classList.add('hidden');
            if (grid) grid.classList.remove('grid-loading');
            
            // Show all items with smooth fade-in
            const items = grid?.querySelectorAll('.photo-item');
            items?.forEach((item, index) => {
                setTimeout(() => {
                    item.style.visibility = 'visible';
                    item.style.opacity = '1';
                    item.style.transition = 'opacity 0.3s ease';
                }, index * 50); // Stagger the fade-in
            });
        }
    }
    /**
     * Edit photo metadata
     * @param {Object} photo - Photo to edit
     */
    editPhoto(photo) {
        console.log('Edit photo:', photo);
        // TODO: Implement photo editing modal
        this.showNotification('Photo editing coming soon!', 'info');
    }
    
    /**
     * Delete photo
     * @param {Object} photo - Photo to delete
     */
    async deletePhoto(photo) {
        if (!confirm('Are you sure you want to delete this photo? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/photos/${photo.id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                // Remove from photos array
                this.photos = this.photos.filter(p => p.id !== photo.id);
                
                // Remove from DOM
                const photoElement = document.querySelector(`[data-photo-id="${photo.id}"]`);
                if (photoElement) {
                    photoElement.remove();
                    
                    // Refresh masonry layout
                    if (this.masonry) {
                        this.masonry.refresh();
                    }
                }
                
                this.showNotification('Photo deleted successfully', 'success');
            } else {
                throw new Error('Failed to delete photo');
            }
        } catch (error) {
            console.error('Delete photo error:', error);
            this.showNotification('Failed to delete photo', 'error');
        }
    }
    
    showUploadModal() {
        document.getElementById('uploadModal')?.classList.remove('hidden');
    }
    
    async handleFileSelect(file) {
        if (!file.type.startsWith('image/')) {
            this.showNotification('Please select an image file', 'error');
            return;
        }
        
        // Check file size (20MB limit)
        const MAX_FILE_SIZE_MB = 20;
        if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
            this.showNotification(`File is too large (max ${MAX_FILE_SIZE_MB}MB)`, 'error');
            return;
        }
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewImg = document.getElementById('previewImage');
            previewImg.src = e.target.result;
            
            // Ensure proper sizing to prevent full-screen display
            previewImg.style.maxWidth = '100%';
            previewImg.style.maxHeight = '200px';
            previewImg.style.width = 'auto';
            previewImg.style.height = 'auto';
            previewImg.style.objectFit = 'contain';
            
            document.getElementById('uploadArea')?.classList.add('hidden');
            document.getElementById('uploadPreview')?.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
        
        this.selectedFile = file;
        
        // Extract and populate EXIF data
        try {
            const exifData = await this.readEXIFData(file);
            this.populateFormWithExif(exifData);
        } catch (error) {
            console.error('Failed to read EXIF data:', error);
        }
    }
    
    populateFormWithExif(exifData) {
        // Populate photographer name (always current user)
        const photographerField = document.getElementById('photographerName');
        if (photographerField) {
            photographerField.value = this.user?.display_name || this.user?.email || 'You';
        }
        
        // Populate technical fields from EXIF
        if (exifData.camera) document.getElementById('cameraInfo').value = exifData.camera;
        if (exifData.lens) document.getElementById('lensInfo').value = exifData.lens;
        if (exifData.iso) document.getElementById('isoValue').value = exifData.iso;
        if (exifData.aperture) document.getElementById('apertureValue').value = `f/${exifData.aperture}`;
        if (exifData.shutterSpeed) {
            const speed = exifData.shutterSpeed;
            document.getElementById('shutterSpeed').value = speed >= 1 ? `${speed}s` : `1/${Math.round(1/speed)}s`;
        }
        if (exifData.focalLength) document.getElementById('focalLength').value = `${Math.round(exifData.focalLength)}mm`;
        if (exifData.gpsLocation) document.getElementById('locationInfo').value = exifData.gpsLocation;
        
        // If artist is in EXIF and different from current user, suggest as model
        if (exifData.artist && exifData.artist !== this.user?.display_name) {
            document.getElementById('modelName').value = exifData.artist;
        }
        
        console.log('Form populated with EXIF data:', exifData);
    }
    
    async uploadPhoto() {
        console.log('Upload started - selectedFile:', this.selectedFile?.name, 'authToken:', !!this.authToken);
        
        if (!this.selectedFile) {
            this.showNotification('Please select a file first', 'error');
            return;
        }
        
        if (!this.authToken) {
            this.showNotification('Please log in to upload photos', 'error');
            return;
        }
        
        const uploadBtn = document.getElementById('submitUpload');
        const originalText = uploadBtn.textContent;
        uploadBtn.textContent = 'Uploading...';
        uploadBtn.disabled = true;
        
        try {
            // Create FormData for file upload
            const formData = new FormData();
            formData.append('file', this.selectedFile);
            
            // Get all metadata from form
            const title = document.getElementById('photoTitle').value.trim();
            const description = document.getElementById('photoDescription').value.trim();
            const isPortfolio = document.getElementById('isPortfolio').checked;
            const isPublic = document.getElementById('isPublic').checked;
            const modelName = document.getElementById('modelName').value.trim();
            const cameraInfo = document.getElementById('cameraInfo').value.trim();
            const lensInfo = document.getElementById('lensInfo').value.trim();
            const locationInfo = document.getElementById('locationInfo').value.trim();
            
            // Collect technical settings
            const iso = document.getElementById('isoValue').value.trim();
            const aperture = document.getElementById('apertureValue').value.trim();
            const shutterSpeed = document.getElementById('shutterSpeed').value.trim();
            const focalLength = document.getElementById('focalLength').value.trim();
            
            // Build settings string from individual values
            const settings = [];
            if (iso) settings.push(iso.startsWith('ISO') ? iso : `ISO ${iso}`);
            if (aperture) settings.push(aperture.startsWith('f/') ? aperture : `f/${aperture}`);
            if (shutterSpeed) settings.push(shutterSpeed);
            if (focalLength) settings.push(focalLength.endsWith('mm') ? focalLength : `${focalLength}mm`);
            const settingsString = settings.join(' | ');
            
            // Add all fields to FormData
            if (title) formData.append('title', title);
            if (description) formData.append('description', description);
            if (cameraInfo) formData.append('camera', cameraInfo);
            if (lensInfo) formData.append('lens', lensInfo);
            if (settingsString) formData.append('settings', settingsString);
            if (locationInfo) formData.append('location', locationInfo);
            if (modelName) formData.append('model_name', modelName);
            
            formData.append('is_portfolio', isPortfolio);
            formData.append('is_public', isPublic);
            
            // Upload to backend
            const response = await fetch(`${API_BASE_URL}/photos/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Photo uploaded successfully:', result);
                
                // Close upload modal
                document.getElementById('uploadModal').classList.add('hidden');
                
                // Reset upload form
                this.resetUploadForm();
                
                // Add new photo to beginning of current photos and grid
                this.prependNewPhoto(result);
                
                // Show success message
                this.showNotification('Photo uploaded successfully!', 'success');
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            this.showNotification('Upload failed: ' + error.message, 'error');
        } finally {
            uploadBtn.textContent = originalText;
            uploadBtn.disabled = false;
        }
    }
    
    async readEXIFData(file) {
        try {
            console.log('Reading EXIF data from:', file.name);
            
            // Read the file as ArrayBuffer for ExifReader
            const arrayBuffer = await file.arrayBuffer();
            const tags = ExifReader.load(arrayBuffer);
            
            console.log('EXIF tags found:', tags);
            
            // Extract key metadata with fallbacks
            const exifData = {
                // Camera information
                camera: this.getExifValue(tags, 'Make', 'Model'),
                lens: this.getExifValue(tags, 'LensModel') || this.getExifValue(tags, 'LensInfo'),
                
                // Technical settings
                iso: this.getExifValue(tags, 'ISO'),
                aperture: this.getExifValue(tags, 'FNumber'),
                shutterSpeed: this.getExifValue(tags, 'ExposureTime'),
                focalLength: this.getExifValue(tags, 'FocalLength'),
                
                // Location data
                gpsLatitude: this.getExifValue(tags, 'GPSLatitude'),
                gpsLongitude: this.getExifValue(tags, 'GPSLongitude'),
                gpsLocation: null, // Will be calculated from lat/lng
                
                // Date/time
                dateTimeOriginal: this.getExifValue(tags, 'DateTimeOriginal'),
                
                // Author/artist information
                artist: this.getExifValue(tags, 'Artist'),
                copyright: this.getExifValue(tags, 'Copyright'),
                
                // Image dimensions and orientation
                imageWidth: this.getExifValue(tags, 'ImageWidth') || this.getExifValue(tags, 'PixelXDimension'),
                imageHeight: this.getExifValue(tags, 'ImageLength') || this.getExifValue(tags, 'PixelYDimension'),
                orientation: this.getExifValue(tags, 'Orientation')
            };
            
            // Format camera info (combine Make + Model)
            if (tags.Make && tags.Model) {
                exifData.camera = `${this.getExifValue(tags, 'Make')} ${this.getExifValue(tags, 'Model')}`;
            }
            
            // Format GPS location if available
            if (exifData.gpsLatitude && exifData.gpsLongitude) {
                exifData.gpsLocation = `${exifData.gpsLatitude.toFixed(6)}, ${exifData.gpsLongitude.toFixed(6)}`;
            }
            
            // Format technical settings string
            const settings = [];
            if (exifData.iso) settings.push(`ISO ${exifData.iso}`);
            if (exifData.aperture) settings.push(`f/${exifData.aperture}`);
            if (exifData.shutterSpeed) {
                // Format shutter speed properly
                const speed = exifData.shutterSpeed;
                settings.push(speed >= 1 ? `${speed}s` : `1/${Math.round(1/speed)}s`);
            }
            if (exifData.focalLength) settings.push(`${Math.round(exifData.focalLength)}mm`);
            
            exifData.settingsString = settings.join(' | ');
            
            return exifData;
            
        } catch (error) {
            console.error('EXIF reading failed:', error);
            return {
                camera: '',
                lens: '',
                iso: '',
                aperture: '',
                shutterSpeed: '',
                focalLength: '',
                settingsString: '',
                gpsLocation: '',
                artist: '',
                dateTimeOriginal: ''
            };
        }
    }
    
    getExifValue(tags, tagName, secondaryTag = null) {
        try {
            let tag = tags[tagName];
            if (!tag && secondaryTag) {
                tag = tags[secondaryTag];
            }
            
            if (!tag) return null;
            
            // Handle different tag value formats
            if (tag.description) return tag.description;
            if (tag.value !== undefined) return tag.value;
            if (Array.isArray(tag) && tag.length > 0) return tag[0];
            
            return tag;
        } catch (error) {
            console.error(`Error reading EXIF tag ${tagName}:`, error);
            return null;
        }
    }
    
    resetUploadForm() {
        // Reset file input
        document.getElementById('fileInput').value = '';
        
        // Reset all form fields
        document.getElementById('photoTitle').value = '';
        document.getElementById('photoDescription').value = '';
        document.getElementById('previewImage').src = '';
        document.getElementById('photographerName').value = '';
        document.getElementById('modelName').value = '';
        document.getElementById('cameraInfo').value = '';
        document.getElementById('lensInfo').value = '';
        document.getElementById('isoValue').value = '';
        document.getElementById('apertureValue').value = '';
        document.getElementById('shutterSpeed').value = '';
        document.getElementById('focalLength').value = '';
        document.getElementById('locationInfo').value = '';
        
        // Reset checkboxes
        document.getElementById('isPortfolio').checked = false;
        document.getElementById('isPublic').checked = true;
        
        // Show upload area, hide preview
        document.getElementById('uploadArea').classList.remove('hidden');
        document.getElementById('uploadPreview').classList.add('hidden');
        
        // Clear selected file
        this.selectedFile = null;
    }
    
    prependNewPhoto(photo) {
        // Add photo to beginning of photos array
        this.photos.unshift(photo);
        
        // Use PhotoDisplay to add the new photo
        const grid = document.getElementById('photoGrid');
        this.photoDisplay.prependNewPhoto(photo, this.user, grid);
        
        // Update masonry reference
        if (this.photoDisplay.masonry) {
            this.masonry = this.photoDisplay.masonry;
        }
    }
    
    async refreshPhotoStreams() {
        // Reset pagination and reload photos
        this.page = 1;
        this.photos = [];
        this.hasMore = true;
        
        // Clear current grid
        const grid = document.getElementById('photoGrid');
        if (grid) grid.innerHTML = '';
        
        // Reload photos for current view
        await this.loadPhotos();
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Hide and remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    toggleProfileDropdown() {
        const dropdown = document.getElementById('profileDropdown');
        dropdown?.classList.toggle('hidden');
    }
    
    hideProfileDropdown() {
        const dropdown = document.getElementById('profileDropdown');
        dropdown?.classList.add('hidden');
    }
    
    async logout() {
        try {
            // Sign out from Firebase
            if (typeof firebase !== 'undefined' && firebase.auth().currentUser) {
                await firebase.auth().signOut();
            }
            
            // Clear local data
            this.user = null;
            this.authToken = null;
            this.photos = [];
            localStorage.removeItem('authToken');
            
            // Clear UI
            this.hideProfileDropdown();
            this.hideProfileModal();
            this.hideProfileView();
            document.getElementById('uploadModal')?.classList.add('hidden');
            
            // Clear photo grid
            const grid = document.getElementById('photoGrid');
            if (grid) grid.innerHTML = '';
            
            // Reset to home view
            this.currentView = 'home';
            this.page = 1;
            this.hasMore = true;
            
            // Update tab state
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.view === 'home');
            });
            
            // Show auth modal
            this.showAuthModal();
            
            this.showNotification('Logged out successfully', 'success');
            
        } catch (error) {
            console.error('Logout error:', error);
            this.showNotification('Logout failed', 'error');
        }
    }

    async showProfileView(userId = null) {
        if (!userId && !this.user) {
            this.showNotification('Please log in to view your profile', 'error');
            return;
        }
        
        // Show modal
        document.getElementById('profileViewModal')?.classList.remove('hidden');
        
        // Show/hide edit button based on whether it's own profile
        const ownActions = document.getElementById('ownProfileActions');
        if (userId && userId !== this.user?.uid) {
            ownActions?.classList.add('hidden');
        } else {
            ownActions?.classList.remove('hidden');
        }
        
        // Load profile data
        await this.loadProfileForView(userId || this.user.uid);
    }
    
    hideProfileView() {
        document.getElementById('profileViewModal')?.classList.add('hidden');
    }
    
    async loadProfileForView(userId) {
        try {
            const endpoint = userId === this.user?.uid ? '/users/me' : `/users/${userId}/public`;
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const profile = await response.json();
                this.populateProfileView(profile);
            } else {
                console.error('Failed to load profile data');
                this.showNotification('Failed to load profile', 'error');
            }
        } catch (error) {
            console.error('Error loading profile:', error);
            this.showNotification('Error loading profile', 'error');
        }
    }
    
    populateProfileView(profile) {
        // Basic information
        document.getElementById('viewDisplayName').textContent = profile.display_name || 'Unknown';
        document.getElementById('viewUsername').textContent = profile.username ? `@${profile.username}` : '';
        document.getElementById('viewUserType').textContent = profile.user_type?.replace(/_/g, ' ') || '';
        document.getElementById('viewTagline').textContent = profile.tagline || '';
        
        // Profile image
        const profileImg = document.getElementById('viewProfileImage');
        profileImg.src = profile.profile_image_url || 
            `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.display_name || 'U')}&background=4a90e2&color=fff`;
        
        // Bio
        const bioSection = document.getElementById('bioSection');
        const bioParagraph = document.getElementById('viewBio');
        if (profile.bio) {
            bioParagraph.textContent = profile.bio;
            bioSection.classList.remove('hidden');
        } else {
            bioSection.classList.add('hidden');
        }
        
        // Artistic statement
        const artisticSection = document.getElementById('artisticSection');
        const artisticParagraph = document.getElementById('viewArtisticStatement');
        if (profile.artistic_statement) {
            artisticParagraph.textContent = profile.artistic_statement;
            artisticSection.classList.remove('hidden');
        } else {
            artisticSection.classList.add('hidden');
        }
        
        // Mission statement
        const missionSection = document.getElementById('missionSection');
        const missionParagraph = document.getElementById('viewMissionStatement');
        if (profile.mission_statement) {
            missionParagraph.textContent = profile.mission_statement;
            missionSection.classList.remove('hidden');
        } else {
            missionSection.classList.add('hidden');
        }
        
        // Professional details
        document.getElementById('viewExperience').textContent = profile.experience_level?.replace(/_/g, ' ') || 'Not specified';
        document.getElementById('viewCity').textContent = profile.city || 'Not specified';
        document.getElementById('viewLocationPreference').textContent = profile.location_preference?.replace(/_/g, ' ') || 'Not specified';
        
        // Photography styles for photographers
        const photographySection = document.getElementById('photographyStylesViewSection');
        if (profile.user_type === 'photographer' && profile.photography_styles?.length > 0) {
            const stylesContainer = document.getElementById('viewPhotographyStyles');
            stylesContainer.innerHTML = profile.photography_styles.map(style => 
                `<span class="style-tag">${style.replace(/_/g, ' ')}</span>`
            ).join('');
            photographySection.classList.remove('hidden');
        } else {
            photographySection.classList.add('hidden');
        }
        
        // Model details
        const modelSection = document.getElementById('modelDetailsViewSection');
        if (profile.user_type === 'model' && profile.model_details) {
            const modelContainer = document.getElementById('viewModelDetails');
            const details = [];
            if (profile.model_details.gender) details.push(`<div class="detail-item"><span class="detail-label">Gender:</span><span class="detail-value">${profile.model_details.gender.replace(/_/g, ' ')}</span></div>`);
            if (profile.model_details.age) details.push(`<div class="detail-item"><span class="detail-label">Age:</span><span class="detail-value">${profile.model_details.age}</span></div>`);
            if (profile.model_details.height) details.push(`<div class="detail-item"><span class="detail-label">Height:</span><span class="detail-value">${profile.model_details.height}</span></div>`);
            if (profile.model_details.weight) details.push(`<div class="detail-item"><span class="detail-label">Build:</span><span class="detail-value">${profile.model_details.weight.replace(/_/g, ' ')}</span></div>`);
            
            modelContainer.innerHTML = details.join('');
            modelSection.classList.remove('hidden');
        } else {
            modelSection.classList.add('hidden');
        }
        
        // Availability
        const availabilityContainer = document.getElementById('viewAvailability');
        const availability = profile.availability_data || {};
        const availabilityItems = [];
        
        if (availability.available_for_hire) {
            availabilityItems.push(`<div class="availability-status"><div class="availability-indicator available"></div><span>Available for hire</span></div>`);
        }
        if (availability.available_for_collaborations) {
            availabilityItems.push(`<div class="availability-status"><div class="availability-indicator available"></div><span>Available for collaborations</span></div>`);
        }
        if (availability.rate_range) {
            availabilityItems.push(`<div class="availability-status"><span><strong>Rate range:</strong> ${availability.rate_range}</span></div>`);
        }
        
        if (availabilityItems.length > 0) {
            availabilityContainer.innerHTML = availabilityItems.join('');
        } else {
            availabilityContainer.innerHTML = '<div class="availability-status"><div class="availability-indicator unavailable"></div><span>Availability not specified</span></div>';
        }
    }

    async showProfileModal(readOnly = false) {
        if (!this.user) {
            this.showNotification('Please log in to edit your profile', 'error');
            return;
        }
        
        // Show modal
        document.getElementById('profileModal')?.classList.remove('hidden');
        
        // Always in edit mode for this modal now
        const modalTitle = document.querySelector('#profileModal h2');
        modalTitle.textContent = 'Edit Profile';
        
        // Load current profile data
        await this.loadCurrentProfile();
        
        // Load photography styles for selection
        await this.loadPhotographyStyles();
    }
    
    setFormReadOnly(readOnly) {
        const formElements = document.querySelectorAll('#profileModal input, #profileModal textarea, #profileModal select');
        formElements.forEach(element => {
            element.disabled = readOnly;
            if (readOnly) {
                element.style.opacity = '0.7';
                element.style.cursor = 'default';
            } else {
                element.style.opacity = '1';
                element.style.cursor = '';
            }
        });
        
        // Hide/show change image button
        const changeImageBtn = document.getElementById('changeImageBtn');
        if (changeImageBtn) {
            changeImageBtn.style.display = readOnly ? 'none' : 'flex';
        }
    }
    
    hideProfileModal() {
        document.getElementById('profileModal')?.classList.add('hidden');
    }
    
    async loadCurrentProfile() {
        try {
            const response = await fetch(`${API_BASE_URL}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const profile = await response.json();
                this.populateProfileForm(profile);
            } else {
                console.error('Failed to load profile data');
            }
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    }
    
    populateProfileForm(profile) {
        // Basic information
        document.getElementById('profileDisplayName').value = profile.display_name || '';
        document.getElementById('profileUsername').value = profile.username || '';
        document.getElementById('profileBio').value = profile.bio || '';
        document.getElementById('profileCity').value = profile.city || '';
        
        // Professional details
        document.getElementById('profileUserType').value = profile.user_type || '';
        document.getElementById('profileExperience').value = profile.experience_level || '';
        document.getElementById('profileTagline').value = profile.tagline || '';
        
        // Profile image
        const profileImg = document.getElementById('profileImagePreview');
        profileImg.src = profile.profile_image_url || 
            `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.display_name || 'U')}&background=4a90e2&color=fff`;
        
        // Model details (show/hide based on user type)
        this.toggleUserTypeFields(profile.user_type);
        if (profile.user_type === 'model') {
            document.getElementById('profileGender').value = profile.model_details?.gender || '';
            document.getElementById('profileAge').value = profile.model_details?.age || '';
            document.getElementById('profileHeight').value = profile.model_details?.height || '';
            document.getElementById('profileWeight').value = profile.model_details?.weight || '';
        }
        
        // Extended fields
        document.getElementById('profileArtisticStatement').value = profile.artistic_statement || '';
        document.getElementById('profileMissionStatement').value = profile.mission_statement || '';
        
        // Availability
        const availability = profile.availability_data || {};
        document.getElementById('profileAvailableForHire').checked = availability.available_for_hire || false;
        document.getElementById('profileAvailableForCollabs').checked = availability.available_for_collaborations || false;
        document.getElementById('profileRateRange').value = availability.rate_range || '';
        
        // Location preference
        document.getElementById('profileLocationPreference').value = profile.location_preference || '';
        
        // Photography styles (for photographers)
        if (profile.user_type === 'photographer' && profile.photography_styles) {
            profile.photography_styles.forEach(style => {
                const checkbox = document.querySelector(`input[name="photography_styles"][value="${style}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
    }
    
    async loadPhotographyStyles() {
        try {
            const response = await fetch(`${API_BASE_URL}/users/styles`);
            if (response.ok) {
                const styles = await response.json();
                this.renderPhotographyStyles(styles);
            }
        } catch (error) {
            console.error('Error loading photography styles:', error);
        }
    }
    
    renderPhotographyStyles(styles) {
        const container = document.getElementById('photographyStyles');
        container.innerHTML = styles.map(style => `
            <label class="checkbox-label">
                <input type="checkbox" name="photography_styles" value="${style}">
                <span class="checkmark"></span>
                ${style.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </label>
        `).join('');
    }
    
    toggleUserTypeFields(userType) {
        const modelSection = document.getElementById('modelDetailsSection');
        const photographySection = document.getElementById('photographyStylesSection');
        
        // Show/hide model-specific fields
        if (userType === 'model') {
            modelSection?.classList.remove('hidden');
        } else {
            modelSection?.classList.add('hidden');
        }
        
        // Show/hide photography styles for photographers
        if (userType === 'photographer') {
            photographySection?.classList.remove('hidden');
        } else {
            photographySection?.classList.add('hidden');
        }
    }
    
    async handleProfileImageSelect(file) {
        if (!file.type.startsWith('image/')) {
            this.showNotification('Please select an image file', 'error');
            return;
        }
        
        // Check file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('Image must be less than 5MB', 'error');
            return;
        }
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('profileImagePreview').src = e.target.result;
        };
        reader.readAsDataURL(file);
        
        this.selectedProfileImage = file;
    }
    
    async saveProfile() {
        const saveBtn = document.getElementById('saveProfile');
        const originalText = saveBtn.textContent;
        saveBtn.textContent = 'Saving...';
        saveBtn.disabled = true;
        
        try {
            // Collect form data
            const profileData = {
                display_name: document.getElementById('profileDisplayName').value.trim(),
                username: document.getElementById('profileUsername').value.trim(),
                bio: document.getElementById('profileBio').value.trim(),
                city: document.getElementById('profileCity').value.trim(),
                user_type: document.getElementById('profileUserType').value,
                experience_level: document.getElementById('profileExperience').value,
                tagline: document.getElementById('profileTagline').value.trim(),
                artistic_statement: document.getElementById('profileArtisticStatement').value.trim(),
                mission_statement: document.getElementById('profileMissionStatement').value.trim(),
                location_preference: document.getElementById('profileLocationPreference').value
            };
            
            // Add model-specific data
            if (profileData.user_type === 'model') {
                profileData.model_details = {
                    gender: document.getElementById('profileGender').value,
                    age: parseInt(document.getElementById('profileAge').value) || null,
                    height: document.getElementById('profileHeight').value.trim(),
                    weight: document.getElementById('profileWeight').value
                };
            }
            
            // Add photography styles for photographers
            if (profileData.user_type === 'photographer') {
                const selectedStyles = Array.from(document.querySelectorAll('input[name="photography_styles"]:checked'))
                    .map(cb => cb.value);
                profileData.photography_styles = selectedStyles;
            }
            
            // Add availability data
            profileData.availability_data = {
                available_for_hire: document.getElementById('profileAvailableForHire').checked,
                available_for_collaborations: document.getElementById('profileAvailableForCollabs').checked,
                rate_range: document.getElementById('profileRateRange').value.trim()
            };
            
            // Upload profile image first if selected
            if (this.selectedProfileImage) {
                await this.uploadProfileImage();
            }
            
            // Update profile
            const response = await fetch(`${API_BASE_URL}/users/me`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });
            
            if (response.ok) {
                const updatedProfile = await response.json();
                
                // Update local user data
                this.user.display_name = updatedProfile.display_name;
                if (updatedProfile.profile_image_url) {
                    this.user.profile_image_url = updatedProfile.profile_image_url;
                }
                
                // Update UI
                this.updateUserUI();
                this.hideProfileModal();
                this.showNotification('Profile updated successfully!', 'success');
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to update profile');
            }
            
        } catch (error) {
            console.error('Profile update error:', error);
            this.showNotification('Failed to update profile: ' + error.message, 'error');
        } finally {
            saveBtn.textContent = originalText;
            saveBtn.disabled = false;
        }
    }
    
    async uploadProfileImage() {
        if (!this.selectedProfileImage) return;
        
        try {
            const formData = new FormData();
            formData.append('file', this.selectedProfileImage);
            
            const response = await fetch(`${API_BASE_URL}/users/me/profile-image`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                // Update the preview and user data
                this.user.profile_image_url = result.image_url;
                this.selectedProfileImage = null;
            } else {
                throw new Error('Failed to upload profile image');
            }
        } catch (error) {
            console.error('Profile image upload error:', error);
            throw error;
        }
    }

    async validateTokenAndLoadUser(token) {
        try {
            // Verify token with backend and get user profile
            const response = await fetch(`${API_BASE_URL}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const profile = await response.json();
                // Set user data from profile
                this.user = {
                    uid: profile.uid,
                    email: profile.email,
                    display_name: profile.display_name,
                    profile_image_url: profile.profile_image_url
                };
                
                // Update UI
                this.hideAuthModal();
                this.updateUserUI();
                this.loadPhotos();
                
                console.log('Token validated and user profile loaded');
                return true;
            } else {
                console.log('Token validation failed:', response.status);
                // Clear invalid token and show auth modal
                this.clearAuthState();
                return false;
            }
        } catch (error) {
            console.error('Token validation error (network/CORS/server issue):', error);
            // Clear invalid token on any error (network, CORS, 500, etc.)
            this.clearAuthState();
            return false;
        }
    }
    
    clearAuthState() {
        // Clear all authentication state
        localStorage.removeItem('authToken');
        this.authToken = null;
        this.user = null;
        console.log('Authentication state cleared - user will need to sign in again');
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