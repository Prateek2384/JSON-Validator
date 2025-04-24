document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const selectFileBtn = document.getElementById('selectFileBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Elements for summary stats
    const blocksFoundElement = document.getElementById('blocksFound');
    const validBlocksElement = document.getElementById('validBlocks');
    const invalidBlocksElement = document.getElementById('invalidBlocks');
    
    // Handle file selection via button
    selectFileBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Handle file selection via drag and drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.backgroundColor = 'rgba(74, 111, 165, 0.1)';
    });
    
    uploadArea.addEventListener('dragleave', function() {
        this.style.backgroundColor = 'rgba(74, 111, 165, 0.05)';
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.backgroundColor = 'rgba(74, 111, 165, 0.05)';
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileUpload();
        }
    });
    
    // Handle file input change
    fileInput.addEventListener('change', handleFileUpload);
    
    function handleFileUpload() {
        const file = fileInput.files[0];
        if (!file) return;
        
        // Check file size (e.g., 10MB limit)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            showError('File size exceeds maximum allowed limit (10MB)');
            return;
        }
        
        // Check file extension
        const validExtensions = ['.pdf', '.docx', '.txt', '.json'];
        const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        if (!validExtensions.includes(fileExt)) {
            showError('Only PDF, DOCX, TXT, or JSON files are supported');
            return;
        }
        
        // Clear previous results and errors
        clearResults();
        hideError();
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        
        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Send to API
        fetch('/validate-mcp/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            let errorMsg = 'An error occurred during validation';
            if (error.detail) {
                if (typeof error.detail === 'string') {
                    errorMsg = error.detail;
                } else if (error.detail.msg) {
                    errorMsg = error.detail.msg;
                }
            }
            showError(errorMsg);
        })
        .finally(() => {
            loadingIndicator.style.display = 'none';
        });
    }
    
    function displayResults(data) {
        // Update summary stats
        blocksFoundElement.textContent = data.blocks_found;
        validBlocksElement.textContent = data.valid_blocks;
        invalidBlocksElement.textContent = data.invalid_blocks;
        
        // Clear previous results
        resultsContainer.innerHTML = '';
        
        if (data.blocks_found === 0) {
            resultsContainer.innerHTML = '<p>No MCP JSON blocks found with BEGIN_KNOWLEDGE/END_KNOWLEDGE markers.</p>';
            return;
        }
        
        // Display each block result
        data.results.forEach((block, index) => {
            const blockCard = document.createElement('div');
            blockCard.className = 'result-card';
            
            const blockHeader = document.createElement('div');
            blockHeader.className = 'result-header';
            
            const blockTitle = document.createElement('div');
            blockTitle.className = 'result-title';
            blockTitle.textContent = `Block #${block.block_number + 1}`;
            
            const blockStatus = document.createElement('div');
            blockStatus.className = `result-status ${block.valid ? 'status-valid' : 'status-invalid'}`;
            blockStatus.textContent = block.valid ? 'VALID' : 'INVALID';
            
            blockHeader.appendChild(blockTitle);
            blockHeader.appendChild(blockStatus);
            blockCard.appendChild(blockHeader);
            
            const blockDetails = document.createElement('div');
            blockDetails.className = 'result-details';
            
            // Add content preview (first 100 chars)
            const contentRow = document.createElement('div');
            contentRow.className = 'detail-row';
            
            const contentLabel = document.createElement('div');
            contentLabel.className = 'detail-label';
            contentLabel.textContent = 'Content:';
            
            const contentValue = document.createElement('div');
            contentValue.textContent = block.content.length > 100 
                ? `${block.content.substring(0, 100)}...` 
                : block.content;
            
            contentRow.appendChild(contentLabel);
            contentRow.appendChild(contentValue);
            blockDetails.appendChild(contentRow);
            
            // Add error message if invalid
            if (!block.valid && block.error) {
                const errorRow = document.createElement('div');
                errorRow.className = 'detail-row';
                
                const errorLabel = document.createElement('div');
                errorLabel.className = 'detail-label';
                errorLabel.textContent = 'Error:';
                
                const errorValue = document.createElement('div');
                errorValue.style.color = 'var(--error-color)';
                errorValue.textContent = block.error;
                
                errorRow.appendChild(errorLabel);
                errorRow.appendChild(errorValue);
                blockDetails.appendChild(errorRow);
            }
            
            blockCard.appendChild(blockDetails);
            resultsContainer.appendChild(blockCard);
        });
    }
    
    function clearResults() {
        blocksFoundElement.textContent = '0';
        validBlocksElement.textContent = '0';
        invalidBlocksElement.textContent = '0';
        resultsContainer.innerHTML = '<p>Upload a document to see validation results.</p>';
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
    
    function hideError() {
        errorMessage.style.display = 'none';
    }
});