/**
 * Listings search functionality
 */

let currentListingsSearch = {};

async function searchListings() {
    try {
        hideError();
        hideNoResults();
        hideInitialHelp();
        showLoading();

        // Get form data
        const data = getFormData('listingsSearchForm');
        
        // Add pagination
        data.offset = currentPage * currentLimit;
        data.limit = currentLimit;
        
        // Store current search for pagination
        currentListingsSearch = data;

        // Make API request
        const result = await makeApiRequest('/api/listings/search', data);
        
        if (result.success) {
            if (result.data.listings && result.data.listings.length > 0) {
                displayListingsResults(result.data.listings, result.listing_type);
                showResults();
                
                // Update pagination
                const hasMore = result.data.has_more || 
                               (result.data.listings.length === currentLimit);
                updatePagination(hasMore, result.total_count);
                
                // Update header
                updateListingTypeHeader(result.listing_type);
            } else {
                showNoResults();
            }
        } else {
            showError(result.error, result.recommendation);
        }
    } catch (error) {
        console.error('Listings search failed:', error);
        showError('Failed to search listings. Please try again.');
    } finally {
        hideLoading();
        
        // Reset form button
        const submitBtn = document.querySelector('#listingsSearchForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-search me-2"></i>Search Listings';
            submitBtn.disabled = false;
        }
    }
}

function displayListingsResults(listings, listingType) {
    const container = document.getElementById('resultsContainer');
    if (!container) return;
    
    let html = '<div class="row">';
    
    listings.forEach(listing => {
        html += createListingCard(listing, listingType);
    });
    
    html += '</div>';
    
    container.innerHTML = html;
    
    // Add animation class
    container.classList.add('fade-in');
    
    // Update results count
    const resultsCount = document.getElementById('resultsCount');
    if (resultsCount) {
        resultsCount.textContent = `Found ${listings.length} listings`;
    }
}

function updateListingTypeHeader(listingType) {
    const header = document.getElementById('listingTypeHeader');
    if (header) {
        header.textContent = listingType === 'sale' ? 'Sale' : 'Rental';
    }
}

// Initialize listings search page
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('listingsSearchForm');
    if (!form) return; // Not on listings page
    
    // Setup form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        currentPage = 0; // Reset pagination
        searchListings();
    });
    
    // Setup pagination
    setupPaginationHandlers(() => {
        // Re-run search with current parameters but new page
        const data = { ...currentListingsSearch };
        data.offset = currentPage * currentLimit;
        
        showLoading();
        makeApiRequest('/api/listings/search', data)
            .then(result => {
                if (result.success && result.data.listings) {
                    displayListingsResults(result.data.listings, result.listing_type);
                    
                    const hasMore = result.data.has_more || 
                                   (result.data.listings.length === currentLimit);
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
            
            if (Object.keys(currentListingsSearch).length > 0) {
                searchListings();
            }
        });
    }
    
    // Listing type change handlers
    const listingTypeRadios = document.querySelectorAll('input[name="listing_type"]');
    listingTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            togglePriceFields(this.value);
            updateFormLabels(this.value);
        });
    });
    
    function togglePriceFields(listingType) {
        const priceFields = document.querySelectorAll('.price-input');
        const rentFields = document.getElementById('rentFields');
        const priceLabel = document.getElementById('priceLabel');
        
        if (listingType === 'rental') {
            priceFields.forEach(field => field.style.display = 'none');
            if (rentFields) rentFields.style.display = 'flex';
            if (priceLabel) priceLabel.textContent = 'Rent Range';
        } else {
            priceFields.forEach(field => field.style.display = 'block');
            if (rentFields) rentFields.style.display = 'none';
            if (priceLabel) priceLabel.textContent = 'Price Range';
        }
    }
    
    function updateFormLabels(listingType) {
        const minLabel = document.getElementById('minPriceLabel');
        const maxLabel = document.getElementById('maxPriceLabel');
        
        if (listingType === 'rental') {
            if (minLabel) minLabel.textContent = 'Min Rent';
            if (maxLabel) maxLabel.textContent = 'Max Rent';
        } else {
            if (minLabel) minLabel.textContent = 'Min Price';
            if (maxLabel) maxLabel.textContent = 'Max Price';
        }
    }
    
    // Initialize form state
    const selectedType = document.querySelector('input[name="listing_type"]:checked');
    if (selectedType) {
        togglePriceFields(selectedType.value);
        updateFormLabels(selectedType.value);
    }
    
    // Form validation
    form.addEventListener('input', function() {
        validateListingsForm();
    });
    
    function validateListingsForm() {
        const city = document.getElementById('city').value.trim();
        const state = document.getElementById('state').value.trim();
        const zipcode = document.getElementById('zipcode').value.trim();
        const lat = document.getElementById('latitude').value;
        const lng = document.getElementById('longitude').value;
        
        const hasLocation = city.length > 0 || state.length > 0 || zipcode.length > 0;
        const hasGeo = lat && lng;
        
        const isValid = hasLocation || hasGeo;
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = !isValid;
        }
    }
    
    // Initial validation
    validateListingsForm();
});
