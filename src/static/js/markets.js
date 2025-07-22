/**
 * Markets statistics functionality
 */

async function searchMarkets() {
    try {
        hideError();
        hideInitialHelp();
        showLoading();

        // Get form data
        const data = getFormData('marketsSearchForm');

        // Make API request
        const result = await makeApiRequest('/api/markets/search', data);
        
        if (result.success) {
            displayMarketsResults(result.data);
            showResults();
        } else {
            showError(result.error, result.message || result.recommendation);
        }
    } catch (error) {
        console.error('Markets request failed:', error);
        showError('Failed to get market data. Please try again.');
    } finally {
        hideLoading();
        
        // Reset form button
        const submitBtn = document.querySelector('#marketsSearchForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-chart-bar me-2"></i>Get Market Data';
            submitBtn.disabled = false;
        }
    }
}

function displayMarketsResults(data) {
    // Update market location header
    updateMarketLocation(data);
    
    // Display sale market data
    if (data.sale_data || data.saleData) {
        displaySaleMarketData(data.sale_data || data.saleData);
        document.getElementById('saleMarketCard').style.display = 'block';
    } else {
        document.getElementById('saleMarketCard').style.display = 'none';
    }
    
    // Display rental market data
    if (data.rental_data || data.rentalData) {
        displayRentalMarketData(data.rental_data || data.rentalData);
        document.getElementById('rentalMarketCard').style.display = 'block';
    } else {
        document.getElementById('rentalMarketCard').style.display = 'none';
    }
    
    // Display overview
    displayMarketOverview(data);
}

function updateMarketLocation(data) {
    const locationElement = document.getElementById('marketLocation');
    if (locationElement) {
        let location = '';
        
        if (data.city && data.state) {
            location = `${data.city}, ${data.state}`;
        } else if (data.zip_code || data.zipCode) {
            location = `ZIP ${data.zip_code || data.zipCode}`;
        } else {
            location = 'Market Area';
        }
        
        locationElement.textContent = location;
    }
}

function displayMarketOverview(data) {
    const saleData = data.sale_data || data.saleData;
    const rentalData = data.rental_data || data.rentalData;
    
    // Total listings
    document.getElementById('totalSaleListings').textContent = 
        saleData?.total_listings || saleData?.totalListings || '-';
    document.getElementById('totalRentalListings').textContent = 
        rentalData?.total_listings || rentalData?.totalListings || '-';
    
    // Median prices
    document.getElementById('medianSalePrice').textContent = 
        saleData?.median_price || saleData?.medianPrice ? 
        formatCurrency(saleData.median_price || saleData.medianPrice) : '-';
    document.getElementById('medianRent').textContent = 
        rentalData?.median_rent || rentalData?.medianRent ? 
        formatCurrency(rentalData.median_rent || rentalData.medianRent) : '-';
}

function displaySaleMarketData(saleData) {
    // Last updated
    const lastUpdated = saleData.last_updated_date || saleData.lastUpdatedDate;
    if (lastUpdated) {
        document.getElementById('saleLastUpdated').textContent = `Last updated: ${formatDate(lastUpdated)}`;
    }
    
    // Overall statistics
    document.getElementById('saleAveragePrice').textContent = 
        saleData.average_price || saleData.averagePrice ? 
        formatCurrency(saleData.average_price || saleData.averagePrice) : '-';
    
    document.getElementById('saleMedianPrice').textContent = 
        saleData.median_price || saleData.medianPrice ? 
        formatCurrency(saleData.median_price || saleData.medianPrice) : '-';
    
    document.getElementById('salePricePerSqft').textContent = 
        saleData.median_price_per_square_foot || saleData.medianPricePerSquareFoot ? 
        formatCurrency(saleData.median_price_per_square_foot || saleData.medianPricePerSquareFoot) : '-';
    
    document.getElementById('saleDaysOnMarket').textContent = 
        saleData.median_days_on_market || saleData.medianDaysOnMarket || '-';
    
    // Property type breakdown
    displayPropertyTypeBreakdown(
        saleData.data_by_property_type || saleData.dataByPropertyType || [], 
        'salePropertyTypeContainer',
        'sale'
    );
    
    // Bedroom breakdown
    displayBedroomBreakdown(
        saleData.data_by_bedrooms || saleData.dataByBedrooms || [],
        'saleBedroomsContainer',
        'sale'
    );
}

function displayRentalMarketData(rentalData) {
    // Last updated
    const lastUpdated = rentalData.last_updated_date || rentalData.lastUpdatedDate;
    if (lastUpdated) {
        document.getElementById('rentalLastUpdated').textContent = `Last updated: ${formatDate(lastUpdated)}`;
    }
    
    // Overall statistics
    document.getElementById('rentalAverageRent').textContent = 
        rentalData.average_rent || rentalData.averageRent ? 
        formatCurrency(rentalData.average_rent || rentalData.averageRent) : '-';
    
    document.getElementById('rentalMedianRent').textContent = 
        rentalData.median_rent || rentalData.medianRent ? 
        formatCurrency(rentalData.median_rent || rentalData.medianRent) : '-';
    
    document.getElementById('rentalRentPerSqft').textContent = 
        rentalData.median_rent_per_square_foot || rentalData.medianRentPerSquareFoot ? 
        formatCurrency(rentalData.median_rent_per_square_foot || rentalData.medianRentPerSquareFoot) : '-';
    
    document.getElementById('rentalDaysOnMarket').textContent = 
        rentalData.median_days_on_market || rentalData.medianDaysOnMarket || '-';
    
    // Property type breakdown
    displayPropertyTypeBreakdown(
        rentalData.data_by_property_type || rentalData.dataByPropertyType || [], 
        'rentalPropertyTypeContainer',
        'rental'
    );
    
    // Bedroom breakdown
    displayBedroomBreakdown(
        rentalData.data_by_bedrooms || rentalData.dataByBedrooms || [],
        'rentalBedroomsContainer',
        'rental'
    );
}

function displayPropertyTypeBreakdown(data, containerId, type) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!data || data.length === 0) {
        container.innerHTML = '<p class="text-muted">No property type breakdown available.</p>';
        return;
    }
    
    const isRental = type === 'rental';
    const priceField = isRental ? 'median_rent' : 'median_price';
    const priceFieldAlt = isRental ? 'medianRent' : 'medianPrice';
    
    let html = '<div class="table-responsive"><table class="table table-sm breakdown-table">';
    html += '<thead><tr>';
    html += '<th>Property Type</th>';
    html += `<th>${isRental ? 'Median Rent' : 'Median Price'}</th>`;
    html += '<th>Total Listings</th>';
    html += '<th>New Listings</th>';
    html += '</tr></thead><tbody>';
    
    data.forEach(item => {
        const price = item[priceField] || item[priceFieldAlt];
        const totalListings = item.total_listings || item.totalListings;
        const newListings = item.new_listings || item.newListings;
        
        html += '<tr>';
        html += `<td>${item.property_type || item.propertyType || 'N/A'}</td>`;
        html += `<td>${price ? formatCurrency(price) : '-'}</td>`;
        html += `<td>${totalListings || '-'}</td>`;
        html += `<td>${newListings || '-'}</td>`;
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

function displayBedroomBreakdown(data, containerId, type) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!data || data.length === 0) {
        container.innerHTML = '<p class="text-muted">No bedroom breakdown available.</p>';
        return;
    }
    
    const isRental = type === 'rental';
    const priceField = isRental ? 'median_rent' : 'median_price';
    const priceFieldAlt = isRental ? 'medianRent' : 'medianPrice';
    
    let html = '<div class="table-responsive"><table class="table table-sm breakdown-table">';
    html += '<thead><tr>';
    html += '<th>Bedrooms</th>';
    html += `<th>${isRental ? 'Median Rent' : 'Median Price'}</th>`;
    html += '<th>Total Listings</th>';
    html += '<th>New Listings</th>';
    html += '</tr></thead><tbody>';
    
    data.forEach(item => {
        const price = item[priceField] || item[priceFieldAlt];
        const totalListings = item.total_listings || item.totalListings;
        const newListings = item.new_listings || item.newListings;
        
        html += '<tr>';
        html += `<td>${item.bedrooms || 'N/A'}</td>`;
        html += `<td>${price ? formatCurrency(price) : '-'}</td>`;
        html += `<td>${totalListings || '-'}</td>`;
        html += `<td>${newListings || '-'}</td>`;
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Initialize markets page
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('marketsSearchForm');
    if (!form) return; // Not on markets page
    
    // Setup form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        searchMarkets();
    });
    
    // Form validation
    form.addEventListener('input', function() {
        validateMarketsForm();
    });
    
    function validateMarketsForm() {
        const city = document.getElementById('city').value.trim();
        const state = document.getElementById('state').value.trim();
        const zipcode = document.getElementById('zipcode').value.trim();
        
        const isValid = city.length > 0 || state.length > 0 || zipcode.length > 0;
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = !isValid;
        }
    }
    
    // Auto-format state input
    const stateInput = document.getElementById('state');
    if (stateInput) {
        stateInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
    
    // Initial validation
    validateMarketsForm();
});
