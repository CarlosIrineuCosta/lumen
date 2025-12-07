/* Series Module
 * Photo series/collections functionality
 * Uses Poor Man's Modules pattern with window.LumenSeries global
 */

window.LumenSeries = {
    // State
    series: [],
    currentSeries: null,
    container: null,
    seriesClickBound: false,
    
    // Show series page
    async show(container) {
        this.cacheContainer(container);
        if (!this.container) {
            console.error('Series view container not found');
            return;
        }

        this.ensureBaseLayout();
        await this.loadSeries();
    },

    cacheContainer(container) {
        if (container) {
            this.container = container;
        } else if (!this.container) {
            this.container = document.getElementById('series-view');
        }
    },

    ensureBaseLayout() {
        if (!this.container) return;

        if (!this.container.querySelector('.series-grid')) {
            this.container.innerHTML = `
                <section class="series-section">
                    <header class="series-header">
                        <h2>Featured Series</h2>
                        <p class="series-subtitle">Curated collections from the Lumen community</p>
                    </header>
                    <div class="series-grid"></div>
                </section>
            `;
        }

        if (!this.seriesClickBound) {
            this.container.addEventListener('click', (event) => {
                const card = event.target.closest('.series-card');
                if (card) {
                    const seriesId = parseInt(card.dataset.seriesId, 10);
                    if (!Number.isNaN(seriesId)) {
                        this.viewSeries(seriesId);
                    }
                }
            });
            this.seriesClickBound = true;
        }
    },
    
    // Load series from API
    async loadSeries() {
        try {
            const response = await LumenAPI.getSeries();
            this.series = response.series || [];
            this.renderSeries();
        } catch (error) {
            console.error('Failed to load series:', error);
            this.handleLoadError();
        }
    },
    
    // Handle series loading error with demo data
    handleLoadError() {
        this.series = [
            {
                id: 1,
                title: 'Urban Landscapes',
                description: 'A collection of cityscapes and urban photography',
                photographer_name: 'Alex Chen',
                photos: [
                    { id: 1, title: 'City Lights', thumbnail_path: 'https://picsum.photos/400/600?random=10' },
                    { id: 2, title: 'Urban Dawn', thumbnail_path: 'https://picsum.photos/400/500?random=11' },
                    { id: 3, title: 'Street Art', thumbnail_path: 'https://picsum.photos/400/700?random=12' },
                    { id: 4, title: 'Architecture', thumbnail_path: 'https://picsum.photos/400/550?random=13' }
                ]
            },
            {
                id: 2,
                title: 'Nature Portraits',
                description: 'Wildlife and nature photography from around the world',
                photographer_name: 'Sarah Johnson',
                photos: [
                    { id: 5, title: 'Forest Trail', thumbnail_path: 'https://picsum.photos/400/600?random=20' },
                    { id: 6, title: 'Mountain Lake', thumbnail_path: 'https://picsum.photos/400/500?random=21' },
                    { id: 7, title: 'Sunset Valley', thumbnail_path: 'https://picsum.photos/400/700?random=22' }
                ]
            },
            {
                id: 3,
                title: 'Portrait Series',
                description: 'Intimate portraits capturing human emotion',
                photographer_name: 'Michael Rodriguez',
                photos: [
                    { id: 8, title: 'Golden Hour', thumbnail_path: 'https://picsum.photos/400/600?random=30' },
                    { id: 9, title: 'Contemplation', thumbnail_path: 'https://picsum.photos/400/500?random=31' },
                    { id: 10, title: 'Joy', thumbnail_path: 'https://picsum.photos/400/700?random=32' },
                    { id: 11, title: 'Reflection', thumbnail_path: 'https://picsum.photos/400/550?random=33' },
                    { id: 12, title: 'Serenity', thumbnail_path: 'https://picsum.photos/400/650?random=34' }
                ]
            }
        ];
        this.renderSeries();
    },
    
    // Render series grid
    renderSeries() {
        this.ensureBaseLayout();
        const container = this.container?.querySelector('.series-grid');
        if (!container) return;
        
        container.innerHTML = this.series.map(series => `
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
        `).join('');
    },
    
    // View individual series
    viewSeries(seriesId) {
        const series = this.series.find(s => s.id === seriesId);
        if (!series) return;
        
        this.currentSeries = series;
        
        // Navigate to gallery with series filter
        LumenRouter.navigate('gallery');
        
        // Apply series filter after navigation
        setTimeout(() => {
            if (LumenGallery.filterBySeries) {
                LumenGallery.filterBySeries(seriesId);
            }
        }, 100);
    },
    
    // Get all photos from all series (for gallery integration)
    getAllPhotos() {
        const allPhotos = [];
        this.series.forEach(series => {
            series.photos.forEach(photo => {
                allPhotos.push({
                    ...photo,
                    series_id: series.id,
                    series_title: series.title,
                    user: { display_name: series.photographer_name }
                });
            });
        });
        return allPhotos;
    },
    
    // Get photos by series ID
    getPhotosBySeries(seriesId) {
        const series = this.series.find(s => s.id === seriesId);
        return series ? series.photos.map(photo => ({
            ...photo,
            series_id: series.id,
            series_title: series.title,
            user: { display_name: series.photographer_name }
        })) : [];
    }
};
