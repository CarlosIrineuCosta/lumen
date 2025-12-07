/* HTML Templates
 * All HTML templates as JavaScript functions
 * Uses Poor Man's Modules pattern with window.LumenTemplates global
 */

window.LumenTemplates = {
    
    // Navigation template
    nav(user) {
        return `
            <div class="nav-container">
                <!-- Logo -->
                <div class="nav-brand">
                    <h1 class="font-display text-2xl font-bold">
                        <span style="background: linear-gradient(135deg, var(--gradient-1), var(--gradient-2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                            Lumen
                        </span>
                    </h1>
                </div>
                
                <!-- Desktop Navigation Links -->
                <div class="nav-menu hidden md:flex">
                    <button data-route="gallery" class="nav-link">
                        Gallery
                    </button>
                    <button data-route="upload" class="nav-link">
                        Upload
                    </button>
                    <button data-route="series" class="nav-link">
                        Series
                    </button>
                    <button data-route="profile" class="nav-link">
                        Profile
                    </button>
                </div>
                
                <!-- Desktop Auth Status -->
                <div class="nav-auth hidden md:flex">
                    ${user ? `
                        <div class="flex items-center space-x-4">
                            <img src="${this.getAvatarUrl(user)}" alt="Avatar" class="avatar avatar-sm">
                            <span class="text-sm">${user.display_name}</span>
                            <button id="logoutBtn" class="btn btn-secondary">
                                Logout
                            </button>
                        </div>
                    ` : `
                        <button id="loginBtn" class="btn btn-primary">
                            Login with Google
                        </button>
                    `}
                </div>
                
                <!-- Mobile Menu Button -->
                <div class="md:hidden flex items-center space-x-4">
                    ${user ? `<span class="text-sm">${user.display_name}</span>` : ''}
                    <button id="mobileMenuBtn" class="btn btn-secondary p-2">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                  d="M4 6h16M4 12h16M4 18h16"></path>
                        </svg>
                    </button>
                </div>
            </div>
            
            <!-- Mobile Navigation Menu -->
            <div id="mobileMenu" class="nav-mobile hidden md:hidden">
                <div class="nav-container">
                    <div class="flex flex-col space-y-3 py-4">
                        <button data-route="gallery" class="nav-link text-left">
                            Gallery
                        </button>
                        <button data-route="upload" class="nav-link text-left">
                            Upload
                        </button>
                        <button data-route="series" class="nav-link text-left">
                            Series
                        </button>
                        <button data-route="profile" class="nav-link text-left">
                            Profile
                        </button>
                        <hr class="border-gray-600 my-2">
                        ${user ? `
                            <button id="mobileLogoutBtn" class="nav-link text-left text-red-400">
                                Logout
                            </button>
                        ` : `
                            <button id="mobileLoginBtn" class="nav-link text-left text-purple-400">
                                Login with Google
                            </button>
                        `}
                    </div>
                </div>
            </div>
        `;
    },
    
    // Gallery template
    gallery() {
        return `
            <div class="container gallery-container">
                <!-- Gallery Header -->
                <div class="gallery-header card">
                    <h2 class="card-title text-center">Photography Gallery</h2>
                    <p class="text-center text-secondary-text">Discover stunning photographs from talented artists</p>
                </div>
                
                <!-- Gallery Controls -->
                <div class="gallery-controls">
                    <div class="control-group">
                        <span class="control-label">Filter:</span>
                        <button data-filter="all" class="filter-btn active">
                            All Photos
                        </button>
                        <button data-filter="photographer" class="filter-btn">
                            By Photographer
                        </button>
                        <button data-filter="location" class="filter-btn">
                            By Location
                        </button>
                        <button data-filter="series" class="filter-btn">
                            Series
                        </button>
                    </div>
                    
                    <div class="control-group">
                        <span class="control-label">Sort:</span>
                        <button data-sort="latest" class="sort-btn active">
                            Latest
                        </button>
                        <button data-sort="popular" class="sort-btn">
                            Popular
                        </button>
                    </div>
                </div>
                
                <!-- Photo Grid Container -->
                <div class="gallery-wrapper">
                    <div id="photoGrid" class="photo-grid justified-gallery"></div>
                </div>
                
                <!-- Load More Section -->
                <div class="text-center">
                    <button id="loadMoreBtn" class="btn btn-secondary load-more-btn">
                        Load More Photos
                    </button>
                    <div id="scroll-sentinel" class="load-more-trigger"></div>
                </div>
            </div>
        `;
    },
    
    // Upload template
    upload() {
        return `
            <div class="container upload-container">
                <div class="upload-header card">
                    <h2 class="card-title text-center">Upload Photos</h2>
                    <p class="text-center text-secondary-text">Share your photography with the world</p>
                </div>
                
                <div class="card">
                    <!-- FilePond Upload Area -->
                    <div class="upload-section">
                        <input type="file" id="fileInput" multiple accept="image/*" data-max-file-size="${LumenConfig.upload.maxFileSize}" data-max-files="${LumenConfig.upload.maxFiles}">
                    </div>
                    
                    <!-- Metadata Form -->
                    <form id="uploadForm" class="upload-section hidden">
                        <h3 class="text-lg font-semibold mb-4">Photo Details</h3>
                        
                        <div class="form-group">
                            <label for="photoTitle" class="form-label">Title</label>
                            <input type="text" id="photoTitle" class="form-input" placeholder="Give your photo a title">
                        </div>
                        
                        <div class="form-group">
                            <label for="photoDescription" class="form-label">Description</label>
                            <textarea id="photoDescription" rows="4" class="form-input form-textarea" placeholder="Tell the story behind your photo"></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="photoTags" class="form-label">Tags</label>
                            <input type="text" id="photoTags" class="form-input" placeholder="nature, landscape, sunset, photography">
                            <small class="text-secondary-text">Separate tags with commas</small>
                        </div>
                        
                        <div class="form-group">
                            <label for="photoLocation" class="form-label">Location</label>
                            <input type="text" id="photoLocation" class="form-input" placeholder="Where was this photo taken?">
                        </div>
                        
                        <div class="flex space-x-4">
                            <button type="button" id="cancelUpload" class="btn btn-secondary flex-1">
                                Cancel
                            </button>
                            <button type="button" id="submitUpload" class="btn btn-primary flex-1">
                                Upload Photos
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },
    
    // Profile template
    profile(user) {
        return `
            <div class="container mx-auto px-4 pt-20">
                <div class="max-w-4xl mx-auto">
                    ${user ? `
                        <div class="glass-card p-6 rounded-lg mb-6">
                            <div class="flex items-center space-x-6">
                                <img src="${this.getAvatarUrl(user)}" alt="Profile" class="w-24 h-24 rounded-full">
                                <div>
                                    <h2 class="text-3xl font-bold">${user.display_name}</h2>
                                    <p class="text-gray-400">${user.email}</p>
                                    <button id="editProfileBtn" class="mt-2 glass-light px-4 py-2 rounded-lg text-sm hover:glass-hover">
                                        Edit Profile
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="glass-card p-6 rounded-lg">
                            <h3 class="text-xl font-semibold mb-4">My Photos</h3>
                            <div id="userPhotos" class="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <!-- User photos will be loaded here -->
                            </div>
                        </div>
                    ` : `
                        <div class="text-center">
                            <h2 class="text-3xl font-bold mb-4">Sign In to View Profile</h2>
                            <p class="text-gray-400 mb-8">Please sign in with your Google account to access your profile.</p>
                            <button id="profileLoginBtn" class="glass-light px-6 py-3 rounded-lg hover:glass-hover">
                                Login with Google
                            </button>
                        </div>
                    `}
                </div>
            </div>
        `;
    },
    
    // Series template
    series(seriesData) {
        return `
            <div class="container series-container">
                <div class="series-header card">
                    <h2 class="card-title text-center">Photo Series</h2>
                    <p class="text-center text-secondary-text">Curated collections of related photographs</p>
                </div>
                
                <div class="series-grid">
                    ${(seriesData || []).map(series => `
                        <div class="series-card glass-card" data-series-id="${series.id}">
                            <div class="series-cover">
                                <div class="series-thumbnails">
                                    ${series.photos.slice(0, 4).map(photo => `
                                        <img src="${photo.thumbnail_path}" alt="${photo.title}" class="series-thumb">
                                    `).join('')}
                                </div>
                                <div class="series-overlay">
                                    <span class="series-count">${series.photos.length} photos</span>
                                </div>
                            </div>
                            <div class="series-info">
                                <h3 class="series-title">${series.title}</h3>
                                <p class="series-description">${series.description || ''}</p>
                                <p class="series-photographer">by ${series.photographer_name}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },
    
    // Auth modal template
    authModal() {
        return `
            <div id="authModal" class="auth-modal-overlay">
                <div class="auth-modal-card">
                    <div class="auth-modal-content">
                        <h2 class="auth-modal-title">Welcome to Lumen</h2>
                        <p class="auth-modal-subtitle">Sign in to upload and manage your photos</p>
                        <button id="googleSignIn" class="auth-modal-button">
                            <svg class="w-5 h-5" viewBox="0 0 24 24">
                                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                            </svg>
                            <span>Sign in with Google</span>
                        </button>
                        <p class="auth-modal-disclaimer">By signing in, you agree to our Terms of Service and Privacy Policy</p>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Get avatar URL helper
    getAvatarUrl(user) {
        if (!user) return '';
        return user.profile_image_url || 
               `https://ui-avatars.com/api/?name=${encodeURIComponent(user.display_name || 'U')}&background=4a90e2&color=fff`;
    },
    
    // Error message template
    errorMessage(message) {
        return `
            <div class="error-toast fixed top-4 right-4 glass-card p-4 rounded-lg text-red-400 border border-red-600 z-50">
                <div class="flex items-center space-x-2">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                    </svg>
                    <span>${message}</span>
                </div>
            </div>
        `;
    },
    
    // Success message template
    successMessage(message) {
        return `
            <div class="success-toast fixed top-4 right-4 glass-card p-4 rounded-lg text-green-400 border border-green-600 z-50">
                <div class="flex items-center space-x-2">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    <span>${message}</span>
                </div>
            </div>
        `;
    }
};