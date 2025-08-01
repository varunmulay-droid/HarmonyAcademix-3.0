// Main JavaScript file for Harmony Hands Student ERP

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeTooltips();
    initializePopovers();
    initializeFormValidation();
    initializeFileUpload();
    initializeNavigation();
    initializeDashboard();
    initializeDateInputs();
    initializeConfirmActions();
    
    console.log('Harmony Hands ERP - JavaScript initialized');
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize Bootstrap popovers
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Form validation enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Show error message
                showAlert('कृपया सर्व आवश्यक फील्ड भरा / Please fill all required fields', 'danger');
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time validation for specific inputs
    const requiredInputs = document.querySelectorAll('input[required], select[required], textarea[required]');
    requiredInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

// Validate individual field
function validateField(field) {
    if (field.checkValidity()) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
    }
}

// File upload enhancement
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const file = this.files[0];
            const maxSize = 16 * 1024 * 1024; // 16MB
            const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'application/pdf'];
            
            if (file) {
                // Check file size
                if (file.size > maxSize) {
                    showAlert('फाइल साइज 16MB पेक्षा कमी असावा / File size should be less than 16MB', 'danger');
                    this.value = '';
                    return;
                }
                
                // Check file type
                if (!allowedTypes.includes(file.type)) {
                    showAlert('केवळ PNG, JPG, JPEG, GIF, PDF फाइल्स स्वीकारल्या जातात / Only PNG, JPG, JPEG, GIF, PDF files are accepted', 'danger');
                    this.value = '';
                    return;
                }
                
                // Show file name
                const label = this.nextElementSibling;
                if (label && label.classList.contains('custom-file-label')) {
                    label.textContent = file.name;
                }
                
                // Add preview for images
                if (file.type.startsWith('image/')) {
                    createImagePreview(this, file);
                }
            }
        });
    });
}

// Create image preview
function createImagePreview(input, file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        let preview = input.parentNode.querySelector('.image-preview');
        if (!preview) {
            preview = document.createElement('div');
            preview.className = 'image-preview mt-2';
            input.parentNode.appendChild(preview);
        }
        
        preview.innerHTML = `
            <img src="${e.target.result}" alt="Preview" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
            <button type="button" class="btn btn-sm btn-danger ms-2" onclick="removePreview(this)">
                <i class="fas fa-times"></i> Remove
            </button>
        `;
    };
    reader.readAsDataURL(file);
}

// Remove image preview
function removePreview(button) {
    const preview = button.parentNode;
    const input = preview.parentNode.querySelector('input[type="file"]');
    input.value = '';
    preview.remove();
}

// Navigation enhancement
function initializeNavigation() {
    // Active page highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Mobile menu auto-close
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        document.addEventListener('click', function(event) {
            const isClickInsideNav = navbarCollapse.contains(event.target);
            const isToggler = navbarToggler.contains(event.target);
            
            if (!isClickInsideNav && !isToggler && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });
    }
}

// Dashboard enhancements
function initializeDashboard() {
    // Animate dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-stat-card, .card');
    dashboardCards.forEach(function(card, index) {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fade-in');
    });
    
    // Auto-refresh dashboard data every 5 minutes
    if (window.location.pathname.includes('dashboard')) {
        setInterval(function() {
            // Only refresh if the page is visible
            if (!document.hidden) {
                refreshDashboardStats();
            }
        }, 300000); // 5 minutes
    }
}

// Refresh dashboard statistics
function refreshDashboardStats() {
    const statCards = document.querySelectorAll('.dashboard-stat-card .stat-number');
    
    // Add loading animation
    statCards.forEach(function(stat) {
        stat.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    });
    
    // In a real implementation, this would make an AJAX call
    setTimeout(function() {
        window.location.reload();
    }, 1000);
}

// Date input enhancements
function initializeDateInputs() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(function(input) {
        // Set max date to today for birth dates
        if (input.name.includes('birth') || input.name.includes('dob')) {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('max', today);
        }
        
        // Set min date to today for future dates
        if (input.name.includes('admission') || input.name.includes('received')) {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('min', today);
        }
    });
}

// Confirmation for important actions
function initializeConfirmActions() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                event.preventDefault();
                return false;
            }
        });
    });
}

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Format numbers with Indian numbering system
function formatIndianNumber(num) {
    return num.toLocaleString('en-IN');
}

// Validate Aadhaar number
function validateAadhaar(aadhaar) {
    const aadhaarPattern = /^\d{12}$/;
    return aadhaarPattern.test(aadhaar);
}

// Validate mobile number
function validateMobile(mobile) {
    const mobilePattern = /^[6-9]\d{9}$/;
    return mobilePattern.test(mobile);
}

// Validate email
function validateEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

// Local storage utilities
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (error) {
        console.error('Error saving to localStorage:', error);
        return false;
    }
}

function getFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('Error reading from localStorage:', error);
        return null;
    }
}

// Form auto-save functionality
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(function(form) {
        const formId = form.getAttribute('data-autosave');
        const inputs = form.querySelectorAll('input, select, textarea');
        
        // Load saved data
        const savedData = getFromLocalStorage(`autosave_${formId}`);
        if (savedData) {
            Object.keys(savedData).forEach(function(key) {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && input.type !== 'file') {
                    input.value = savedData[key];
                }
            });
        }
        
        // Save data on input
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    if (input.type !== 'file') {
                        data[key] = value;
                    }
                }
                saveToLocalStorage(`autosave_${formId}`, data);
            });
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(`autosave_${formId}`);
        });
    });
}

// Print functionality
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Print</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                body { font-family: 'Noto Sans Devanagari', sans-serif; }
                @media print {
                    .no-print { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${element.outerHTML}
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
    setTimeout(() => printWindow.close(), 1000);
}

// Export functions for global use
window.HarmonyHands = {
    showAlert,
    validateAadhaar,
    validateMobile,
    validateEmail,
    printElement,
    saveToLocalStorage,
    getFromLocalStorage,
    formatIndianNumber
};

// Service Worker registration (for future PWA support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Handle online/offline status
window.addEventListener('online', function() {
    showAlert('इंटरनेट कनेक्शन पुनर्स्थापित झाले / Internet connection restored', 'success');
});

window.addEventListener('offline', function() {
    showAlert('इंटरनेट कनेक्शन नाही / No internet connection', 'warning');
});
