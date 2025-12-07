/* Search Module
 * Handles photo, user, and tag search functionality
 * Uses Poor Man's Modules pattern with window.LumenSearch global
 */

window.LumenSearch = {
    initialized: false,
    searchTimeout: null,
    searchDelay: 300, // milliseconds
    currentQuery: '',
    currentResults: [],
    selectedIndex: -1,

    // Initialize search module
    init() {
        if (this.initialized) {
            console.log('LumenSearch: Already initialized, skipping...');
            return;
        }

        console.log('LumenSearch: Initializing...');
        this.setupSearchInput();
        this.setupKeyboardNavigation();
        this.initialized = true;
        console.log('LumenSearch: Initialization complete.');
    },

    // Setup search input handler with debouncing
    setupSearchInput() {
        const searchInput = document.getElementById('search-input');
        if (!searchInput) {
            console.error('LumenSearch: search-input element not found');
            return;
        }

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            this.handleSearchInput(query);
        });

        searchInput.addEventListener('focus', () => {
            if (this.currentQuery && this.currentResults.length > 0) {
                this.showResults();
            }
        });
    },

    // Handle search input with debouncing
    handleSearchInput(query) {
        this.currentQuery = query;

        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        // Clear results if query is empty
        if (!query) {
            this.clearResults();
            return;
        }

        // Debounce search requests
        this.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, this.searchDelay);
    },

    // Perform the actual search
    async performSearch(query) {
        console.log('LumenSearch: Searching for:', query);

        try {
            // Show loading state
            this.showLoading();

            let results = [];

            // Try API search first
            try {
                const response = await fetch(`${LumenConfig.api.baseURL}/api/v1/search?q=${encodeURIComponent(query)}&limit=10`, {
                    headers: {
                        'Authorization': LumenAuth.token ? `Bearer ${LumenAuth.token}` : '',
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    results = data.results || [];
                }
            } catch (apiError) {
                console.log('LumenSearch: API search not available, using local search');
            }

            // If API search failed or returned no results, use local search
            if (results.length === 0) {
                results = this.searchLocalData(query);
            }

            this.currentResults = results;
            this.selectedIndex = -1;
            this.displayResults(this.currentResults);

        } catch (error) {
            console.error('LumenSearch: Search error:', error);
            this.showError('Search failed. Please try again.');
        }
    },

    // Search through local gallery data
    searchLocalData(query) {
        const results = [];
        const lowerQuery = query.toLowerCase();

        // Get photos from LumenGallery if available
        if (window.LumenGallery && LumenGallery.allPhotos) {
            const photos = LumenGallery.allPhotos.filter(photo => {
                const title = (photo.title || '').toLowerCase();
                const description = (photo.description || '').toLowerCase();
                const userName = (photo.user?.display_name || '').toLowerCase();
                const location = (photo.location_display || '').toLowerCase();

                return title.includes(lowerQuery) ||
                       description.includes(lowerQuery) ||
                       userName.includes(lowerQuery) ||
                       location.includes(lowerQuery);
            });

            // Convert to search result format
            photos.forEach(photo => {
                results.push({
                    type: 'photo',
                    id: photo.id,
                    title: photo.title,
                    thumbnail_path: photo.thumbnail_path || photo.file_path,
                    user: photo.user
                });
            });

            // Extract unique users from photos
            const userMap = new Map();
            LumenGallery.allPhotos.forEach(photo => {
                if (photo.user) {
                    const userId = photo.user.id || photo.user.display_name;
                    const userName = (photo.user.display_name || '').toLowerCase();

                    if (userName.includes(lowerQuery) && !userMap.has(userId)) {
                        userMap.set(userId, {
                            type: 'user',
                            id: userId,
                            display_name: photo.user.display_name,
                            username: photo.user.username,
                            photo_count: LumenGallery.allPhotos.filter(p =>
                                p.user?.display_name === photo.user.display_name
                            ).length
                        });
                    }
                }
            });

            results.push(...userMap.values());
        }

        // Generate some sample tags if query matches common photography terms
        const commonTags = ['nature', 'landscape', 'portrait', 'street', 'urban', 'architecture', 'sunset', 'mountains', 'beach', 'city'];
        commonTags.forEach(tag => {
            if (tag.includes(lowerQuery)) {
                results.push({
                    type: 'tag',
                    name: tag,
                    count: Math.floor(Math.random() * 50) + 1
                });
            }
        });

        console.log('LumenSearch: Local search results:', results);
        return results.slice(0, 10); // Limit to 10 results
    },

    // Display search results
    displayResults(results) {
        const resultsContainer = document.getElementById('search-results');
        if (!resultsContainer) {
            console.error('LumenSearch: search-results container not found');
            return;
        }

        if (!results || results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="text-center py-8 text-white/60">
                    <svg class="w-12 h-12 mx-auto mb-2 opacity-50" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                    </svg>
                    <p>No results found for "${this.currentQuery}"</p>
                    <p class="text-sm mt-1">Try searching for photos, photographers, or tags</p>
                </div>
            `;
            return;
        }

        // Group results by type
        const photos = results.filter(r => r.type === 'photo');
        const users = results.filter(r => r.type === 'user');
        const tags = results.filter(r => r.type === 'tag');

        let html = '';

        // Display photos
        if (photos.length > 0) {
            html += `<div class="mb-4">
                <h4 class="text-sm font-medium text-white/80 mb-2">Photos</h4>
                <div class="space-y-2">`;

            photos.forEach((photo, index) => {
                html += `
                    <div class="search-result-item flex items-center gap-3 p-2 rounded-lg hover:bg-white/10 cursor-pointer"
                         data-type="photo" data-id="${photo.id}" data-index="${index}">
                        <img src="${photo.thumbnail_path}" alt="${photo.title}" class="w-12 h-12 object-cover rounded">
                        <div class="flex-1">
                            <p class="text-white font-medium text-sm">${photo.title || 'Untitled'}</p>
                            <p class="text-white/60 text-xs">by ${photo.user?.display_name || 'Unknown'}</p>
                        </div>
                    </div>
                `;
            });
            html += '</div></div>';
        }

        // Display users
        if (users.length > 0) {
            html += `<div class="mb-4">
                <h4 class="text-sm font-medium text-white/80 mb-2">Photographers</h4>
                <div class="space-y-2">`;

            users.forEach((user, index) => {
                html += `
                    <div class="search-result-item flex items-center gap-3 p-2 rounded-lg hover:bg-white/10 cursor-pointer"
                         data-type="user" data-id="${user.id}" data-index="${photos.length + index}">
                        <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                            ${(user.display_name || user.username || 'U').charAt(0).toUpperCase()}
                        </div>
                        <div class="flex-1">
                            <p class="text-white font-medium text-sm">${user.display_name || user.username}</p>
                            <p class="text-white/60 text-xs">${user.photo_count || 0} photos</p>
                        </div>
                    </div>
                `;
            });
            html += '</div></div>';
        }

        // Display tags
        if (tags.length > 0) {
            html += `<div class="mb-4">
                <h4 class="text-sm font-medium text-white/80 mb-2">Tags</h4>
                <div class="flex flex-wrap gap-2">`;

            tags.forEach((tag, index) => {
                html += `
                    <span class="search-result-item px-3 py-1 bg-white/10 rounded-full text-sm text-white hover:bg-white/20 cursor-pointer"
                          data-type="tag" data-value="${tag.name}" data-index="${photos.length + users.length + index}">
                        #${tag.name} (${tag.count || 0})
                    </span>
                `;
            });
            html += '</div></div>';
        }

        resultsContainer.innerHTML = html;
        this.setupResultClickHandlers();
    },

    // Setup click handlers for search results
    setupResultClickHandlers() {
        const resultItems = document.querySelectorAll('.search-result-item');
        resultItems.forEach(item => {
            item.addEventListener('click', () => {
                const type = item.dataset.type;
                const id = item.dataset.id;
                const value = item.dataset.value;

                this.handleResultClick(type, id, value);
            });
        });
    },

    // Handle clicks on search results
    handleResultClick(type, id, value) {
        console.log('LumenSearch: Result clicked:', { type, id, value });

        // Close search overlay
        const app = document.querySelector('[data-app="lumen"]') || window.LumenApp;
        if (app && app.hideSearchOverlay) {
            app.hideSearchOverlay();
        }

        // Navigate based on result type
        switch (type) {
            case 'photo':
                this.openPhoto(id);
                break;
            case 'user':
                this.openUserProfile(id);
                break;
            case 'tag':
                this.searchByTag(value);
                break;
        }
    },

    // Open photo in lightbox
    openPhoto(photoId) {
        if (window.LumenGallery && LumenGallery.openPhotoById) {
            LumenGallery.openPhotoById(photoId);
        } else {
            console.log('Would open photo:', photoId);
        }
    },

    // Open user profile
    openUserProfile(userId) {
        if (window.LumenProfile && LumenProfile.showUserProfile) {
            LumenProfile.showUserProfile(userId);
        } else {
            console.log('Would open user profile:', userId);
        }
    },

    // Filter gallery by tag
    searchByTag(tagName) {
        if (window.LumenGallery && LumenGallery.filterByTag) {
            LumenGallery.filterByTag(tagName);
        } else {
            console.log('Would filter by tag:', tagName);
        }
    },

    // Setup keyboard navigation
    setupKeyboardNavigation() {
        const searchInput = document.getElementById('search-input');
        if (!searchInput) return;

        searchInput.addEventListener('keydown', (e) => {
            const resultItems = document.querySelectorAll('.search-result-item');

            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.selectedIndex = Math.min(this.selectedIndex + 1, resultItems.length - 1);
                    this.updateSelection(resultItems);
                    break;

                case 'ArrowUp':
                    e.preventDefault();
                    this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                    this.updateSelection(resultItems);
                    break;

                case 'Enter':
                    e.preventDefault();
                    if (this.selectedIndex >= 0 && resultItems[this.selectedIndex]) {
                        resultItems[this.selectedIndex].click();
                    }
                    break;

                case 'Escape':
                    const app = document.querySelector('[data-app="lumen"]') || window.LumenApp;
                    if (app && app.hideSearchOverlay) {
                        app.hideSearchOverlay();
                    }
                    break;
            }
        });
    },

    // Update visual selection
    updateSelection(resultItems) {
        resultItems.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('bg-white/20');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('bg-white/20');
            }
        });
    },

    // Show loading state
    showLoading() {
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="text-center py-8">
                    <div class="loading loading-spinner loading-md text-white/60"></div>
                    <p class="text-white/60 mt-2">Searching...</p>
                </div>
            `;
        }
    },

    // Show error message
    showError(message) {
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="text-center py-8 text-red-400">
                    <svg class="w-12 h-12 mx-auto mb-2" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                        <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z"/>
                    </svg>
                    <p>${message}</p>
                </div>
            `;
        }
    },

    // Show results container
    showResults() {
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.classList.remove('hidden');
        }
    },

    // Clear search results
    clearResults() {
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }
        this.currentResults = [];
        this.selectedIndex = -1;
    }
};