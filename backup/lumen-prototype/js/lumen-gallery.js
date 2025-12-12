// Lumen Gallery - Professional Photography Platform
// Focus: People-first discovery, not image browsing

class LumenGallery {
    constructor() {
        this.currentMode = 'latest';
        this.photos = [];
        this.page = 1;
        this.loading = false;
        this.hasMore = true;
        
        this.init();
    }
    
    init() {
        // Initialize Justified Gallery
        this.setupGallery();
        
        // Bind events
        this.bindEvents();
        
        // Load initial photos
        this.loadPhotos();
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
        // Simulate API call - replace with actual backend
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