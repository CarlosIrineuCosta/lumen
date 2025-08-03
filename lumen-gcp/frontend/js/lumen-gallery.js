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
    
    async init() {
        // Check authentication first
        await this.initAuth();
        
        // Initialize gallery if authenticated
        if (this.user) {
            this.setupGallery();
            this.bindEvents();
            this.loadPhotos();
        } else {
            this.showAuthRequired();
        }
    }
    
    async initAuth() {
        return new Promise((resolve) => {
            // Handle redirect result first
            firebase.auth().getRedirectResult().then((result) => {
                if (result.user) {
                    console.log('Sign in successful (redirect):', result.user);
                    // User will be handled by onAuthStateChanged
                }
            }).catch((error) => {
                console.error('Redirect result error:', error);
                // Show error in auth page if needed
            });
            
            firebase.auth().onAuthStateChanged(async (user) => {
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
                        
                        resolve();
                    } catch (error) {
                        console.error('Auth token error:', error);
                        this.showAuthRequired();
                        resolve();
                    }
                } else {
                    this.user = null;
                    this.authToken = null;
                    this.showAuthRequired();
                    resolve();
                }
            });
        });
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
                            <img src="https://via.placeholder.com/40" alt="User" class="user-avatar">
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
        const userAvatar = document.querySelector('.user-avatar');
        if (userAvatar) {
            // Use Firebase user photo if available, fallback to profile photo or default
            const photoUrl = this.user?.photoURL || profile?.profile_image_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(this.user?.displayName || this.user?.email || 'User')}&background=4a90e2&color=fff`;
            userAvatar.src = photoUrl;
            userAvatar.alt = this.user?.displayName || this.user?.email || 'User';
        }
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
        
        // Clear gallery
        $('#photo-grid').empty();
        
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
        photos.forEach(photo => {
            const $item = this.createPhotoElement(photo);
            $('#photo-grid').append($item);
        });
        
        // Re-justify the gallery
        $('#photo-grid').justifiedGallery('norewind');
    }
    
    createPhotoElement(photo) {
        const $link = $('<a>', {
            href: photo.url,
            class: 'gallery-item'
        }).data('photo', photo);
        
        const $img = $('<img>', {
            src: photo.thumbnail,
            alt: `Photo by ${photo.photographer.name}`
        });
        
        const $overlay = $('<div>', { class: 'photo-overlay' });
        const $photographerInfo = $(`
            <div class="overlay-photographer">
                <img src="${photo.photographer.avatar}" alt="${photo.photographer.name}" class="overlay-avatar">
                <div class="overlay-info">
                    <h4>${photo.photographer.name}</h4>
                    <p>${photo.photographer.location}</p>
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
}

// Initialize gallery when DOM is ready
$(document).ready(() => {
    new LumenGallery();
});