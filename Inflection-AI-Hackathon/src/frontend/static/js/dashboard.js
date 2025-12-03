/**
 * Agri-Adapt AI Dashboard JavaScript
 * Handles API integration, form submission, and visualizations
 */

class AgriAdaptDashboard {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.counties = [];
        this.currentPrediction = null;
        this.charts = {};
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadCounties();
            this.setupEventListeners();
            this.setupCharts();
            console.log('Dashboard initialized successfully');
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.showError('Failed to initialize dashboard. Please refresh the page.');
        }
    }
    
    async loadCounties() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/counties`);
            if (!response.ok) throw new Error('Failed to fetch counties');
            
            const data = await response.json();
            this.counties = data.counties;
            this.populateCountyDropdown();
            
        } catch (error) {
            console.error('Error loading counties:', error);
            // Fallback to hardcoded counties if API fails
            this.counties = [
                "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita Taveta", "Garissa",
                "Wajir", "Mandera", "Marsabit", "Isiolo", "Meru", "Tharaka Nithi", "Embu",
                "Kitui", "Machakos", "Makueni", "Nyandarua", "Nyeri", "Kirinyaga", "Murang'a",
                "Kiambu", "Turkana", "West Pokot", "Samburu", "Trans Nzoia", "Uasin Gishu",
                "Elgeyo Marakwet", "Nandi", "Baringo", "Laikipia", "Nakuru", "Narok",
                "Kajiado", "Kericho", "Bomet", "Kakamega", "Vihiga", "Bungoma", "Busia",
                "Siaya", "Kisumu", "Homa Bay", "Migori", "Kisii", "Nyamira", "Nairobi"
            ];
            this.populateCountyDropdown();
        }
    }
    
    populateCountyDropdown() {
        const countySelect = document.getElementById('county');
        if (!countySelect) return;
        
        // Clear existing options
        countySelect.innerHTML = '<option value="">Select your county</option>';
        
        // Add county options
        this.counties.forEach(county => {
            const option = document.createElement('option');
            option.value = county;
            option.textContent = county;
            countySelect.appendChild(option);
        });
    }
    
    setupEventListeners() {
        const form = document.getElementById('resilienceForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        // Add input validation
        this.setupInputValidation();
    }
    
    setupInputValidation() {
        const inputs = ['rainfall', 'soilPh', 'organicCarbon'];
        
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('blur', () => this.validateInput(input));
                input.addEventListener('input', () => this.clearValidation(input));
            }
        });
    }
    
    validateInput(input) {
        const value = parseFloat(input.value);
        const isValid = this.isValidInput(input.id, value);
        
        if (!isValid) {
            input.classList.add('is-invalid');
            this.showInputError(input, this.getErrorMessage(input.id, value));
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            this.clearInputError(input);
        }
        
        return isValid;
    }
    
    isValidInput(inputId, value) {
        if (isNaN(value)) return false;
        
        switch (inputId) {
            case 'rainfall':
                return value >= 0 && value <= 3000;
            case 'soilPh':
                return value >= 4.0 && value <= 10.0;
            case 'organicCarbon':
                return value >= 0.1 && value <= 10.0;
            default:
                return true;
        }
    }
    
    getErrorMessage(inputId, value) {
        if (isNaN(value)) return 'Please enter a valid number';
        
        switch (inputId) {
            case 'rainfall':
                return 'Rainfall must be between 0 and 3000 mm';
            case 'soilPh':
                return 'Soil pH must be between 4.0 and 10.0';
            case 'organicCarbon':
                return 'Organic carbon must be between 0.1 and 10.0%';
            default:
                return 'Invalid input';
        }
    }
    
    showInputError(input, message) {
        this.clearInputError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        input.parentNode.appendChild(errorDiv);
    }
    
    clearInputError(input) {
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) errorDiv.remove();
    }
    
    clearValidation(input) {
        input.classList.remove('is-valid', 'is-invalid');
        this.clearInputError(input);
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        // Validate all inputs
        const inputs = ['rainfall', 'soilPh', 'organicCarbon', 'county'];
        let isValid = true;
        
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input && inputId !== 'county') {
                if (!this.validateInput(input)) {
                    isValid = false;
                }
            }
        });
        
        if (!isValid) {
            this.showError('Please correct the errors above before submitting.');
            return;
        }
        
        // Get form data
        const formData = this.getFormData();
        if (!formData) return;
        
        // Show loading state
        this.showLoading(true);
        
        try {
            const prediction = await this.getPrediction(formData);
            this.displayResults(prediction);
            this.showLoading(false);
        } catch (error) {
            console.error('Prediction failed:', error);
            this.showError('Failed to get prediction. Please try again.');
            this.showLoading(false);
        }
    }
    
    getFormData() {
        const county = document.getElementById('county').value;
        const rainfall = parseFloat(document.getElementById('rainfall').value);
        const soilPh = parseFloat(document.getElementById('soilPh').value);
        const organicCarbon = parseFloat(document.getElementById('organicCarbon').value);
        
        if (!county) {
            this.showError('Please select a county.');
            return null;
        }
        
        return {
            county,
            rainfall,
            soil_ph: soilPh,
            organic_carbon: organicCarbon
        };
    }
    
    async getPrediction(formData) {
        const response = await fetch(`${this.apiBaseUrl}/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Request-Timestamp': new Date().toISOString()
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Prediction request failed');
        }
        
        return await response.json();
    }
    
    displayResults(prediction) {
        this.currentPrediction = prediction;
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        
        // Update gauge
        this.updateGauge(prediction.prediction.resilience_score);
        
        // Update metrics
        this.updateMetrics(prediction);
        
        // Update feature importance chart
        this.updateFeatureImportance(prediction.model_info.feature_importance);
        
        // Add recommendation
        this.addRecommendation(prediction.prediction.resilience_score);
        
        // Scroll to results
        resultsSection?.scrollIntoView({ behavior: 'smooth' });
    }
    
    updateGauge(score) {
        const gaugeValue = document.getElementById('gaugeValue');
        if (gaugeValue) {
            gaugeValue.textContent = `${score}%`;
        }
        
        // Update gauge chart
        if (this.charts.gauge) {
            this.charts.gauge.data.datasets[0].data = [score, 100 - score];
            this.charts.gauge.update();
        }
    }
    
    updateMetrics(prediction) {
        const predictedYield = document.getElementById('predictedYield');
        if (predictedYield) {
            predictedYield.textContent = `${prediction.prediction.predicted_yield} t/ha`;
        }
    }
    
    updateFeatureImportance(featureImportance) {
        if (this.charts.featureImportance) {
            const labels = Object.keys(featureImportance);
            const data = Object.values(featureImportance);
            
            this.charts.featureImportance.data.labels = labels;
            this.charts.featureImportance.data.datasets[0].data = data;
            this.charts.featureImportance.update();
        }
    }
    
    addRecommendation(score) {
        const recommendationDiv = document.getElementById('recommendation');
        if (!recommendationDiv) return;
        
        let recommendation = '';
        let alertClass = '';
        
        if (score >= 70) {
            recommendation = '<strong>High Resilience:</strong> Excellent conditions for maize farming. Consider drought-tolerant varieties for insurance.';
            alertClass = 'alert-success';
        } else if (score >= 50) {
            recommendation = '<strong>Medium Resilience:</strong> Moderate conditions. Use drought-resistant seeds and consider irrigation.';
            alertClass = 'alert-warning';
        } else {
            recommendation = '<strong>Low Resilience:</strong> Challenging conditions. Consider alternative crops or extensive irrigation.';
            alertClass = 'alert-danger';
        }
        
        recommendationDiv.innerHTML = `
            <div class="alert ${alertClass} mb-0" role="alert">
                <i class="fas fa-lightbulb me-2"></i>
                ${recommendation}
            </div>
        `;
    }
    
    setupCharts() {
        this.setupGaugeChart();
        this.setupFeatureImportanceChart();
    }
    
    setupGaugeChart() {
        const ctx = document.getElementById('resilienceGauge');
        if (!ctx) return;
        
        this.charts.gauge = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Resilience Score', 'Remaining'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#198754', '#e9ecef'],
                    borderWidth: 0,
                    cutout: '75%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        });
    }
    
    setupFeatureImportanceChart() {
        const ctx = document.getElementById('featureImportanceChart');
        if (!ctx) return;
        
        this.charts.featureImportance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Rainfall', 'Soil pH', 'Organic Carbon'],
                datasets: [{
                    label: 'Feature Importance',
                    data: [0.4, 0.35, 0.25],
                    backgroundColor: ['#198754', '#0d6efd', '#ffc107'],
                    borderColor: ['#157347', '#0b5ed7', '#e0a800'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${(context.parsed.y * 100).toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            callback: function(value) {
                                return (value * 100).toFixed(0) + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    showLoading(show) {
        const calculateBtn = document.getElementById('calculateBtn');
        if (calculateBtn) {
            calculateBtn.disabled = show;
            calculateBtn.innerHTML = show ? 
                '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Calculating...' :
                '<i class="fas fa-calculator me-2"></i>Calculate Resilience Score';
        }
        
        // Show/hide loading modal
        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        if (show) {
            loadingModal.show();
        } else {
            loadingModal.hide();
        }
    }
    
    showError(message) {
        // Create error alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of main content
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
    
    showSuccess(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const main = document.querySelector('main');
        if (main) {
            main.insertBefore(alertDiv, main.firstChild);
            
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.agriAdaptDashboard = new AgriAdaptDashboard();
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        // Show fallback error message
        const main = document.querySelector('main');
        if (main) {
            main.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">Dashboard Error</h4>
                    <p>Failed to initialize the dashboard. Please refresh the page or contact support.</p>
                    <hr>
                    <p class="mb-0">Error: ${error.message}</p>
                </div>
            `;
        }
    }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AgriAdaptDashboard;
}
