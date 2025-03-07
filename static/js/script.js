// Form Validation
document.addEventListener('DOMContentLoaded', function() {
    // Get all forms with the class 'needs-validation'
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});

// Format phone numbers as they are typed
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value.length <= 3) {
                    value = value;
                } else if (value.length <= 6) {
                    value = value.slice(0, 3) + '-' + value.slice(3);
                } else {
                    value = value.slice(0, 3) + '-' + value.slice(3, 6) + '-' + value.slice(6, 10);
                }
                e.target.value = value;
            }
        });
    });
});

// Preview image before upload
document.addEventListener('DOMContentLoaded', function() {
    const photoInput = document.getElementById('photo');
    if (photoInput) {
        photoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const preview = document.createElement('img');
                        preview.src = e.target.result;
                        preview.className = 'img-thumbnail mt-2';
                        preview.style.maxHeight = '200px';
                        
                        const container = photoInput.parentElement;
                        const existingPreview = container.querySelector('img');
                        if (existingPreview) {
                            container.removeChild(existingPreview);
                        }
                        container.appendChild(preview);
                    }
                    reader.readAsDataURL(file);
                } else {
                    alert('Please select an image file.');
                    photoInput.value = '';
                }
            }
        });
    }
});

// Print functionality
function printContent(elementId) {
    const content = document.getElementById(elementId);
    const originalContents = document.body.innerHTML;
    
    document.body.innerHTML = content.innerHTML;
    window.print();
    document.body.innerHTML = originalContents;
    
    // Reinitialize any JavaScript that was removed
    location.reload();
}

// Export table to Excel
function exportTableToExcel(tableId, filename = '') {
    const table = document.getElementById(tableId);
    const wb = XLSX.utils.table_to_book(table, { sheet: "Sheet1" });
    XLSX.writeFile(wb, filename || 'export.xlsx');
}

// Confirm delete with custom message
function confirmDelete(itemName, deleteUrl) {
    if (confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
        window.location.href = deleteUrl;
    }
}

// Handle barangay-sitio relationship
function updateSitioOptions(barangayId, sitioSelect) {
    if (!barangayId) {
        sitioSelect.innerHTML = '<option value="">Select Sitio</option>';
        sitioSelect.disabled = true;
        return;
    }
    
    fetch(`/voter/get_sitios/${barangayId}`)
        .then(response => response.json())
        .then(sitios => {
            sitioSelect.innerHTML = '<option value="">Select Sitio</option>';
            sitios.forEach(sitio => {
                const option = document.createElement('option');
                option.value = sitio.id;
                option.textContent = sitio.name;
                sitioSelect.appendChild(option);
            });
            sitioSelect.disabled = false;
        })
        .catch(error => {
            console.error('Error fetching sitios:', error);
            sitioSelect.innerHTML = '<option value="">Error loading sitios</option>';
            sitioSelect.disabled = true;
        });
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
});

// Handle form submission with file upload
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[enctype="multipart/form-data"]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const fileInputs = form.querySelectorAll('input[type="file"]');
            fileInputs.forEach(input => {
                if (input.files.length > 0) {
                    const file = input.files[0];
                    const maxSize = 5 * 1024 * 1024; // 5MB
                    
                    if (file.size > maxSize) {
                        e.preventDefault();
                        alert('File size should not exceed 5MB');
                        input.value = '';
                    }
                }
            });
        });
    });
}); 