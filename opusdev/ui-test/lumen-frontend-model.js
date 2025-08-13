// Lumen Frontend Data Model & API Pseudo-Code
// This file demonstrates the frontend architecture without touching the backend

class LumenDataModel {
    constructor() {
        this.currentUser = null;
        this.photos = [];
        this.photographers = [];
        this.appreciations = new Map(); // photo_id -> count (private)
        this.notifications = [];
    }
    
    // ============== PSEUDO DATABASE CALLS ==============
    // These would be replaced with actual API calls to FastAPI backend
    
    async getHomeFeed() {
        // PSEUDO: GET /api/feed/home
        // Returns photos from followed photographers, chronological
        return {
            photos: [
                {
                    id: 'photo_001',
                    photographer_id: 'user_123',
                    photographer_name: 'Xinyi Deng',
                    photographer_avatar: '/avatars/xinyi.jpg',
                    image_url: '/photos/full/photo_001.jpg',
                    thumbnail_url: '/photos/thumb/photo_001.jpg',
                    title: 'Morning Light',
                    uploaded_at: '2025-01-15T10:30:00Z',
                    tags: ['Urban', 'Portrait', 'Natural Light'],
                    properties: {
                        color_mode: 'B&W',
                        aspect_ratio: '3:2',
                        camera: 'Leica M10',
                        lens: '50mm f/1.4'
                    },
                    appreciation_count: null, // Hidden from public
                    has_appreciated: false,
                    comments_count: 3
                }
            ],
            next_cursor: 'cursor_xyz'
        };
    }
    
    async getDiscoverFeed(filters = {}) {
        // PSEUDO: GET /api/feed/discover
        // Params: tags[], time_range, location_radius
        return {
            photos: [
                {
                    id: 'photo_002',
                    photographer_id: 'user_456',
                    photographer_name: 'Will Kinsler',
                    is_patron: true,
                    image_url: '/photos/full/photo_002.jpg',
                    thumbnail_url: '/photos/thumb/photo_002.jpg',
                    tags: ['Studio', 'Fashion', 'Studio Lighting'],
                    properties: {
                        color_mode: 'Color',
                        aspect_ratio: '4:5'
                    },
                    uploaded_at: '2025-01-15T09:15:00Z'
                }
            ]
        };
    }
    
    async getPhotographerProfile(photographer_id) {
        // PSEUDO: GET /api/photographers/{id}
        return {
            id: photographer_id,
            username: 'xinyideng',
            display_name: 'Xinyi Deng',
            bio: 'Natural light photographer based in San Francisco',
            avatar_url: '/avatars/xinyi.jpg',
            location: 'San Francisco, CA',
            website: 'https://xinyideng.com',
            equipment: ['Leica M10', 'Hasselblad 500C'],
            specialties: ['Portrait', 'Fashion', 'Street'],
            stats: {
                photos_count: 245,
                followers_count: 1823,
                following_count: 156,
                collaborations_count: 12
            },
            is_following: false,
            is_connected: false, // Mutual follow
            recent_photos: [] // Last 12 photos
        };
    }
    
    async appreciatePhoto(photo_id) {
        // PSEUDO: POST /api/photos/{id}/appreciate
        // This is a toggle - appreciate or remove appreciation
        return {
            appreciated: true,
            // Count is private, only shown to photo owner
        };
    }
    
    async getNotifications() {
        // PSEUDO: GET /api/notifications
        return {
            notifications: [
                {
                    id: 'notif_001',
                    type: 'appreciation',
                    from_user: {
                        id: 'user_789',
                        name: 'Kat Zdan',
                        avatar: '/avatars/kat.jpg'
                    },
                    photo: {
                        id: 'photo_003',
                        thumbnail: '/photos/thumb/photo_003.jpg'
                    },
                    created_at: '2025-01-15T10:00:00Z',
                    read: false
                },
                {
                    id: 'notif_002',
                    type: 'comment',
                    from_user: {
                        id: 'user_123',
                        name: 'Xinyi Deng',
                        avatar: '/avatars/xinyi.jpg'
                    },
                    comment_text: 'Thank you Charles!',
                    photo: {
                        id: 'photo_004',
                        thumbnail: '/photos/thumb/photo_004.jpg'
                    },
                    created_at: '2025-01-14T23:00:00Z',
                    read: true
                }
            ],
            unread_count: 1
        };
    }
    
    async getPhotoDetails(photo_id) {
        // PSEUDO: GET /api/photos/{id}
        return {
            id: photo_id,
            photographer: {
                id: 'user_123',
                name: 'Xinyi Deng',
                avatar: '/avatars/xinyi.jpg'
            },
            image_urls: {
                full: '/photos/full/photo_001.jpg',
                large: '/photos/large/photo_001.jpg',
                medium: '/photos/medium/photo_001.jpg',
                thumbnail: '/photos/thumb/photo_001.jpg'
            },
            title: 'Morning Light in the City',
            description: 'Captured during golden hour in downtown SF',
            tags: ['Urban', 'Portrait', 'Natural Light'],
            properties: {
                color_mode: 'B&W',
                aspect_ratio: '3:2',
                orientation: 'Landscape',
                camera: 'Leica M10',
                lens: '50mm f/1.4',
                iso: 400,
                aperture: 'f/2.8',
                shutter_speed: '1/250',
                focal_length: '50mm',
                taken_at: '2025-01-14T07:30:00Z',
                location: {
                    city: 'San Francisco',
                    country: 'USA',
                    coordinates: null // Privacy setting
                }
            },
            stats: {
                views: 1245,
                appreciation_count: null, // Only visible to owner
                comments_count: 8,
                downloads_count: null // Only visible to owner
            },
            rights: {
                license: 'All Rights Reserved',
                download_enabled: false,
                print_available: true
            },
            series: {
                id: 'series_001',
                name: 'Urban Mornings',
                position: 3,
                total: 12
            }
        };
    }
    
    async searchPhotos(query, filters) {
        // PSEUDO: GET /api/search
        // Params: q, tags[], color_mode, date_range, photographer_id
        return {
            results: [],
            facets: {
                tags: {
                    'Portrait': 145,
                    'Urban': 89,
                    'Studio': 67
                },
                color_modes: {
                    'B&W': 234,
                    'Color': 456
                }
            }
        };
    }
}

// ============== UI COMPONENTS ==============

class PhotoCard {
    constructor(photo) {
        this.photo = photo;
    }
    
    render() {
        return `
            <div class="photo-card" data-photo-id="${this.photo.id}">
                <div class="photo-image-container">
                    <img src="${this.photo.thumbnail_url}" 
                         alt="${this.photo.title}"
                         loading="lazy"
                         class="photo-image">
                    <div class="photo-overlay">
                        <button class="appreciate-btn" data-appreciated="${this.photo.has_appreciated}">
                            <span class="appreciate-icon">✨</span>
                        </button>
                    </div>
                </div>
                <div class="photo-info">
                    <div class="photographer-info">
                        <img src="${this.photo.photographer_avatar}" 
                             alt="${this.photo.photographer_name}"
                             class="photographer-avatar">
                        <span class="photographer-name">${this.photo.photographer_name}</span>
                    </div>
                    <div class="photo-meta">
                        <span class="photo-tags">${this.photo.tags.join(' • ')}</span>
                        <span class="photo-time">${this.formatTime(this.photo.uploaded_at)}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    formatTime(timestamp) {
        // Convert to relative time
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        const hours = Math.floor(diff / (1000 * 60 * 60));
        
        if (hours < 1) return 'Just now';
        if (hours < 24) return `${hours}h ago`;
        if (hours < 48) return 'Yesterday';
        return date.toLocaleDateString();
    }
}

// ============== LATERAL NAVIGATION ==============

class PhotoViewer {
    constructor(photos, currentIndex, context) {
        this.photos = photos;
        this.currentIndex = currentIndex;
        this.context = context; // 'home', 'discover', 'profile', 'search'
        this.preloadRadius = 3;
    }
    
    async navigateNext() {
        if (this.currentIndex < this.photos.length - 1) {
            this.currentIndex++;
            await this.preloadImages();
            return this.photos[this.currentIndex];
        }
        // Load more photos if at end
        await this.loadMorePhotos();
    }
    
    async navigatePrevious() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            return this.photos[this.currentIndex];
        }
        return null;
    }
    
    async preloadImages() {
        // Preload next 3 images for smooth swiping
        const start = Math.max(0, this.currentIndex - this.preloadRadius);
        const end = Math.min(this.photos.length, this.currentIndex + this.preloadRadius);
        
        for (let i = start; i < end; i++) {
            const img = new Image();
            img.src = this.photos[i].image_url;
        }
    }
    
    async loadMorePhotos() {
        // Load next batch based on context
        const dataModel = new LumenDataModel();
        let newPhotos;
        
        switch(this.context) {
            case 'home':
                newPhotos = await dataModel.getHomeFeed();
                break;
            case 'discover':
                newPhotos = await dataModel.getDiscoverFeed();
                break;
            // etc...
        }
        
        this.photos.push(...newPhotos.photos);
    }
}

// ============== TAG SELECTION UI ==============

class TagSelector {
    constructor() {
        this.categories = {
            setting: ['Studio', 'Urban', 'Nature', 'Indoor', 'Underwater'],
            style: ['Portrait', 'Fashion', 'Fine Art', 'Documentary', 'Editorial', 'Boudoir'],
            content: ['Artistic Nude', 'Implied Nude', 'Lingerie', 'Swimwear'],
            process: ['Film', 'Instant Film', 'Alternative Process'],
            lighting: ['Natural Light', 'Studio Lighting', 'Mixed Light']
        };
        
        this.selected = {
            setting: null,
            style: null,
            content: null
        };
        
        this.maxTags = 3;
    }
    
    render() {
        return `
            <div class="tag-selector">
                <div class="tag-category required">
                    <label>Setting</label>
                    <select class="tag-dropdown" data-category="setting">
                        <option value="">Select...</option>
                        ${this.categories.setting.map(tag => 
                            `<option value="${tag}">${tag}</option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="tag-category required">
                    <label>Style</label>
                    <select class="tag-dropdown" data-category="style">
                        <option value="">Select...</option>
                        ${this.categories.style.map(tag => 
                            `<option value="${tag}">${tag}</option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="tag-category optional">
                    <label>Content</label>
                    <select class="tag-dropdown" data-category="content">
                        <option value="">None</option>
                        ${this.categories.content.map(tag => 
                            `<option value="${tag}">${tag}</option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="tag-count">
                    ${this.getSelectedCount()} / ${this.maxTags} tags
                </div>
            </div>
        `;
    }
    
    getSelectedCount() {
        return Object.values(this.selected).filter(v => v !== null).length;
    }
    
    validateCombination() {
        // Prevent invalid combinations
        if (this.selected.setting === 'Urban' && this.selected.style === 'Boudoir') {
            return {
                valid: false,
                message: 'Boudoir requires Indoor or Studio setting'
            };
        }
        return { valid: true };
    }
}

// ============== CLIENT-SIDE IMAGE ANALYSIS ==============

class ImageAnalyzer {
    constructor() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
    }
    
    async analyzeImage(file) {
        const img = new Image();
        const url = URL.createObjectURL(file);
        
        return new Promise((resolve) => {
            img.onload = () => {
                // Set canvas size to reasonable sample size
                const sampleSize = 256;
                const scale = Math.min(sampleSize / img.width, sampleSize / img.height);
                
                this.canvas.width = img.width * scale;
                this.canvas.height = img.height * scale;
                
                // Draw scaled image
                this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
                
                // Get image data
                const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
                const pixels = imageData.data;
                
                // Analyze properties
                const analysis = {
                    colorMode: this.detectColorMode(pixels),
                    aspectRatio: this.calculateAspectRatio(img.width, img.height),
                    orientation: this.detectOrientation(img.width, img.height),
                    dimensions: {
                        width: img.width,
                        height: img.height
                    }
                };
                
                // Clean up
                URL.revokeObjectURL(url);
                
                resolve(analysis);
            };
            
            img.src = url;
        });
    }
    
    detectColorMode(pixels) {
        // Sample every 10th pixel for speed
        const samples = [];
        for (let i = 0; i < pixels.length; i += 40) { // 4 channels * 10
            const r = pixels[i];
            const g = pixels[i + 1];
            const b = pixels[i + 2];
            
            // Calculate color variance
            const avg = (r + g + b) / 3;
            const variance = Math.abs(r - avg) + Math.abs(g - avg) + Math.abs(b - avg);
            samples.push(variance);
        }
        
        // Calculate average variance
        const avgVariance = samples.reduce((a, b) => a + b, 0) / samples.length;
        
        // Threshold for B&W detection
        if (avgVariance < 5) {
            return 'B&W';
        } else if (avgVariance < 15) {
            return 'Monochrome'; // Sepia, split-tone, etc.
        } else {
            return 'Color';
        }
    }
    
    calculateAspectRatio(width, height) {
        const gcd = (a, b) => b === 0 ? a : gcd(b, a % b);
        const divisor = gcd(width, height);
        const ratioW = width / divisor;
        const ratioH = height / divisor;
        
        // Common ratios
        const commonRatios = {
            '1:1': 1,
            '4:5': 0.8,
            '3:4': 0.75,
            '2:3': 0.667,
            '3:2': 1.5,
            '16:9': 1.778,
            '21:9': 2.333
        };
        
        const actual = width / height;
        
        // Find closest common ratio
        let closest = '1:1';
        let minDiff = Math.abs(actual - 1);
        
        for (const [name, value] of Object.entries(commonRatios)) {
            const diff = Math.abs(actual - value);
            if (diff < minDiff) {
                minDiff = diff;
                closest = name;
            }
        }
        
        // If very close to common ratio, use it
        if (minDiff < 0.05) {
            return closest;
        }
        
        // Otherwise return calculated ratio
        return `${ratioW}:${ratioH}`;
    }
    
    detectOrientation(width, height) {
        const ratio = width / height;
        
        if (Math.abs(ratio - 1) < 0.1) {
            return 'Square';
        } else if (ratio > 2) {
            return 'Panoramic';
        } else if (ratio > 1) {
            return 'Landscape';
        } else {
            return 'Portrait';
        }
    }
    
    async extractEXIF(file) {
        // This would use ExifReader library
        // Return null if no EXIF or stripped
        try {
            const tags = await ExifReader.load(file);
            return {
                camera: tags.Make?.description + ' ' + tags.Model?.description,
                lens: tags.LensModel?.description,
                iso: tags.ISOSpeedRatings?.description,
                aperture: tags.FNumber?.description,
                shutterSpeed: tags.ExposureTime?.description,
                focalLength: tags.FocalLength?.description,
                dateTaken: tags.DateTimeOriginal?.description,
                gps: tags.GPSLatitude ? {
                    lat: tags.GPSLatitude.description,
                    lng: tags.GPSLongitude.description
                } : null
            };
        } catch (e) {
            return null;
        }
    }
}

// Export for use in main app
export {
    LumenDataModel,
    PhotoCard,
    PhotoViewer,
    TagSelector,
    ImageAnalyzer
};