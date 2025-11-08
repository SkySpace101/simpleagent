// SimpleAgent - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const queryForm = document.getElementById('queryForm');
    const templateBtn = document.getElementById('templateBtn');
    const templatesSection = document.getElementById('templatesSection');
    const templatesGrid = document.getElementById('templatesGrid');
    const outputSection = document.getElementById('outputSection');
    const outputContent = document.getElementById('outputContent');
    const downloadSection = document.getElementById('downloadSection');
    const downloadLink = document.getElementById('downloadLink');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');

    // Load templates
    loadTemplates();

    // Template button toggle
    templateBtn.addEventListener('click', function() {
        templatesSection.style.display = templatesSection.style.display === 'none' ? 'block' : 'none';
    });

    // Form submission
    queryForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(queryForm);
        const query = formData.get('query');
        const file = formData.get('file');

        if (!query.trim()) {
            showError('Please enter a query');
            return;
        }

        // Hide previous outputs
        hideAllSections();
        showLoading();

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Error processing query');
            }

            hideLoading();
            showOutput(data);

        } catch (err) {
            hideLoading();
            showError(err.message || 'An error occurred while processing your query');
        }
    });

    async function loadTemplates() {
        try {
            const response = await fetch('/api/query-templates');
            const data = await response.json();
            
            templatesGrid.innerHTML = '';
            data.templates.forEach(template => {
                const card = document.createElement('div');
                card.className = 'template-card';
                card.innerHTML = `
                    <h4>${template.name}</h4>
                    <p>${template.query.substring(0, 100)}...</p>
                `;
                card.addEventListener('click', function() {
                    document.getElementById('query').value = template.query;
                    templatesSection.style.display = 'none';
                });
                templatesGrid.appendChild(card);
            });
        } catch (err) {
            console.error('Error loading templates:', err);
        }
    }

    function showOutput(data) {
        outputSection.style.display = 'block';
        
        if (data.output_type === 'codebase') {
            outputContent.textContent = `Codebase generated successfully!\n\nOutput Type: ${data.output_type}\nFiles: Ready for download`;
            downloadSection.style.display = 'block';
            downloadLink.href = data.download_url;
            downloadLink.textContent = 'Download Codebase (ZIP)';
        } else {
            outputContent.textContent = `Text response generated successfully!\n\nOutput Type: ${data.output_type}\n\nDownload the file to view the full response.`;
            downloadSection.style.display = 'block';
            downloadLink.href = data.download_url;
            downloadLink.textContent = 'Download Response (TXT)';
        }
    }

    function showLoading() {
        loading.style.display = 'block';
    }

    function hideLoading() {
        loading.style.display = 'none';
    }

    function showError(message) {
        error.style.display = 'block';
        errorMessage.textContent = message;
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            error.style.display = 'none';
        }, 5000);
    }

    function hideAllSections() {
        outputSection.style.display = 'none';
        downloadSection.style.display = 'none';
        error.style.display = 'none';
    }
});


