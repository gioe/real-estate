/**
 * Properties search functionality
 */

let currentPropertiesSearch = {};

async function searchProperties() {
    try {
        hideError();
        hideNoResults();
        hideInitialHelp();
        showLoading();

        // Get form data
        const data = getFormData('propertiesSearchForm');
        
        // Add pagination
        data.offset = currentPage * currentLimit;
        data.limit = currentLimit;
        
        // Store current search for pagination
        currentPropertiesSearch = data;

        // Make API request
        const result = await makeApiRequest('/api/properties/search', data);
        
        if (result.success) {
            if (result.data.properties && result.data.properties.length > 0) {
                displayPropertiesResults(result.data.properties);
                showResults();
                
                // Update pagination
                const hasMore = result.data.has_more || 
                               (result.data.properties.length === currentLimit);
                updatePagination(hasMore, result.total_count);
            } else {
                showNoResults();
            }
        } else {
            showError(result.error, result.recommendation);
        }
    } catch (error) {
        console.error('Properties search failed:', error);
        showError('Failed to search properties. Please try again.');
    } finally {
        hideLoading();
        
        // Reset form button
        const submitBtn = document.querySelector('#propertiesSearchForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-search me-2"></i>Search Properties';
            submitBtn.disabled = false;
        }
    }
}

function displayPropertiesResults(properties) {
    const container = document.getElementById('resultsContainer');
    if (!container) return;
    
    let html = '<div class="row">';
    
    properties.forEach(property => {
        html += createPropertyCard(property);
    });
    
    html += '</div>';
    
    container.innerHTML = html;
    
    // Add animation class
    container.classList.add('fade-in');
    
    // Update results count
    const resultsCount = document.getElementById('resultsCount');
    if (resultsCount) {
        resultsCount.textContent = `Found ${properties.length} properties`;
    }
}

// Initialize properties search page
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('propertiesSearchForm');
    if (!form) return; // Not on properties page
    
    // Setup form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        currentPage = 0; // Reset pagination
        searchProperties();
    });
    
    // Setup pagination
    setupPaginationHandlers(() => {
        // Re-run search with current parameters but new page
        const data = { ...currentPropertiesSearch };
        data.offset = currentPage * currentLimit;
        
        showLoading();
        makeApiRequest('/api/properties/search', data)
            .then(result => {
                if (result.success && result.data.properties) {
                    displayPropertiesResults(result.data.properties);
                    
                    const hasMore = result.data.has_more || 
                                   (result.data.properties.length === currentLimit);
                    updatePagination(hasMore, result.total_count);
                }
            })
            .catch(error => {
                console.error('Pagination failed:', error);
                showError('Failed to load results. Please try again.');
            })
            .finally(() => {
                hideLoading();
            });
    });
    
    // Setup limit change handler
    const limitSelect = document.getElementById('limit');
    if (limitSelect) {
        limitSelect.addEventListener('change', function() {
            currentLimit = parseInt(this.value);
            currentPage = 0; // Reset pagination
            
            if (Object.keys(currentPropertiesSearch).length > 0) {
                searchProperties();
            }
        });
    }
    
    // Tab switching handlers
    const tabButtons = document.querySelectorAll('#searchTypeTabs button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Clear form fields when switching tabs
            setTimeout(() => {
                clearFormFields();
            }, 100);
        });
    });
    
    function clearFormFields() {
        const activeTab = document.querySelector('#searchTypeTabs .nav-link.active').id;
        
        // Clear all input fields
        const inputs = form.querySelectorAll('input[type="text"], input[type="number"]');
        inputs.forEach(input => {
            // Only clear fields that are not in the active tab
            const tabPane = input.closest('.tab-pane');
            if (tabPane && !tabPane.classList.contains('show')) {
                input.value = '';
            }
        });
    }
    
    // Form validation
    form.addEventListener('input', function() {
        validatePropertiesForm();
    });
    
    function validatePropertiesForm() {
        const activeTab = document.querySelector('#searchTypeTabs .nav-link.active').id;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        let isValid = false;
        
        if (activeTab === 'address-tab') {
            const address = document.getElementById('address').value.trim();
            isValid = address.length > 0;
        } else if (activeTab === 'location-tab') {
            const city = document.getElementById('city').value.trim();
            const state = document.getElementById('state').value.trim();
            const zipcode = document.getElementById('zipcode').value.trim();
            isValid = city.length > 0 || state.length > 0 || zipcode.length > 0;
        } else if (activeTab === 'geo-tab') {
            const lat = document.getElementById('latitude').value;
            const lng = document.getElementById('longitude').value;
            isValid = lat && lng;
        }
        
        if (submitBtn) {
            submitBtn.disabled = !isValid;
        }
    }
    
    // Initial validation
    validatePropertiesForm();
});
