/* Gallery Module
 * Photo gallery logic converted from Alpine.js to vanilla JavaScript
 * Integrates justifiedGallery + lightGallery for photo display
 * Uses Poor Man's Modules pattern with window.LumenGallery global
 */

window.LumenGallery = {
    // State
    initialized: false,
    photos: [],
    allPhotos: [],
    currentFilter: 'all',
    currentCategory: 'all',
    currentSort: 'latest',
    currentPage: 1,
    hasMore: false,
    totalPhotos: 0,
    loading: false,
    lightGalleryInstance: null,
    masonryInstance: null,
    managementMode: false, // Track if we're in photo management mode
    currentPhotoId: null,  // Track current photo being edited
    container: null,

    // Initialize gallery
    init(container) {
        this.cacheContainer(container);

        if (this.initialized) {
            // On subsequent route visits, ensure gallery stays in sync when data exists
            if (this.photos.length > 0) {
                this.renderGallery();
            }
            return;
        }

        this.initialized = true;
        this.setupEventListeners();
        this.loadPhotos();
    },

    cacheContainer(container) {
        if (container) {
            this.container = container;
        } else if (!this.container) {
            this.container = document.getElementById('photo-gallery');
        }
    },

    renderSkeleton() {
        if (window.LumenTemplates?.gallery?.loadingSkeleton) {
            return window.LumenTemplates.gallery.loadingSkeleton();
        }
        return '';
    },

    // Setup event listeners
    setupEventListeners() {
        // Filter buttons
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.filterBy(e.target.dataset.filter);
                this.updateFilterUI(e.target);
            });
        });

        // Category tabs
        document.querySelectorAll('[data-category]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.filterByCategory(e.target.dataset.category);
                this.updateCategoryUI(e.target);
            });
        });

        // Sort buttons
        document.querySelectorAll('[data-sort]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.sortBy(e.target.dataset.sort);
                this.updateSortUI(e.target);
            });
        });

        // Load more button
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                this.loadMorePhotos();
            });
        }

        // My Photos button
        const myPhotosBtn = document.getElementById('my-photos-toggle');
        if (myPhotosBtn) {
            myPhotosBtn.addEventListener('click', () => {
                this.toggleMyPhotos();
            });
        }

        // Edit photo modal event listeners
        this.setupEditModalListeners();

        // Infinite scroll
        this.setupInfiniteScroll();

        // Window resize handler for responsive gallery
        this.setupResizeHandler();
    },

    // Setup infinite scroll
    setupInfiniteScroll() {
        window.addEventListener('scroll', () => {
            if (this.loading || !this.hasMore) return;

            const scrollTop = window.pageYOffset;
            const windowHeight = window.innerHeight;
            const docHeight = document.documentElement.scrollHeight;

            if (scrollTop + windowHeight >= docHeight - 1000) {
                this.loadMorePhotos();
            }
        });
    },

    // Setup window resize handler for responsive gallery
    setupResizeHandler() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (this.masonryInstance && this.photos.length > 0) {
                    // Re-render gallery with new dimensions
                    this.renderGallery();
                }
            }, 250);
        });
    },

    // Load photos from API
    async loadPhotos() {
        if (this.loading) return;

        this.loading = true;
        this.showLoading();

        try {
            const response = await LumenAPI.getPhotos(this.currentPage);

            // Map backend response to frontend format
            const mappedPhotos = (response.photos || []).map(photo => ({
                id: photo.id,
                title: photo.title,
                description: photo.description,
                thumbnail_path: photo.thumbnail_url,
                file_path: photo.image_url,
                user: {
                    display_name: photo.photographer_name
                },
                like_count: photo.like_count,
                location_display: photo.location_display,
                upload_date: photo.upload_date
            }));

            if (this.currentPage === 1) {
                this.allPhotos = mappedPhotos;
                this.photos = [...mappedPhotos];
            } else {
                this.allPhotos = [...this.allPhotos, ...mappedPhotos];
            }

            this.totalPhotos = response.total_count || mappedPhotos.length;
            this.hasMore = response.has_more || false;

            this.applyCurrentFilters();
            this.renderGallery();

            console.log(`Loaded ${mappedPhotos.length} photos (${this.totalPhotos} total)`);

        } catch (error) {
            console.error('Failed to load photos:', error);
            this.handleLoadError();
        } finally {
            this.loading = false;
            this.hideLoading();
        }
    },

    // Load more photos (pagination)
    async loadMorePhotos() {
        if (this.loading || !this.hasMore) return;

        this.currentPage++;
        await this.loadPhotos();
    },

    // Handle photo loading error with demo data
    handleLoadError() {
        this.photos = [
            { id: 1, title: 'Demo Photo 1', thumbnail_path: 'https://picsum.photos/400/600?random=1', file_path: 'https://picsum.photos/1200/1800?random=1', user: { display_name: 'Demo User' } },
            { id: 2, title: 'Demo Photo 2', thumbnail_path: 'https://picsum.photos/400/500?random=2', file_path: 'https://picsum.photos/1200/1500?random=2', user: { display_name: 'Demo User' } },
            { id: 3, title: 'Demo Photo 3', thumbnail_path: 'https://picsum.photos/400/700?random=3', file_path: 'https://picsum.photos/1200/2100?random=3', user: { display_name: 'Demo User' } },
        ];
        this.allPhotos = [...this.photos];
        this.renderGallery();
    },

    // Render gallery with justifiedGallery
    renderGallery(container) {
        this.cacheContainer(container);
        const targetContainer = this.container;
        if (!targetContainer) return;

        // Clear existing content
        targetContainer.innerHTML = '';

        // Create photo elements
        this.photos.forEach((photo, index) => {
            const photoElement = this.createPhotoElement(photo, index);
            targetContainer.appendChild(photoElement);
        });

        // Initialize Masonry for proper column-based layout
        this.initializeMasonry(targetContainer);

        // Setup lightGallery after masonry is ready
        setTimeout(() => {
            this.initializeLightGallery();
        }, 300);
    },

    // Initialize Masonry for proper column-based layout
    initializeMasonry(container) {
        if (typeof Masonry === 'undefined') {
            console.warn('Masonry not available');
            return;
        }

        // Destroy existing instance
        if (this.masonryInstance) {
            this.masonryInstance.destroy();
            this.masonryInstance = null;
        }

        // Calculate column width based on container width (not viewport)
        // Account for the 20px padding on each side from CSS
        const containerPadding = 40; // 20px left + 20px right padding from .photo-gallery CSS
        const containerWidth = (container.offsetWidth || container.clientWidth || window.innerWidth) - containerPadding;
        const gutter = 10;
        let columnCount;

        // Target 3-5 columns depending on available space
        if (containerWidth >= 2200) { // Large available space
            columnCount = 5; // 5 columns
        } else if (containerWidth >= 1600) { // Medium-large space
            columnCount = 4; // 4 columns
        } else if (containerWidth >= 1000) { // Medium space
            columnCount = 3; // 3 columns
        } else { // Small space
            columnCount = 2; // 2 columns
        }

        // Calculate exact column width to fill entire container
        const totalGutterSpace = gutter * (columnCount - 1);
        const availableWidth = containerWidth - totalGutterSpace;
        const columnWidth = Math.floor(availableWidth / columnCount);

        // Apply column width to photo items via CSS
        const items = container.querySelectorAll('.photo-item');
        items.forEach(item => {
            item.style.width = `${columnWidth}px`;
            item.style.marginBottom = `${gutter}px`;
        });

        console.log(`Container: ${containerWidth}px, columnWidth: ${columnWidth}px, columns: ${columnCount}, gutters: ${totalGutterSpace}px`);

        // Initialize Masonry with calculated dimensions
        this.masonryInstance = new Masonry(container, {
            itemSelector: '.photo-item',
            columnWidth: columnWidth,
            gutter: gutter,
            horizontalOrder: true,
            fitWidth: true,  // Center the grid if there's extra space
            percentPosition: false // Use absolute positioning for better control
        });

        // Wait for images to load, then layout
        const images = container.querySelectorAll('.photo-item img');
        let loadedCount = 0;

        images.forEach(img => {
            if (img.complete) {
                loadedCount++;
            } else {
                img.addEventListener('load', () => {
                    loadedCount++;
                    // Re-layout after each image loads
                    this.masonryInstance.layout();
                });
            }
        });

        // Initial layout
        setTimeout(() => {
            this.masonryInstance.layout();
        }, 100);

        console.log('Masonry initialized with', images.length, 'photos');
    },

    // Create individual photo element with accessibility and proper attributes
    createPhotoElement(photo, index) {
        const div = document.createElement('div');
        div.className = 'photo-item';
        div.dataset.index = index;
        div.dataset.src = photo.file_path || photo.thumbnail_path;
        div.setAttribute('tabindex', '0');
        div.setAttribute('role', 'button');
        div.setAttribute('aria-label', `View photo: ${photo.title || 'Untitled'} by ${photo.user.display_name}`);

        // Apply CSS for masonry layout
        div.style.position = 'relative';
        div.style.marginBottom = '10px';
        div.style.cursor = 'pointer';
        div.style.overflow = 'hidden';
        div.style.borderRadius = '4px';

        const img = document.createElement('img');
        img.src = photo.file_path;
        img.alt = photo.title || 'Photo';
        img.loading = 'lazy';

        // Make image fill container width, maintain aspect ratio
        img.style.width = '100%';
        img.style.height = 'auto';
        img.style.display = 'block';

        img.addEventListener('load', () => {
            img.classList.add('loaded');
        });

        const overlay = document.createElement('div');
        overlay.className = 'photo-overlay';
        overlay.style.position = 'absolute';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.right = '0';
        overlay.style.bottom = '0';
        overlay.style.background = 'linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.4) 100%)';
        overlay.style.color = 'white';
        overlay.style.padding = '12px';
        overlay.style.display = 'flex';
        overlay.style.flexDirection = 'column';
        overlay.style.justifyContent = 'flex-end';
        overlay.style.opacity = '0';
        overlay.style.transition = 'opacity 0.3s ease';

        // Check if device is mobile for cleaner display
        const isMobile = window.innerWidth <= 768;

        if (!isMobile) {
            overlay.innerHTML = `
                <h3 style="font-size: 12px; font-weight: 500; margin: 0 0 3px 0; line-height: 1.2; opacity: 0.9;">${photo.title || 'Untitled'}</h3>
                <p style="font-size: 10px; font-weight: 400; margin: 0 0 1px 0; opacity: 0.7;">by ${photo.user.display_name}</p>
                ${photo.location_display ? `<p style="font-size: 9px; font-weight: 400; margin: 0; opacity: 0.6;">${photo.location_display}</p>` : ''}
                ${photo.like_count ? `<p style="font-size: 9px; font-weight: 400; margin: 1px 0 0 0; opacity: 0.6;">${photo.like_count} likes</p>` : ''}
            `;

            // Show overlay on hover with reduced opacity
            div.addEventListener('mouseenter', () => {
                overlay.style.opacity = '0.7';
            });

            div.addEventListener('mouseleave', () => {
                overlay.style.opacity = '0';
            });
        } else {
            // On mobile, only show title on hover and make it very subtle
            overlay.innerHTML = `
                <h3 style="font-size: 11px; font-weight: 400; margin: 0; line-height: 1.2; opacity: 0.8;">${photo.title || 'Untitled'}</h3>
            `;

            div.addEventListener('mouseenter', () => {
                overlay.style.opacity = '0.5';
            });

            div.addEventListener('mouseleave', () => {
                overlay.style.opacity = '0';
            });
        }

        div.appendChild(img);
        div.appendChild(overlay);

        // Add management overlay if in management mode
        this.addManagementOverlay(div, photo);

        return div;
    },

    // Initialize lightGallery with dynamic content
    initializeLightGallery() {
        if (typeof lightGallery === 'undefined') {
            console.warn('lightGallery not loaded');
            return;
        }

        const container = this.container || document.getElementById('photo-gallery');
        if (!container) return;

        // Destroy existing instance
        if (this.lightGalleryInstance) {
            this.lightGalleryInstance.destroy();
            this.lightGalleryInstance = null;
        }

        // Add data attributes to photo items for lightGallery
        container.querySelectorAll('.photo-item').forEach((item, index) => {
            const photo = this.photos[index];
            if (photo) {
                item.setAttribute('data-src', photo.file_path || photo.thumbnail_path);
                item.setAttribute('data-sub-html', `
                    <h4>${photo.title || 'Untitled'}</h4>
                    <p>by ${photo.user.display_name}</p>
                    ${photo.location_display ? `<p>${photo.location_display}</p>` : ''}
                `);
            }
        });

        // Initialize lightGallery
        this.lightGalleryInstance = lightGallery(container, {
            ...LumenConfig.gallery.lightbox,
            selector: '.photo-item',
            download: false,
            zoom: true,
            thumbnail: true,
            animateThumb: false,
            showThumbByDefault: false,
            // Mobile touch support
            swipeToClose: true,
            closable: true,
            escKey: true
        });

        // Add mobile tap-to-close functionality
        this.addMobileTapToClose();

        // Add keyboard support
        container.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                const focusedItem = document.activeElement;
                const index = Array.from(container.children).indexOf(focusedItem);
                if (index !== -1) {
                    e.preventDefault();
                    focusedItem.click();
                }
            }
        });
    },

    // Add mobile tap-to-close functionality
    addMobileTapToClose() {
        // Wait for lightGallery to be ready
        setTimeout(() => {
            const lgContainer = document.querySelector('.lg-container');
            if (!lgContainer) return;

            let tapCount = 0;
            let tapTimeout = null;

            // Check if device is mobile
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
                            ('ontouchstart' in window) ||
                            (window.innerWidth <= 768);

            if (isMobile) {
                const lgImage = lgContainer.querySelector('.lg-image');
                if (lgImage) {
                    lgImage.addEventListener('click', (e) => {
                        // Prevent default zoom behavior on mobile
                        if (e.target.tagName === 'IMG') {
                            e.preventDefault();
                            e.stopPropagation();

                            tapCount++;

                            if (tapTimeout) {
                                clearTimeout(tapTimeout);
                            }

                            // Single tap: show/hide caption and controls
                            if (tapCount === 1) {
                                tapTimeout = setTimeout(() => {
                                    this.toggleLightboxUI();
                                    tapCount = 0;
                                }, 300);
                            }
                            // Double tap: close lightbox
                            else if (tapCount === 2) {
                                clearTimeout(tapTimeout);
                                tapCount = 0;
                                this.lightGalleryInstance.closeGallery();
                            }
                        }
                    });
                }
            }
        }, 100);
    },

    // Toggle lightbox UI visibility
    toggleLightboxUI() {
        const lgContainer = document.querySelector('.lg-container');
        if (!lgContainer) return;

        const toolbar = lgContainer.querySelector('.lg-toolbar');
        const subHtml = lgContainer.querySelector('.lg-sub-html');
        const actions = lgContainer.querySelector('.lg-actions');

        const isHidden = toolbar?.style.opacity === '0';

        if (toolbar) {
            toolbar.style.opacity = isHidden ? '1' : '0';
            toolbar.style.transition = 'opacity 0.3s ease';
        }
        if (subHtml) {
            subHtml.style.opacity = isHidden ? '0.8' : '0';
            subHtml.style.transition = 'opacity 0.3s ease';
        }
        if (actions) {
            actions.style.opacity = isHidden ? '1' : '0';
            actions.style.transition = 'opacity 0.3s ease';
        }
    },


    // Filter photos by category tabs
    filterByCategory(category) {
        console.log('Filtering by category:', category);
        this.currentCategory = category;
        this.applyCurrentFilters();
        this.renderGallery();
    },

    // Filter photos by category
    filterBy(category) {
        console.log('Filtering by:', category);
        this.currentFilter = category;
        this.applyCurrentFilters();
        this.renderGallery();
    },

    // Sort photos
    sortBy(sortType) {
        console.log('Sorting by:', sortType);
        this.currentSort = sortType;
        this.applyCurrentFilters();
        this.renderGallery();
    },

    // Apply current filters and sorting
    applyCurrentFilters() {
        let filtered = [...this.allPhotos];

        // Apply category filter first
        if (this.currentCategory && this.currentCategory !== 'all') {
            filtered = filtered.filter(photo => photo.category === this.currentCategory);
        }

        // Apply secondary filter
        if (this.currentFilter === 'photographer') {
            const photographerCounts = {};
            this.allPhotos.forEach(photo => {
                const name = photo.user.display_name;
                photographerCounts[name] = (photographerCounts[name] || 0) + 1;
            });
            filtered = filtered.filter(photo => photographerCounts[photo.user.display_name] > 1);
        } else if (this.currentFilter === 'location') {
            filtered = filtered.filter(photo =>
                photo.location_display && !photo.location_display.includes('Test Location')
            );
        } else if (this.currentFilter === 'series') {
            // Show photos that are part of series collections
            if (window.LumenSeries) {
                filtered = LumenSeries.getAllPhotos();
            }
        }

        // Apply sort
        if (this.currentSort === 'latest') {
            filtered.sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date));
        } else if (this.currentSort === 'popular') {
            filtered.sort((a, b) => b.like_count - a.like_count);
        }

        this.photos = filtered;
        console.log(`Applied filters: ${filtered.length} photos shown`);
    },

    // Update filter UI
    updateFilterUI(activeButton) {
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.classList.remove('active');
        });
        activeButton.classList.add('active');
    },

    // Update category UI
    updateCategoryUI(activeButton) {
        document.querySelectorAll('[data-category]').forEach(btn => {
            btn.classList.remove('tab-active');
        });
        activeButton.classList.add('tab-active');
    },

    // Update sort UI
    updateSortUI(activeButton) {
        document.querySelectorAll('[data-sort]').forEach(btn => {
            btn.classList.remove('active');
        });
        activeButton.classList.add('active');
    },

    // Show loading state
    showLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = 'flex';
        }
    },

    // Hide loading state
    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = 'none';
        }
    },

    // Clear gallery (used on logout)
    clear() {
        this.photos = [];
        this.allPhotos = [];
        this.currentPage = 1;
        this.hasMore = false;

        const container = this.container || document.getElementById('photo-gallery');
        if (container) {
            container.innerHTML = '';
        }

        if (this.lightGalleryInstance) {
            this.lightGalleryInstance.destroy();
            this.lightGalleryInstance = null;
        }

        if (this.masonryInstance) {
            this.masonryInstance.destroy();
            this.masonryInstance = null;
        }
    },

    // Filter by specific series
    filterBySeries(seriesId) {
        if (window.LumenSeries) {
            this.allPhotos = LumenSeries.getPhotosBySeries(seriesId);
            this.photos = [...this.allPhotos];
            this.currentFilter = 'series';
            this.renderGallery();

            // Update UI
            document.querySelectorAll('[data-filter]').forEach(btn => {
                btn.classList.remove('active');
            });
            const seriesBtn = document.querySelector('[data-filter="series"]');
            if (seriesBtn) seriesBtn.classList.add('active');
        }
    },

    // Refresh gallery (reload from API)
    async refresh() {
        this.clear();
        this.currentPage = 1;
        await this.loadPhotos();
    },

    // Photo editing functionality
    currentEditingPhoto: null,

    // Setup photo modal with edit functionality
    setupPhotoModal(photo, isOwner = false) {
        const modal = document.getElementById('photo-modal');
        const modalImage = document.getElementById('modal-image');
        const editBtn = document.getElementById('edit-photo-btn');
        const deleteBtn = document.getElementById('delete-photo-btn');

        if (modalImage && photo) {
            modalImage.src = photo.image_url;
            modalImage.alt = photo.title || 'Photo';
        }

        // Show/hide edit/delete buttons based on ownership
        if (editBtn && deleteBtn) {
            if (isOwner) {
                editBtn.style.display = 'inline-block';
                deleteBtn.style.display = 'inline-block';

                // Setup edit button handler
                editBtn.onclick = () => this.openEditModal(photo);
                deleteBtn.onclick = () => this.deletePhoto(photo.id);
            } else {
                editBtn.style.display = 'none';
                deleteBtn.style.display = 'none';
            }
        }

        // Store current photo for reference
        this.currentEditingPhoto = photo;

        if (modal) {
            modal.classList.remove('hidden');
        }
    },

    // Open photo edit modal
    openEditModal(photo) {
        const editModal = document.getElementById('photo-edit-modal');
        const photoModal = document.getElementById('photo-modal');

        // Hide photo modal
        if (photoModal) {
            photoModal.classList.add('hidden');
        }

        // Populate edit form with current values
        this.populateEditForm(photo);

        // Show edit modal
        if (editModal) {
            editModal.classList.remove('hidden');
        }

        this.setupEditModalHandlers(photo);
    },

    // Populate edit form with photo data
    populateEditForm(photo) {
        document.getElementById('edit-photo-title').value = photo.title || '';
        document.getElementById('edit-photo-description').value = photo.description || '';
        document.getElementById('edit-photo-tags').value = (photo.user_tags || []).join(', ');
        document.getElementById('edit-photo-public').checked = photo.is_public || false;
        document.getElementById('edit-photo-portfolio').checked = photo.is_portfolio || false;
        document.getElementById('edit-content-rating').value = photo.content_rating || 'general';
    },

    // Setup edit modal event handlers
    setupEditModalHandlers(photo) {
        const editModal = document.getElementById('photo-edit-modal');
        const closeBtn = document.getElementById('photo-edit-close');
        const cancelBtn = document.getElementById('cancel-photo-edit');
        const form = document.getElementById('photo-edit-form');

        // Close handlers
        const closeModal = () => {
            if (editModal) {
                editModal.classList.add('hidden');
            }
        };

        if (closeBtn) closeBtn.onclick = closeModal;
        if (cancelBtn) cancelBtn.onclick = closeModal;

        // Click outside to close
        if (editModal) {
            editModal.onclick = (e) => {
                if (e.target === editModal) {
                    closeModal();
                }
            };
        }

        // Form submit handler
        if (form) {
            form.onsubmit = (e) => {
                e.preventDefault();
                this.savePhotoChanges(photo.id);
            };
        }
    },

    // Save photo changes
    async savePhotoChanges(photoId) {
        try {
            const formData = new FormData(document.getElementById('photo-edit-form'));
            const data = {
                title: formData.get('title') || null,
                description: formData.get('description') || null,
                user_tags: formData.get('user_tags') ?
                    formData.get('user_tags').split(',').map(tag => tag.trim()).filter(tag => tag) : [],
                is_public: formData.get('is_public') === 'on',
                is_portfolio: formData.get('is_portfolio') === 'on',
                content_rating: formData.get('content_rating') || 'general'
            };

            const response = await LumenAPI.updatePhoto(photoId, data);

            if (response) {
                LumenUtils.showSuccess('Photo updated successfully!');

                // Close edit modal
                document.getElementById('photo-edit-modal').classList.add('hidden');

                // Update photo in current data
                const photoIndex = this.photos.findIndex(p => p.id === photoId);
                if (photoIndex !== -1) {
                    this.photos[photoIndex] = {...this.photos[photoIndex], ...data};
                }

                // Refresh gallery if needed
                this.refresh();
            }
        } catch (error) {
            console.error('Error updating photo:', error);
            LumenUtils.showError('Failed to update photo. Please try again.');
        }
    },

    // Delete photo
    async deletePhoto(photoId) {
        if (!confirm('Are you sure you want to delete this photo? This action cannot be undone.')) {
            return;
        }

        try {
            await LumenAPI.deletePhoto(photoId);
            LumenUtils.showSuccess('Photo deleted successfully!');

            // Close modal
            const photoModal = document.getElementById('photo-modal');
            if (photoModal) {
                photoModal.classList.add('hidden');
            }

            // Remove from local data
            this.photos = this.photos.filter(p => p.id !== photoId);
            this.allPhotos = this.allPhotos.filter(p => p.id !== photoId);

            // Refresh gallery
            this.refresh();
        } catch (error) {
            console.error('Error deleting photo:', error);
            LumenUtils.showError('Failed to delete photo. Please try again.');
        }
    },

    // My Photos Management Functions
    toggleMyPhotos() {
        this.managementMode = !this.managementMode;
        const btn = document.getElementById('my-photos-toggle');

        if (this.managementMode) {
            // Switch to management mode - show only user's photos
            this.currentFilter = 'my_photos';
            btn.classList.add('btn-active');
            btn.title = 'Show All Photos';
            this.loadMyPhotos();
        } else {
            // Switch back to public gallery
            this.currentFilter = 'all';
            btn.classList.remove('btn-active');
            btn.title = 'My Photos';
            this.loadPhotos();
        }
    },

    async loadMyPhotos() {
        if (!window.LumenAuth?.user) {
            LumenUtils.showError('Please log in to view your photos');
            return;
        }

        try {
            this.loading = true;
            this.showLoading();

            const response = await LumenAPI.getMyPhotos({
                page: this.currentPage,
                limit: 20,
                category: this.currentCategory !== 'all' ? this.currentCategory : null
            });

            if (this.currentPage === 1) {
                this.photos = response.photos || [];
                this.allPhotos = response.photos || [];
            } else {
                this.photos = [...this.photos, ...(response.photos || [])];
                this.allPhotos = [...this.allPhotos, ...(response.photos || [])];
            }

            this.totalPhotos = response.total || 0;
            this.hasMore = response.has_more || false;

            this.renderGallery();
        } catch (error) {
            console.error('Error loading my photos:', error);
            LumenUtils.showError('Failed to load your photos');
        } finally {
            this.loading = false;
            this.hideLoading();
        }
    },

    setupEditModalListeners() {
        // Edit photo modal event listeners
        const editSaveBtn = document.getElementById('edit-photo-save');
        const editCancelBtn = document.getElementById('edit-photo-cancel');
        const editDeleteBtn = document.getElementById('edit-photo-delete');

        if (editSaveBtn) {
            editSaveBtn.addEventListener('click', () => this.savePhotoEdits());
        }

        if (editCancelBtn) {
            editCancelBtn.addEventListener('click', () => this.closeEditModal());
        }

        if (editDeleteBtn) {
            editDeleteBtn.addEventListener('click', () => this.confirmDeletePhoto());
        }
    },

    openPhotoEditModal(photo) {
        this.currentPhotoId = photo.id;
        const modal = document.getElementById('edit-photo-modal');

        // Populate form fields
        document.getElementById('edit-photo-title').value = photo.title || '';
        document.getElementById('edit-photo-category').value = photo.category || 'portrait';
        document.getElementById('edit-photo-tags').value = photo.user_tags ? photo.user_tags.join(', ') : '';
        document.getElementById('edit-photo-description').value = photo.description || '';
        document.getElementById('edit-photo-public').checked = photo.is_public !== false;

        // Load and populate series dropdown
        this.loadSeriesOptions();

        // Show modal
        if (modal && typeof modal.showModal === 'function') {
            modal.showModal();
        }
    },

    async loadSeriesOptions() {
        const select = document.getElementById('edit-photo-series');
        if (!select) {
            console.error('Series dropdown not found');
            return;
        }

        // Show loading state
        const originalDisabled = select.disabled;
        select.disabled = true;

        // Add loading option
        const loadingOption = document.createElement('option');
        loadingOption.value = '';
        loadingOption.textContent = 'Loading series...';
        loadingOption.disabled = true;

        // Clear existing options and add loading state
        select.innerHTML = '';
        select.appendChild(loadingOption);

        try {
            const series = await LumenAPI.getSeries();

            // Clear loading state
            select.innerHTML = '';

            // Add default "No series" option
            const noSeriesOption = document.createElement('option');
            noSeriesOption.value = '';
            noSeriesOption.textContent = 'No series';
            select.appendChild(noSeriesOption);

            // Add series options
            if (series && series.length > 0) {
                series.forEach(s => {
                    const option = document.createElement('option');
                    option.value = s.id;
                    option.textContent = s.title;
                    select.appendChild(option);
                });
            }

            // Add "Create new series" option
            const createSeriesOption = document.createElement('option');
            createSeriesOption.value = '__create_new__';
            createSeriesOption.textContent = '+ Create new series';
            createSeriesOption.style.fontStyle = 'italic';
            createSeriesOption.style.color = '#8b5cf6';
            select.appendChild(createSeriesOption);

            // Handle selection change
            select.removeEventListener('change', this.handleSeriesChange);
            this.handleSeriesChange = (e) => {
                if (e.target.value === '__create_new__') {
                    e.target.value = ''; // Reset to "No series"
                    this.showCreateSeriesModal();
                }
            };
            select.addEventListener('change', this.handleSeriesChange);

        } catch (error) {
            console.error('Error loading series:', error);

            // Show error state
            select.innerHTML = '';

            const errorOption = document.createElement('option');
            errorOption.value = '';
            errorOption.textContent = 'Failed to load series';
            errorOption.disabled = true;
            select.appendChild(errorOption);

            const retryOption = document.createElement('option');
            retryOption.value = '__retry__';
            retryOption.textContent = 'Retry loading series';
            retryOption.style.fontStyle = 'italic';
            select.appendChild(retryOption);

            // Handle retry
            select.removeEventListener('change', this.handleSeriesRetry);
            this.handleSeriesRetry = (e) => {
                if (e.target.value === '__retry__') {
                    this.loadSeriesOptions();
                }
            };
            select.addEventListener('change', this.handleSeriesRetry);

            // Show user-friendly error message
            if (window.LumenUtils) {
                LumenUtils.showError('Failed to load series. You can retry or continue without selecting a series.');
            }
        } finally {
            select.disabled = originalDisabled;
        }
    },

    async savePhotoEdits() {
        if (!this.currentPhotoId) return;

        try {
            const formData = new FormData();
            formData.append('title', document.getElementById('edit-photo-title').value);
            formData.append('category', document.getElementById('edit-photo-category').value);
            formData.append('user_tags', document.getElementById('edit-photo-tags').value);
            formData.append('description', document.getElementById('edit-photo-description').value);
            formData.append('is_public', document.getElementById('edit-photo-public').checked);

            const seriesId = document.getElementById('edit-photo-series').value;
            if (seriesId) {
                formData.append('series_id', seriesId);
            }

            await LumenAPI.updatePhoto(this.currentPhotoId, formData);

            LumenUtils.showSuccess('Photo updated successfully!');
            this.closeEditModal();

            // Refresh gallery if in management mode
            if (this.managementMode) {
                this.currentPage = 1;
                this.loadMyPhotos();
            }
        } catch (error) {
            console.error('Error updating photo:', error);
            LumenUtils.showError('Failed to update photo. Please try again.');
        }
    },

    closeEditModal() {
        const modal = document.getElementById('edit-photo-modal');
        if (modal && typeof modal.close === 'function') {
            modal.close();
        }
        this.currentPhotoId = null;
    },

    confirmDeletePhoto() {
        if (!this.currentPhotoId) return;

        if (confirm('Are you sure you want to delete this photo? This action cannot be undone.')) {
            this.deletePhotoById(this.currentPhotoId);
        }
    },

    async deletePhotoById(photoId) {
        try {
            await LumenAPI.deletePhoto(photoId);

            LumenUtils.showSuccess('Photo deleted successfully!');
            this.closeEditModal();

            // Remove from local data
            this.photos = this.photos.filter(p => p.id !== photoId);
            this.allPhotos = this.allPhotos.filter(p => p.id !== photoId);

            // Refresh gallery
            this.renderGallery();
        } catch (error) {
            console.error('Error deleting photo:', error);
            LumenUtils.showError('Failed to delete photo. Please try again.');
        }
    },

    // Add management overlay to photo cards when in management mode
    addManagementOverlay(photoCard, photo) {
        if (!this.managementMode) return;

        const overlay = document.createElement('div');
        overlay.className = 'absolute inset-0 glass opacity-0 hover:opacity-100 transition-opacity duration-200 flex justify-end items-start p-2 gap-2';
        overlay.innerHTML = `
            <button class="btn btn-circle btn-sm glass border-white/20 hover:bg-white/20"
                    onclick="LumenGallery.openPhotoEditModal(${JSON.stringify(photo).replace(/"/g, '&quot;')})"
                    title="Edit Photo">
                <svg class="w-4 h-4" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708L10.5 8.207l-3-3L12.146.146zM11.207 9L8 5.793 1.146 12.646a.5.5 0 0 0-.146.354v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .354-.146L11.207 9zM4 15.5a.5.5 0 0 1-.5-.5v-3a.5.5 0 0 1 .146-.354L8.793 6.5 12.5 10.207l-5.147 5.147a.5.5 0 0 1-.353.146H4z"/>
                </svg>
            </button>
            <button class="btn btn-circle btn-sm glass border-red-400/20 bg-red-500/20 text-red-300 hover:bg-red-500/30"
                    onclick="LumenGallery.confirmDeletePhotoCard('${photo.id}')"
                    title="Delete Photo">
                <svg class="w-4 h-4" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                    <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                </svg>
            </button>
        `;

        photoCard.style.position = 'relative';
        photoCard.appendChild(overlay);
    },

    confirmDeletePhotoCard(photoId) {
        if (confirm('Are you sure you want to delete this photo? This action cannot be undone.')) {
            this.deletePhotoById(photoId);
        }
    },

    // Show modal to create a new series
    showCreateSeriesModal() {
        const modal = document.createElement('dialog');
        modal.className = 'glass-modal';
        modal.innerHTML = `
            <div class="glass-modal-box">
                <h3>Create New Series</h3>
                <form id="create-series-form" class="space-y-4">
                    <div>
                        <label for="new-series-title" class="block text-sm font-medium mb-2">Series Title</label>
                        <input type="text" id="new-series-title" name="title" required
                               class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500"
                               placeholder="Enter series title">
                    </div>
                    <div>
                        <label for="new-series-description" class="block text-sm font-medium mb-2">Description (Optional)</label>
                        <textarea id="new-series-description" name="description" rows="3"
                                  class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500"
                                  placeholder="Describe your series"></textarea>
                    </div>
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" id="cancel-create-series"
                                class="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition">
                            Cancel
                        </button>
                        <button type="submit" id="create-series-btn"
                                class="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg transition">
                            Create Series
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        // Setup event listeners
        const form = modal.querySelector('#create-series-form');
        const cancelBtn = modal.querySelector('#cancel-create-series');
        const createBtn = modal.querySelector('#create-series-btn');
        const titleInput = modal.querySelector('#new-series-title');

        const closeModal = () => {
            document.body.removeChild(modal);
        };

        cancelBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const title = titleInput.value.trim();
            const description = modal.querySelector('#new-series-description').value.trim();

            if (!title) {
                if (window.LumenUtils) {
                    LumenUtils.showError('Series title is required');
                }
                return;
            }

            // Disable button during creation
            createBtn.disabled = true;
            createBtn.textContent = 'Creating...';

            try {
                const response = await LumenAPI.createSeries({ title, description });

                if (response && response.id) {
                    if (window.LumenUtils) {
                        LumenUtils.showSuccess('Series created successfully!');
                    }

                    // Reload series options and select the new series
                    await this.loadSeriesOptions();
                    const select = document.getElementById('edit-photo-series');
                    if (select) {
                        select.value = response.id;
                    }

                    closeModal();
                } else {
                    throw new Error('Failed to create series');
                }
            } catch (error) {
                console.error('Error creating series:', error);
                if (window.LumenUtils) {
                    LumenUtils.showError('Failed to create series. Please try again.');
                }
            } finally {
                createBtn.disabled = false;
                createBtn.textContent = 'Create Series';
            }
        });

        // Show modal and focus on title input
        modal.showModal();
        setTimeout(() => titleInput.focus(), 100);
    }
};
