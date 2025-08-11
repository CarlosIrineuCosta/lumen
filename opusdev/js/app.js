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
                this.applyMasonryLayout();
            }, 250);
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
            let endpoint = this.getEndpointForView(this.currentView);
            
            const response = await fetch(`${API_BASE_URL}${endpoint}?page=${this.page}&limit=20`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                const newPhotos = data.photos || data.users || data; // Handle different response formats
                
                this.photos = [...this.photos, ...newPhotos];
                this.hasMore = data.has_more !== false;
                
                // Set display context and render
                this.photoDisplay.setContext(this.currentView);
                this.photoDisplay.renderPhotos(newPhotos, this.user, document.getElementById('photoGrid'));
                
                this.page++;
            }
        } catch (error) {
            console.error('Failed to load photos:', error);
            this.photoDisplay.showEmptyState();
        } finally {
            this.loading = false;
            document.getElementById('loadingIndicator')?.classList.add('hidden');
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
                
            case 'photographers':
                // Photographer discovery
                return '/users/photographers';
                
            case 'nearby':
                // Geographic discovery
                return '/photos/nearby?radius=30';
                
            case 'portfolio':
                // User's portfolio photos only
                return `/photos/user/${this.user?.uid}?portfolio_only=true`;
                
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