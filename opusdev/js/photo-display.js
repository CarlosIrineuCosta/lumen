// Photo Display System - Reusable photo grid display logic
// Handles different contexts: Home feed, Discovery, Portfolio, etc.

class PhotoDisplay {
    constructor(masonry) {
        this.masonry = masonry;
        this.displayContext = 'home'; // home, discovery, portfolio, photographers
    }
    
    setContext(context) {
        this.displayContext = context;
        console.log(`Photo display context set to: ${context}`);
    }
    
    /**
     * Main photo rendering function - context-aware
     * @param {Array} photos - Array of photo objects
     * @param {Object} user - Current user object
     * @param {HTMLElement} grid - Grid container element
     */
    renderPhotos(photos, user, grid) {
        if (!grid) return;
        
        // Always hide empty state when we have photos to render
        document.getElementById('emptyState')?.classList.add('hidden');
        
        if (photos.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Show loading state and hide grid during positioning
        this.showGridLoading(true);
        
        photos.forEach(photo => {
            const item = this.createPhotoElement(photo, user);
            // Initially hide the item to prevent flickering
            item.style.opacity = '0';
            item.style.visibility = 'hidden';
            grid.appendChild(item);
        });
        
        // Initialize or refresh masonry layout
        if (!this.masonry) {
            const SimpleMasonry = window.SimpleMasonry;
            this.masonry = new SimpleMasonry('#photoGrid', {
                itemSelector: '.photo-item',
                columnWidth: 300,
                gutter: 16,
                onComplete: () => this.showGridLoading(false)
            });
        } else {
            // For view changes, refresh the entire layout
            this.masonry.refresh(() => this.showGridLoading(false));
        }
    }
    
    /**
     * Create photo element based on context
     * @param {Object} photo - Photo data
     * @param {Object} user - Current user
     * @returns {HTMLElement} Photo element
     */
    createPhotoElement(photo, user) {
        const div = document.createElement('div');
        div.className = 'photo-item';
        div.dataset.photoId = photo.id;
        
        // Check if photo is part of a series
        const isSeries = photo.series && photo.series.length > 1;
        
        // Create image element 
        const img = document.createElement('img');
        img.src = photo.image_url || photo.url || photo.thumbnail_url;
        img.alt = photo.title || 'Photo';
        
        // Create overlay structure - context dependent
        const overlay = document.createElement('div');
        overlay.className = 'photo-overlay';
        
        // Context-specific overlay content
        const overlayContent = this.createOverlayContent(photo, user);
        overlay.innerHTML = overlayContent;
        
        // Assemble the photo item
        div.appendChild(img);
        
        if (isSeries) {
            const seriesIndicator = document.createElement('div');
            seriesIndicator.className = 'series-indicator';
            seriesIndicator.textContent = `${photo.series.length} photos`;
            div.appendChild(seriesIndicator);
        }
        
        div.appendChild(overlay);
        
        // Add interaction handlers
        div.addEventListener('click', () => {
            this.handlePhotoClick(photo, isSeries);
        });
        
        // Add context menu for own photos
        if (this.isOwnPhoto(photo, user)) {
            div.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.showPhotoContextMenu(e, photo);
            });
        }
        
        return div;
    }
    
    /**
     * Create overlay content based on display context
     * @param {Object} photo - Photo data
     * @param {Object} user - Current user
     * @returns {string} HTML content for overlay
     */
    createOverlayContent(photo, user) {
        const isOwnPhoto = this.isOwnPhoto(photo, user);
        
        switch (this.displayContext) {
            case 'home':
                // Home feed: Show photographer unless it's your own photo
                if (isOwnPhoto) {
                    return `
                        <div class="photo-info">
                            <div class="photo-title">${photo.title || ''}</div>
                            <div class="photo-time">${this.formatTimeAgo(photo.upload_date)}</div>
                        </div>
                    `;
                } else {
                    return `
                        <div class="photo-photographer">${photo.photographer_name || photo.username || 'Unknown'}</div>
                        <div class="photo-location">${photo.location || ''}</div>
                        <div class="photo-time">${this.formatTimeAgo(photo.upload_date)}</div>
                    `;
                }
                
            case 'discovery':
                // Discovery: Always show photographer and encourage following
                return `
                    <div class="photo-photographer">${photo.photographer_name || photo.username || 'Unknown'}</div>
                    <div class="photo-location">${photo.location || ''}</div>
                    <div class="discovery-actions">
                        <button class="btn-follow" data-photographer="${photo.user_id}">Follow</button>
                    </div>
                `;
                
            case 'portfolio':
                // Portfolio: Minimal info, focus on the work
                return `
                    <div class="photo-title">${photo.title || ''}</div>
                    <div class="photo-technical">${photo.camera || ''} ${photo.settings || ''}</div>
                `;
                
            case 'photographers':
                // Photographer profiles: Show technical details
                return `
                    <div class="photo-photographer">${photo.photographer_name || photo.username || 'Unknown'}</div>
                    <div class="photo-technical">${photo.camera || ''}</div>
                    <div class="photo-location">${photo.location || ''}</div>
                `;
                
            default:
                return `
                    <div class="photo-photographer">${photo.photographer_name || photo.username || 'Unknown'}</div>
                    <div class="photo-location">${photo.location || ''}</div>
                `;
        }
    }
    
    /**
     * Check if photo belongs to current user
     * @param {Object} photo - Photo data
     * @param {Object} user - Current user
     * @returns {boolean}
     */
    isOwnPhoto(photo, user) {
        return photo.user_id === user?.uid || 
               photo.photographer_id === user?.uid ||
               photo.username === user?.email;
    }
    
    /**
     * Format time ago string
     * @param {string} dateString - ISO date string
     * @returns {string} Formatted time ago
     */
    formatTimeAgo(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
        
        return date.toLocaleDateString();
    }
    
    /**
     * Handle photo click events
     * @param {Object} photo - Photo data
     * @param {boolean} isSeries - Whether photo is part of series
     */
    handlePhotoClick(photo, isSeries) {
        // Emit custom event for the main app to handle
        const event = new CustomEvent('photoClicked', {
            detail: { photo, isSeries, context: this.displayContext }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Show context menu for photo actions (edit/delete)
     * @param {Event} e - Right-click event
     * @param {Object} photo - Photo data
     */
    showPhotoContextMenu(e, photo) {
        // Emit custom event for context menu
        const event = new CustomEvent('photoContextMenu', {
            detail: { photo, x: e.clientX, y: e.clientY }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Show empty state based on context
     */
    showEmptyState() {
        const emptyState = document.getElementById('emptyState');
        if (!emptyState) return;
        
        const messages = {
            home: {
                title: 'Your feed is empty',
                message: 'Follow photographers to see their latest work',
                action: 'Discover Photographers'
            },
            discovery: {
                title: 'Discover new work',
                message: 'Explore photographers and find inspiration',
                action: 'View All Photos'
            },
            portfolio: {
                title: 'No portfolio photos',
                message: 'Mark photos as portfolio to showcase your best work',
                action: 'Upload Photo'
            },
            photographers: {
                title: 'No photographers yet',
                message: 'Be the first to join the community',
                action: 'Upload Photo'
            }
        };
        
        const config = messages[this.displayContext] || messages.home;
        
        emptyState.innerHTML = `
            <h2>${config.title}</h2>
            <p>${config.message}</p>
            <button class="btn-primary">${config.action}</button>
        `;
        
        emptyState.classList.remove('hidden');
    }
    
    /**
     * Show/hide grid loading state
     * @param {boolean} show - Whether to show loading
     */
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
     * Add a new photo to the display
     * @param {Object} photo - New photo data
     * @param {Object} user - Current user
     * @param {HTMLElement} grid - Grid container
     */
    prependNewPhoto(photo, user, grid) {
        // Create photo element with initial hiding
        const item = this.createPhotoElement(photo, user);
        item.style.opacity = '0';
        item.style.visibility = 'hidden';
        
        // Add to beginning of grid
        if (grid) {
            grid.prepend(item);
            
            // Add to masonry with smooth reveal
            if (this.masonry) {
                this.masonry.addItem(item);
                
                // Reveal the new item with animation
                setTimeout(() => {
                    item.style.visibility = 'visible';
                    item.style.opacity = '1';
                    item.style.transition = 'opacity 0.5s ease';
                }, 200);
            }
        }
        
        // Hide empty state if it was showing
        document.getElementById('emptyState')?.classList.add('hidden');
    }
}

export default PhotoDisplay;
