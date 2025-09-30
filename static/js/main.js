// Main JavaScript for Resume AI Optimizer

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const preview = this.parentElement.querySelector('.file-preview');
                if (preview) {
                    preview.textContent = `Selected: ${file.name}`;
                    preview.classList.add('text-success');
                }
            }
        });
    });

    // Progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 100);
    });

    // Card hover effects
    const cards = document.querySelectorAll('.card, .feature-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Template selection enhancement
    const templateRadios = document.querySelectorAll('.template-radio input[type="radio"]');
    templateRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            // Remove active class from all labels
            document.querySelectorAll('.template-radio label').forEach(label => {
                label.classList.remove('active');
            });
            
            // Add active class to selected label
            if (this.checked) {
                this.nextElementSibling.classList.add('active');
            }
        });
    });

    // Chat functionality
    const chatForm = document.querySelector('#chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const questionInput = this.querySelector('input[name="question"]');
            const question = questionInput.value.trim();
            
            if (question) {
                addChatMessage('user', question);
                questionInput.value = '';
                
                // Simulate AI response (replace with actual API call)
                setTimeout(() => {
                    addChatMessage('assistant', 'Thank you for your question. I\'ll provide a helpful answer based on your resume and job description.');
                }, 1000);
            }
        });
    }

    // Tip completion functionality
    const tipCheckboxes = document.querySelectorAll('.tip-checkbox');
    tipCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const tipId = this.value;
            const isCompleted = this.checked;
            
            // Update progress
            updateTipProgress(tipId, isCompleted);
        });
    });

    // Resume preview enhancement
    const resumePreview = document.querySelector('.resume-preview');
    if (resumePreview) {
        // Add copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-outline-primary btn-sm position-absolute top-0 end-0 m-2';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
        copyBtn.addEventListener('click', function() {
            copyToClipboard(resumePreview.textContent);
            this.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-copy"></i> Copy';
            }, 2000);
        });
        resumePreview.style.position = 'relative';
        resumePreview.appendChild(copyBtn);
    }

    // Handle resume analysis form submission
    const resumeForm = document.getElementById('resume-analysis-form');
    if (resumeForm) {
        resumeForm.addEventListener('submit', function(e) {
            // Allow natural form submission
        });
    }
    
    // Handle tip completion checkboxes
    document.addEventListener('change', function(e) {
        if (e.target.type === 'checkbox' && e.target.dataset.tipId) {
            console.log('Checkbox changed for tip:', e.target.dataset.tipId);
            const tipId = e.target.dataset.tipId;
            const isCompleted = e.target.checked;
            
            // Send AJAX request to mark tip as completed
            fetch(`/interview/tip/${tipId}/complete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'is_completed': isCompleted
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Tip completion updated successfully');
                    // Refresh page to update UI and check level progression
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                } else {
                    console.error('Error updating tip completion:', data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });

    // Auto-save form data (excluding file inputs and job description to prevent persistence)
    const formInputs = document.querySelectorAll('input:not([type="file"]):not([name="job_description"]), textarea:not([name="job_description"]), select');
    formInputs.forEach(input => {
        // Skip job description field completely
        if (input.name === 'job_description') return;
        
        input.addEventListener('input', function() {
            const formId = this.closest('form').id || 'default';
            const inputName = this.name;
            const inputValue = this.value;
            
            // Save to localStorage
            localStorage.setItem(`${formId}_${inputName}`, inputValue);
        });
        
        // Restore saved data (but not for job description)
        if (input.name !== 'job_description') {
            const formId = input.closest('form').id || 'default';
            const inputName = input.name;
            const savedValue = localStorage.getItem(`${formId}_${inputName}`);
            if (savedValue) {
                input.value = savedValue;
            }
        }
    });

    // Responsive navigation
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close mobile menu when clicking on a link
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navbarCollapse.classList.remove('show');
            });
        });
    }
});

// Utility functions
function addChatMessage(role, content) {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function updateTipProgress(tipId, isCompleted) {
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.querySelector('.progress-text');
    
    if (progressBar && progressText) {
        const currentProgress = parseInt(progressBar.style.width) || 0;
        const newProgress = isCompleted ? currentProgress + 20 : currentProgress - 20;
        
        progressBar.style.width = Math.max(0, Math.min(100, newProgress)) + '%';
        progressText.textContent = `${Math.max(0, Math.min(100, newProgress))}% Complete`;
    }
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copied to clipboard!', 'success');
    }
}

function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast show bg-${type} text-white`;
    toast.innerHTML = `
        <div class="toast-body">
            ${message}
            <button type="button" class="btn-close btn-close-white ms-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// AJAX utility functions
function makeRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Export functions for use in other scripts
window.ResumeOptimizer = {
    addChatMessage,
    updateTipProgress,
    copyToClipboard,
    showToast,
    makeRequest
};

