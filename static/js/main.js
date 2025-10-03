// Main JavaScript functionality for Email Automation Dashboard

// Global variables
let statusUpdateInterval;
let campaignStatus = {
    running: false,
    progress: 0,
    total: 0,
    sent: 0,
    failed: 0
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize status polling if on campaign page
    if (window.location.pathname.includes('campaign')) {
        startStatusPolling();
    }
    
    // Initialize file upload handlers
    initializeFileUpload();
    
    // Initialize form validations
    initializeFormValidation();
    
    // Initialize copy functionality
    initializeCopyButtons();
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeFileUpload() {
    const fileInput = document.getElementById('csv_file');
    if (fileInput) {
        // File validation
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFile(file);
            }
        });
        
        // Drag and drop functionality
        const uploadArea = document.querySelector('.file-upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('dragover', handleDragOver);
            uploadArea.addEventListener('dragleave', handleDragLeave);
            uploadArea.addEventListener('drop', handleDrop);
        }
    }
}

function validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['text/csv', 'application/csv'];
    
    if (file.size > maxSize) {
        showAlert('File size too large. Please select a file smaller than 10MB.', 'danger');
        return false;
    }
    
    if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.csv')) {
        showAlert('Please select a CSV file.', 'danger');
        return false;
    }
    
    return true;
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const fileInput = document.getElementById('csv_file');
        if (fileInput) {
            fileInput.files = files;
            validateFile(files[0]);
        }
    }
}

function initializeFormValidation() {
    // Real-time form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function initializeCopyButtons() {
    // Copy to clipboard functionality
    document.addEventListener('click', function(e) {
        if (e.target.closest('.copy-log')) {
            const button = e.target.closest('.copy-log');
            const text = button.getAttribute('data-log');
            copyToClipboard(text, button);
        }
    });
}

function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-secondary');
        
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
        }, 1000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showAlert('Failed to copy to clipboard', 'danger');
    });
}

function startStatusPolling() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
    
    statusUpdateInterval = setInterval(updateCampaignStatus, 2000);
    updateCampaignStatus(); // Initial update
}

function stopStatusPolling() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
        statusUpdateInterval = null;
    }
}

function updateCampaignStatus() {
    fetch('/campaign_status')
        .then(response => response.json())
        .then(data => {
            updateCampaignUI(data);
        })
        .catch(error => {
            console.error('Error fetching campaign status:', error);
        });
}

function updateCampaignUI(status) {
    // Update counters
    updateCounter('total-emails', status.total || 0);
    updateCounter('sent-emails', status.sent || 0);
    updateCounter('failed-emails', status.failed || 0);
    
    // Update progress
    const total = status.total || 0;
    const sent = status.sent || 0;
    const progress = total > 0 ? Math.round((sent / total) * 100) : 0;
    
    updateProgressBar(progress);
    updateProgressText(sent, total);
    
    // Update status indicators
    updateStatusIndicators(status);
    
    // Update buttons
    updateCampaignButtons(status.running);
}

function updateCounter(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
        element.classList.add('status-update');
        setTimeout(() => element.classList.remove('status-update'), 500);
    }
}

function updateProgressBar(percentage) {
    const progressBar = document.getElementById('progress-bar');
    const progressPercentage = document.getElementById('progress-percentage');
    
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
    }
    
    if (progressPercentage) {
        progressPercentage.textContent = percentage + '%';
    }
}

function updateProgressText(sent, total) {
    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.textContent = `${sent} / ${total}`;
    }
}

function updateStatusIndicators(status) {
    const statusText = document.getElementById('status-text');
    const statusBadge = document.getElementById('campaign-status-badge');
    const currentEmailDiv = document.getElementById('current-email');
    
    if (statusText) {
        if (status.running) {
            statusText.textContent = 'Campaign is running...';
            if (status.current_email) {
                const currentEmailText = document.getElementById('current-email-text');
                if (currentEmailText) {
                    currentEmailText.textContent = status.current_email;
                }
                if (currentEmailDiv) {
                    currentEmailDiv.style.display = 'block';
                }
            }
        } else if (status.results) {
            statusText.textContent = 'Campaign completed!';
            if (currentEmailDiv) {
                currentEmailDiv.style.display = 'none';
            }
        } else {
            statusText.textContent = 'Ready to start campaign';
            if (currentEmailDiv) {
                currentEmailDiv.style.display = 'none';
            }
        }
    }
    
    if (statusBadge) {
        if (status.running) {
            statusBadge.textContent = 'Running';
            statusBadge.className = 'badge bg-success';
        } else if (status.results) {
            statusBadge.textContent = 'Completed';
            statusBadge.className = 'badge bg-info';
        } else {
            statusBadge.textContent = 'Ready';
            statusBadge.className = 'badge bg-secondary';
        }
    }
}

function updateCampaignButtons(isRunning) {
    const startBtn = document.getElementById('start-campaign');
    const stopBtn = document.getElementById('stop-campaign');
    
    if (startBtn) {
        startBtn.disabled = isRunning;
    }
    
    if (stopBtn) {
        stopBtn.disabled = !isRunning;
    }
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of main content
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(alertDiv, main.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

function showLoadingState(button, text = 'Loading...') {
    const originalHTML = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>${text}`;
    
    return function() {
        button.disabled = false;
        button.innerHTML = originalHTML;
    };
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Utility functions
function formatNumber(num) {
    return num.toLocaleString();
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

// Export functions for use in other scripts
window.EmailAutomation = {
    showAlert,
    showLoadingState,
    debounce,
    formatNumber,
    formatDate,
    formatDuration
};

