// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initImageUpload();
    initButtonListeners();
    initDropZone();
    initCounterAnimation();
});

// Image Upload Functionality
function initImageUpload() {
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const preview = document.getElementById('preview');
    
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    imagePreview.classList.remove('hidden');
                }
                reader.readAsDataURL(file);
            }
        });
    }
}

// Initialize Button Event Listeners
function initButtonListeners() {
    // Load Model Button
    const loadModelBtn = document.getElementById('loadModelBtn');
    if (loadModelBtn) {
        loadModelBtn.addEventListener('click', function() {
            showLoading(true);
            
            // Simulate loading delay (would be a real API call in production)
            setTimeout(function() {
                showLoading(false);
                showNotification('Model loaded successfully', 'success');
            }, 1500);
        });
    }
    
    // Load Indices Button
    const loadIndicesBtn = document.getElementById('loadIndicesBtn');
    if (loadIndicesBtn) {
        loadIndicesBtn.addEventListener('click', function() {
            showLoading(true);
            
            // Simulate loading delay (would be a real API call in production)
            setTimeout(function() {
                showLoading(false);
                showNotification('Class indices loaded successfully', 'success');
            }, 1200);
        });
    }
    
    // Diagnose Button
    const diagnoseBtn = document.getElementById('diagnoseBtn');
    if (diagnoseBtn) {
        diagnoseBtn.addEventListener('click', function() {
            diagnose();
        });
    }
    
    // Download Report Button
    const downloadReportBtn = document.getElementById('downloadReportBtn');
    if (downloadReportBtn) {
        downloadReportBtn.addEventListener('click', function() {
            downloadPDF();
        });
    }
    
    // View Analysis Button
    const viewAnalysisBtn = document.getElementById('viewAnalysisBtn');
    if (viewAnalysisBtn) {
        viewAnalysisBtn.addEventListener('click', function() {
            showComparison();
        });
    }
    
    // Feedback Button
    const feedbackBtn = document.getElementById('feedbackBtn');
    if (feedbackBtn) {
        feedbackBtn.addEventListener('click', function() {
            showFeedbackForm();
        });
    }
}

// Drag and Drop Functionality
function initDropZone() {
    const dropZone = document.getElementById('dropZone');
    const imageInput = document.getElementById('imageInput');
    
    if (dropZone && imageInput) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropZone.classList.add('border-highlight');
        }
        
        function unhighlight() {
            dropZone.classList.remove('border-highlight');
        }
        
        // Handle dropped files
        dropZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length) {
                imageInput.files = files;
                // Trigger change event manually
                const event = new Event('change', { bubbles: true });
                imageInput.dispatchEvent(event);
            }
        }
    }
}

// Counter Animation for Stats
function initCounterAnimation() {
    const stats = document.querySelectorAll('.stat-number');
    
    if (stats.length) {
        const options = {
            threshold: 0.7
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;
                    const targetValue = parseInt(target.getAttribute('data-count'));
                    let count = 0;
                    const duration = 2000; // 2 seconds
                    const interval = duration / targetValue;
                    
                    const counter = setInterval(function() {
                        count++;
                        target.textContent = count;
                        
                        if (count >= targetValue) {
                            clearInterval(counter);
                            target.textContent = targetValue.toLocaleString() + (target.textContent.includes('+') ? '+' : '');
                        }
                    }, interval);
                    
                    observer.unobserve(target);
                }
            });
        }, options);
        
        stats.forEach(stat => {
            observer.observe(stat);
        });
    }
}

// Diagnose Function
function diagnose() {
    const fileInput = document.getElementById('imageInput');
    if (!fileInput.files.length) {
        showNotification('Please select an image first', 'warning');
        return;
    }
    
    // Disable diagnose button and show loading state
    const diagnoseBtn = document.getElementById('diagnoseBtn');
    diagnoseBtn.disabled = true;
    diagnoseBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    
    showLoading(true);
    
    // Simulate API call delay (would be a real API call in production)
    setTimeout(function() {
        showLoading(false);
        
        // Generate mock diagnosis data
        const mockData = generateMockDiagnosis();
        
        // Display results
        displayResults(mockData);
        
        // Reset button state
        diagnoseBtn.disabled = false;
        diagnoseBtn.innerHTML = '<i class="fas fa-microscope"></i> Diagnose Now';
        
        showNotification('Diagnosis completed successfully', 'success');
    }, 2500);
}

// Generate Mock Diagnosis Data
function generateMockDiagnosis() {
    // Random disease status (80% chance of disease, 20% chance of healthy)
    const isHealthy = Math.random() > 0.8;
    
    // Random confidence score between 0.85 and 0.99
    const confidenceScore = (Math.random() * (0.99 - 0.85) + 0.85).toFixed(4);
    
    // Random disease percentage for diseased plants
    const diseasePercentage = isHealthy ? 0 : Math.floor(Math.random() * (100 - 30) + 30);
    
    // Mock disease details
    const diseaseDetails = isHealthy ? null : {
        lacking_trait: ['Nitrogen', 'Phosphorus', 'Potassium'][Math.floor(Math.random() * 3)],
        symptoms: [
            'Yellowing of leaves',
            'Stunted growth',
            'Leaf spots',
            'Wilting',
            'Curling of leaves'
        ].sort(() => 0.5 - Math.random()).slice(0, 3),
        treatment: [
            'Apply balanced NPK fertilizer',
            'Increase watering frequency',
            'Apply fungicide spray',
            'Prune affected areas',
            'Improve soil drainage'
        ][Math.floor(Math.random() * 5)]
    };
    
    return {
        data: {
            plant_name: ['Tomato', 'Potato', 'Corn', 'Apple', 'Rice'][Math.floor(Math.random() * 5)],
            disease_percentage: diseasePercentage,
            status: isHealthy ? 'Healthy' : 'Diseased',
            confidence_score: confidenceScore,
            disease_details: diseaseDetails,
            timestamp: new Date().toISOString()
        }
    };
}

// Display Results
function displayResults(data) {
    console.log("Displaying results:", data);
    const resultDiv = document.getElementById('result');
    const diagnosisData = data.data;
    
    resultDiv.innerHTML = `
        <div class="space-y-4">
            <div class="bg-white p-4 rounded-lg shadow">
                <h3 class="text-lg font-semibold mb-3">Basic Information</h3>
                <div class="result-grid">
                    <div class="result-label">Plant Name:</div>
                    <div>${diagnosisData.plant_name || 'N/A'}</div>
                    
                    <div class="result-label">Disease Percentage:</div>
                    <div>${diagnosisData.disease_percentage || 0}%</div>
                    
                    <div class="result-label">Status:</div>
                    <div class="${diagnosisData.status === 'Healthy' ? 'text-success' : 'text-error'} font-semibold">
                        ${diagnosisData.status || 'Unknown'}
                    </div>
                    
                    <div class="result-label">Confidence Score:</div>
                    <div>${diagnosisData.confidence_score ? (diagnosisData.confidence_score * 100).toFixed(2) : 0}%</div>
                </div>
            </div>

            ${diagnosisData.disease_details ? `
                <div class="bg-white p-4 rounded-lg shadow">
                    <h3 class="text-lg font-semibold mb-3">Disease Details</h3>
                    <div class="result-grid">
                        <div class="result-label">Lacking Trait:</div>
                        <div>${diagnosisData.disease_details.lacking_trait || 'N/A'}</div>
                        
                        ${diagnosisData.disease_details.symptoms ? `
                            <div class="result-label">Symptoms:</div>
                            <div>${diagnosisData.disease_details.symptoms.join(', ') || 'N/A'}</div>
                        ` : ''}
                        
                        <div class="result-label">Treatment:</div>
                        <div>${diagnosisData.disease_details.treatment || 'N/A'}</div>
                    </div>
                </div>
            ` : ''}

            <div class="bg-white p-4 rounded-lg shadow">
                <div class="result-label">Diagnosis Time:</div>
                <div>${new Date(diagnosisData.timestamp).toLocaleString()}</div>
            </div>
        </div>`;
    
    // Add some CSS for the result grid
    const style = document.createElement('style');
    style.textContent = `
        .result-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 0.5rem 1rem;
        }
        .result-label {
            font-weight: 500;
            color: var(--text-dark);
        }
        .text-success {
            color: var(--success);
        }
        .text-error {
            color: var(--error);
        }
        .space-y-4 > * {
            margin-bottom: 1rem;
        }
        .space-y-4 > *:last-child {
            margin-bottom: 0;
        }
    `;
    document.head.appendChild(style);
    
    document.getElementById('resultSection').classList.remove('hidden');
}

// Download PDF Report
function downloadPDF() {
    showLoading(true);
    
    // Get the result section
    const resultSection = document.getElementById('resultSection');
    
    // Clone it to avoid modifying the original
    const clone = resultSection.cloneNode(true);
    
    // Add some styling for the PDF
    clone.style.padding = '20px';
    clone.style.maxWidth = '800px';
    clone.style.margin = '0 auto';
    clone.style.backgroundColor = 'white';
    
    // Add a header to the PDF
    const header = document.createElement('div');
    header.innerHTML = `
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #0d9488; font-size: 24px; margin-bottom: 10px;">Plant Disease Diagnosis Report</h1>
            <p style="color: #666; font-size: 14px;">Generated on ${new Date().toLocaleString()}</p>
        </div>
    `;
    clone.insertBefore(header, clone.firstChild);
    
    // Configure PDF options
    const options = {
        margin: 10,
        filename: `plant-diagnosis-report-${Date.now()}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    // Generate PDF
    setTimeout(function() {
        html2pdf().from(clone).set(options).save();
        showLoading(false);
        showNotification('PDF report downloaded successfully', 'success');
    }, 1500);
}

// Show Comparison
function showComparison() {
    const comparisonSection = document.getElementById('comparisonSection');
    const comparisonResults = document.getElementById('comparisonResults');
    
    // Show loading
    showLoading(true);
    
    // Generate mock comparison data
    setTimeout(function() {
        // Generate 3 mock results
        const mockResults = [];
        for (let i = 0; i < 3; i++) {
            mockResults.push(generateMockDiagnosis().data);
        }
        
        // Clear previous results
        comparisonResults.innerHTML = '';
        
        // Add each result card
        mockResults.forEach(result => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h3 class="text-lg font-semibold">${result.plant_name}</h3>
                <div class="status ${result.status === 'Healthy' ? 'status-healthy' : 'status-diseased'}">
                    ${result.status}
                </div>
                <div class="details">
                    <p><strong>Confidence:</strong> ${(result.confidence_score * 100).toFixed(2)}%</p>
                    <p><strong>Disease %:</strong> ${result.disease_percentage}%</p>
                    <p><strong>Date:</strong> ${new Date(result.timestamp).toLocaleDateString()}</p>
                </div>
            `;
            comparisonResults.appendChild(card);
        });
        
        // Add some CSS for the comparison cards
        const style = document.createElement('style');
        style.textContent = `
            .status {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 500;
                margin: 8px 0;
            }
            .status-healthy {
                background-color: rgba(16, 185, 129, 0.2);
                color: var(--success);
            }
            .status-diseased {
                background-color: rgba(239, 68, 68, 0.2);
                color: var(--error);
            }
            .details {
                font-size: 0.9rem;
                color: var(--text-light);
            }
            .details p {
                margin-bottom: 4px;
            }
        `;
        document.head.appendChild(style);
        
        // Show comparison section
        comparisonSection.classList.remove('hidden');
        
        // Hide loading
        showLoading(false);
    }, 1800);
}

// Show Feedback Form
function showFeedbackForm() {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    // Create modal content
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Provide Your Feedback</h3>
                <button class="close-btn">&times;</button>
            </div>
            <div class="modal-body">
                <form id="feedbackForm">
                    <div class="form-group">
                        <label for="rating">Rate your experience:</label>
                        <div class="rating-container">
                            <span class="star" data-value="1"><i class="far fa-star"></i></span>
                            <span class="star" data-value="2"><i class="far fa-star"></i></span>
                            <span class="star" data-value="3"><i class="far fa-star"></i></span>
                            <span class="star" data-value="4"><i class="far fa-star"></i></span>
                            <span class="star" data-value="5"><i class="far fa-star"></i></span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="feedbackText">Comments:</label>
                        <textarea id="feedbackText" rows="4" placeholder="Share your thoughts about the diagnosis..."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="email">Email (optional):</label>
                        <input type="email" id="email" placeholder="Your email address">
                    </div>
                    <button type="submit" class="btn btn-primary">Submit Feedback</button>
                </form>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.appendChild(modal);
    
    // Add CSS for modal
    const style = document.createElement('style');
    style.textContent = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }
        .modal-content {
            background-color: white;
            border-radius: 10px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
        }
        .modal-header h3 {
            margin: 0;
            color: var(--primary-dark);
        }
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #999;
        }
        .modal-body {
            padding: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        .rating-container {
            display: flex;
            gap: 10px;
        }
        .star {
            font-size: 1.5rem;
            color: #ccc;
            cursor: pointer;
        }
        .star.active i {
            font-weight: 900;
            color: #f59e0b;
        }
        textarea, input[type="email"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: inherit;
        }
    `;
    document.head.appendChild(style);
    
    // Handle close button
    const closeBtn = modal.querySelector('.close-btn');
    closeBtn.addEventListener('click', function() {
        modal.remove();
    });
    
    // Handle star rating
    const stars = modal.querySelectorAll('.star');
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const value = parseInt(this.getAttribute('data-value'));
            
            // Reset all stars
            stars.forEach(s => {
                s.classList.remove('active');
                s.innerHTML = '<i class="far fa-star"></i>';
            });
            
            // Fill stars up to selected value
            for (let i = 0; i < stars.length; i++) {
                if (i < value) {
                    stars[i].classList.add('active');
                    stars[i].innerHTML = '<i class="fas fa-star"></i>';
                }
            }
        });
    });
    
    // Handle form submission
    const feedbackForm = modal.querySelector('#feedbackForm');
    feedbackForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get active stars count
        const rating = modal.querySelectorAll('.star.active').length;
        const feedbackText = modal.querySelector('#feedbackText').value;
        const email = modal.querySelector('#email').value;
        
        // Validate
        if (rating === 0) {
            alert('Please provide a rating');
            return;
        }
        
        if (!feedbackText.trim()) {
            alert('Please provide some feedback');
            return;
        }
        
        // In a real app, you would send this data to the server
        console.log({
            rating,
            feedbackText,
            email
        });
        
        // Close modal
        modal.remove();
        
        // Show success notification
        showNotification('Thank you for your feedback!', 'success');
    });
}

// Show/Hide Loading Overlay
function showLoading(show = true) {
    const loader = document.getElementById('loadingOverlay');
    if (show) {
        loader.classList.remove('hidden');
    } else {
        loader.classList.add('hidden');
    }
}

// Show Notification
function showNotification(message, type) {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add CSS for notification fade out
const notificationStyle = document.createElement('style');
notificationStyle.textContent = `
    .notification {
        transition: opacity 0.3s ease;
    }
`;
document.head.appendChild(notificationStyle);
