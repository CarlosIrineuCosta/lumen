/* Lumen Neumorphic Mockup - Interactive Demo
 * Basic functionality for theme switching, photo loading, and UI interactions
 */

// Sample photos from API (real photos from Lumen database)
const samplePhotos = [
    {
        id: 'd1a8174f-2a5d-474a-ba2c-ad97a30ddc4d',
        title: 'Switch',
        photographer: 'Carlos Irineu da Costa',
        image_url: 'http://100.106.201.33:8080/storage/images/original/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/d1a8174f-2a5d-474a-ba2c-ad97a30ddc4d.jpeg',
        thumbnail_url: 'http://100.106.201.33:8080/storage/images/thumb/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/d1a8174f-2a5d-474a-ba2c-ad97a30ddc4d.webp'
    },
    {
        id: 'dd645554-cb86-4a25-9372-f69f3753e200',
        title: 'Natasha',
        photographer: 'Carlos Irineu da Costa',
        image_url: 'http://100.106.201.33:8080/storage/images/original/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/dd645554-cb86-4a25-9372-f69f3753e200.jpeg',
        thumbnail_url: 'http://100.106.201.33:8080/storage/images/thumb/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/dd645554-cb86-4a25-9372-f69f3753e200.webp'
    },
    {
        id: '1f5eaa27-3694-49df-925b-f3b8a711fe51',
        title: 'Natasha Rio 2025',
        photographer: 'Carlos Irineu da Costa',
        image_url: 'http://100.106.201.33:8080/storage/images/original/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/1f5eaa27-3694-49df-925b-f3b8a711fe51.jpeg',
        thumbnail_url: 'http://100.106.201.33:8080/storage/images/thumb/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/1f5eaa27-3694-49df-925b-f3b8a711fe51.webp'
    },
    {
        id: '5e5ab605-6f44-4751-8d55-8c3d8a4a40b7',
        title: 'Birdy',
        photographer: 'Carlos Irineu da Costa',
        image_url: 'http://100.106.201.33:8080/storage/images/original/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/5e5ab605-6f44-4751-8d55-8c3d8a4a40b7.jpeg',
        thumbnail_url: 'http://100.106.201.33:8080/storage/images/thumb/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/5e5ab605-6f44-4751-8d55-8c3d8a4a40b7.webp'
    },
    {
        id: '2e339c26-e6a2-49f2-8e6a-c0c09f28205d',
        title: 'Trumpet #2',
        photographer: 'Carlos Irineu da Costa',
        image_url: 'http://100.106.201.33:8080/storage/images/original/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/2e339c26-e6a2-49f2-8e6a-c0c09f28205d.jpeg',
        thumbnail_url: 'http://100.106.201.33:8080/storage/images/thumb/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/2e339c26-e6a2-49f2-8e6a-c0c09f28205d.webp'
    },
    {
        id: 'edd346a1-a3b8-471b-9226-c47be56ee050',
        title: 'Trumpet',
        photographer: 'Carlos Irineu da Costa',
        image_url: 'http://100.106.201.33:8080/storage/images/original/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/edd346a1-a3b8-471b-9226-c47be56ee050.jpeg',
        thumbnail_url: 'http://100.106.201.33:8080/storage/images/thumb/9pGzwsVBRMaSxMOZ6QNTJJjnl1b2/edd346a1-a3b8-471b-9226-c47be56ee050.webp'
    },
    {
        id: '32102e91-11b7-4e4d-99d4-f3b380c81daa',
        title: 'Siren, dry',
        photographer: 'Carlos Irineu',
        image_url: 'http://100.106.201.33:8080/storage/images/original/fsrh3LxGVNV2veJIM6J2QYKd9Kl2/32102e91-11b7-4e4d-99d4-f3b380c81daa.jpeg',
        thumbnail_url: 'http://100.106.201.33:8080/storage/images/thumb/fsrh3LxGVNV2veJIM6J2QYKd9Kl2/32102e91-11b7-4e4d-99d4-f3b380c81daa.webp'
    },
    {
        id: 'b6ed3b47-1346-42f1-9d55-92d67764f2ec',
        title: 'Window Bent',
        photographer: 'Carlos Irineu',
        image_url: 'http://100.106.201.33:8080/storage/images/original/fsrh3LxGVNV2veJIM6J2QYKd9Kl2/b6ed3b47-1346-42f1-9d55-92d67764f2ec.jpeg',
        thumbnail_url: 'http://100.106.201.33:8080/storage/images/thumb/fsrh3LxGVNV2veJIM6J2QYKd9Kl2/b6ed3b47-1346-42f1-9d55-92d67764f2ec.webp'
    }
];

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    loadPhotos();
    setupEventListeners();

    console.log('🎨 Lumen Neumorphic Mockup loaded');
});

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('neu-theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('neu-theme', newTheme);

    // Add visual feedback
    const button = event.target;
    button.style.transform = 'scale(0.9)';
    setTimeout(() => {
        button.style.transform = '';
    }, 150);
}

// Photo Grid Management
function loadPhotos() {
    const photoGrid = document.getElementById('photoGrid');
    if (!photoGrid) return;

    // Show loading state
    photoGrid.innerHTML = '<div class="neu-spinner large" style="margin: 40px auto;"></div>';

    // Simulate loading delay for demo
    setTimeout(() => {
        photoGrid.innerHTML = '';

        samplePhotos.forEach(photo => {
            const photoCard = createPhotoCard(photo);
            photoGrid.appendChild(photoCard);
        });

        // Add some duplicate cards for demo grid
        samplePhotos.slice(0, 4).forEach(photo => {
            const photoCard = createPhotoCard({...photo, id: photo.id + '_dup'});
            photoGrid.appendChild(photoCard);
        });
    }, 1000);
}

function createPhotoCard(photo) {
    const card = document.createElement('div');
    card.className = 'neu-surface photo-card';
    card.onclick = () => openPhotoModal(photo);

    card.innerHTML = `
        <img src="${photo.thumbnail_url}" alt="${photo.title}"
             onerror="this.src='${photo.image_url}'">
        <div class="photo-overlay">
            <div class="photo-title">${photo.title}</div>
            <div class="photo-meta">by ${photo.photographer}</div>
        </div>
    `;

    return card;
}

// Modal Management
function openPhotoModal(photo) {
    const modal = document.getElementById('photoModal');
    const modalImage = document.getElementById('modalImage');

    modalImage.src = photo.image_url;
    modalImage.alt = photo.title;
    modal.classList.add('active');

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('photoModal');
    modal.classList.remove('active');

    // Restore body scroll
    document.body.style.overflow = '';
}

function showUploadModal() {
    const backdrop = document.getElementById('uploadBackdrop');
    const modal = document.getElementById('uploadModal');

    backdrop.classList.add('active');
    modal.classList.add('active');

    // Simulate upload progress
    setTimeout(() => {
        simulateUploadProgress();
    }, 1000);
}

function hideUploadModal() {
    const backdrop = document.getElementById('uploadBackdrop');
    const modal = document.getElementById('uploadModal');

    backdrop.classList.remove('active');
    modal.classList.remove('active');

    // Reset progress
    const progressFill = document.querySelector('.neu-progress-linear-fill');
    if (progressFill) {
        progressFill.style.width = '0%';
    }
}

function simulateUploadProgress() {
    const progressFill = document.querySelector('.neu-progress-linear-fill');
    const progressText = document.querySelector('.neu-modal-body [style*="font-size: 12px"]');

    if (!progressFill) return;

    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 100) progress = 100;

        progressFill.style.width = progress + '%';
        if (progressText) {
            progressText.textContent = Math.round(progress) + '% uploaded';
        }

        if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                hideUploadModal();
                showToast('Upload completed!', 'success');
            }, 500);
        }
    }, 200);
}

// Event Listeners
function setupEventListeners() {
    // Dropdown functionality
    setupDropdowns();

    // Navigation tabs
    setupNavigation();

    // Filter chips
    setupFilters();

    // Modal close on backdrop click
    document.getElementById('photoModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });

    document.getElementById('uploadBackdrop').addEventListener('click', function(e) {
        if (e.target === this) {
            hideUploadModal();
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
            hideUploadModal();
        }
        if (e.key === 't' && e.ctrlKey) {
            e.preventDefault();
            toggleTheme();
        }
    });
}

function setupDropdowns() {
    document.querySelectorAll('.neu-dropdown').forEach(dropdown => {
        const button = dropdown.querySelector('.neu-dropdown-button');
        const menu = dropdown.querySelector('.neu-dropdown-menu');

        button.addEventListener('click', function(e) {
            e.stopPropagation();

            // Close other dropdowns
            document.querySelectorAll('.neu-dropdown').forEach(other => {
                if (other !== dropdown) {
                    other.classList.remove('active');
                    other.querySelector('.neu-dropdown-button').classList.remove('active');
                }
            });

            // Toggle current dropdown
            dropdown.classList.toggle('active');
            button.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            dropdown.classList.remove('active');
            button.classList.remove('active');
        });

        // Handle menu items
        menu.querySelectorAll('.neu-dropdown-item').forEach(item => {
            item.addEventListener('click', function() {
                console.log('Dropdown item clicked:', item.textContent);
                dropdown.classList.remove('active');
                button.classList.remove('active');

                // Show feedback
                showToast(`${item.textContent} clicked`, 'info');
            });
        });
    });
}

function setupNavigation() {
    document.querySelectorAll('.neu-nav-item').forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            document.querySelectorAll('.neu-nav-item').forEach(i => i.classList.remove('active'));

            // Add active class to clicked item
            item.classList.add('active');

            console.log('Navigation:', item.textContent);
            showToast(`Switched to ${item.textContent}`, 'info');
        });
    });
}

function setupFilters() {
    document.querySelectorAll('.neu-chip, .neu-pill').forEach(filter => {
        filter.addEventListener('click', function() {
            // Handle category chips (exclusive selection)
            if (filter.classList.contains('neu-chip')) {
                const parent = filter.closest('.filter-chips');
                parent.querySelectorAll('.neu-chip').forEach(chip => chip.classList.remove('active'));
                filter.classList.add('active');
            }
            // Handle tag pills (multiple selection)
            else if (filter.classList.contains('neu-pill')) {
                filter.classList.toggle('active');
            }

            console.log('Filter:', filter.textContent);
            showToast(`Filter: ${filter.textContent}`, 'info');
        });
    });
}

// Toast Notifications
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.neu-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'neu-toast-container';
        document.body.appendChild(container);
    }

    // Create toast
    const toast = document.createElement('div');
    toast.className = `neu-toast ${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <div class="neu-toast-icon">${icons[type] || icons.info}</div>
        <div class="neu-toast-content">
            <div class="neu-toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
            <div class="neu-toast-message">${message}</div>
        </div>
        <button class="neu-toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => toast.classList.add('active'), 100);

    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove('active');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }, 4000);
}

// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.neu-search-input');
    const searchButton = document.querySelector('.neu-search-button');

    if (searchInput && searchButton) {
        searchButton.addEventListener('click', function() {
            const query = searchInput.value.trim();
            if (query) {
                console.log('Search query:', query);
                showToast(`Searching for: "${query}"`, 'info');

                // Simulate search with loading
                searchButton.textContent = 'Searching...';
                searchButton.classList.add('loading');

                setTimeout(() => {
                    searchButton.textContent = 'Search';
                    searchButton.classList.remove('loading');
                    showToast(`Found results for "${query}"`, 'success');
                }, 2000);
            }
        });

        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchButton.click();
            }
        });
    }
});

// Window Functions (for inline event handlers)
window.toggleTheme = toggleTheme;
window.openPhotoModal = openPhotoModal;
window.closeModal = closeModal;
window.showUploadModal = showUploadModal;
window.hideUploadModal = hideUploadModal;