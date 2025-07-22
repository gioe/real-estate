/**
 * Main JavaScript file for RentCast API Explorer
 * Handles common functionality across all pages
 */

// Global variables
let currentPage = 0;
let currentLimit = 20;
let currentResults = [];

// Utility functions
function formatCurrency(amount) {
    if (!amount) return '-';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatNumber(number) {
    if (!number) return '-';
    return new Intl.NumberFormat('en-US').format(number);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    try {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (e) {
        return dateString;
    }
}

function formatDistance(distance) {
    if (!distance) return '-';
    return `${distance.toFixed(2)} mi`;
}

function formatCorrelation(correlation) {
    if (!correlation) return '-';
    return `${(correlation * 100).toFixed(1)}%`;
}

function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

function showError(message, recommendation = '') {
    hideLoading();
    const errorElement = document.getElementById('errorMessage');
    if (errorElement) {
        document.getElementById('errorText').textContent = message;
        if (recommendation) {
            document.getElementById('errorRecommendation').textContent = recommendation;
        }
        errorElement.style.display = 'block';
    } else {
        alert('Error: ' + message);
    }
}

function hideError() {
    const errorElement = document.getElementById('errorMessage');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

function showNoResults() {
    hideLoading();
    const noResultsElement = document.getElementById('noResultsMessage');
    if (noResultsElement) {
        noResultsElement.style.display = 'block';
    }
}

function hideNoResults() {
    const noResultsElement = document.getElementById('noResultsMessage');
    if (noResultsElement) {
        noResultsElement.style.display = 'none';
    }
}

function showResults() {
    hideLoading();
    hideError();
    hideNoResults();
    const resultsElement = document.getElementById('resultsSection');
    if (resultsElement) {
        resultsElement.style.display = 'block';
    }
}

function hideInitialHelp() {
    const helpElement = document.getElementById('initialHelp');
    if (helpElement) {
        helpElement.style.display = 'none';
    }
}

// API request wrapper
async function makeApiRequest(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Request failed');
        }

        return result;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Form data collection
function getFormData(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (value.trim() !== '') {
            data[key] = value;
        }
    }
    
    return data;
}

// Create property/listing card HTML
function createPropertyCard(property) {
    const bedrooms = property.bedrooms || 0;
    const bathrooms = property.bathrooms || 0;
    const sqft = property.square_footage || property.squareFootage;
    const yearBuilt = property.year_built || property.yearBuilt;
    
    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="property-card">
                <div class="property-image">
                    <i class="fas fa-home"></i>
                </div>
                <div class="property-details">
                    <div class="property-title">${property.formatted_address || property.formattedAddress || 'Address Not Available'}</div>
                    <div class="property-address">${property.city || ''}, ${property.state || ''} ${property.zip_code || property.zipCode || ''}</div>
                    <div class="property-specs">
                        <span><i class="fas fa-bed me-1"></i>${bedrooms} bed</span>
                        <span><i class="fas fa-bath me-1"></i>${bathrooms} bath</span>
                        ${sqft ? `<span><i class="fas fa-expand me-1"></i>${formatNumber(sqft)} sqft</span>` : ''}
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            ${property.property_type || property.propertyType ? 
                                `<span class="badge badge-custom badge-property-type">${property.property_type || property.propertyType}</span>` : ''}
                            ${yearBuilt ? `<small class="text-muted d-block mt-1">Built ${yearBuilt}</small>` : ''}
                        </div>
                        ${property.id ? `<a href="/property/${property.id}" class="btn btn-sm btn-outline-primary">View Details</a>` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createListingCard(listing, listingType = 'sale') {
    const bedrooms = listing.bedrooms || 0;
    const bathrooms = listing.bathrooms || 0;
    const sqft = listing.square_footage || listing.squareFootage;
    const price = listing.price;
    const daysOnMarket = listing.days_on_market || listing.daysOnMarket;
    
    const priceLabel = listingType === 'sale' ? 'Price' : 'Rent';
    const priceDisplay = price ? formatCurrency(price) : 'Price Not Available';
    
    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="listing-card">
                <div class="listing-image">
                    <i class="fas ${listingType === 'sale' ? 'fa-home' : 'fa-key'}"></i>
                </div>
                <div class="listing-details">
                    <div class="listing-title">${listing.formatted_address || listing.formattedAddress || 'Address Not Available'}</div>
                    <div class="listing-address">${listing.city || ''}, ${listing.state || ''} ${listing.zip_code || listing.zipCode || ''}</div>
                    <div class="listing-specs">
                        <span><i class="fas fa-bed me-1"></i>${bedrooms} bed</span>
                        <span><i class="fas fa-bath me-1"></i>${bathrooms} bath</span>
                        ${sqft ? `<span><i class="fas fa-expand me-1"></i>${formatNumber(sqft)} sqft</span>` : ''}
                    </div>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div class="listing-price">${priceDisplay}</div>
                        ${daysOnMarket ? `<span class="badge badge-custom badge-days-on-market">${daysOnMarket} days</span>` : ''}
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            ${listing.property_type || listing.propertyType ? 
                                `<span class="badge badge-custom badge-property-type">${listing.property_type || listing.propertyType}</span>` : ''}
                            ${listing.status ? 
                                `<span class="badge badge-custom badge-status-${listing.status.toLowerCase()}">${listing.status}</span>` : ''}
                        </div>
                        ${listing.id ? `<a href="/listing/${listingType}/${listing.id}" class="btn btn-sm btn-outline-primary">View Details</a>` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createComparableCard(comparable, isRental = false) {
    const price = isRental ? comparable.rent : comparable.price;
    const priceLabel = isRental ? 'Rent' : 'Price';
    
    return `
        <div class="comparable-card">
            <div class="row">
                <div class="col-md-8">
                    <div class="fw-bold">${comparable.formatted_address || comparable.formattedAddress || 'Address Not Available'}</div>
                    <small class="text-muted">${comparable.city || ''}, ${comparable.state || ''} ${comparable.zip_code || comparable.zipCode || ''}</small>
                    <div class="mt-2">
                        <span class="me-3"><i class="fas fa-bed me-1"></i>${comparable.bedrooms || 0} bed</span>
                        <span class="me-3"><i class="fas fa-bath me-1"></i>${comparable.bathrooms || 0} bath</span>
                        ${comparable.square_footage || comparable.squareFootage ? 
                            `<span><i class="fas fa-expand me-1"></i>${formatNumber(comparable.square_footage || comparable.squareFootage)} sqft</span>` : ''}
                    </div>
                </div>
                <div class="col-md-4 text-end">
                    <div class="comparable-price">${price ? formatCurrency(price) : 'N/A'}</div>
                    <div class="d-flex justify-content-end gap-2 mt-1">
                        ${comparable.distance ? `<small class="comparable-distance">${formatDistance(comparable.distance)}</small>` : ''}
                        ${comparable.correlation ? `<small class="comparable-correlation">${formatCorrelation(comparable.correlation)}</small>` : ''}
                    </div>
                    ${comparable.days_old || comparable.daysOld ? 
                        `<small class="text-muted">${comparable.days_old || comparable.daysOld} days old</small>` : ''}
                </div>
            </div>
        </div>
    `;
}

// Pagination functions
function updatePagination(hasMore, totalCount = null) {
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    const resultsCount = document.getElementById('resultsCount');
    
    if (prevBtn) {
        prevBtn.disabled = currentPage === 0;
    }
    
    if (nextBtn) {
        nextBtn.disabled = !hasMore;
    }
    
    if (resultsCount && totalCount !== null) {
        const startResult = currentPage * currentLimit + 1;
        const endResult = Math.min((currentPage + 1) * currentLimit, totalCount);
        resultsCount.textContent = `Showing ${startResult}-${endResult} of ${formatNumber(totalCount)} results`;
    }
}

function setupPaginationHandlers(searchFunction) {
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    if (prevBtn) {
        prevBtn.onclick = () => {
            if (currentPage > 0) {
                currentPage--;
                searchFunction();
            }
        };
    }
    
    if (nextBtn) {
        nextBtn.onclick = () => {
            currentPage++;
            searchFunction();
        };
    }
}

// Initialize common functionality when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    });
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add loading states to form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.dataset.noLoading) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
                submitBtn.disabled = true;
                
                // Reset button after 30 seconds as failsafe
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 30000);
            }
        });
    });
});
