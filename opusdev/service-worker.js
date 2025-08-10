// Lumen PWA Service Worker
// Handles offline functionality and caching

const CACHE_NAME = 'lumen-v1';
const API_CACHE = 'lumen-api-v1';
const IMAGE_CACHE = 'lumen-images-v1';

// Assets to cache on install
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/css/app.css',
    '/js/app.js',
    '/manifest.json'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(name => name.startsWith('lumen-') && name !== CACHE_NAME)
                    .map(name => caches.delete(name))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache when possible
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Handle API requests - network first
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // Cache successful responses
                    if (response.ok) {
                        const cache = caches.open(API_CACHE);
                        cache.then(c => c.put(request, response.clone()));
                    }
                    return response;
                })
                .catch(() => {
                    // Try cache if network fails
                    return caches.match(request);
                })
        );
        return;
    }
    
    // Handle images - cache first
    if (request.destination === 'image') {
        event.respondWith(
            caches.match(request)
                .then(cached => {
                    if (cached) return cached;
                    
                    return fetch(request).then(response => {
                        const cache = caches.open(IMAGE_CACHE);
                        cache.then(c => c.put(request, response.clone()));
                        return response;
                    });
                })
        );
        return;
    }
    
    // Handle static assets - cache first
    event.respondWith(
        caches.match(request)
            .then(cached => cached || fetch(request))
    );
});