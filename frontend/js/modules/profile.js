/* Profile Module
 * User profile management
 * Uses Poor Man's Modules pattern with window.LumenProfile global
 */

window.LumenProfile = {
    // State
    user: null,
    userPhotos: [],
    userStats: null,
    editMode: false,
    currentUserId: null,
    isOwnProfile: false,
    profileView: null,
    eventsBound: false,
    boundProfileClickHandler: null,
    profileViewListenerAttached: false,
    
    // Initialize profile functionality
    init(container) {
        this.cacheElements(container);
        this.bindDelegatedEvents();
    },

    cacheElements(container) {
        if (container) {
            this.profileView = container;
        } else if (!this.profileView) {
            this.profileView = document.getElementById('profile-view');
        }
    },

    bindDelegatedEvents() {
        if (!this.boundProfileClickHandler) {
            this.boundProfileClickHandler = this.handleProfileViewClick.bind(this);
        }

        if (this.profileView && !this.profileViewListenerAttached) {
            this.profileView.addEventListener('click', this.boundProfileClickHandler);
            this.profileViewListenerAttached = true;
        }

        if (!this.eventsBound) {
            document.addEventListener('click', (event) => {
                const loginTrigger = event.target.closest('[data-profile-action="prompt-login"]');
                if (loginTrigger) {
                    event.preventDefault();
                    if (window.LumenAuth) {
                        LumenAuth.signIn();
                    }
                }
            });
            this.eventsBound = true;
        }
    },
    
    // Show profile modal/settings
    async showProfile(userId = null, options = {}) {
        const { container = null } = options;
        this.cacheElements(container);
        const renderInView = options.renderInView ?? Boolean(this.profileView);

        this.bindDelegatedEvents();

        // If no userId provided, show current user's profile
        if (!userId && window.LumenAuth?.isAuthenticated()) {
            userId = 'me';
        }
        
        if (!userId) {
            if (window.LumenAuth?.signIn) {
                LumenAuth.signIn();
            }
            return;
        }
        
        this.currentUserId = userId;
        this.isOwnProfile = userId === 'me';
        
        try {
            await this.loadUserProfile(userId);
            await this.loadUserPhotos(userId);
            await this.loadUserStats(userId);
            if (renderInView && this.profileView) {
                this.renderProfileView();
            } else {
                this.renderProfileModal();
            }
        } catch (error) {
            console.error('Failed to load profile:', error);
            LumenUtils.showError('Failed to load profile');
        }
    },
    
    // Load user profile data
    async loadUserProfile(userId) {
        try {
            if (userId === 'me') {
                const response = await LumenAPI.getUserProfile();
                this.user = response;
            } else {
                // For public profiles, use direct request with proper prefix
                const response = await LumenAPI.request(`/api/v1/users/${userId}/public`);
                this.user = response;
            }
        } catch (error) {
            console.error('Failed to load user profile:', error);
            throw error;
        }
    },
    
    // Load user's photos
    async loadUserPhotos(userId) {
        try {
            const response = await LumenAPI.getUserPhotos(userId);
            this.userPhotos = response.photos || [];
        } catch (error) {
            console.error('Failed to load user photos:', error);
            throw error;
        }
    },
    
    // Load user statistics
    async loadUserStats(userId) {
        try {
            const response = await LumenAPI.getUserStats(userId);
            this.userStats = response;
        } catch (error) {
            console.error('Failed to load user stats:', error);
            // Don't throw error for stats, just log it
            this.userStats = {
                photo_count: this.userPhotos.length,
                total_likes: 0,
                follower_count: 0,
                following_count: 0
            };
        }
    },

    getProfileTemplateData() {
        const user = this.user || {};
        const stats = this.userStats || {};

        return {
            avatar: user.avatar_url || user.avatar || '/images/default-avatar.jpg',
            name: user.display_name || user.name || user.full_name || 'Lumen Photographer',
            username: user.username || user.handle || (user.email ? user.email.split('@')[0] : 'member'),
            bio: user.bio || '',
            stats: {
                photos: stats.photo_count ?? this.userPhotos.length ?? 0,
                followers: stats.follower_count ?? 0,
                following: stats.following_count ?? 0
            },
            isOwnProfile: this.isOwnProfile
        };
    },

    renderProfileView() {
        if (!this.profileView) {
            console.error('Profile view container not found');
            return;
        }

        const templateData = this.getProfileTemplateData();
        const headerHtml = window.LumenTemplates?.profile?.header
            ? LumenTemplates.profile.header(templateData)
            : this.renderHeaderFallback(templateData);
        const tabsHtml = window.LumenTemplates?.profile?.tabs
            ? LumenTemplates.profile.tabs('photos')
            : '';

        const photosSection = this.renderPhotosSection();
        const statsSection = this.renderStatsSection();

        this.profileView.innerHTML = `
            <div class="profile-shell">
                ${headerHtml}
                ${tabsHtml}
                ${photosSection}
                ${statsSection}
            </div>
        `;

        this.profileView.classList.remove('glass-hidden');
        this.decorateProfileHeader();
    },

    decorateProfileHeader() {
        if (!this.profileView) return;

        const primaryAction = this.profileView.querySelector('.profile-actions button, .profile-actions .btn-primary');
        if (this.isOwnProfile && primaryAction) {
            primaryAction.dataset.profileAction = 'edit-profile';
        }
    },

    renderHeaderFallback(data) {
        return `
            <header class="profile-header">
                <img class="profile-avatar" src="${data.avatar}" alt="${data.name}">
                <div class="profile-info">
                    <h1 class="profile-name">${data.name}</h1>
                    <div class="profile-username">@${data.username}</div>
                    ${data.bio ? `<div class="profile-bio">${data.bio}</div>` : ''}
                    <div class="profile-stats">
                        <div class="profile-stat">
                            <span class="profile-stat-number">${data.stats.photos}</span>
                            <span class="profile-stat-label">Photos</span>
                        </div>
                        <div class="profile-stat">
                            <span class="profile-stat-number">${data.stats.followers}</span>
                            <span class="profile-stat-label">Followers</span>
                        </div>
                        <div class="profile-stat">
                            <span class="profile-stat-number">${data.stats.following}</span>
                            <span class="profile-stat-label">Following</span>
                        </div>
                    </div>
                    ${data.isOwnProfile ? `
                        <div class="profile-actions">
                            <button class="btn-primary" data-profile-action="edit-profile">Edit Profile</button>
                        </div>
                    ` : ''}
                </div>
            </header>
        `;
    },

    renderPhotosSection() {
        const heading = this.isOwnProfile ? 'Your Photos' : 'Photos';

        if (!this.userPhotos || this.userPhotos.length === 0) {
            const emptyStateMessage = this.isOwnProfile
                ? 'You have not uploaded any photos yet.'
                : 'No photos to show yet.';
            return `
                <section class="photos-section">
                    <h3>${heading}</h3>
                    <div class="no-photos">${emptyStateMessage}</div>
                </section>
            `;
        }

        const photosMarkup = this.userPhotos.map((photo, index) => {
            const title = photo.title || 'Untitled';
            const thumbnail = photo.thumbnail_url || photo.thumbnail_path || photo.image_url;
            const likeCount = photo.like_count ?? 0;

            return `
                <div class="user-photo-item" data-profile-action="view-photo" data-photo-index="${index}">
                    <img src="${thumbnail}" alt="${title}">
                    <div class="photo-info">
                        <h4>${title}</h4>
                        <span>${likeCount} likes</span>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <section class="photos-section">
                <h3>${heading}</h3>
                <div class="user-photos-grid">
                    ${photosMarkup}
                </div>
            </section>
        `;
    },

    renderStatsSection() {
        if (!this.userStats) {
            return '';
        }

        const stats = this.userStats;
        const sectionTitle = this.isOwnProfile ? 'Your Statistics' : 'Statistics';
        const joinDate = stats.join_date ? new Date(stats.join_date).toLocaleDateString() : null;

        return `
            <section class="stats-section">
                <h3>${sectionTitle}</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h4>Photos Uploaded</h4>
                        <span class="big-number">${stats.photo_count ?? this.userPhotos.length ?? 0}</span>
                    </div>
                    <div class="stat-card">
                        <h4>Total Likes</h4>
                        <span class="big-number">${stats.total_likes ?? 0}</span>
                    </div>
                    <div class="stat-card">
                        <h4>Followers</h4>
                        <span class="big-number">${stats.follower_count ?? 0}</span>
                    </div>
                    <div class="stat-card">
                        <h4>Following</h4>
                        <span class="big-number">${stats.following_count ?? 0}</span>
                    </div>
                    ${joinDate ? `
                        <div class="stat-card full-width">
                            <h4>Member Since</h4>
                            <span class="date-text">${joinDate}</span>
                        </div>
                    ` : ''}
                </div>
            </section>
        `;
    },

    handleProfileViewClick(event) {
        const editButton = event.target.closest('[data-profile-action="edit-profile"]');
        if (editButton) {
            event.preventDefault();
            this.openSettingsModal();
            return;
        }

        const photoCard = event.target.closest('[data-profile-action="view-photo"]');
        if (photoCard) {
            event.preventDefault();
            const index = parseInt(photoCard.getAttribute('data-photo-index'), 10);
            if (!Number.isNaN(index) && this.userPhotos[index]) {
                this.viewPhoto(this.userPhotos[index]);
            }
        }
    },

    openSettingsModal() {
        if (!this.isOwnProfile) {
            return;
        }
        this.renderProfileModal();
    },
    
    // Render user's photos
    renderUserPhotos() {
        const container = document.getElementById('userPhotos');
        if (!container) return;
        
        if (this.userPhotos.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center py-8">
                    <p class="text-gray-400 mb-4">You haven't uploaded any photos yet.</p>
                    <button onclick="LumenRouter.navigate('upload')" class="glass-light px-4 py-2 rounded-lg hover:glass-hover">
                        Upload Your First Photo
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.userPhotos.map(photo => `
            <div class="glass-card rounded-lg overflow-hidden hover:glass-hover transition">
                <img src="${photo.thumbnail_url}" alt="${photo.title}" class="w-full h-32 object-cover">
                <div class="p-3">
                    <h4 class="font-medium text-sm mb-1 truncate">${photo.title || 'Untitled'}</h4>
                    <p class="text-xs text-gray-400">${photo.like_count || 0} likes</p>
                </div>
            </div>
        `).join('');
        
        // Add click listeners for photo viewing
        container.querySelectorAll('.glass-card').forEach((card, index) => {
            card.addEventListener('click', () => {
                this.viewPhoto(this.userPhotos[index]);
            });
        });
    },
    
    // Render profile modal
    renderProfileModal() {
        const contentWrapper = document.getElementById('settings-modal-content-wrapper');
        if (!contentWrapper) {
            console.error('Could not find settings modal content wrapper');
            return;
        }

        if (this.isOwnProfile) {
            contentWrapper.innerHTML = this.generateSettingsContent();
        } else {
            // Placeholder for public profile view
            contentWrapper.innerHTML = `<p>Public profile view not yet implemented.</p>`;
        }
        
        LumenUI.showModal('settings-modal');
    },
    
    // Generate settings content for own profile
    generateSettingsContent() {
        return `
            <div class="settings-sidebar">
                <div class="settings-header">
                    <h2>Settings</h2>
                    <form method="dialog">
                         <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
                    </form>
                </div>
                <nav class="settings-nav">
                    <a href="#" class="settings-nav-item active" data-settings="profile" onclick="LumenProfile.showSettingsTab('profile')">Edit Profile</a>
                    <a href="#" class="settings-nav-item" data-settings="stats" onclick="LumenProfile.showSettingsTab('stats')">Statistics</a>
                    <a href="#" class="settings-nav-item" data-settings="notifications" onclick="LumenProfile.showSettingsTab('notifications')">Notifications</a>
                    <a href="#" class="settings-nav-item" data-settings="blocked" onclick="LumenProfile.showSettingsTab('blocked')">Blocked Accounts</a>
                    <a href="#" class="settings-nav-item" data-settings="account" onclick="LumenProfile.showSettingsTab('account')">Account</a>
                    <a href="#" class="settings-nav-item" data-settings="privacy" onclick="LumenProfile.showSettingsTab('privacy')">Privacy</a>
                    <a href="#" class="settings-nav-item danger" data-settings="signout" onclick="LumenProfile.handleSignOut()">Sign Out</a>
                    <a href="#" class="settings-nav-item danger" data-settings="delete" onclick="LumenProfile.showSettingsTab('delete')">Delete Account</a>
                </nav>
            </div>
            <div class="settings-main">
                <div id="settings-content-area">
                    ${this.generateProfileTab()}
                </div>
            </div>
        `;
    },
    
    // Generate profile edit tab
    generateProfileTab() {
        const user = this.user;
        const stats = this.userStats;
        
        return `
            <div class="profile-edit-section">
                <h3>Profile Information</h3>
                <div class="profile-form">
                    <div class="form-group">
                        <label>Display Name</label>
                        <input type="text" id="displayName" value="${user.display_name || ''}" class="form-input">
                    </div>
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" id="handle" value="${user.handle || ''}" class="form-input">
                    </div>
                    <div class="form-group">
                        <label>Bio</label>
                        <textarea id="bio" class="form-textarea" rows="4">${user.bio || ''}</textarea>
                    </div>
                    <div class="profile-stats">
                        <div class="stat-item">
                            <span class="stat-number">${stats?.photo_count || 0}</span>
                            <span class="stat-label">Photos</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${stats?.total_likes || 0}</span>
                            <span class="stat-label">Likes</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${stats?.follower_count || 0}</span>
                            <span class="stat-label">Followers</span>
                        </div>
                    </div>
                    <div class="form-actions">
                        <button onclick="LumenProfile.saveProfile()" class="btn-primary">Save Changes</button>
                        <button onclick="LumenProfile.closeProfileModal()" class="btn-secondary">Cancel</button>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Close profile modal
    closeProfileModal() {
        LumenUI.hideModal('settings-modal');
    },
    
    // Show different settings tabs
    showSettingsTab(tabName) {
        const contentArea = document.getElementById('settings-content-area');
        
        // Update active nav item
        document.querySelectorAll('.settings-nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-settings="${tabName}"]`).classList.add('active');
        
        // Load tab content
        switch (tabName) {
            case 'profile':
                contentArea.innerHTML = this.generateProfileTab();
                break;
            case 'stats':
                contentArea.innerHTML = this.generateStatsTab();
                break;
            default:
                contentArea.innerHTML = `<div class="tab-placeholder">
                    <h3>${tabName.charAt(0).toUpperCase() + tabName.slice(1)}</h3>
                    <p>This section is coming soon.</p>
                </div>`;
        }
    },
    
    
    // Generate stats tab
    generateStatsTab() {
        const stats = this.userStats;
        const joinDate = stats?.join_date ? new Date(stats.join_date).toLocaleDateString() : 'Unknown';
        
        return `
            <div class="stats-section">
                <h3>Your Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h4>Photos Uploaded</h4>
                        <span class="big-number">${stats?.photo_count || 0}</span>
                    </div>
                    <div class="stat-card">
                        <h4>Total Likes</h4>
                        <span class="big-number">${stats?.total_likes || 0}</span>
                    </div>
                    <div class="stat-card">
                        <h4>Followers</h4>
                        <span class="big-number">${stats?.follower_count || 0}</span>
                    </div>
                    <div class="stat-card">
                        <h4>Following</h4>
                        <span class="big-number">${stats?.following_count || 0}</span>
                    </div>
                    <div class="stat-card full-width">
                        <h4>Member Since</h4>
                        <span class="date-text">${joinDate}</span>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Handle sign out
    async handleSignOut() {
        let confirmed = true;

        if (window.LumenUI?.confirm) {
            confirmed = await LumenUI.confirm('Are you sure you want to sign out?', {
                title: 'Sign out',
                confirmText: 'Sign out',
                cancelText: 'Stay signed in',
                variant: 'danger'
            });
        } else {
            confirmed = window.confirm('Are you sure you want to sign out?');
        }

        if (!confirmed) {
            return;
        }

        await LumenAuth.signOut();
        this.closeProfileModal();
        if (window.LumenUtils?.showSuccess) {
            LumenUtils.showSuccess('You have been signed out.');
        }
    },
    
    // Save profile changes (from settings modal)
    async saveProfile() {
        try {
            const displayName = document.getElementById('displayName')?.value;
            const handle = document.getElementById('handle')?.value;
            const bio = document.getElementById('bio')?.value;
            
            if (!displayName) {
                LumenUtils.showError('Display name is required');
                return;
            }
            
            const updateData = {
                display_name: displayName,
                username: handle,
                bio: bio
            };
            
            // Update profile via API
            const updatedProfile = await LumenAPI.updateUserProfile(updateData);
            
            // Update local user object with the response from backend
            this.user = updatedProfile;
            
            LumenUtils.showSuccess('Profile updated successfully');
            
            // Refresh the settings content with new data
            this.showSettingsTab('profile');
        } catch (error) {
            console.error('Failed to save profile:', error);
            LumenUtils.showError('Failed to save profile changes');
        }
    },
    
    // View individual photo
    viewPhoto(photo) {
        // Create a temporary lightGallery for this photo
        if (typeof lightGallery !== 'undefined') {
            const tempContainer = document.createElement('div');
            document.body.appendChild(tempContainer);
            
            const lg = lightGallery(tempContainer, {
                dynamic: true,
                dynamicEl: [{
                    src: photo.image_url,
                    thumb: photo.thumbnail_url,
                    subHtml: `<h4>${photo.title || 'Untitled'}</h4><p>${photo.description || ''}</p>`
                }],
                addClass: 'lg-glass-theme',
                onCloseAfter: () => {
                    lg.destroy();
                    if (tempContainer.parentNode) {
                        tempContainer.parentNode.removeChild(tempContainer);
                    }
                }
            });
            
            lg.openGallery();
        }
    },
    
    // Show edit profile modal
    showEditModal() {
        if (!this.user) return;
        
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-80 backdrop-blur-sm flex items-center justify-center z-50';
        modal.id = 'editProfileModal';
        
        modal.innerHTML = `
            <div class="glass-card p-6 rounded-lg max-w-md mx-4 w-full">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xl font-semibold">Edit Profile</h3>
                    <button id="closeEditModal" class="text-gray-400 hover:text-white">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="editProfileForm" class="space-y-4">
                    <div class="text-center mb-4">
                        <img src="${LumenAuth.getAvatarUrl()}" alt="Profile" class="w-20 h-20 rounded-full mx-auto mb-2">
                        <button type="button" id="changeAvatarBtn" class="text-sm text-purple-400 hover:text-purple-300">
                            Change Avatar
                        </button>
                        <input type="file" id="avatarInput" accept="image/*" class="hidden">
                    </div>
                    
                    <div>
                        <label for="displayName" class="block text-sm font-medium mb-2">Display Name</label>
                        <input type="text" id="displayName" value="${this.user.display_name || ''}" 
                               class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500">
                    </div>
                    
                    <div>
                        <label for="email" class="block text-sm font-medium mb-2">Email</label>
                        <input type="email" id="email" value="${this.user.email || ''}" disabled
                               class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-400">
                        <p class="text-xs text-gray-500 mt-1">Email cannot be changed</p>
                    </div>
                    
                    <div class="flex space-x-3 pt-4">
                        <button type="button" id="cancelEdit" 
                                class="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition">
                            Cancel
                        </button>
                        <button type="submit" id="saveProfile"
                                class="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg transition">
                            Save Changes
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add event listeners for modal
        this.setupModalEventListeners(modal);
    },
    
    // Setup modal event listeners
    setupModalEventListeners(modal) {
        // Close modal
        const closeModal = () => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        };
        
        modal.getElementById('closeEditModal')?.addEventListener('click', closeModal);
        modal.getElementById('cancelEdit')?.addEventListener('click', closeModal);
        
        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
        
        // Avatar change
        modal.getElementById('changeAvatarBtn')?.addEventListener('click', () => {
            modal.getElementById('avatarInput')?.click();
        });
        
        modal.getElementById('avatarInput')?.addEventListener('change', (e) => {
            this.handleAvatarChange(e.target.files[0], modal);
        });
        
        // Form submission
        modal.getElementById('editProfileForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveProfile(modal);
        });
    },
    
    // Handle avatar image change
    async handleAvatarChange(file, modal) {
        if (!file || !LumenUtils.validateImageFile(file)) {
            LumenUtils.showError('Please select a valid image file');
            return;
        }
        
        if (!LumenUtils.validateFileSize(file)) {
            LumenUtils.showError('Image file is too large');
            return;
        }
        
        try {
            // Preview the new avatar
            const reader = new FileReader();
            reader.onload = (e) => {
                const avatarImg = modal.querySelector('img');
                if (avatarImg) {
                    avatarImg.src = e.target.result;
                }
            };
            reader.readAsDataURL(file);
            
            // Store file for upload
            this.newAvatarFile = file;
            
        } catch (error) {
            console.error('Failed to preview avatar:', error);
            LumenUtils.showError('Failed to preview new avatar');
        }
    },
    
    
    // Refresh profile display
    refreshProfileDisplay() {
        // Navigation is static - no need to update
        
        // Re-render profile page if we're on it
        if (window.LumenRouter && LumenRouter.getCurrentRoute() === 'profile') {
            this.cacheElements();
            this.renderProfileView();
        }
    }
};
