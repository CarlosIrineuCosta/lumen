/*
 * =================================================================================================
 * CRITICAL INSTRUCTION: DO NOT CHANGE API ENDPOINTS
 * =================================================================================================
 * The authoritative source for all API endpoints is the documentation at `docs/core/API.md`.
 * Do not change, add, or remove API call definitions here without updating the documentation first.
 * Before assuming an API endpoint is incorrect, verify the entire frontend rendering and JS logic.
 * =================================================================================================
 */

/* API Module
 * API wrapper with CORS fix and authentication
 * Uses Poor Man's Modules pattern with window.LumenAPI global
 */

window.LumenAPI = {
    // Error rate limiting to prevent spam
    lastErrorTime: 0,
    ERROR_COOLDOWN: 3000, // 3 seconds
    
    // Initialize API module
    init() {
        console.log('LumenAPI initialized');
    },
    
    // Base request method with authentication and error handling
    async request(endpoint, options = {}) {
        const token = window.LumenAuth ? LumenAuth.getToken() : null;
        
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include' // CRITICAL for CORS with authentication
        };
        
        // Add authorization header if token is available
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const url = `${LumenConfig.api.baseURL}${endpoint}`;
        
        const t0 = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
        try {
            if (window.LumenConfig?.app?.debug) {
                console.debug('[LumenAPI] request', { url, method: options.method || 'GET' });
            }
            const response = await fetch(url, {
                ...config,
                credentials: 'include'  // CRITICAL FOR CORS - Always include credentials
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`API Error ${response.status}:`, errorText);
                throw new Error(`API Error: ${response.status} - ${errorText}`);
            }
            
            // Handle empty responses
            const text = await response.text();
            if (!text) return null;
            
            try {
                return JSON.parse(text);
            } catch (e) {
                return text;
            }
        } catch (error) {
            const t1 = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
            console.error('[LumenAPI] request failed', { url, method: options.method || 'GET', duration_ms: Math.round(t1 - t0), error });
            
            // Show user-friendly error message with rate limiting
            if (window.LumenUtils && Date.now() - this.lastErrorTime > this.ERROR_COOLDOWN) {
                if (error.message.includes('401')) {
                    LumenUtils.showError('Authentication required. Please sign in.');
                } else if (error.message.includes('403')) {
                    LumenUtils.showError('Access denied.');
                } else if (error.message.includes('404')) {
                    LumenUtils.showError('Resource not found.');
                } else if (error.message.includes('500')) {
                    LumenUtils.showError('Server error. Please try again later.');
                } else {
                    LumenUtils.showError('Connection issue. Please refresh the page.');
                }
                this.lastErrorTime = Date.now();
            }
            
            throw error;
        }
    },
    
    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },
    
    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },
    
    // File upload with FormData
    async uploadFile(endpoint, formData) {
        const token = window.LumenAuth ? LumenAuth.getToken() : null;
        
        const config = {
            method: 'POST',
            body: formData,
            credentials: 'include'
        };
        
        if (token) {
            config.headers = {
                'Authorization': `Bearer ${token}`
            };
        }
        
        try {
            const response = await fetch(`${LumenConfig.api.baseURL}${endpoint}`, config);
            
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('File upload failed:', error);
            if (window.LumenUtils) {
                LumenUtils.showError('File upload failed. Please try again.');
            }
            throw error;
        }
    },
    
    // === PHOTO API METHODS ===
    
    // Get photos with pagination
    async getPhotos(page = 1, limit = 20) {
        return this.get(`${LumenConfig.api.endpoints.photos}?page=${page}&limit=${limit}`);
    },
    
    // Get photo by ID
    async getPhoto(photoId) {
        return this.get(`${LumenConfig.api.endpoints.photos}${photoId}`);
    },
    
    // Upload photo
    async uploadPhoto(file, metadata = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Add metadata fields
        if (metadata.title) formData.append('title', metadata.title);
        if (metadata.description) formData.append('description', metadata.description);
        if (metadata.tags) formData.append('tags', JSON.stringify(metadata.tags));
        if (metadata.location) formData.append('location', metadata.location);
        if (metadata.camera_info) formData.append('camera_info', JSON.stringify(metadata.camera_info));
        
        return this.uploadFile(`${LumenConfig.api.endpoints.photos}`, formData);
    },
    
    // Delete photo
    async deletePhoto(photoId) {
        return this.delete(`${LumenConfig.api.endpoints.photos}${photoId}`);
    },

    // === PHOTO MANAGEMENT API METHODS ===

    // Get current user's photos for management
    async getMyPhotos(options = {}) {
        const params = new URLSearchParams();
        if (options.page) params.append('page', options.page);
        if (options.limit) params.append('limit', options.limit);
        if (options.category) params.append('category', options.category);
        if (options.series_id) params.append('series_id', options.series_id);
        if (options.include_deleted) params.append('include_deleted', options.include_deleted);

        return this.get(`${LumenConfig.api.endpoints.photos}mine?${params.toString()}`);
    },

    // Update photo with form data (replaces the previous updatePhoto method)
    async updatePhoto(photoId, formData) {
        return this.request(`${LumenConfig.api.endpoints.photos}${photoId}`, {
            method: 'PUT',
            body: formData,
            headers: {} // Let browser set Content-Type for FormData
        });
    },

    // Toggle photo visibility
    async togglePhotoVisibility(photoId, isPublic) {
        const formData = new FormData();
        formData.append('is_public', isPublic);

        return this.request(`${LumenConfig.api.endpoints.photos}${photoId}/visibility`, {
            method: 'PATCH',
            body: formData,
            headers: {} // Let browser set Content-Type for FormData
        });
    },

    // Batch operations on photos
    async batchUpdatePhotos(photoIds, action, options = {}) {
        const formData = new FormData();
        photoIds.forEach(id => formData.append('photo_ids', id));
        formData.append('action', action);

        if (options.series_id) formData.append('series_id', options.series_id);
        if (options.category) formData.append('category', options.category);
        if (options.is_public !== undefined) formData.append('is_public', options.is_public);

        return this.request(`${LumenConfig.api.endpoints.photos}batch`, {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set Content-Type for FormData
        });
    },
    
    // === USER API METHODS ===
    
    // Get current user profile
    async getUserProfile() {
        return this.get(`${LumenConfig.api.endpoints.users}me`);
    },
    
    // Update user profile
    async updateUserProfile(data) {
        return this.put(`${LumenConfig.api.endpoints.users}me`, data);
    },
    
    // Upload user profile image
    async uploadProfileImage(file) {
        const formData = new FormData();
        formData.append('file', file);
        return this.uploadFile(`${LumenConfig.api.endpoints.users}me/avatar`, formData);
    },
    
    // Get user photos with pagination
    async getUserPhotos(userId = 'me', page = 1, limit = 20) {
        return this.get(`${LumenConfig.api.endpoints.users}${userId}/photos?page=${page}&limit=${limit}`);
    },
    
    // Get user statistics
    async getUserStats(userId = 'me') {
        // The /stats endpoint is authenticated and gets stats for the current user.
        if (userId === 'me') {
            return this.get(`${LumenConfig.api.endpoints.users}stats`);
        }
        // For getting other users' stats, if that functionality is ever built.
        return this.get(`${LumenConfig.api.endpoints.users}${userId}/stats`);
    },
    
    // === SERIES API METHODS ===
    
    // Get user's photo series
    async getSeries() {
        return this.get('/api/v1/series');
    },
    
    // Create new series
    async createSeries(data) {
        return this.post('/api/v1/series', data);
    },
    
    // Update series
    async updateSeries(seriesId, data) {
        return this.put(`/api/v1/series/${seriesId}`, data);
    },
    
    // Delete series
    async deleteSeries(seriesId) {
        return this.delete(`/api/v1/series/${seriesId}`);
    },
    
    // Add photos to series
    async addPhotosToSeries(seriesId, photoIds) {
        return this.post(`/api/v1/series/${seriesId}/photos`, { photo_ids: photoIds });
    },
    
    // Remove photos from series
    async removePhotosFromSeries(seriesId, photoIds) {
        return this.delete(`/api/v1/series/${seriesId}/photos`, { photo_ids: photoIds });
    },
    
    // === UTILITY METHODS ===
    
    // Health check
    async healthCheck() {
        return this.get('/api/v1/health');
    },
    
    // Get API info
    async getApiInfo() {
        return this.get('/api/v1/');
    }
};
