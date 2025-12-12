// Simple Masonry Implementation for Lumen
// Drop-in replacement for broken CSS Grid masonry

class SimpleMasonry {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
        
        this.options = {
            itemSelector: '.photo-item',
            columnWidth: 300,
            gutter: 16,
            onComplete: null,
            ...options
        };
        
        this.columns = [];
        this.items = [];
        this.resizeTimeout = null;
        
        this.init();
    }
    
    init() {
        // Setup container styles
        this.container.style.position = 'relative';
        
        // Calculate columns based on container width
        this.calculateColumns();
        
        // Position existing items
        this.positionItems();
        
        // Setup resize listener
        window.addEventListener('resize', () => this.handleResize());
    }
    
    calculateColumns() {
        const containerWidth = this.container.offsetWidth;
        const columnWidth = this.options.columnWidth;
        const gutter = this.options.gutter;
        
        // Calculate number of columns that fit
        const columnsCount = Math.floor((containerWidth + gutter) / (columnWidth + gutter));
        this.columnsCount = Math.max(1, columnsCount);
        
        // Initialize column heights
        this.columns = new Array(this.columnsCount).fill(0);
        
        console.log(`Masonry: ${this.columnsCount} columns, ${columnWidth}px wide`);
    }
    
    positionItems() {
        const items = this.container.querySelectorAll(this.options.itemSelector);
        
        // Reset column heights
        this.columns = new Array(this.columnsCount).fill(0);
        
        // Clear any existing positioning flags
        items.forEach(item => {
            item.removeAttribute('data-masonry-positioned');
        });
        
        // Wait for all images to load, then position all items in order
        this.waitForImages(items).then(() => {
            console.log(`All images loaded, positioning ${items.length} items`);
            // Position items sequentially to maintain proper column heights
            items.forEach(item => {
                this.positionItem(item);
            });
            this.updateContainerHeight();
            console.log(`Masonry layout complete. Container height: ${this.container.style.height}`);
            
            // Call completion callback if provided
            if (this.options.onComplete) {
                this.options.onComplete();
            }
        });
    }
    
    async waitForImages(items) {
        const promises = [];
        let imageCount = 0;
        
        items.forEach(item => {
            const images = item.querySelectorAll('img');
            imageCount += images.length;
            images.forEach(img => {
                if (!img.complete || img.naturalHeight === 0) {
                    promises.push(new Promise(resolve => {
                        img.onload = () => {
                            console.log(`Image loaded: ${img.src}`);
                            resolve();
                        };
                        img.onerror = () => {
                            console.log(`Image failed to load: ${img.src}`);
                            resolve();
                        };
                    }));
                }
            });
        });
        
        console.log(`Waiting for ${promises.length} images to load out of ${imageCount} total`);
        return Promise.all(promises);
    }
    
    positionItem(item) {
        // Find shortest column
        let shortestColumn = 0;
        let shortestHeight = this.columns[0];
        
        for (let i = 1; i < this.columns.length; i++) {
            if (this.columns[i] < shortestHeight) {
                shortestHeight = this.columns[i];
                shortestColumn = i;
            }
        }
        
        // Calculate position
        const x = shortestColumn * (this.options.columnWidth + this.options.gutter);
        const y = shortestHeight;
        
        // Position the item
        item.style.position = 'absolute';
        item.style.left = `${x}px`;
        item.style.top = `${y}px`;
        item.style.width = `${this.options.columnWidth}px`;
        
        // Update column height
        const itemHeight = item.offsetHeight;
        this.columns[shortestColumn] = y + itemHeight + this.options.gutter;
    }
    
    addItem(item) {
        // For single item additions (like new uploads)
        const images = item.querySelectorAll('img');
        if (images.length > 0) {
            const promises = [];
            images.forEach(img => {
                if (!img.complete || img.naturalHeight === 0) {
                    promises.push(new Promise(resolve => {
                        img.onload = resolve;
                        img.onerror = resolve;
                    }));
                }
            });
            
            Promise.all(promises).then(() => {
                this.positionItem(item);
                this.updateContainerHeight();
            });
        } else {
            this.positionItem(item);
            this.updateContainerHeight();
        }
    }
    
    updateContainerHeight() {
        const maxHeight = Math.max(...this.columns);
        this.container.style.height = `${maxHeight}px`;
    }
    
    handleResize() {
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            this.calculateColumns();
            this.positionItems();
        }, 250);
    }
    
    refresh(callback = null) {
        this.calculateColumns();
        this.positionItems();
        
        if (callback) {
            // Small delay to ensure positioning is complete
            setTimeout(callback, 100);
        }
    }
    
    destroy() {
        window.removeEventListener('resize', this.handleResize);
        
        // Reset item styles
        const items = this.container.querySelectorAll(this.options.itemSelector);
        items.forEach(item => {
            item.style.position = '';
            item.style.left = '';
            item.style.top = '';
            item.style.width = '';
        });
        
        // Reset container
        this.container.style.position = '';
        this.container.style.height = '';
    }
}

export default SimpleMasonry;
