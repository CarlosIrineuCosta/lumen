window.LumenUpload = {
    initialized: false,
    
    init: function() {
        if (this.initialized) {
            console.log('LumenUpload: Already initialized, skipping...');
            return;
        }
        
        console.log('LumenUpload: Initializing...');
        const addPhotoButton = document.getElementById('add-photo');
        
        if (addPhotoButton) {
            console.log('LumenUpload: Found #add-photo button.');
            addPhotoButton.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('LumenUpload: #add-photo button clicked.');
                this.showUploadModal();
            });
            this.initialized = true;
            console.log('LumenUpload: Initialization complete.');
        } else {
            console.error('LumenUpload: #add-photo button not found.');
        }
    },

    showUploadModal: function() {
        console.log('LumenUpload: showUploadModal() called');

        // Reset modal state
        this.resetModalState();

        // Setup event listeners for the DaisyUI modal
        this.setupModalEventListeners();

        // Show the modal using LumenUI
        if (window.LumenUI) {
            LumenUI.showModal('upload-modal');
        } else {
            // Fallback if LumenUI not available
            const modal = document.getElementById('upload-modal');
            if (modal && typeof modal.showModal === 'function') {
                modal.showModal();
            }
        }

        // Initialize FilePond
        console.log('LumenUpload: Initializing FilePond');
        this.initFilePond();

        // Load series options
        this.loadSeriesOptions();
    },

    closeUploadModal: function() {
        console.log('LumenUpload: closeUploadModal() called');

        // Clean up FilePond if it exists
        if (this.filePond) {
            this.filePond.destroy();
            this.filePond = null;
        }

        // Close modal using LumenUI
        if (window.LumenUI) {
            LumenUI.hideModal('upload-modal');
        } else {
            // Fallback if LumenUI not available
            const modal = document.getElementById('upload-modal');
            if (modal && typeof modal.close === 'function') {
                modal.close();
            }
        }
    },

    resetModalState: function() {
        // Reset form fields
        const titleInput = document.getElementById('photo-title');
        const descriptionInput = document.getElementById('photo-description');
        const categorySelect = document.getElementById('photo-category');
        const seriesSelect = document.getElementById('photo-series');
        const metadataSection = document.getElementById('metadata-section');
        const saveButton = document.getElementById('upload-save');

        if (titleInput) titleInput.value = '';
        if (descriptionInput) descriptionInput.value = '';
        if (categorySelect) categorySelect.value = 'portrait';
        if (seriesSelect) seriesSelect.value = '';
        if (metadataSection) metadataSection.classList.add('hidden');
        if (saveButton) {
            saveButton.disabled = true;
            saveButton.innerHTML = 'Upload & Save';
            saveButton.classList.remove('uploading', 'success');
        }

        // Clean up FilePond if it exists
        if (this.filePond) {
            this.filePond.destroy();
            this.filePond = null;
        }
    },

    setupModalEventListeners: function() {
        // Remove existing listeners to prevent duplicates
        const cancelButton = document.getElementById('upload-cancel');
        const saveButton = document.getElementById('upload-save');

        if (cancelButton) {
            cancelButton.removeEventListener('click', this.closeUploadModal);
            cancelButton.addEventListener('click', () => this.closeUploadModal());
        }

        if (saveButton) {
            saveButton.removeEventListener('click', this.handleSave);
            saveButton.addEventListener('click', () => this.handleSave());
        }
    },

    handleSave: function() {
        console.log('LumenUpload: Save button clicked');
        
        if (!this.filePond || this.filePond.getFiles().length === 0) {
            LumenUtils.showError('Please select files to upload first.');
            return;
        }
        
        // Get form data
        const title = document.getElementById('photo-title').value.trim();
        const description = document.getElementById('photo-description').value.trim();
        const fileCount = this.filePond.getFiles().length;
        
        console.log(`Uploading ${fileCount} files with metadata:`, { title, description });
        console.log('Auth token:', LumenAuth.token ? 'Present' : 'Missing');
        console.log('Auth user:', LumenAuth.user);
        
        // Disable save button during upload
        const saveButton = document.getElementById('upload-save');
        if (saveButton) {
            saveButton.disabled = true;
            saveButton.innerHTML = 'Uploading...';
        }
        
        // Start the upload process
        this.processUpload();
    },

    initFilePond: function() {
        const inputElement = document.querySelector('#photo-upload-input');
        const container = document.querySelector('#filepond-container');

        // Register the Image Preview plugin
        FilePond.registerPlugin(FilePondPluginImagePreview);

        // Clear and setup the container
        if (container) {
            container.innerHTML = '';
            // Move the input to the container
            container.appendChild(inputElement);
        }

        // Create a FilePond instance with improved workflow
        const pond = FilePond.create(inputElement, {
            credits: false,
            storeAsFile: true,
            allowMultiple: true,
            maxFiles: 10,
            labelIdle: 'Drag & Drop your photos or <span class="filepond--label-action">Browse</span><br>Up to 10 files, 10MB each',

            // Don't auto-upload, let user control when to save
            instantUpload: false,

            // Handle file additions
            onaddfile: (error, file) => {
                if (!error) {
                    LumenUpload.updateUploadInterface();
                }
            },

            // Handle file removals
            onremovefile: (error, file) => {
                if (!error) {
                    LumenUpload.updateUploadInterface();
                }
            },

            // Handle completion of all file uploads (MOVED TO ROOT LEVEL)
            onprocessfiles: () => {
                console.log('All files uploaded successfully');
                LumenUpload.handleUploadSuccess();
            },

            server: {
                process: {
                    url: `${LumenConfig.api.baseURL}/api/v1/photos/upload`,
                    headers: {
                        'Authorization': `Bearer ${LumenAuth.token}`
                    },
                    onload: (response) => {
                        console.log('File uploaded successfully');
                        return response;
                    },
                    onerror: (response) => {
                        console.error('FilePond upload error:', response);

                        // Reset button state on error
                        LumenUpload.resetUploadButton();

                        // Check if it's a 422 validation error
                        if (response && response.includes && response.includes('422')) {
                            LumenUtils.showError('Upload validation failed. Please check your authentication.');
                        } else {
                            LumenUtils.showError('Upload failed. Please try again.');
                        }
                        return response;
                    },
                    ondata: (formData) => {
                        // Append metadata to the upload request
                        const title = document.getElementById('photo-title')?.value || '';
                        const description = document.getElementById('photo-description')?.value || '';
                        const category = document.getElementById('photo-category')?.value || 'portrait';
                        const seriesId = this.getSeriesValue();

                        if (title) formData.append('title', title);
                        if (description) formData.append('description', description);
                        formData.append('category', category);
                        if (seriesId) formData.append('series_id', seriesId);

                        return formData;
                    }
                }
            }
        });
        
        // Store the pond instance for later use
        this.filePond = pond;
    },

    updateUploadInterface: function() {
        const metadataSection = document.getElementById('metadata-section');
        const saveButton = document.getElementById('upload-save');
        const fileCount = this.filePond ? this.filePond.getFiles().length : 0;
        
        console.log(`LumenUpload: ${fileCount} files selected`);
        
        if (fileCount > 0) {
            // Show metadata section and enable save button
            if (metadataSection) {
                metadataSection.classList.remove('hidden');
            }
            if (saveButton) {
                saveButton.disabled = false;
                saveButton.innerHTML = `Upload ${fileCount} Photo${fileCount > 1 ? 's' : ''}`;
                saveButton.classList.remove('uploading', 'success');
            }
        } else {
            // Hide metadata section and disable save button
            if (metadataSection) {
                metadataSection.classList.add('hidden');
            }
            if (saveButton) {
                saveButton.disabled = true;
                saveButton.innerHTML = 'Upload & Save';
                saveButton.classList.remove('uploading', 'success');
            }
        }
    },

    processUpload: function() {
        if (this.filePond) {
            // Show uploading state
            this.showUploadingState();
            // Process all files
            this.filePond.processFiles();
        }
    },

    showUploadingState: function() {
        const saveButton = document.getElementById('upload-save');
        if (saveButton) {
            saveButton.disabled = true;
            saveButton.innerHTML = `
                <span class="loading loading-spinner loading-sm"></span>
                Uploading...
            `;
            saveButton.classList.add('uploading');
        }
    },

    resetUploadButton: function() {
        const saveButton = document.getElementById('upload-save');
        if (saveButton) {
            saveButton.disabled = false;
            saveButton.innerHTML = 'Upload & Save';
            saveButton.classList.remove('uploading');
        }
    },

    handleUploadSuccess: function() {
        const fileCount = this.filePond ? this.filePond.getFiles().length : 0;

        // Show success message
        LumenUtils.showSuccess(`Successfully uploaded ${fileCount} photo${fileCount > 1 ? 's' : ''}!`);

        // Update button to show success state
        const saveButton = document.getElementById('upload-save');
        if (saveButton) {
            saveButton.innerHTML = `
                <svg class="w-4 h-4 mr-2" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
                </svg>
                Uploaded Successfully!
            `;
            saveButton.classList.remove('uploading');
            saveButton.classList.add('success');
        }

        // Auto-close modal after success
        setTimeout(() => {
            this.closeUploadModal();

            // Refresh gallery if available
            if (window.LumenGallery && LumenGallery.loadPhotos) {
                console.log('Refreshing gallery after upload...');
                LumenGallery.loadPhotos();
            }

            // Also refresh the gallery display
            if (window.LumenGallery && LumenGallery.renderGallery) {
                setTimeout(() => {
                    console.log('Re-rendering gallery...');
                    LumenGallery.renderGallery();
                }, 500);
            }
        }, 2000);
    },

    // Load series options for dropdown
    loadSeriesOptions: async function() {
        try {
            const series = await LumenAPI.getSeries();
            const select = document.getElementById('photo-series');

            if (!select) return;

            // Clear existing options except "No series"
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }

            // Add series options
            if (series && series.length > 0) {
                series.forEach(s => {
                    const option = document.createElement('option');
                    option.value = s.id;
                    option.textContent = s.title;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading series options:', error);
            // Series loading failure shouldn't block upload, so just log it
        }
    },

    // Get series value from form
    getSeriesValue: function() {
        const seriesSelect = document.getElementById('photo-series');
        return seriesSelect ? seriesSelect.value : '';
    }
};