// Lumen Photo Viewer with Series Support
// Glass-inspired implementation with improvements

export class PhotoViewer {
    constructor() {
        this.currentPhoto = 0;
        this.currentSeries = [];
        this.isStripMode = false;
        this.stripMargin = 30;
        this.maxSeriesPhotos = 5;
        this.allPhotos = [];
        this.currentUserPhotos = [];
        this.navigationContext = null;
        this.previousMode = null; // Remember what mode we were in before opening
        
        this.initElements();
        this.bindEvents();
    }

    initElements() {
        // Create viewer DOM if it doesn't exist
        if (!document.getElementById('enhancedPhotoViewer')) {
            this.createViewerDOM();
        }
        
        this.viewer = document.getElementById('enhancedPhotoViewer');
        this.mainPhoto = document.getElementById('mainPhotoImg');
        this.seriesStrip = document.getElementById('seriesStrip');
        this.stripContainer = document.getElementById('stripContainer');
        this.photoInfo = document.getElementById('photoInfoPanel');
        this.photographerName = document.getElementById('viewerPhotographerName');
        this.photographerAvatar = document.getElementById('viewerPhotographerAvatar');
        this.closeBtn = document.getElementById('viewerCloseBtn');
        this.prevBtn = document.getElementById('prevPhotoBtn');
        this.nextBtn = document.getElementById('nextPhotoBtn');
        this.infoBtn = document.getElementById('infoToggleBtn');
        this.stripModeBtn = document.getElementById('stripModeBtn');
    }

    createViewerDOM() {
        const viewerHTML = `
            <div id="enhancedPhotoViewer" class="enhanced-photo-viewer hidden">
                <!-- Header with photographer info -->
                <div class="viewer-header">
                    <div class="photographer-info">
                        <div class="photographer-avatar">
                            <img id="viewerPhotographerAvatar" src="" alt="Avatar">
                        </div>
                        <a href="#" id="viewerPhotographerName" class="photographer-name"></a>
                    </div>
                    <div class="viewer-controls">
                        <button class="control-btn" id="stripModeBtn" title="Strip view - See all photos vertically">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="4"/>
                                <rect x="3" y="10" width="18" height="4"/>
                                <rect x="3" y="17" width="18" height="4"/>
                            </svg>
                        </button>
                        <button class="control-btn" id="infoToggleBtn" title="Photo info">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <path d="M12 16v-4M12 8h.01"/>
                            </svg>
                        </button>
                        <button class="control-btn" id="viewerCloseBtn" title="Close">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/>
                                <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- Main Photo Display -->
                <div class="photo-display" id="photoDisplay">
                    <button class="nav-arrow prev" id="prevPhotoBtn">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="15 18 9 12 15 6"/>
                        </svg>
                    </button>
                    <img id="mainPhotoImg" src="" alt="" class="main-photo">
                    <button class="nav-arrow next" id="nextPhotoBtn">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="9 18 15 12 9 6"/>
                        </svg>
                    </button>
                </div>

                <!-- Vertical Strip Container -->
                <div class="strip-container" id="stripContainer"></div>

                <!-- Photo Info Panel -->
                <div class="photo-info-panel hidden" id="photoInfoPanel">
                    <h3 class="photo-title" id="photoTitle">Untitled</h3>
                    <p class="photo-description" id="photoDescription"></p>
                    <div class="photo-metadata">
                        <span class="metadata-item" id="photoCamera"></span>
                        <span class="metadata-item" id="photoSettings"></span>
                    </div>
                </div>

                <!-- Series Thumbnails -->
                <div class="series-strip hidden" id="seriesStrip"></div>

                <!-- Series Indicator -->
                <div class="series-indicator hidden" id="seriesIndicator">
                    <span id="seriesCount">1 / 1</span>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', viewerHTML);
        this.addViewerStyles();
    }

    addViewerStyles() {
        if (document.getElementById('photoViewerStyles')) return;
        
        const styles = `
            <style id="photoViewerStyles">
                .enhanced-photo-viewer {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100vh;
                    background-color: #0a0a0a;
                    z-index: 2000;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }

                .enhanced-photo-viewer.hidden {
                    display: none;
                }

                .viewer-header {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    padding: 20px;
                    background: linear-gradient(to bottom, rgba(0,0,0,0.8) 0%, transparent 100%);
                    z-index: 10;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .photographer-info {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                }

                .photographer-avatar {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    overflow: hidden;
                    background: #333;
                }

                .photographer-avatar img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }

                .photographer-name {
                    font-family: 'Montserrat', sans-serif;
                    font-weight: 500;
                    font-size: 16px;
                    color: #ffffff;
                    text-decoration: none;
                }

                .photographer-name:hover {
                    text-decoration: underline;
                }

                .viewer-controls {
                    display: flex;
                    gap: 16px;
                }

                .control-btn {
                    background: none;
                    border: none;
                    color: #ffffff;
                    cursor: pointer;
                    padding: 8px;
                    transition: opacity 0.2s;
                    opacity: 0.8;
                }

                .control-btn:hover {
                    opacity: 1;
                }

                .photo-display {
                    flex: 1;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    position: relative;
                    overflow: hidden;
                    padding: 80px 20px 120px;
                }

                .main-photo {
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain;
                    transition: opacity 0.3s ease;
                }

                .nav-arrow {
                    position: absolute;
                    top: 50%;
                    transform: translateY(-50%);
                    background: rgba(255,255,255,0.1);
                    border: none;
                    color: white;
                    padding: 20px 15px;
                    cursor: pointer;
                    transition: background 0.2s;
                    z-index: 5;
                }

                .nav-arrow:hover {
                    background: rgba(255,255,255,0.2);
                }

                .nav-arrow.prev {
                    left: 20px;
                }

                .nav-arrow.next {
                    right: 20px;
                }

                .nav-arrow.hidden {
                    display: none;
                }

                .series-strip {
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    padding: 20px;
                    background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 100%);
                    display: flex;
                    justify-content: center;
                    gap: 8px;
                    z-index: 10;
                    height: 100px;
                    align-items: center;
                }

                .series-thumb {
                    width: 60px;
                    height: 60px;
                    cursor: pointer;
                    opacity: 0.6;
                    transition: opacity 0.2s, transform 0.2s;
                    border: 2px solid transparent;
                    overflow: hidden;
                    border-radius: 4px;
                }

                .series-thumb.active {
                    opacity: 1;
                    border-color: #ffffff;
                    transform: scale(1.1);
                }

                .series-thumb:hover {
                    opacity: 0.9;
                    transform: scale(1.05);
                }

                .series-thumb img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }

                .series-indicator {
                    position: absolute;
                    bottom: 120px;
                    right: 20px;
                    background: rgba(0,0,0,0.7);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 14px;
                    backdrop-filter: blur(10px);
                }

                .enhanced-photo-viewer.strip-mode .photo-display {
                    display: none;
                }

                .strip-container {
                    display: none;
                    width: 100%;
                    height: 100vh;
                    overflow-y: auto;
                    overflow-x: hidden;
                    padding: 80px 20px 20px;
                }

                .enhanced-photo-viewer.strip-mode .strip-container {
                    display: block;
                }

                .enhanced-photo-viewer.strip-mode .series-strip {
                    display: none;
                }

                .strip-photo {
                    width: 100%;
                    margin-bottom: var(--strip-margin, 30px);
                    display: block;
                    cursor: pointer;
                }

                .strip-photo img {
                    width: 100%;
                    height: auto;
                    display: block;
                }

                .photo-info-panel {
                    position: absolute;
                    bottom: 120px;
                    left: 20px;
                    right: 20px;
                    max-width: 600px;
                    background: rgba(0,0,0,0.8);
                    padding: 20px;
                    border-radius: 8px;
                    backdrop-filter: blur(10px);
                }

                .photo-info-panel.hidden {
                    display: none;
                }

                .photo-title {
                    font-family: 'Montserrat', sans-serif;
                    font-size: 18px;
                    font-weight: 500;
                    margin: 0 0 8px 0;
                    color: #ffffff;
                }

                .photo-description {
                    font-size: 14px;
                    line-height: 1.6;
                    color: #cccccc;
                    margin: 0 0 12px 0;
                }

                .photo-metadata {
                    display: flex;
                    gap: 16px;
                    font-size: 12px;
                    color: #999;
                }

                @media (max-width: 768px) {
                    .series-thumb {
                        width: 50px;
                        height: 50px;
                    }

                    .nav-arrow {
                        padding: 15px 10px;
                    }

                    .strip-photo {
                        margin-bottom: 15px;
                    }
                }

                @media (orientation: landscape) and (max-height: 600px) {
                    .viewer-header {
                        padding: 10px 20px;
                    }

                    .photo-display {
                        padding: 60px 20px 80px;
                    }

                    .series-strip {
                        height: 80px;
                        padding: 10px;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    bindEvents() {
        // Viewer controls
        this.closeBtn?.addEventListener('click', () => this.close());
        this.prevBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.navigate(-1);
        });
        this.nextBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.navigate(1);
        });
        this.infoBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleInfo();
        });
        this.stripModeBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleStripMode();
        });

        // Click anywhere on photo to close (but not on controls)
        this.viewer?.addEventListener('click', (e) => {
            // Don't close if clicking on controls, info panel, or navigation
            if (e.target.closest('.viewer-controls') || 
                e.target.closest('.nav-arrow') ||
                e.target.closest('.photo-info-panel') ||
                e.target.closest('.series-strip') ||
                e.target.closest('.strip-container')) {
                return;
            }
            this.close();
        });

        // Keyboard navigation
        this.keyboardHandler = (e) => {
            if (!this.viewer.classList.contains('hidden')) {
                switch(e.key) {
                    case 'Escape':
                        this.close();
                        break;
                    case 'ArrowLeft':
                        this.navigate(-1);
                        break;
                    case 'ArrowRight':
                        this.navigate(1);
                        break;
                    case 'ArrowUp':
                        if (this.currentSeries.length > 1) {
                            this.toggleStripMode();
                        }
                        break;
                    case 'i':
                    case 'I':
                        this.toggleInfo();
                        break;
                }
            }
        };
        document.addEventListener('keydown', this.keyboardHandler);

        // Touch gestures
        this.setupTouchGestures();
    }

    setupTouchGestures() {
        let touchStartX = 0;
        let touchStartY = 0;
        
        this.viewer?.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });

        this.viewer?.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;
            
            if (Math.abs(deltaX) > Math.abs(deltaY)) {
                if (deltaX > 50) {
                    this.navigate(-1);
                } else if (deltaX < -50) {
                    this.navigate(1);
                }
            } else {
                if (deltaY > 50 && this.currentSeries.length > 1) {
                    this.toggleStripMode();
                }
            }
        });
    }

    open(photo, allPhotos = [], isSeries = false, navigationContext = null) {
        // Store navigation context and all photos for navigation
        this.navigationContext = navigationContext;
        this.allPhotos = allPhotos;
        
        // Determine if this is a series
        if (isSeries && photo.series) {
            this.currentSeries = photo.series.slice(0, this.maxSeriesPhotos);
            this.currentPhoto = 0;
            this.renderSeriesThumbs();
            document.getElementById('seriesIndicator')?.classList.remove('hidden');
        } else {
            // Find the correct index of the clicked photo in allPhotos
            this.currentPhoto = allPhotos.findIndex(p => p.id === photo.id);
            if (this.currentPhoto === -1) {
                // If photo not found in allPhotos, add it at the beginning
                this.allPhotos = [photo, ...allPhotos];
                this.currentPhoto = 0;
            }
            
            // Also find photos from the same user for user-specific navigation
            const userId = photo.user_id || photo.photographer_id;
            if (userId && allPhotos.length > 0) {
                this.currentUserPhotos = allPhotos.filter(p => 
                    (p.user_id || p.photographer_id) === userId
                );
                if (this.currentUserPhotos.length === 0) {
                    this.currentUserPhotos = [photo];
                }
            } else {
                this.currentUserPhotos = [photo];
            }
            this.currentSeries = allPhotos; // Use all photos as default navigation set
            
            // Hide series UI for single photos
            document.getElementById('seriesStrip')?.classList.add('hidden');
            document.getElementById('seriesIndicator')?.classList.add('hidden');
        }
        
        this.updateDisplay();
        this.viewer?.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.viewer?.classList.add('hidden');
        this.viewer?.classList.remove('strip-mode');
        this.isStripMode = false;
        document.body.style.overflow = '';
        this.photoInfo?.classList.add('hidden');
    }

    navigate(direction) {
        if (this.isStripMode) return;
        
        // Choose navigation set based on context
        let photos;
        let contextTitle = '';
        
        if (this.currentSeries.length > 1) {
            // Series navigation
            photos = this.currentSeries;
            contextTitle = 'in this series';
        } else if (this.navigationContext?.type === 'user_photos' || this.currentUserPhotos.length > 1) {
            // Same photographer navigation
            photos = this.currentUserPhotos;
            contextTitle = `by ${photos[0]?.photographer_name || photos[0]?.username || 'this photographer'}`;
        } else {
            // Default to all photos in current context
            photos = this.allPhotos;
            const contextMap = {
                'home': 'in your feed',
                'discover': 'in discover',
                'photographers': 'photographer profiles',
                'nearby': 'nearby photos',
                'portfolio': 'in your portfolio'
            };
            contextTitle = contextMap[this.navigationContext?.type] || 'in this view';
        }
        
        const newIndex = this.currentPhoto + direction;
        
        if (newIndex >= 0 && newIndex < photos.length) {
            this.currentPhoto = newIndex;
            this.updateDisplay();
            
            // Update context info in UI if needed
            this.updateNavigationHint(this.currentPhoto + 1, photos.length, contextTitle);
        }
    }

    updateNavigationHint(current, total, contextTitle) {
        // Update series indicator with context
        const indicator = document.getElementById('seriesCount');
        if (indicator) {
            indicator.textContent = `${current} / ${total} ${contextTitle}`;
        }
    }

    updateDisplay() {
        if (this.isStripMode) return;
        
        // Use the same logic as navigate() to get the correct photo array
        let photos;
        if (this.currentSeries.length > 1) {
            photos = this.currentSeries;
        } else if (this.navigationContext?.type === 'user_photos' || this.currentUserPhotos.length > 1) {
            photos = this.currentUserPhotos;
        } else {
            photos = this.allPhotos;
        }
        
        const photo = photos[this.currentPhoto];
        
        if (!photo) return;
        
        // Update main photo
        this.mainPhoto.src = photo.image_url || photo.url || photo.original_url || photo.thumbnail_url;
        this.mainPhoto.alt = photo.title || 'Photo';
        
        // Update photographer info
        this.photographerName.textContent = photo.photographer_name || photo.username || 'Unknown';
        this.photographerAvatar.src = photo.photographer_avatar || 
            `https://ui-avatars.com/api/?name=${encodeURIComponent(photo.photographer_name || 'U')}&background=4a90e2&color=fff`;
        
        // Update navigation visibility
        this.prevBtn?.classList.toggle('hidden', this.currentPhoto === 0);
        this.nextBtn?.classList.toggle('hidden', this.currentPhoto === photos.length - 1);
        
        // Update series indicator
        if (photos.length > 1) {
            const indicator = document.getElementById('seriesCount');
            if (indicator) {
                indicator.textContent = `${this.currentPhoto + 1} / ${photos.length}`;
            }
        }
        
        // Update active thumbnail
        this.updateActiveThumbnail();
        
        // Update photo info
        this.updatePhotoInfo(photo);
    }

    updatePhotoInfo(photo) {
        const title = document.getElementById('photoTitle');
        const description = document.getElementById('photoDescription');
        const camera = document.getElementById('photoCamera');
        const settings = document.getElementById('photoSettings');
        
        // Update title - handle empty titles better
        if (title) {
            title.textContent = photo.title || `Photo by ${photo.photographer_name || photo.username || 'Unknown'}`;
        }
        
        // Build description with photographer and model info
        if (description) {
            let descriptionText = '';
            
            // Add photo description if available
            if (photo.description) {
                descriptionText += photo.description;
            }
            
            // Add photographer info
            if (photo.photographer_name || photo.username) {
                const photographerName = photo.photographer_name || photo.username;
                if (descriptionText) descriptionText += '\n\n';
                descriptionText += `📸 Photographer: ${photographerName}`;
            }
            
            // Add model info (only if not empty)
            if (photo.model_name && photo.model_name.trim()) {
                descriptionText += `\n👤 Model: ${photo.model_name}`;
            }
            
            // Add location if available
            if (photo.location) {
                descriptionText += `\n📍 Location: ${photo.location}`;
            }
            
            description.textContent = descriptionText || 'No description available';
        }
        
        // Update camera info
        if (camera) {
            let cameraText = '';
            if (photo.camera || photo.camera_make) {
                cameraText = photo.camera || `${photo.camera_make} ${photo.camera_model || ''}`.trim();
            }
            if (photo.lens) {
                if (cameraText) cameraText += ' • ';
                cameraText += photo.lens;
            }
            camera.textContent = cameraText || '';
        }
        
        // Update technical settings
        if (settings) {
            const settingsText = [];
            if (photo.settings) {
                // Use pre-formatted settings string if available
                settingsText.push(photo.settings);
            } else {
                // Build from individual fields
                if (photo.focal_length) settingsText.push(`${photo.focal_length}mm`);
                if (photo.aperture) settingsText.push(`f/${photo.aperture}`);
                if (photo.shutter_speed) settingsText.push(photo.shutter_speed);
                if (photo.iso) settingsText.push(`ISO ${photo.iso}`);
            }
            settings.textContent = settingsText.join(' • ') || '';
        }
    }

    renderSeriesThumbs() {
        if (this.currentSeries.length <= 1) {
            this.seriesStrip?.classList.add('hidden');
            return;
        }
        
        this.seriesStrip.innerHTML = '';
        this.seriesStrip?.classList.remove('hidden');
        
        this.currentSeries.forEach((photo, index) => {
            const thumb = document.createElement('div');
            thumb.className = 'series-thumb';
            if (index === this.currentPhoto) {
                thumb.classList.add('active');
            }
            
            const img = document.createElement('img');
            img.src = photo.thumbnail_url || photo.image_url || photo.url;
            img.alt = `Photo ${index + 1}`;
            thumb.appendChild(img);
            
            thumb.addEventListener('click', () => {
                if (this.isStripMode) {
                    this.toggleStripMode();
                }
                this.currentPhoto = index;
                this.updateDisplay();
            });
            
            this.seriesStrip?.appendChild(thumb);
        });
    }

    updateActiveThumbnail() {
        const thumbs = this.seriesStrip?.querySelectorAll('.series-thumb');
        thumbs?.forEach((thumb, index) => {
            thumb.classList.toggle('active', index === this.currentPhoto);
        });
    }

    toggleStripMode() {
        // Get the current photo collection for strip mode
        let photos;
        if (this.currentSeries.length > 1) {
            photos = this.currentSeries;
        } else if (this.currentUserPhotos.length > 1) {
            photos = this.currentUserPhotos;
        } else if (this.allPhotos.length > 1) {
            photos = this.allPhotos;
        } else {
            // Not enough photos for strip mode
            return;
        }
        
        this.isStripMode = !this.isStripMode;
        
        if (this.isStripMode) {
            this.viewer?.classList.add('strip-mode');
            this.renderStrip(photos);
        } else {
            this.viewer?.classList.remove('strip-mode');
            this.updateDisplay();
        }
        
        // Update button tooltip
        const stripBtn = document.getElementById('stripModeBtn');
        if (stripBtn) {
            stripBtn.title = this.isStripMode ? 
                'Return to single photo view' : 
                'Strip view - See all photos vertically';
        }
    }

    renderStrip(photos = null) {
        if (!this.stripContainer) return;
        
        // Use provided photos or default to current series
        const photosToRender = photos || this.currentSeries;
        
        this.stripContainer.innerHTML = '';
        this.stripContainer.style.setProperty('--strip-margin', `${this.stripMargin}px`);
        
        photosToRender.forEach((photo, index) => {
            const stripPhoto = document.createElement('div');
            stripPhoto.className = 'strip-photo';
            
            const img = document.createElement('img');
            img.src = photo.image_url || photo.url || photo.original_url || photo.thumbnail_url;
            img.alt = photo.title || `Photo ${index + 1}`;
            stripPhoto.appendChild(img);
            
            stripPhoto.addEventListener('click', () => {
                this.currentPhoto = index;
                this.toggleStripMode();
            });
            
            this.stripContainer.appendChild(stripPhoto);
        });
    }

    toggleInfo() {
        this.photoInfo?.classList.toggle('hidden');
    }

    setStripMargin(margin) {
        this.stripMargin = margin;
        if (this.isStripMode && this.stripContainer) {
            this.stripContainer.style.setProperty('--strip-margin', `${margin}px`);
        }
    }
}

// Export for use in main app
export default PhotoViewer;