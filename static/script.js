function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Update sections
    document.querySelectorAll('.main-content section').forEach(section => {
        section.classList.remove('active-section');
        section.classList.add('hidden-section');
    });

    const activeSection = document.getElementById(`${tabName}-section`);
    activeSection.classList.remove('hidden-section');
    activeSection.classList.add('active-section');
}

// Password Visibility Toggle
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
    } else {
        input.type = "password";
    }
}

// Image Preview and Drag/Drop Logic for both forms
['encode', 'decode'].forEach(prefix => {
    const fileInput = document.getElementById(`${prefix}-image`);
    const dropArea = fileInput.closest('.file-drop-area');
    const previewContainer = document.getElementById(`${prefix}-preview-container`);
    const previewImg = document.getElementById(`${prefix}-preview`);
    const fileMessage = dropArea.querySelector('.file-message');

    // Handle Drag and Drop visuals
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false);
    });

    // Handle File Selection
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    dropArea.addEventListener('drop', function(e) {
        let dt = e.dataTransfer;
        let files = dt.files;
        fileInput.files = files; // Assign files to input
        handleFiles(files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                fileMessage.textContent = file.name;
                
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    previewContainer.classList.remove('hidden');
                }
                reader.readAsDataURL(file);
            } else {
                fileMessage.textContent = "Please select a valid image file.";
                previewContainer.classList.add('hidden');
            }
        }
    }
});

// Setup button loading states
function setLoading(btnId, isLoading) {
    const btn = document.getElementById(btnId);
    const text = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.loader');
    
    if (isLoading) {
        text.classList.add('hidden');
        loader.classList.remove('hidden');
        btn.disabled = true;
    } else {
        text.classList.remove('hidden');
        loader.classList.add('hidden');
        btn.disabled = false;
    }
}

// Handle Encode Submission
document.getElementById('encode-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    setLoading('encode-submit', true);
    
    const resultDiv = document.getElementById('encode-result');
    resultDiv.classList.add('hidden');
    resultDiv.className = 'result-message hidden';
    
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/api/encode', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            // It's a file download
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            
            // Extract filename from header if possible, else default
            let filename = "secret_image.png";
            const disposition = response.headers.get('content-disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                const matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) { 
                    filename = matches[1].replace(/['"]/g, '');
                }
            }
            
            // Trigger download
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);
            
            resultDiv.textContent = "Success! Your secure image is downloading.";
            resultDiv.classList.add('success');
            resultDiv.classList.remove('hidden');
            
            // Reset form
            e.target.reset();
            document.getElementById('encode-preview-container').classList.add('hidden');
            document.querySelector('#encode-section .file-message').textContent = "or drag and drop here";
        } else {
            const data = await response.json();
            throw new Error(data.error || "Failed to encode image");
        }
    } catch (error) {
        resultDiv.textContent = "Error: " + error.message;
        resultDiv.classList.add('error-message');
        resultDiv.classList.remove('hidden');
    } finally {
        setLoading('encode-submit', false);
    }
});

// Handle Decode Submission
document.getElementById('decode-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    setLoading('decode-submit', true);
    
    const resultBox = document.getElementById('decode-result');
    const errorDiv = document.getElementById('decode-error');
    
    resultBox.classList.add('hidden');
    errorDiv.classList.add('hidden');
    
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/api/decode', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('decrypted-text').textContent = data.message;
            resultBox.classList.remove('hidden');
            
            // Reset form but keep image preview
            document.getElementById('decode-password').value = '';
        } else {
            throw new Error(data.error || "Failed to decode image");
        }
    } catch (error) {
        errorDiv.textContent = "Error: " + error.message;
        errorDiv.classList.remove('hidden');
    } finally {
        setLoading('decode-submit', false);
    }
});

// Copy button logic
document.getElementById('copy-btn').addEventListener('click', () => {
    const text = document.getElementById('decrypted-text').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copy-btn');
        btn.textContent = "✅";
        setTimeout(() => { btn.textContent = "📋"; }, 2000);
    });
});
