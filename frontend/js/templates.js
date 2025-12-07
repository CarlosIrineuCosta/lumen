// Lumen Templates - HTML Generation
// Global namespace: window.LumenTemplates

window.LumenTemplates = {
    
    // Photo Gallery Templates
    gallery: {
        // Individual photo item for justified gallery
        photoItem: function(photo) {
            return `
                <a href="${photo.urls.large}" 
                   class="photo-item" 
                   data-photo-id="${photo.id}"
                   data-author="${photo.author?.name || 'Unknown'}"
                   data-title="${photo.title || 'Untitled'}">
                    <img src="${photo.urls.small}" 
                         alt="${photo.title || 'Photo by ' + (photo.author?.name || 'Unknown')}"
                         loading="lazy"
                         width="${photo.width || 400}"
                         height="${photo.height || 300}">
                    <div class="photo-overlay">
                        <div class="photo-overlay-title">${photo.title || 'Untitled'}</div>
                        <div class="photo-overlay-author">by ${photo.author?.name || 'Unknown'}</div>
                    </div>
                </a>
            `;
        },

        // Empty gallery state
        emptyState: function(message = "No photos to display") {
            return `
                <div class="empty-state">
                    <div class="empty-state-icon">📷</div>
                    <div class="empty-state-title">${message}</div>
                    <div class="empty-state-description">
                        Upload some photos to get started
                    </div>
                </div>
            `;
        },

        // Loading skeleton for gallery
        loadingSkeleton: function(count = 12) {
            let items = '';
            for (let i = 0; i < count; i++) {
                const height = 200 + Math.random() * 200; // Random height 200-400px
                items += `
                    <div class="photo-skeleton" style="height: ${height}px; width: 300px; margin: 2px;">
                    </div>
                `;
            }
            return `<div class="gallery-loading">${items}</div>`;
        }
    },

    // Profile Templates
    profile: {
        // Profile header
        header: function(user) {
            return `
                <div class="profile-header">
                    <img class="profile-avatar" 
                         src="${user.avatar || '/images/default-avatar.jpg'}" 
                         alt="${user.name}">
                    <div class="profile-info">
                        <h1 class="profile-name">${user.name}</h1>
                        <div class="profile-username">@${user.username}</div>
                        <div class="profile-bio">${user.bio || ''}</div>
                        <div class="profile-stats">
                            <div class="profile-stat">
                                <span class="profile-stat-number">${user.stats?.photos || 0}</span>
                                <span class="profile-stat-label">Photos</span>
                            </div>
                            <div class="profile-stat">
                                <span class="profile-stat-number">${user.stats?.followers || 0}</span>
                                <span class="profile-stat-label">Followers</span>
                            </div>
                            <div class="profile-stat">
                                <span class="profile-stat-number">${user.stats?.following || 0}</span>
                                <span class="profile-stat-label">Following</span>
                            </div>
                        </div>
                        <div class="profile-actions">
                            ${user.isOwnProfile ? 
                                '<button class="profile-btn primary">Edit Profile</button>' :
                                '<button class="profile-btn primary">Follow</button><button class="profile-btn">Message</button>'
                            }
                        </div>
                    </div>
                </div>
            `;
        },

        // Profile tabs
        tabs: function(activeTab = 'photos') {
            const tabs = ['photos', 'series', 'appreciations'];
            return `
                <div class="profile-tabs">
                    ${tabs.map(tab => `
                        <button class="profile-tab ${tab === activeTab ? 'active' : ''}" 
                                data-tab="${tab}">
                            ${tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    `).join('')}
                </div>
            `;
        }
    },

    // Series Templates
    series: {
        // Series view layout
        view: function(series) {
            return `
                <div class="series-sidebar">
                    <h1 class="series-title">${series.title}</h1>
                    <div class="series-meta">
                        <div class="series-count">${series.photos?.length || 0} photos</div>
                        <div class="series-date">${new Date(series.createdAt).toLocaleDateString()}</div>
                    </div>
                    <div class="series-author">
                        <img class="series-author-avatar" 
                             src="${series.author?.avatar || '/images/default-avatar.jpg'}" 
                             alt="${series.author?.name}">
                        <span class="series-author-name">${series.author?.name}</span>
                    </div>
                    <div class="series-description">${series.description || ''}</div>
                    ${series.appreciations ? `
                        <div class="series-appreciation">
                            <div class="appreciation-header">
                                <span class="appreciation-icon">⭐</span>
                                <span class="appreciation-text">Appreciations</span>
                            </div>
                            <div class="appreciation-count">${series.appreciations}</div>
                        </div>
                    ` : ''}
                </div>
                <div class="series-content">
                    <div class="series-grid">
                        ${series.photos?.map(photo => `
                            <div class="series-photo" data-photo-id="${photo.id}">
                                <img src="${photo.urls.medium}" 
                                     alt="${photo.title || 'Series photo'}"
                                     loading="lazy">
                            </div>
                        `).join('') || ''}
                    </div>
                </div>
            `;
        }
    },

    // Modal Templates
    modals: {
        // Photo details modal
        photoDetails: function(photo) {
            return `
                <div class="photo-info">
                    <div class="photo-author">
                        <img class="author-avatar" 
                             src="${photo.author?.avatar || '/images/default-avatar.jpg'}" 
                             alt="${photo.author?.name}">
                        <span class="author-name">${photo.author?.name || 'Unknown'}</span>
                    </div>
                    <h3 class="photo-title">${photo.title || 'Untitled'}</h3>
                    <div class="photo-meta">
                        ${photo.tags?.length ? `
                            <div class="photo-tags">
                                ${photo.tags.map(tag => `<span class="photo-tag">${tag}</span>`).join('')}
                            </div>
                        ` : ''}
                        ${photo.camera ? `
                            <div class="photo-camera">${photo.camera}</div>
                        ` : ''}
                        ${photo.settings ? `
                            <div class="photo-settings">${photo.settings}</div>
                        ` : ''}
                        <div class="photo-date">${new Date(photo.createdAt).toLocaleDateString()}</div>
                    </div>
                    <div class="photo-actions">
                        <button class="action-btn">Appreciate</button>
                        <button class="action-btn secondary">Follow ${photo.author?.name}</button>
                    </div>
                </div>
            `;
        },

        // Settings content
        settingsContent: {
            profile: function(user) {
                return `
                    <div class="settings-section">
                        <h3>Edit Profile</h3>
                        <div class="settings-form">
                            <div class="form-group">
                                <label>Profile Photo</label>
                                <div class="profile-photo-upload">
                                    <img src="${user.avatar || '/images/default-avatar.jpg'}" 
                                         alt="Profile photo" class="current-avatar">
                                    <button class="btn-secondary">Change Photo</button>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Name</label>
                                <input type="text" class="form-input" value="${user.name}" placeholder="Your name">
                            </div>
                            <div class="form-group">
                                <label>Username</label>
                                <input type="text" class="form-input" value="${user.username}" placeholder="@username">
                            </div>
                            <div class="form-group">
                                <label>Bio</label>
                                <textarea class="form-input" rows="4" placeholder="Tell us about yourself">${user.bio || ''}</textarea>
                            </div>
                            <div class="form-group">
                                <label>Website</label>
                                <input type="url" class="form-input" value="${user.website || ''}" placeholder="https://your-website.com">
                            </div>
                            <div class="form-actions">
                                <button class="btn-primary">Save Changes</button>
                                <button class="btn-secondary">Cancel</button>
                            </div>
                        </div>
                    </div>
                `;
            },

            notifications: function() {
                return `
                    <div class="settings-section">
                        <h3>Notification Preferences</h3>
                        <div class="settings-form">
                            <div class="form-group">
                                <label class="checkbox-label">
                                    <input type="checkbox" checked> Email notifications
                                </label>
                            </div>
                            <div class="form-group">
                                <label class="checkbox-label">
                                    <input type="checkbox" checked> New followers
                                </label>
                            </div>
                            <div class="form-group">
                                <label class="checkbox-label">
                                    <input type="checkbox"> Photo appreciations
                                </label>
                            </div>
                            <div class="form-actions">
                                <button class="btn-primary">Save Preferences</button>
                            </div>
                        </div>
                    </div>
                `;
            }
        }
    },

    // Search Templates
    search: {
        // Search results
        results: function(results, query) {
            if (!results || results.length === 0) {
                return `
                    <div class="search-empty">
                        <div class="search-empty-icon">🔍</div>
                        <div class="search-empty-title">No results found</div>
                        <div class="search-empty-description">
                            Try different keywords or browse our categories
                        </div>
                    </div>
                `;
            }

            return `
                <div class="search-results-header">
                    <h3>Results for "${query}"</h3>
                    <span class="search-count">${results.length} photos</span>
                </div>
                <div class="search-results-grid">
                    ${results.map(photo => this.parent.gallery.photoItem(photo)).join('')}
                </div>
            `;
        },

        // Search suggestions
        suggestions: function(suggestions) {
            if (!suggestions || suggestions.length === 0) return '';
            
            return `
                <div class="search-suggestions">
                    <div class="search-suggestions-title">Popular searches</div>
                    <div class="search-suggestions-list">
                        ${suggestions.map(suggestion => `
                            <button class="search-suggestion" data-query="${suggestion}">
                                ${suggestion}
                            </button>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    },

    // Navigation Templates
    navigation: {
        // Category filter items
        categoryItem: function(category, isActive = false) {
            return `
                <button class="category-item ${isActive ? 'active' : ''}" 
                        data-category="${category.slug}">
                    ${category.name}
                </button>
            `;
        }
    },

    // Authentication Templates
    authModal: function() {
        return `
            <div class="auth-modal-overlay">
                <div class="auth-modal-content">
                    <div class="auth-modal-header">
                        <h2>Sign In</h2>
                        <button class="auth-modal-close">×</button>
                    </div>
                    <div class="auth-modal-body">
                        <button id="googleSignIn" class="auth-btn google-btn">
                            Sign in with Google
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    // Utility Templates
    utils: {
        // Loading spinner
        loading: function(message = 'Loading...') {
            return `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div class="loading-message">${message}</div>
                </div>
            `;
        },

        // Error message
        error: function(message = 'Something went wrong') {
            return `
                <div class="error-container">
                    <div class="error-icon">⚠️</div>
                    <div class="error-message">${message}</div>
                    <button class="error-retry btn-secondary">Try Again</button>
                </div>
            `;
        },

        // Success toast
        toast: function(message, type = 'success') {
            const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
            return `
                <div class="toast toast-${type}">
                    <div class="toast-icon">${icon}</div>
                    <div class="toast-message">${message}</div>
                    <button class="toast-close">×</button>
                </div>
            `;
        }
    }
};

// Template helpers
window.LumenTemplates.helpers = {
    // Escape HTML to prevent XSS
    escape: function(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format date relative to now
    formatRelativeDate: function(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 7) {
            return new Date(date).toLocaleDateString();
        } else if (days > 0) {
            return `${days} day${days > 1 ? 's' : ''} ago`;
        } else if (hours > 0) {
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else if (minutes > 0) {
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else {
            return 'Just now';
        }
    },

    // Truncate text
    truncate: function(str, length = 100) {
        if (!str || str.length <= length) return str;
        return str.substring(0, length).trim() + '...';
    },

    // Generate placeholder image URL
    placeholder: function(width = 400, height = 300, text = '') {
        return `https://via.placeholder.com/${width}x${height}/333333/999999?text=${encodeURIComponent(text || `${width}×${height}`)}`;
    }
};

// Template compilation and caching
window.LumenTemplates.cache = new Map();

window.LumenTemplates.compile = function(templateName, data) {
    const cacheKey = `${templateName}_${JSON.stringify(data)}`;
    
    if (this.cache.has(cacheKey)) {
        return this.cache.get(cacheKey);
    }
    
    // Find template function by path (e.g., 'gallery.photoItem')
    const parts = templateName.split('.');
    let template = this;
    
    for (const part of parts) {
        if (template && typeof template === 'object' && part in template) {
            template = template[part];
        } else {
            throw new Error(`Template not found: ${templateName}`);
        }
    }
    
    if (typeof template !== 'function') {
        throw new Error(`Template is not a function: ${templateName}`);
    }
    
    const result = template(data);
    
    // Cache the result if it's not too large
    if (result.length < 10000) {
        this.cache.set(cacheKey, result);
    }
    
    return result;
};

// Clear template cache
window.LumenTemplates.clearCache = function() {
    this.cache.clear();
    if (window.LumenConfig?.app?.debug) {
        console.log('🗑️ Template cache cleared');
    }
};

// Template debugging
if (window.LumenConfig?.app?.debug) {
    window.DEBUG_TEMPLATES = window.LumenTemplates;
    console.log('📄 Lumen Templates loaded');
}