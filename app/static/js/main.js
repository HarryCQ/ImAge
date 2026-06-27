// Main JavaScript for Image Gallery

document.addEventListener('DOMContentLoaded', function() {

    // --- Drag & Drop Upload ---
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const uploadPreview = document.getElementById('upload-preview');
    const uploadBtn = document.getElementById('upload-btn');

    if (dropzone && fileInput) {
        // Click to select files
        dropzone.addEventListener('click', () => fileInput.click());

        // File selection changed
        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });

        // Drag events
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });

        function handleFiles(files) {
            if (files.length === 0) return;

            uploadPreview.innerHTML = '';
            let validFiles = 0;

            for (let file of files) {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        uploadPreview.appendChild(img);
                    };
                    reader.readAsDataURL(file);
                    validFiles++;
                }
            }

            if (validFiles > 0) {
                uploadBtn.style.display = 'block';
                // Update the file input to include all files
                const dt = new DataTransfer();
                for (let file of files) {
                    if (file.type.startsWith('image/')) {
                        dt.items.add(file);
                    }
                }
                fileInput.files = dt.files;
            }
        }
    }

    // --- Auto-hide flash messages ---
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s ease';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 4000);
    });

    // --- Image click to view full size (lightbox effect) ---
    const galleryImages = document.querySelectorAll('.image-card > a[target="_blank"]');
    galleryImages.forEach(link => {
        link.addEventListener('click', function(e) {
            // Let the link open in a new tab normally
            // This is fine for now
        });
    });

});
