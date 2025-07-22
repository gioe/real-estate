/**
 * AVM (Automated Valuation Model) functionality
 */

let currentEstimateType = 'value';

async function getAVMEstimate() {
    try {
        hideError();
        hideInitialHelp();
        showLoading();

        // Get form data
        const data = getFormData('avmSearchForm');
        
        // Determine API endpoint based on estimate type
        const endpoint = currentEstimateType === 'value' ? '/api/avm/value' : '/api/avm/rent';

        // Make API request
        const result = await makeApiRequest(endpoint, data);
        
        if (result.success) {
            displayAVMResults(result.data, currentEstimateType);
            showResults();
        } else {
            showError(result.error, result.message || result.recommendation);
        }
    } catch (error) {
        console.error('AVM request failed:', error);
        showError('Failed to get estimate. Please try again.');
    } finally {
        hideLoading();
        
        // Reset form button
        const submitBtn = document.querySelector('#avmSearchForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-calculator me-2"></i>Get Estimate';
            submitBtn.disabled = false;
        }
    }
}

function displayAVMResults(data, estimateType) {
    const isRental = estimateType === 'rent';
    
    // Update estimate type title
    const titleElement = document.getElementById('estimateTypeTitle');
    if (titleElement) {
        titleElement.textContent = isRental ? 'Rental Value' : 'Property Value';
    }
    
    const labelElement = document.getElementById('estimateLabel');
    if (labelElement) {
        labelElement.textContent = isRental ? 'Rent' : 'Value';
    }
    
    // Update main estimate values
    const mainValue = isRental ? data.rent : data.price;
    const lowValue = isRental ? data.rent_range_low || data.rentRangeLow : data.price_range_low || data.priceRangeLow;
    const highValue = isRental ? data.rent_range_high || data.rentRangeHigh : data.price_range_high || data.priceRangeHigh;
    
    document.getElementById('estimateValue').textContent = mainValue ? formatCurrency(mainValue) : 'N/A';
    document.getElementById('estimateLow').textContent = lowValue ? formatCurrency(lowValue) : 'N/A';
    document.getElementById('estimateHigh').textContent = highValue ? formatCurrency(highValue) : 'N/A';
    
    // Update progress bar for confidence range
    updateConfidenceRange(lowValue, mainValue, highValue);
    
    // Show property location if available
    if (data.latitude && data.longitude) {
        document.getElementById('propLatitude').textContent = data.latitude.toFixed(6);
        document.getElementById('propLongitude').textContent = data.longitude.toFixed(6);
        document.getElementById('locationCard').style.display = 'block';
    } else {
        document.getElementById('locationCard').style.display = 'none';
    }
    
    // Display comparables
    displayComparables(data.comparables || [], isRental);
}

function updateConfidenceRange(low, estimate, high) {
    if (!low || !estimate || !high) {
        return;
    }
    
    const total = high - low;
    const lowRange = estimate - low;
    const highRange = high - estimate;
    
    const lowPercent = (lowRange / total) * 100;
    const estimatePercent = 2; // Small fixed width for the estimate line
    const highPercent = (highRange / total) * 100;
    
    const progressBars = document.querySelectorAll('#confidenceRange .progress-bar');
    if (progressBars.length >= 3) {
        progressBars[0].style.width = `${lowPercent}%`;
        progressBars[1].style.width = `${estimatePercent}%`;
        progressBars[2].style.width = `${highPercent}%`;
    }
}

function displayComparables(comparables, isRental) {
    const container = document.getElementById('comparablesContainer');
    const countElement = document.getElementById('comparablesCount');
    
    if (!container || !countElement) return;
    
    countElement.textContent = comparables.length;
    
    if (comparables.length === 0) {
        container.innerHTML = '<p class="text-muted">No comparable properties available.</p>';
        return;
    }
    
    let html = '';
    comparables.forEach(comparable => {
        html += createComparableCard(comparable, isRental);
    });
    
    container.innerHTML = html;
}

// Initialize AVM page
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('avmSearchForm');
    if (!form) return; // Not on AVM page
    
    // Setup form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        getAVMEstimate();
    });
    
    // Setup estimate type change handlers
    const estimateTypeRadios = document.querySelectorAll('input[name="estimate_type"]');
    estimateTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            currentEstimateType = this.value;
            updateEstimateTypeLabels(this.value);
        });
    });
    
    function updateEstimateTypeLabels(estimateType) {
        const isRental = estimateType === 'rent';
        
        // Update button text
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            const icon = isRental ? 'fa-home' : 'fa-calculator';
            const text = isRental ? 'Get Rental Estimate' : 'Get Value Estimate';
            submitBtn.innerHTML = `<i class="fas ${icon} me-2"></i>${text}`;
        }
    }
    
    // Initialize estimate type
    const selectedType = document.querySelector('input[name="estimate_type"]:checked');
    if (selectedType) {
        currentEstimateType = selectedType.value;
        updateEstimateTypeLabels(currentEstimateType);
    }
    
    // Form validation
    form.addEventListener('input', function() {
        validateAVMForm();
    });
    
    function validateAVMForm() {
        const address = document.getElementById('address').value.trim();
        const zipcode = document.getElementById('zipcode').value.trim();
        const lat = document.getElementById('latitude').value;
        const lng = document.getElementById('longitude').value;
        
        const hasAddress = address.length > 0 || zipcode.length > 0;
        const hasCoords = lat && lng;
        
        const isValid = hasAddress || hasCoords;
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = !isValid;
        }
        
        // Show/hide coordinate section based on address input
        const coordsAccordion = document.getElementById('coordsCollapse');
        if (coordsAccordion) {
            if (hasAddress && !hasCoords) {
                // If address is provided, collapse coordinates
                const bsCollapse = new bootstrap.Collapse(coordsAccordion, { hide: true });
            }
        }
    }
    
    // Coordinate input handlers
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    
    if (latInput && lngInput) {
        [latInput, lngInput].forEach(input => {
            input.addEventListener('input', function() {
                // Clear address fields if coordinates are being entered
                if (this.value && (latInput.value || lngInput.value)) {
                    document.getElementById('address').value = '';
                    document.getElementById('zipcode').value = '';
                }
            });
        });
    }
    
    // Address input handlers
    const addressInput = document.getElementById('address');
    const zipcodeInput = document.getElementById('zipcode');
    
    if (addressInput && zipcodeInput) {
        [addressInput, zipcodeInput].forEach(input => {
            input.addEventListener('input', function() {
                // Clear coordinates if address is being entered
                if (this.value) {
                    if (latInput) latInput.value = '';
                    if (lngInput) lngInput.value = '';
                }
            });
        });
    }
    
    // Initial validation
    validateAVMForm();
});
