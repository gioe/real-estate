/**
 * Deals Search JavaScript Module
 * Handles deal searching, display, and interactions
 */

class DealsSearchManager {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentDeals = [];
        this.metricExplanations = {}; // Store explanations by metric type and deal ID
    }

    initializeElements() {
        this.form = document.getElementById('dealsSearchForm');
        this.resultsSection = document.getElementById('resultsSection');
        this.summarySection = document.getElementById('summarySection');
        this.dealsResults = document.getElementById('dealsResults');
        this.noResults = document.getElementById('noResults');
        this.errorAlert = document.getElementById('errorAlert');
        this.errorMessage = document.getElementById('errorMessage');
        this.resultsCount = document.getElementById('resultsCount');
        
        // Summary elements
        this.totalDeals = document.getElementById('totalDeals');
        this.avgScore = document.getElementById('avgScore');
        this.avgCapRate = document.getElementById('avgCapRate');
        this.avgCashFlow = document.getElementById('avgCashFlow');
    }

    bindEvents() {
        this.form.addEventListener('submit', (e) => this.handleSearch(e));
    }

    async handleSearch(event) {
        event.preventDefault();
        
        const formData = new FormData(this.form);
        const searchParams = {
            zip_code: document.getElementById('zipCode').value.trim(),
            min_score: parseFloat(document.getElementById('minScore').value) || 0,
            min_cap_rate: parseFloat(document.getElementById('minCapRate').value) || 0,
            min_cash_flow: parseFloat(document.getElementById('minCashFlow').value) || 0,
            limit: parseInt(document.getElementById('maxResults').value) || 20
        };

        if (!searchParams.zip_code) {
            this.showError('Please enter a zip code');
            return;
        }

        this.hideAllSections();
        this.showLoadingSpinner();

        try {
            // Search for deals
            const dealsResponse = await this.searchDeals(searchParams);
            
            // Get summary data
            const summaryResponse = await this.getDealsSummary(searchParams.zip_code);
            
            if (dealsResponse.success) {
                this.currentDeals = dealsResponse.data;
                this.displayResults(dealsResponse, summaryResponse);
            } else {
                this.showError(dealsResponse.error || 'Failed to search deals');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('An error occurred while searching for deals');
        } finally {
            this.hideLoadingSpinner();
        }
    }

    async searchDeals(params) {
        const response = await fetch('/api/deals/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
        return await response.json();
    }

    async getDealsSummary(zipCode) {
        try {
            const response = await fetch(`/api/deals/summary/${zipCode}`);
            return await response.json();
        } catch (error) {
            console.warn('Failed to get summary data:', error);
            return { success: false };
        }
    }

    displayResults(dealsResponse, summaryResponse) {
        const deals = dealsResponse.data || [];
        
        if (deals.length === 0) {
            this.showNoResults();
            return;
        }

        // Display summary if available
        if (summaryResponse && summaryResponse.success) {
            this.displaySummary(summaryResponse.data);
        }

        // Display deals
        this.displayDeals(deals);
        this.updateResultsCount(deals.length, dealsResponse.zip_code);
        
        this.resultsSection.style.display = 'block';
    }

    displaySummary(summary) {
        this.totalDeals.textContent = summary.total_deals || 0;
        this.avgScore.textContent = summary.avg_deal_score ? `${summary.avg_deal_score}/100` : 'N/A';
        this.avgCapRate.textContent = summary.avg_cap_rate ? `${summary.avg_cap_rate}%` : 'N/A';
        this.avgCashFlow.textContent = summary.avg_monthly_cash_flow ? `$${summary.avg_monthly_cash_flow.toLocaleString()}` : 'N/A';
        
        this.summarySection.style.display = 'block';
    }

    displayDeals(deals) {
        const dealsHtml = deals.map(deal => this.createDealCard(deal)).join('');
        this.dealsResults.innerHTML = dealsHtml;
    }

    createDealCard(deal) {
        const score = deal.overall_score || deal.investment_score || 0;
        const scoreClass = this.getScoreClass(score);
        const capRate = deal.cap_rate ? `${deal.cap_rate.toFixed(2)}%` : 'N/A';
        const cashFlow = deal.monthly_cash_flow ? `$${deal.monthly_cash_flow.toLocaleString()}` : 'N/A';
        const price = deal.price || deal.purchase_price;
        const estimatedValue = deal.estimated_value;
        const estRent = deal.estimated_rent;
        
        return `
            <div class="card deal-card mb-3">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="card-title mb-1">
                                    <i class="fas fa-home me-2"></i>
                                    ${deal.address || 'Address Not Available'}
                                </h5>
                                <div class="deal-score ${scoreClass}">
                                    ${score.toFixed(1)}
                                </div>
                            </div>
                            
                            <div class="text-muted mb-2">
                                <i class="fas fa-map-marker-alt me-1"></i>
                                ${deal.city || 'Unknown'}, ${deal.state || 'Unknown'}
                                ${deal.zip_code ? `• ${deal.zip_code}` : ''}
                            </div>
                            
                            <div class="row g-2 mb-3">
                                ${deal.bedrooms ? `
                                    <div class="col-auto">
                                        <small class="badge bg-light text-dark">
                                            <i class="fas fa-bed me-1"></i>${deal.bedrooms} bed
                                        </small>
                                    </div>
                                ` : ''}
                                ${deal.bathrooms ? `
                                    <div class="col-auto">
                                        <small class="badge bg-light text-dark">
                                            <i class="fas fa-bath me-1"></i>${deal.bathrooms} bath
                                        </small>
                                    </div>
                                ` : ''}
                                ${deal.square_feet ? `
                                    <div class="col-auto">
                                        <small class="badge bg-light text-dark">
                                            <i class="fas fa-ruler-combined me-1"></i>${deal.square_feet.toLocaleString()} sqft
                                        </small>
                                    </div>
                                ` : ''}
                                <div class="col-auto">
                                    <small class="badge bg-info">
                                        <i class="fas fa-chart-line me-1"></i>${deal.source || 'Analysis'}
                                    </small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <div class="row g-2 text-center">
                                ${price ? this.createMetricTile(
                                    `$${price.toLocaleString()}`, 
                                    'List Price', 
                                    'text-primary',
                                    'list-price',
                                    this.getMetricExplanation('list-price', deal),
                                    6,
                                    deal.id || deal.property_id
                                ) : ''}
                                ${estimatedValue ? this.createMetricTile(
                                    `$${estimatedValue.toLocaleString()}`, 
                                    'Est. Value', 
                                    'text-success',
                                    'estimated-value',
                                    this.getMetricExplanation('estimated-value', deal),
                                    6,
                                    deal.id || deal.property_id
                                ) : ''}
                                ${this.createMetricTile(
                                    capRate, 
                                    'Cap Rate', 
                                    'text-warning',
                                    'cap-rate',
                                    this.getMetricExplanation('cap-rate', deal),
                                    6,
                                    deal.id || deal.property_id
                                )}
                                ${this.createMetricTile(
                                    cashFlow, 
                                    'Cash Flow', 
                                    'text-info',
                                    'cash-flow',
                                    this.getMetricExplanation('cash-flow', deal),
                                    6,
                                    deal.id || deal.property_id
                                )}
                                ${estRent ? this.createMetricTile(
                                    `$${estRent.toLocaleString()}/mo`, 
                                    'Est. Rent', 
                                    'text-secondary',
                                    'estimated-rent',
                                    this.getMetricExplanation('estimated-rent', deal),
                                    12,
                                    deal.id || deal.property_id
                                ) : ''}
                            </div>
                        </div>
                    </div>
                    
                    ${this.createAgentDescription(deal)}
                    ${this.createDealInsights(deal)}
                </div>
            </div>
        `;
    }

    createAgentDescription(deal) {
        if (!deal.agent_description) {
            return '';
        }
        
        return `
            <div class="mt-3 pt-3 border-top">
                <h6 class="text-primary mb-2">
                    <i class="fas fa-user-tie me-2"></i>Agent Analysis
                </h6>
                <div class="agent-description text-muted" style="line-height: 1.6;">
                    ${this.formatAgentDescription(deal.agent_description)}
                </div>
            </div>
        `;
    }
    
    formatAgentDescription(description) {
        if (!description) return '';
        
        // Convert markdown-style formatting to HTML
        return description
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // **bold** to <strong>
            .replace(/🌟|⭐|✅|👍|📊|💎|💰|⚠️|🏠|🔨|📈|💎|💰|🎯|🚀|👨‍💼/g, '<span class="me-1">$&</span>') // Add spacing to emojis
            .replace(/\n/g, '<br>'); // Line breaks
    }

    createMetricTile(value, label, colorClass, metricType, explanation, colSize = 6, dealId = null) {
        const uniqueId = `metric-${metricType}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Store explanation for later retrieval
        if (dealId) {
            const key = `${dealId}-${metricType}`;
            this.metricExplanations[key] = explanation;
        }
        
        return `
            <div class="col-${colSize}">
                <div class="border rounded p-2 metric-tile" 
                     data-metric-type="${metricType}"
                     data-deal-id="${dealId || ''}"
                     data-explanation-key="${dealId ? `${dealId}-${metricType}` : ''}">
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <div class="fw-bold ${colorClass}">${value}</div>
                        <i class="fas fa-info-circle metric-info-icon text-muted" 
                           data-bs-toggle="modal" 
                           data-bs-target="#metricModal"
                           data-metric-title="${this.escapeAttribute(label)}"
                           data-metric-type="${metricType}"
                           data-deal-id="${dealId || ''}"
                           title="Click for explanation"
                           style="cursor: pointer; font-size: 0.8rem;"></i>
                    </div>
                    <small class="text-muted">${label}</small>
                </div>
            </div>
        `;
    }

    getMetricExplanation(metricType, deal) {
        const price = deal.asking_price || deal.price || deal.purchase_price || 0;
        const estValue = deal.estimated_value || 0;
        const estRent = deal.estimated_rent || 0;
        const capRate = deal.cap_rate || 0;
        const cashFlow = deal.monthly_cash_flow || 0;
        const expenses = deal.estimated_expenses || 0;
        const overallScore = deal.overall_score || 0;
        const valueDiscount = deal.value_discount_pct || 0;

        switch (metricType) {
            case 'list-price':
                return `<strong>List Price</strong> is the asking price set by the seller. This is what they're currently asking for the property.<br><br>
                        <strong>Current Value:</strong> $${price.toLocaleString()}<br><br>
                        This represents the starting point for negotiations and should be compared to the estimated market value to determine if it's fairly priced.<br><br>
                        <strong>Investment Context:</strong> This is the amount you'll need to negotiate and potentially pay for the property.`;

            case 'estimated-value':
                const valueDiff = valueDiscount || (price && estValue ? ((estValue - price) / price * 100) : 0);
                return `<strong>Estimated Value</strong> is the AI-powered market valuation based on comparable properties, market trends, and property characteristics.<br><br>
                        <strong>Calculation Method:</strong> Automated Valuation Model (AVM)<br>
                        <strong>Estimated Value:</strong> $${estValue.toLocaleString()}<br>
                        <strong>List Price:</strong> $${price.toLocaleString()}<br>
                        <strong>Value Difference:</strong> ${valueDiff > 0 ? '+' : ''}${valueDiff.toFixed(1)}%<br><br>
                        ${valueDiff > 5 ? '✅ <strong>Great Value:</strong> Property appears significantly undervalued' : 
                          valueDiff > 0 ? '⚖️ <strong>Fair Value:</strong> Property is reasonably priced' :
                          valueDiff < -5 ? '⚠️ <strong>Premium Pricing:</strong> Property appears overvalued' :
                          '📊 <strong>Market Value:</strong> Property is priced at market value'}<br><br>
                        <strong>Investment Insight:</strong> ${Math.abs(valueDiff)}% ${valueDiff > 0 ? 'below' : 'above'} estimated market value.`;

            case 'cap-rate':
                if (capRate > 0) {
                    const annualRent = estRent * 12;
                    const netIncome = annualRent - (expenses * 12);
                    return `<strong>Capitalization Rate (Cap Rate)</strong> measures the return on investment based on the property's income potential.<br><br>
                            <strong>Formula:</strong> (Annual Net Income ÷ Property Price) × 100<br><br>
                            <strong>Calculation:</strong><br>
                            • Annual Gross Rent: $${annualRent.toLocaleString()}<br>
                            • Annual Expenses: $${(expenses * 12).toLocaleString()}<br>
                            • Annual Net Income: $${netIncome.toLocaleString()}<br>
                            • Property Price: $${price.toLocaleString()}<br>
                            • Cap Rate: <strong>${capRate.toFixed(1)}%</strong><br><br>
                            <strong>Interpretation:</strong><br>
                            ${capRate >= 10 ? '🌟 <strong>Excellent:</strong> Very strong return' :
                              capRate >= 8 ? '✅ <strong>Good:</strong> Above-average return' :
                              capRate >= 6 ? '👍 <strong>Fair:</strong> Decent return' :
                              '⚠️ <strong>Low:</strong> Below-average return'}`;
                } else {
                    return `<strong>Capitalization Rate (Cap Rate)</strong> measures the return on investment based on rental income potential.<br><br>
                            <strong>Formula:</strong> (Annual Net Income ÷ Property Price) × 100<br><br>
                            <strong>Current Status:</strong> ⚠️ Cap rate data not available for this property.<br><br>
                            <strong>What this means:</strong><br>
                            • This might be a property for sale (not rental)<br>
                            • Rental income estimates are not available<br>
                            • You may need to research local rental rates manually<br><br>
                            <strong>Investment Context:</strong> Consider if this property is suitable for rental income or if it's primarily an appreciation play.`;
                }

            case 'cash-flow':
                if (cashFlow !== 0) {
                    const monthlyIncome = estRent || 0;
                    const monthlyExpenses = expenses || 0;
                    const mortgage = (price * 0.8 * 0.0067) || 0; // Rough mortgage estimate
                    return `<strong>Monthly Cash Flow</strong> is the net monthly income after all expenses are paid.<br><br>
                            <strong>Formula:</strong> Monthly Rent - Monthly Expenses - Mortgage Payment<br><br>
                            <strong>Calculation:</strong><br>
                            • Monthly Rent: $${monthlyIncome.toLocaleString()}<br>
                            • Operating Expenses: $${monthlyExpenses.toLocaleString()}<br>
                            • Estimated Mortgage: $${mortgage.toFixed(0)}<br>
                            • <strong>Net Cash Flow: $${cashFlow.toFixed(0)}</strong><br><br>
                            <strong>Interpretation:</strong><br>
                            ${cashFlow >= 500 ? '💰 <strong>Excellent:</strong> Strong positive cash flow' :
                              cashFlow >= 200 ? '✅ <strong>Good:</strong> Healthy cash flow' :
                              cashFlow >= 0 ? '👍 <strong>Break-even:</strong> Covers expenses' :
                              '⚠️ <strong>Negative:</strong> Requires monthly contribution'}<br><br>
                            <em>Note: Mortgage estimate assumes 20% down, 6.7% interest rate</em>`;
                } else {
                    return `<strong>Monthly Cash Flow</strong> is the net monthly income after all expenses are paid.<br><br>
                            <strong>Formula:</strong> Monthly Rent - Operating Expenses - Mortgage Payment<br><br>
                            <strong>Current Status:</strong> ⚠️ Cash flow data not available for this property.<br><br>
                            <strong>What this means:</strong><br>
                            • Rental income projections not available<br>
                            • This may be a fix-and-flip or appreciation play<br>
                            • You'll need to research local rental rates<br><br>
                            <strong>Investment Context:</strong> Consider your investment strategy - is this for rental income or capital appreciation?`;
                }

            case 'estimated-rent':
                if (estRent > 0) {
                    const rentYield = price ? (estRent / price * 100 * 12) : 0;
                    return `<strong>Estimated Monthly Rent</strong> is the AI-predicted rental income based on comparable rentals in the area.<br><br>
                            <strong>Current Estimate:</strong> $${estRent.toLocaleString()}/month<br>
                            <strong>Annual Rent:</strong> $${(estRent * 12).toLocaleString()}<br>
                            <strong>Gross Rental Yield:</strong> ${rentYield.toFixed(2)}%<br><br>
                            <strong>Calculation Method:</strong><br>
                            • Comparable rental analysis<br>
                            • Property size and features<br>
                            • Local market conditions<br>
                            • Recent rental transactions<br><br>
                            <strong>Rental Yield Analysis:</strong><br>
                            ${rentYield >= 12 ? '🌟 <strong>Excellent:</strong> Very high rental yield' :
                              rentYield >= 10 ? '✅ <strong>Good:</strong> Above-average yield' :
                              rentYield >= 8 ? '👍 <strong>Fair:</strong> Decent rental yield' :
                              '⚠️ <strong>Low:</strong> Below-average yield'}`;
                } else {
                    return `<strong>Estimated Monthly Rent</strong> is the predicted rental income this property could generate.<br><br>
                            <strong>Current Status:</strong> ⚠️ Rental estimates not available for this property.<br><br>
                            <strong>What this means:</strong><br>
                            • Limited comparable rental data in the area<br>
                            • Property may not be suitable for rental<br>
                            • Manual market research recommended<br><br>
                            <strong>Research Suggestions:</strong><br>
                            • Check Zillow, Rentometer, or local listings<br>
                            • Contact local property managers<br>
                            • Analyze similar properties in the neighborhood<br><br>
                            <strong>Investment Context:</strong> Consider if rental income is part of your investment strategy for this property.`;
                }

            default:
                return `<strong>Metric Information</strong><br><br>
                        Detailed calculation information is not available for this specific metric. This could be due to:<br><br>
                        • Limited data availability<br>
                        • Property type restrictions<br>
                        • Market data limitations<br><br>
                        <strong>Recommendation:</strong> Contact a local real estate professional for more detailed analysis.`;
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    escapeAttribute(text) {
        if (!text) return '';
        return text.replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    createDealInsights(deal) {
        const insights = [];
        
        if (deal.overall_score >= 80) {
            insights.push('<span class="badge bg-success">Excellent Deal</span>');
        } else if (deal.overall_score >= 70) {
            insights.push('<span class="badge bg-warning">Good Deal</span>');
        }
        
        if (deal.cap_rate >= 10) {
            insights.push('<span class="badge bg-primary">High Cap Rate</span>');
        }
        
        if (deal.monthly_cash_flow >= 500) {
            insights.push('<span class="badge bg-info">Strong Cash Flow</span>');
        }
        
        if (deal.confidence_score >= 0.8) {
            insights.push('<span class="badge bg-secondary">High Confidence</span>');
        }
        
        if (insights.length === 0) {
            return '';
        }
        
        return `
            <div class="mt-3 pt-3 border-top">
                <div class="d-flex flex-wrap gap-2">
                    ${insights.join('')}
                </div>
            </div>
        `;
    }

    getScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 70) return 'good';
        if (score >= 60) return 'fair';
        return 'poor';
    }

    updateResultsCount(count, zipCode) {
        this.resultsCount.textContent = `${count} deals found in ${zipCode}`;
    }

    showNoResults() {
        this.noResults.style.display = 'block';
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorAlert.style.display = 'block';
    }

    hideAllSections() {
        this.resultsSection.style.display = 'none';
        this.summarySection.style.display = 'none';
        this.noResults.style.display = 'none';
        this.errorAlert.style.display = 'none';
    }

    showLoadingSpinner() {
        document.getElementById('loadingSpinner').style.display = 'flex';
    }

    hideLoadingSpinner() {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
}

// Initialize the deals search manager when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.dealsSearchManager = new DealsSearchManager();
});
