// Lumen Gallery - Professional Photography Platform
// Focus: People-first discovery, not image browsing

class LumenGallery {
    constructor() {
        this.currentMode = 'latest';
        this.photos = [];
        this.page = 1;
        this.loading = false;
        this.hasMore = true;
        this.user = null;
        this.authToken = null;
        
        this.init();
    }
    
    init() {
        console.log('LumenGallery initializing...');
        console.log('Masonry available:', typeof Masonry !== 'undefined');
        console.log('imagesLoaded available:', typeof imagesLoaded !== 'undefined');
        
        // Check if Firebase is loaded
        if (typeof firebase === 'undefined') {
            console.error('Firebase not loaded');
            this.showAuthRequired();
            return;
        }
        
        // Initialize authentication - this will handle the rest
        this.initAuth();
    }
    
    initAuth() {
        console.log('Initializing Firebase auth...');
        
        try {
            // Handle redirect result first
            firebase.auth().getRedirectResult().then((result) => {
                if (result.user) {
                    console.log('Sign in successful (redirect):', result.user);
                    // User will be handled by onAuthStateChanged
                }
            }).catch((error) => {
                console.error('Redirect result error:', error);
                // Still show auth page if there's an error
                this.showAuthRequired();
            });
            
            firebase.auth().onAuthStateChanged(async (user) => {
                console.log('Auth state changed:', user ? 'User logged in' : 'User logged out');
                
                if (user) {
                    this.user = user;
                    try {
                        this.authToken = await user.getIdToken();
                        await this.syncUserProfile();
                        
                        // Hide auth screen and show main app
                        this.hideAuthRequired();
                        this.updateUserUI({}); // Update UI with Firebase user data
                        this.setupGallery();
                        this.bindEvents();
                        this.loadPhotos();
                        
                    } catch (error) {
                        console.error('Auth token error:', error);
                        this.showAuthRequired();
                    }
                } else {
                    this.user = null;
                    this.authToken = null;
                    this.showAuthRequired();
                }
            });
        } catch (error) {
            console.error('Firebase init error:', error);
            this.showAuthRequired();
        }
    }
    
    async syncUserProfile() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/profile`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const profile = await response.json();
                this.updateUserUI(profile);
            } else if (response.status === 404) {
                // User exists in Firebase but not in our database
                this.showProfileCompletion();
            }
        } catch (error) {
            console.error('Profile sync error:', error);
        }
    }
    
    showAuthRequired() {
        document.body.innerHTML = `
            <div class="auth-required">
                <div class="auth-container">
                    <h1>LUMEN</h1>
                    <p>Photography Without Compromise</p>
                    <button id="sign-in-btn" class="btn-primary">Sign In with Google</button>
                    <div id="auth-error" style="margin-top: 16px; color: #ea4335; font-size: 14px; display: none;"></div>
                </div>
            </div>
        `;
        
        document.getElementById('sign-in-btn').onclick = async () => {
            try {
                const button = document.getElementById('sign-in-btn');
                const errorDiv = document.getElementById('auth-error');
                
                button.disabled = true;
                button.textContent = 'Signing in...';
                errorDiv.style.display = 'none';
                
                const provider = new firebase.auth.GoogleAuthProvider();
                provider.addScope('email');
                provider.addScope('profile');
                
                // Try popup first, fallback to redirect if domain unauthorized
                try {
                    const result = await firebase.auth().signInWithPopup(provider);
                    console.log('Sign in successful (popup):', result.user);
                } catch (popupError) {
                    console.log('Popup failed, trying redirect:', popupError.code);
                    
                    if (popupError.code === 'auth/unauthorized-domain' || 
                        popupError.code === 'auth/popup-blocked' ||
                        popupError.code === 'auth/popup-closed-by-user') {
                        
                        // Use redirect method instead
                        button.textContent = 'Redirecting...';
                        await firebase.auth().signInWithRedirect(provider);
                        return; // Don't reset button state as we're redirecting
                    } else {
                        throw popupError; // Re-throw other errors
                    }
                }
                
            } catch (error) {
                console.error('Sign in error:', error);
                const errorDiv = document.getElementById('auth-error');
                const button = document.getElementById('sign-in-btn');
                
                button.disabled = false;
                button.textContent = 'Sign In with Google';
                
                if (error.code === 'auth/unauthorized-domain') {
                    errorDiv.innerHTML = `
                        <strong>Domain Authorization Required</strong><br>
                        This Tailscale domain needs to be authorized in Firebase Console.<br>
                        <small>Trying redirect method instead...</small>
                    `;
                    // Automatically try redirect
                    setTimeout(() => {
                        button.click();
                    }, 2000);
                } else if (error.code === 'auth/popup-closed-by-user') {
                    errorDiv.textContent = 'Sign-in was cancelled. Please try again.';
                } else if (error.code === 'auth/popup-blocked') {
                    errorDiv.textContent = 'Popup was blocked. Trying redirect method...';
                    setTimeout(() => {
                        button.click();
                    }, 1000);
                } else {
                    errorDiv.textContent = `Error: ${error.message}`;
                }
                errorDiv.style.display = 'block';
            }
        };
    }
    
    hideAuthRequired() {
        // Restore the main app HTML structure
        document.body.innerHTML = `
            <!-- Header -->
            <header class="main-header">
                <div class="header-container">
                    <div class="logo">
                        <h1>LUMEN</h1>
                        <span class="tagline">Photography Without Compromise</span>
                    </div>
                    <nav class="main-nav">
                        <a href="#" class="nav-link active">Discover</a>
                        <a href="#" class="nav-link">Network</a>
                        <a href="#" class="nav-link">Portfolio</a>
                        <a href="#" class="nav-link">Profile</a>
                    </nav>
                    <div class="user-actions">
                        <button class="btn-upload">Upload</button>
                        <div class="user-menu">
                            <img src="https://via.placeholder.com/40" alt="User" class="user-avatar" id="user-avatar">
                            <div class="user-dropdown" id="user-dropdown">
                                <div class="dropdown-header">
                                    <img src="https://via.placeholder.com/50" alt="User" class="dropdown-avatar">
                                    <div class="dropdown-user-info">
                                        <div class="dropdown-name">Loading...</div>
                                        <div class="dropdown-email">Loading...</div>
                                    </div>
                                </div>
                                <div class="dropdown-divider"></div>
                                <a href="#" class="dropdown-item" id="menu-profile">
                                    <span class="dropdown-icon">👤</span>
                                    Edit Profile
                                </a>
                                <a href="#" class="dropdown-item" id="menu-uploads">
                                    <span class="dropdown-icon">📸</span>
                                    My Uploads
                                </a>
                                <a href="#" class="dropdown-item" id="menu-settings">
                                    <span class="dropdown-icon">⚙️</span>
                                    Settings
                                </a>
                                <div class="dropdown-divider"></div>
                                <a href="#" class="dropdown-item" id="menu-logout">
                                    <span class="dropdown-icon">🚪</span>
                                    Sign Out
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Discovery Mode Selector -->
            <div class="discovery-modes">
                <button class="mode-btn active" data-mode="latest">Latest Work</button>
                <button class="mode-btn" data-mode="photographers">Photographers</button>
                <button class="mode-btn" data-mode="models">Models</button>
                <button class="mode-btn" data-mode="nearby">Nearby (30km)</button>
                <button class="mode-btn" data-mode="collaborations">Open for Work</button>
            </div>

            <!-- Main Gallery Container -->
            <main class="main-content">
                <div id="photo-grid" class="justified-gallery">
                    <!-- Photos will be dynamically loaded here -->
                </div>
                
                <!-- Loading indicator -->
                <div class="loading-spinner" id="loading">
                    <div class="spinner"></div>
                </div>
            </main>

            <!-- Lightbox -->
            <div id="lightbox" class="lightbox">
                <div class="lightbox-content">
                    <button class="lightbox-close">&times;</button>
                    <div class="lightbox-image-container">
                        <img src="" alt="" class="lightbox-image">
                    </div>
                    <div class="lightbox-info">
                        <div class="photographer-info">
                            <img src="" alt="" class="photographer-avatar">
                            <div class="photographer-details">
                                <h3 class="photographer-name"></h3>
                                <p class="photographer-location"></p>
                                <button class="btn-connect">Connect</button>
                            </div>
                        </div>
                        <div class="photo-metadata">
                            <div class="tech-info"></div>
                            <div class="photo-tags"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    showProfileCompletion() {
        // TODO: Show profile completion form
        console.log('Profile completion needed');
    }
    
    updateUserUI(profile) {
        const photoUrl = this.user?.photoURL || profile?.profile_image_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(this.user?.displayName || this.user?.email || 'User')}&background=4a90e2&color=fff`;
        const displayName = this.user?.displayName || profile?.display_name || 'User';
        const email = this.user?.email || 'No email';
        
        // Update header avatar
        const userAvatar = document.querySelector('.user-avatar');
        if (userAvatar) {
            userAvatar.src = photoUrl;
            userAvatar.alt = displayName;
        }
        
        // Update dropdown header
        const dropdownAvatar = document.querySelector('.dropdown-avatar');
        const dropdownName = document.querySelector('.dropdown-name');
        const dropdownEmail = document.querySelector('.dropdown-email');
        
        if (dropdownAvatar) dropdownAvatar.src = photoUrl;
        if (dropdownName) dropdownName.textContent = displayName;
        if (dropdownEmail) dropdownEmail.textContent = email;
    }
    
    setupGallery() {
        $('#photo-grid').justifiedGallery({
            rowHeight: 240,
            maxRowHeight: 400,
            margins: 3,
            border: 0,
            lastRow: 'nojustify',
            captions: false,
            cssAnimation: true,
            imagesAnimationDuration: 300,
            waitThumbnailsLoad: true
        }).on('jg.complete', () => {
            $('#photo-grid').addClass('loaded');
        });
    }
    bindEvents() {
        // Mode switching
        $('.mode-btn').on('click', (e) => {
            const mode = $(e.target).data('mode');
            this.switchMode(mode);
        });
        
        // Infinite scroll
        $(window).on('scroll', () => {
            if (this.shouldLoadMore()) {
                this.loadPhotos();
            }
        });
        
        // Photo click
        $(document).on('click', '.gallery-item', (e) => {
            e.preventDefault();
            const photoData = $(e.currentTarget).data('photo');
            this.openLightbox(photoData);
        });
        
        // Lightbox close
        $('.lightbox-close').on('click', () => {
            this.closeLightbox();
        });
        
        // ESC key to close lightbox
        $(document).on('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeLightbox();
            }
        });
        
        // User menu dropdown
        $(document).on('click', '#user-avatar', (e) => {
            e.stopPropagation();
            $('#user-dropdown').toggleClass('active');
        });
        
        // Close dropdown when clicking outside
        $(document).on('click', (e) => {
            if (!$(e.target).closest('.user-menu').length) {
                $('#user-dropdown').removeClass('active');
            }
        });
        
        // Menu item handlers
        $(document).on('click', '#menu-logout', (e) => {
            e.preventDefault();
            this.handleLogout();
        });
        
        $(document).on('click', '#menu-profile', (e) => {
            e.preventDefault();
            this.showProfileEditor();
        });
        
        $(document).on('click', '#menu-uploads', (e) => {
            e.preventDefault();
            this.showUserUploads();
        });
        
        // Upload button
        $(document).on('click', '.btn-upload', (e) => {
            e.preventDefault();
            this.showUploadDialog();
        });
    }
    switchMode(mode) {
        if (mode === this.currentMode) return;
        
        // Update UI
        $('.mode-btn').removeClass('active');
        $(`.mode-btn[data-mode="${mode}"]`).addClass('active');
        
        // Reset state
        this.currentMode = mode;
        this.page = 1;
        this.photos = [];
        this.hasMore = true;
        
        // Clear gallery and reset masonry properly
        if (this.masonry) {
            this.masonry.destroy();
        }
        $('#photo-grid').empty().append('<div class="masonry-grid-sizer"></div>');
        this.setupGallery();
        
        // Load new content
        this.loadPhotos();
    }
    
    shouldLoadMore() {
        if (this.loading || !this.hasMore) return false;
        
        const scrollPos = $(window).scrollTop() + $(window).height();
        const threshold = $(document).height() - 200;
        
        return scrollPos > threshold;
    }
    
    async loadPhotos() {
        if (this.loading) return;
        
        this.loading = true;
        $('#loading').addClass('active');
        
        try {
            // In production, this would call your FastAPI backend
            const photos = await this.fetchPhotos();
            this.renderPhotos(photos);
            this.page++;
        } catch (error) {
            console.error('Error loading photos:', error);
        } finally {
            this.loading = false;
            $('#loading').removeClass('active');
        }
    }
    async fetchPhotos() {
        try {
            const endpoint = this.getEndpointForMode();
            const response = await fetch(`${API_BASE_URL}${endpoint}?page=${this.page}&limit=20`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.photos || data.users || data; // Handle different response formats
            } else {
                console.error('API Error:', response.status);
                return this.getFallbackPhotos(); // Fallback to mock data
            }
        } catch (error) {
            console.error('Fetch error:', error);
            return this.getFallbackPhotos(); // Fallback to mock data
        }
    }
    
    getEndpointForMode() {
        switch (this.currentMode) {
            case 'latest':
                return '/photos/recent';
            case 'photographers':
                return '/discovery/photographers';
            case 'models':
                return '/discovery/models';
            case 'nearby':
                return '/discovery/nearby';
            case 'collaborations':
                return '/discovery/collaborations';
            default:
                return '/photos/recent';
        }
    }
    
    getFallbackPhotos() {
        // Fallback mock data for development
        const basePhotos = [
            {
                id: 1,
                url: 'https://source.unsplash.com/800x1200/?portrait',
                thumbnail: 'https://source.unsplash.com/400x600/?portrait',
                photographer: {
                    name: 'Anna Silva',
                    location: 'São Paulo, Brazil',
                    avatar: 'https://i.pravatar.cc/150?img=1'
                },
                metadata: {
                    camera: 'Canon EOS R5',
                    lens: '85mm f/1.4',
                    iso: 200,
                    aperture: 'f/2.8',
                    shutter: '1/125s'
                },
                tags: ['portrait', 'studio', 'professional']
            },
            {
                id: 2,
                url: 'https://source.unsplash.com/1200x800/?fashion',
                thumbnail: 'https://source.unsplash.com/600x400/?fashion',
                photographer: {
                    name: 'Marcus Klein',
                    location: 'Berlin, Germany',
                    avatar: 'https://i.pravatar.cc/150?img=2'
                },
                metadata: {
                    camera: 'Sony A7III',
                    lens: '24-70mm f/2.8',
                    iso: 400,
                    aperture: 'f/4',
                    shutter: '1/250s'
                },
                tags: ['fashion', 'outdoor', 'editorial']
            }
        ];
        
        // Generate more photos with variations
        const photos = [];
        for (let i = 0; i < 12; i++) {
            const base = basePhotos[i % basePhotos.length];
            photos.push({
                ...base,
                id: this.page * 100 + i,
                url: `${base.url}&sig=${this.page}${i}`,
                thumbnail: `${base.thumbnail}&sig=${this.page}${i}`
            });
        }
        
        return photos;
    }
    renderPhotos(photos) {
        console.log('renderPhotos called with', photos.length, 'photos');
        console.log('Masonry instance:', this.masonry);
        
        if (!this.masonry) {
            console.error('Masonry not initialized');
            return;
        }
        
        const container = document.querySelector('#photo-grid');
        console.log('Container found:', !!container);
        
        const newElements = [];
        
        photos.forEach((photo, index) => {
            console.log(`Creating photo element ${index + 1}:`, photo.title);
            const $item = this.createPhotoElement(photo);
            container.appendChild($item[0]); // Append DOM element, not jQuery object
            newElements.push($item[0]);
        });
        
        console.log('Added', newElements.length, 'new elements to DOM');
        
        // Wait for images to load, then layout
        if (typeof imagesLoaded !== 'undefined' && newElements.length > 0) {
            console.log('Using imagesLoaded for layout...');
            imagesLoaded(newElements, () => {
                console.log('Images loaded, applying masonry layout...');
                this.masonry.appended(newElements);
                this.masonry.layout();
                $('#photo-grid').addClass('loaded');
                console.log('Masonry layout updated with', newElements.length, 'new items');
            });
        } else {
            console.log('Using fallback timeout for layout...');
            // Fallback if imagesLoaded not available
            setTimeout(() => {
                this.masonry.layout();
                $('#photo-grid').addClass('loaded');
                console.log('Fallback layout applied');
            }, 100);
        }
    }
    
    createPhotoElement(photo) {
        // Handle both mock data format and real API format
        const imageUrl = photo.image_url || photo.url;
        const thumbnailUrl = photo.thumbnail_url || photo.thumbnail || imageUrl;
        const photographerName = photo.photographer_name || photo.photographer?.name || 'Unknown Photographer';
        const location = photo.location_display || photo.photographer?.location || 'Unknown Location';
        const photoTitle = photo.title || 'Untitled';
        
        const $link = $('<a>', {
            href: imageUrl,
            class: 'masonry-item gallery-item',
            'data-photo-id': photo.id
        }).data('photo', photo);
        
        // Create skeleton loader first
        const $skeleton = $('<div>', { class: 'photo-skeleton' });
        $link.append($skeleton);
        
        // Create image with loading handling
        const $img = $('<img>', {
            alt: `${photoTitle} by ${photographerName}`,
            class: 'gallery-image'
        });
        
        // Show skeleton while loading, then fade in image
        $img.on('load', () => {
            $skeleton.fadeOut(200, () => {
                $img.fadeIn(300);
            });
        }).on('error', () => {
            $skeleton.html('<div class="photo-error">Image failed to load</div>');
        });
        
        // Set source after event handlers are attached
        $img.attr('src', thumbnailUrl);
        
        const $overlay = $('<div>', { class: 'photo-overlay' });
        const $photographerInfo = $(`
            <div class="overlay-photographer">
                <div class="overlay-info">
                    <h4 class="photo-title">${photoTitle}</h4>
                    <p class="photographer-name">${photographerName}</p>
                    <p class="photo-location">${location}</p>
                    ${photo.user_tags && photo.user_tags.length > 0 ? 
                        `<div class="photo-tags">${photo.user_tags.map(tag => `<span class="tag">${tag}</span>`).join('')}</div>` : 
                        ''
                    }
                </div>
            </div>
        `);
        
        $overlay.append($photographerInfo);
        $link.append($img, $overlay);
        
        return $link;
    }
    openLightbox(photo) {
        // Update image
        $('.lightbox-image').attr('src', photo.url);
        
        // Update photographer info
        $('.photographer-avatar').attr('src', photo.photographer.avatar);
        $('.photographer-name').text(photo.photographer.name);
        $('.photographer-location').text(photo.photographer.location);
        
        // Update metadata
        const techInfo = `
            <div><span>Camera</span><span>${photo.metadata.camera}</span></div>
            <div><span>Lens</span><span>${photo.metadata.lens}</span></div>
            <div><span>ISO</span><span>${photo.metadata.iso}</span></div>
            <div><span>Aperture</span><span>${photo.metadata.aperture}</span></div>
            <div><span>Shutter</span><span>${photo.metadata.shutter}</span></div>
        `;
        $('.tech-info').html(techInfo);
        
        // Update tags
        const tags = photo.tags.map(tag => 
            `<span class="tag">${tag}</span>`
        ).join('');
        $('.photo-tags').html(tags);
        
        // Show lightbox
        $('#lightbox').addClass('active');
        $('body').css('overflow', 'hidden');
    }
    
    closeLightbox() {
        $('#lightbox').removeClass('active');
        $('body').css('overflow', 'auto');
    }
    
    async handleLogout() {
        try {
            await firebase.auth().signOut();
            // The onAuthStateChanged handler will take care of showing the auth screen
        } catch (error) {
            console.error('Logout error:', error);
            alert('Error signing out. Please try again.');
        }
    }
    
    showProfileEditor() {
        $('#user-dropdown').removeClass('active');
        
        const profileHtml = `
            <div class="modal-overlay" id="profile-modal">
                <div class="modal-content profile-editor">
                    <div class="modal-header">
                        <h2>Edit Profile</h2>
                        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="profile-form" class="profile-form">
                            <div class="form-group">
                                <label for="display_name">Display Name</label>
                                <input type="text" id="display_name" name="display_name" placeholder="Your name" required>
                            </div>
                            <div class="form-group">
                                <label for="bio">Bio</label>
                                <textarea id="bio" name="bio" placeholder="Tell us about yourself..." rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="city">City</label>
                                <input type="text" id="city" name="city" placeholder="Your city">
                            </div>
                            <div class="form-group">
                                <label for="user_type">I am a...</label>
                                <select id="user_type" name="user_type" required>
                                    <option value="">Select type</option>
                                    <option value="photographer">Photographer</option>
                                    <option value="model">Model</option>
                                </select>
                            </div>
                            <div class="form-group" id="model-fields" style="display: none;">
                                <h3>Model Information</h3>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="gender">Gender</label>
                                        <select id="gender" name="gender">
                                            <option value="">Select gender</option>
                                            <option value="Male">Male</option>
                                            <option value="Female">Female</option>
                                            <option value="Non-binary">Non-binary</option>
                                            <option value="Other">Other</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="age">Age</label>
                                        <input type="number" id="age" name="age" min="16" max="80">
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="height_cm">Height (cm)</label>
                                        <input type="number" id="height_cm" name="height_cm" min="120" max="220">
                                    </div>
                                    <div class="form-group">
                                        <label for="weight_kg">Weight (kg)</label>
                                        <input type="number" id="weight_kg" name="weight_kg" min="30" max="200">
                                    </div>
                                </div>
                            </div>
                            <div class="form-actions">
                                <button type="button" class="btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                                <button type="submit" class="btn-primary">Save Profile</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(profileHtml);
        
        // Show/hide model fields based on user type
        $('#user_type').on('change', function() {
            if ($(this).val() === 'model') {
                $('#model-fields').show();
            } else {
                $('#model-fields').hide();
            }
        });
        
        // Handle form submission
        $('#profile-form').on('submit', (e) => {
            e.preventDefault();
            this.saveProfile();
        });
    }
    
    async saveProfile() {
        const formData = new FormData(document.getElementById('profile-form'));
        const profileData = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/profile`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });
            
            if (response.ok) {
                const updatedProfile = await response.json();
                this.updateUserUI(updatedProfile);
                $('#profile-modal').remove();
                alert('Profile updated successfully!');
            } else {
                throw new Error('Failed to save profile');
            }
        } catch (error) {
            console.error('Profile save error:', error);
            alert('Error saving profile. Please try again.');
        }
    }
    
    async showUserUploads() {
        $('#user-dropdown').removeClass('active');
        
        const uploadsHtml = `
            <div class="modal-overlay" id="uploads-modal">
                <div class="modal-content uploads-view">
                    <div class="modal-header">
                        <h2>My Uploads</h2>
                        <button class="modal-close" onclick="document.getElementById('uploads-modal').remove()">&times;</button>
                    </div>
                    
                    <div class="uploads-container">
                        <div class="uploads-header">
                            <div class="uploads-stats" id="uploads-stats">
                                <span class="stat-item">
                                    <strong id="total-photos">0</strong>
                                    <span>Photos</span>
                                </span>
                                <span class="stat-item">
                                    <strong id="total-views">0</strong>
                                    <span>Views</span>
                                </span>
                                <span class="stat-item">
                                    <strong>0</strong>
                                    <span>Likes</span>
                                </span>
                            </div>
                            <div class="uploads-actions">
                                <button class="btn-secondary" onclick="window.location.reload()">Refresh</button>
                                <button class="btn-primary" onclick="document.getElementById('uploads-modal').remove(); $('.btn-upload').click();">Upload New</button>
                            </div>
                        </div>
                        
                        <div class="uploads-grid" id="user-uploads-grid">
                            <div class="loading-spinner active" id="uploads-loading">
                                <div class="spinner"></div>
                                <p>Loading your photos...</p>
                            </div>
                        </div>
                        
                        <div class="uploads-empty" id="uploads-empty" style="display: none;">
                            <div class="empty-state">
                                <div class="empty-icon">📸</div>
                                <h3>No photos yet</h3>
                                <p>Start building your portfolio by uploading your first photo</p>
                                <button class="btn-primary" onclick="document.getElementById('uploads-modal').remove(); $('.btn-upload').click();">Upload Photo</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(uploadsHtml);
        await this.loadUserPhotos();
    }
    
    async loadUserPhotos() {
        try {
            const user = firebase.auth().currentUser;
            if (!user) {
                this.showUploadError('Please sign in to view your uploads');
                return;
            }
            
            const idToken = await user.getIdToken();
            const response = await fetch(`${API_BASE_URL}/photos/user`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${idToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.renderUserPhotos(data.photos || []);
            } else {
                console.error('Failed to load user photos:', response.status);
                this.showEmptyUploads();
            }
        } catch (error) {
            console.error('Error loading user photos:', error);
            this.showEmptyUploads();
        } finally {
            $('#uploads-loading').removeClass('active');
        }
    }
    
    renderUserPhotos(photos) {
        if (!photos || photos.length === 0) {
            this.showEmptyUploads();
            return;
        }
        
        // Update stats
        $('#total-photos').text(photos.length);
        $('#total-views').text(photos.reduce((sum, photo) => sum + (photo.views || 0), 0));
        
        const $grid = $('#user-uploads-grid');
        $grid.empty();
        
        photos.forEach(photo => {
            const $item = this.createUserPhotoElement(photo);
            $grid.append($item);
        });
    }
    
    createUserPhotoElement(photo) {
        const uploadDate = new Date(photo.created_at).toLocaleDateString();
        
        const $item = $(`
            <div class="user-photo-item" data-photo-id="${photo.id}">
                <div class="user-photo-image">
                    <img src="${photo.thumbnail_url || photo.storage_url}" alt="${photo.title}">
                    <div class="user-photo-overlay">
                        <button class="btn-icon" onclick="window.open('${photo.storage_url}', '_blank')" title="View Full Size">
                            <span>🔍</span>
                        </button>
                        <button class="btn-icon delete-photo" data-photo-id="${photo.id}" title="Delete Photo">
                            <span>🗑️</span>
                        </button>
                    </div>
                </div>
                <div class="user-photo-info">
                    <h4>${photo.title || 'Untitled'}</h4>
                    <p class="photo-date">Uploaded ${uploadDate}</p>
                    <div class="photo-stats">
                        <span class="stat">${photo.views || 0} views</span>
                        <span class="stat">${photo.likes || 0} likes</span>
                    </div>
                </div>
            </div>
        `);
        
        // Add delete handler
        $item.find('.delete-photo').on('click', (e) => {
            e.stopPropagation();
            this.deleteUserPhoto(photo.id);
        });
        
        return $item;
    }
    
    showEmptyUploads() {
        $('#user-uploads-grid').hide();
        $('#uploads-empty').show();
        $('#total-photos').text('0');
        $('#total-views').text('0');
    }
    
    async deleteUserPhoto(photoId) {
        if (!confirm('Are you sure you want to delete this photo? This action cannot be undone.')) {
            return;
        }
        
        try {
            const user = firebase.auth().currentUser;
            if (!user) {
                this.showNotification('Please sign in to delete photos', 'error');
                return;
            }
            
            const idToken = await user.getIdToken();
            const response = await fetch(`${API_BASE_URL}/photos/${photoId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${idToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // Remove from UI
                $(`.user-photo-item[data-photo-id="${photoId}"]`).fadeOut(300, function() {
                    $(this).remove();
                    
                    // Check if any photos remain
                    if ($('#user-uploads-grid .user-photo-item').length === 0) {
                        $('#uploads-empty').show();
                        $('#user-uploads-grid').hide();
                    }
                    
                    // Update stats
                    const remainingPhotos = $('#user-uploads-grid .user-photo-item').length;
                    $('#total-photos').text(remainingPhotos);
                });
                
                this.showNotification('Photo deleted successfully', 'success');
            } else {
                const errorData = await response.json();
                this.showNotification('Failed to delete photo: ' + (errorData.detail || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Error deleting photo:', error);
            this.showNotification('Error deleting photo: ' + error.message, 'error');
        }
    }
    
    showUploadDialog() {
        const uploadHtml = `
            <div class="modal-overlay" id="upload-modal">
                <div class="modal-content upload-dialog">
                    <div class="modal-header">
                        <h2>Upload Photo</h2>
                        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <!-- File Upload Area -->
                        <div class="upload-zone" id="upload-zone">
                            <div class="upload-zone-content">
                                <div class="upload-icon">📸</div>
                                <h3>Drag & drop your photo here</h3>
                                <p>or click to browse files</p>
                                <div class="upload-specs">
                                    <small>Supports: JPG, PNG, WEBP • Max size: 10MB • Min resolution: 800x600</small>
                                </div>
                                <input type="file" id="file-input" accept="image/jpeg,image/jpg,image/png,image/webp" style="display: none;">
                            </div>
                        </div>
                        
                        <!-- Upload Progress -->
                        <div class="upload-progress" id="upload-progress" style="display: none;">
                            <div class="progress-bar">
                                <div class="progress-fill" id="progress-fill"></div>
                            </div>
                            <div class="progress-text">
                                <span id="progress-percentage">0%</span>
                                <span id="progress-status">Preparing upload...</span>
                            </div>
                        </div>
                        
                        <!-- Image Preview & Metadata (initially hidden) -->
                        <div class="upload-preview" id="upload-preview" style="display: none;">
                            <div class="preview-image-container">
                                <img id="preview-image" src="" alt="Preview">
                                <div class="image-info">
                                    <span id="image-filename"></span>
                                    <span id="image-size"></span>
                                    <span id="image-dimensions"></span>
                                </div>
                            </div>
                            
                            <div class="upload-metadata">
                                <form id="upload-form" class="upload-form">
                                    <div class="form-group">
                                        <label for="photo-title">Title</label>
                                        <input type="text" id="photo-title" name="title" placeholder="Give your photo a title..." required>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="photo-description">Description</label>
                                        <textarea id="photo-description" name="description" placeholder="Tell the story behind this photo..." rows="3"></textarea>
                                    </div>
                                    
                                    <div class="form-row">
                                        <div class="form-group">
                                            <label for="photo-location">Location</label>
                                            <input type="text" id="photo-location" name="location" placeholder="Where was this taken?">
                                        </div>
                                        <div class="form-group">
                                            <label for="content-rating">Content Rating</label>
                                            <select id="content-rating" name="content_rating">
                                                <option value="general">General</option>
                                                <option value="artistic_nude">Artistic Nude</option>
                                                <option value="mature">Mature</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label for="photo-tags">Tags</label>
                                        <input type="text" id="photo-tags" name="tags" placeholder="portrait, studio, fashion, natural light..." title="Separate tags with commas">
                                        <small>Separate tags with commas</small>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label class="checkbox-label">
                                            <input type="checkbox" id="portfolio-piece" name="is_portfolio">
                                            <span class="checkmark"></span>
                                            Add to portfolio (featured work)
                                        </label>
                                    </div>
                                    
                                    <div class="form-actions">
                                        <button type="button" class="btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                                        <button type="submit" class="btn-primary" id="upload-btn">
                                            <span class="btn-text">Upload Photo</span>
                                            <span class="btn-spinner" style="display: none;">⏳</span>
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                        
                        <!-- Error Display -->
                        <div class="upload-error" id="upload-error" style="display: none;">
                            <div class="error-icon">❌</div>
                            <div class="error-message" id="error-message"></div>
                            <button class="btn-secondary" onclick="document.getElementById('upload-error').style.display='none'; document.getElementById('upload-zone').style.display='block';">Try Again</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(uploadHtml);
        this.initializeUploadHandlers();
    }
    
    initializeUploadHandlers() {
        const uploadZone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');
        
        // Click to browse
        uploadZone.addEventListener('click', () => {
            fileInput.click();
        });
        
        // File selection
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleFileSelection(file);
            }
        });
        
        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });
        
        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelection(files[0]);
            }
        });
        
        // Form submission
        document.getElementById('upload-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handlePhotoUpload();
        });
    }
    
    handleFileSelection(file) {
        // Validate file
        const validation = this.validateImageFile(file);
        if (!validation.valid) {
            this.showUploadError(validation.error);
            return;
        }
        
        // Show preview
        this.showImagePreview(file);
    }
    
    validateImageFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        
        if (!allowedTypes.includes(file.type)) {
            return { valid: false, error: 'Please select a valid image file (JPG, PNG, or WEBP)' };
        }
        
        if (file.size > maxSize) {
            return { valid: false, error: 'File size must be less than 10MB' };
        }
        
        return { valid: true };
    }
    
    showImagePreview(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            // Hide upload zone, show preview
            document.getElementById('upload-zone').style.display = 'none';
            document.getElementById('upload-preview').style.display = 'block';
            
            // Set preview image
            const previewImg = document.getElementById('preview-image');
            previewImg.src = e.target.result;
            
            // Set file info
            document.getElementById('image-filename').textContent = file.name;
            document.getElementById('image-size').textContent = this.formatFileSize(file.size);
            
            // Get image dimensions
            previewImg.onload = () => {
                document.getElementById('image-dimensions').textContent = `${previewImg.naturalWidth} × ${previewImg.naturalHeight}`;
            };
            
            // Store file for upload
            this.selectedFile = file;
        };
        
        reader.readAsDataURL(file);
    }
    
    showUploadError(message) {
        document.getElementById('upload-zone').style.display = 'none';
        document.getElementById('upload-error').style.display = 'block';
        document.getElementById('error-message').textContent = message;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async handlePhotoUpload() {
        try {
            const uploadBtn = document.getElementById('upload-btn');
            const progressDiv = document.getElementById('upload-progress');
            const previewDiv = document.getElementById('upload-preview');
            const errorDiv = document.getElementById('upload-error');
            
            // Show upload progress
            previewDiv.style.display = 'none';
            progressDiv.style.display = 'block';
            
            // Get form data
            const form = document.getElementById('upload-form');
            const formData = new FormData(form);
            
            // Get the selected file
            if (!this.selectedFile) {
                this.showUploadError('No file selected');
                return;
            }
            
            // ARCHITECTURE: Option A - Backend Handles Storage Upload
            // Flow: Frontend → Backend (with file) → Backend uploads to Firebase Storage → Database
            // Benefits: Better security, backend controls permissions, simpler error handling
            
            document.getElementById('progress-status').textContent = 'Uploading photo...';
            
            // Get current user for authentication
            const user = firebase.auth().currentUser;
            if (!user) {
                this.showUploadError('Please sign in to upload photos');
                return;
            }
            
            // Get Firebase auth token for backend authentication
            const idToken = await user.getIdToken();
            
            // Prepare multipart form data matching backend API expectations
            const uploadFormData = new FormData();
            uploadFormData.append('file', this.selectedFile);  // Actual file for backend to upload
            uploadFormData.append('title', formData.get('title') || 'Untitled');
            uploadFormData.append('description', formData.get('description') || '');
            uploadFormData.append('camera', formData.get('camera') || '');
            uploadFormData.append('lens', formData.get('lens') || '');
            uploadFormData.append('settings', formData.get('settings') || '');
            uploadFormData.append('location', formData.get('location') || '');
            if (formData.get('tags')) {
                uploadFormData.append('user_tags', formData.get('tags'));
            }
            
            // Send everything to backend - backend will handle Firebase Storage upload
            const response = await fetch(`${API_BASE_URL}/photos/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${idToken}`
                    // Note: No Content-Type header - browser sets multipart boundary automatically
                },
                body: uploadFormData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to upload photo');
            }
            
            const result = await response.json();
            
            // Success - close modal and refresh gallery
            document.getElementById('upload-modal').remove();
            this.showNotification('Photo uploaded successfully!', 'success');
            
            // Reset gallery state and refresh completely
            this.page = 1;
            this.photos = [];
            this.hasMore = true;
            
            // Clear gallery and reload with masonry reset
            if (this.masonry) {
                this.masonry.destroy();
            }
            $('#photo-grid').empty().append('<div class="masonry-grid-sizer"></div>');
            this.setupGallery();
            this.loadPhotos();
            
        } catch (error) {
            console.error('Upload process error:', error);
            this.showUploadError('Upload failed: ' + error.message);
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;
        
        // Add to body
        document.body.appendChild(notification);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 4000);
        
        // Close button handler
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
    }
}

// Initialize gallery when DOM is ready
$(document).ready(() => {
    new LumenGallery();
});