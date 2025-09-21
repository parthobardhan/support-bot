// Configuration
const API_BASE_URL = 'http://localhost:5001/api';

// Global state
let currentSearchType = 'hybrid';
let currentFilters = {};
let allFilters = {};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadFilterOptions();
});

function initializeApp() {
    // Set up search type toggle
    document.querySelectorAll('.btn-search-type').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.btn-search-type').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentSearchType = this.dataset.type;
        });
    });
    
    // Focus on search input
    document.getElementById('searchInput').focus();
}

function handleEnterKey(event) {
    if (event.key === 'Enter') {
        performSearch();
    }
}

function searchSample(query) {
    document.getElementById('searchInput').value = query;
    performSearch();
}

async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    // Show loading, hide samples
    showLoading(true);
    document.getElementById('sampleQueries').style.display = 'none';
    
    try {
        const searchData = {
            query: query,
            type: currentSearchType,
            limit: 20,
            filters: currentFilters
        };
        
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(searchData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Search error:', error);
        showError('Search failed. Please check if the backend server is running.');
    } finally {
        showLoading(false);
    }
}

function displayResults(data) {
    const resultsContainer = document.getElementById('searchResults');
    const statsContainer = document.getElementById('searchStats');
    const resultsCount = document.getElementById('resultsCount');
    
    // Show stats
    statsContainer.style.display = 'block';
    resultsCount.textContent = `${data.total} results`;
    
    if (data.results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="text-center my-5">
                <i class="fas fa-search fa-4x text-muted mb-3"></i>
                <h5 class="text-muted">No results found</h5>
                <p class="text-muted">Try adjusting your search query or filters</p>
            </div>
        `;
        return;
    }
    
    // Display results
    let resultsHtml = '';
    
    data.results.forEach(result => {
        const typeIcon = getTypeIcon(result.type);
        const typeBadge = getTypeBadge(result.type);
        const priorityBadge = result.metadata.priority ? 
            `<span class="badge bg-${getPriorityColor(result.metadata.priority)} me-2">${result.metadata.priority}</span>` : '';
        
        resultsHtml += `
            <div class="card result-card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0">
                            <i class="${typeIcon} me-2"></i>
                            ${result.title}
                        </h5>
                        <span class="badge score-badge ms-2">
                            Score: ${result.score.toFixed(3)}
                        </span>
                    </div>
                    
                    <div class="mb-2">
                        ${typeBadge}
                        ${priorityBadge}
                        ${result.metadata.product ? `<span class="badge bg-info me-2">${result.metadata.product}</span>` : ''}
                        ${result.metadata.category ? `<span class="badge bg-secondary me-2">${result.metadata.category}</span>` : ''}
                    </div>
                    
                    <p class="card-text text-muted">
                        ${result.summary || result.content}
                    </p>
                    
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            ${result.metadata.created_date ? 
                                `Created: ${new Date(result.metadata.created_date).toLocaleDateString()}` : ''
                            }
                        </small>
                        <div>
                            <button class="btn btn-outline-primary btn-sm" onclick="showDocument('${result.id}')">
                                <i class="fas fa-eye"></i> View Details
                            </button>
                            <button class="btn btn-outline-secondary btn-sm ms-1" onclick="findSimilar('${result.id}')">
                                <i class="fas fa-sitemap"></i> Similar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = resultsHtml;
}

function getTypeIcon(type) {
    const icons = {
        'jira': 'fas fa-bug',
        'documentation': 'fas fa-book',
        'knowledge': 'fas fa-lightbulb'
    };
    return icons[type] || 'fas fa-file';
}

function getTypeBadge(type) {
    const badges = {
        'jira': '<span class="badge bg-danger me-2">Jira Ticket</span>',
        'documentation': '<span class="badge bg-primary me-2">Documentation</span>',
        'knowledge': '<span class="badge bg-success me-2">Knowledge Base</span>'
    };
    return badges[type] || `<span class="badge bg-secondary me-2">${type}</span>`;
}

function getPriorityColor(priority) {
    const colors = {
        'Highest': 'danger',
        'High': 'warning',
        'Medium': 'info',
        'Low': 'secondary',
        'Lowest': 'light'
    };
    return colors[priority] || 'secondary';
}

async function showDocument(docId) {
    try {
        const response = await fetch(`${API_BASE_URL}/document/${docId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const doc = await response.json();
        
        document.getElementById('documentModalTitle').textContent = doc.title;
        
        let modalBody = `
            <div class="mb-3">
                ${getTypeBadge(doc.type)}
                ${doc.priority ? `<span class="badge bg-${getPriorityColor(doc.priority)}">${doc.priority}</span>` : ''}
            </div>
            
            <div class="mb-3">
                <h6>Summary:</h6>
                <p>${doc.summary || 'No summary available'}</p>
            </div>
            
            <div class="mb-3">
                <h6>Content:</h6>
                <div style="max-height: 400px; overflow-y: auto;">
                    <p>${doc.content || 'No content available'}</p>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <h6>Metadata:</h6>
                    <ul class="list-unstyled">
                        ${doc.product ? `<li><strong>Product:</strong> ${doc.product}</li>` : ''}
                        ${doc.category ? `<li><strong>Category:</strong> ${doc.category}</li>` : ''}
                        ${doc.status ? `<li><strong>Status:</strong> ${doc.status}</li>` : ''}
                        ${doc.author ? `<li><strong>Author:</strong> ${doc.author}</li>` : ''}
                        ${doc.created_date ? `<li><strong>Created:</strong> ${new Date(doc.created_date).toLocaleDateString()}</li>` : ''}
                    </ul>
                </div>
                <div class="col-md-6">
                    ${doc.tags && doc.tags.length > 0 ? `
                        <h6>Tags:</h6>
                        <div class="mb-3">
                            ${doc.tags.map(tag => `<span class="badge bg-light text-dark me-1">${tag}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.getElementById('documentModalBody').innerHTML = modalBody;
        
        const modal = new bootstrap.Modal(document.getElementById('documentModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading document:', error);
        alert('Failed to load document details');
    }
}

async function findSimilar(docId) {
    try {
        const response = await fetch(`${API_BASE_URL}/similar/${docId}?limit=5`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.similar_documents.length === 0) {
            alert('No similar documents found');
            return;
        }
        
        let modalBody = `
            <p class="text-muted mb-3">Documents similar to the selected item:</p>
            <div class="list-group">
        `;
        
        data.similar_documents.forEach(doc => {
            modalBody += `
                <div class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${doc.title}</h6>
                        <span class="badge score-badge">Score: ${doc.score.toFixed(3)}</span>
                    </div>
                    <p class="mb-1 text-muted">${doc.summary}</p>
                    <div class="mt-2">
                        ${getTypeBadge(doc.type)}
                        ${doc.metadata.product ? `<span class="badge bg-info">${doc.metadata.product}</span>` : ''}
                        <button class="btn btn-sm btn-outline-primary ms-2" onclick="showDocument('${doc.id}')">
                            View Details
                        </button>
                    </div>
                </div>
            `;
        });
        
        modalBody += `</div>`;
        
        document.getElementById('documentModalTitle').textContent = 'Similar Documents';
        document.getElementById('documentModalBody').innerHTML = modalBody;
        
        const modal = new bootstrap.Modal(document.getElementById('documentModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error finding similar documents:', error);
        alert('Failed to find similar documents');
    }
}

async function loadFilterOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/filters`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        allFilters = await response.json();
        
        // Populate type filters (checkboxes)
        const typeFiltersContainer = document.getElementById('typeFilters');
        typeFiltersContainer.innerHTML = '';
        
        if (allFilters.types) {
            allFilters.types.forEach(type => {
                if (type) {
                    typeFiltersContainer.innerHTML += `
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="${type}" id="type_${type}" onchange="updateFilters()">
                            <label class="form-check-label" for="type_${type}">
                                <i class="${getTypeIcon(type)}"></i> ${type.charAt(0).toUpperCase() + type.slice(1)}
                            </label>
                        </div>
                    `;
                }
            });
        }
        
        // Populate product filter
        const productFilter = document.getElementById('productFilter');
        if (allFilters.products) {
            allFilters.products.forEach(product => {
                if (product) {
                    const option = document.createElement('option');
                    option.value = product;
                    option.textContent = product;
                    productFilter.appendChild(option);
                }
            });
        }
        
        // Populate priority filter  
        const priorityFilter = document.getElementById('priorityFilter');
        if (allFilters.priorities) {
            allFilters.priorities.forEach(priority => {
                if (priority) {
                    const option = document.createElement('option');
                    option.value = priority;
                    option.textContent = priority;
                    priorityFilter.appendChild(option);
                }
            });
        }
        
        // Add event listeners
        productFilter.addEventListener('change', updateFilters);
        priorityFilter.addEventListener('change', updateFilters);
        
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

function updateFilters() {
    currentFilters = {};
    
    // Get selected types
    const selectedTypes = [];
    document.querySelectorAll('#typeFilters input[type="checkbox"]:checked').forEach(checkbox => {
        selectedTypes.push(checkbox.value);
    });
    
    if (selectedTypes.length > 0) {
        currentFilters.type = { $in: selectedTypes };
    }
    
    // Get selected product
    const selectedProduct = document.getElementById('productFilter').value;
    if (selectedProduct) {
        currentFilters.product = selectedProduct;
    }
    
    // Get selected priority
    const selectedPriority = document.getElementById('priorityFilter').value;
    if (selectedPriority) {
        currentFilters.priority = selectedPriority;
    }
    
    // If there's a current search, re-run it with new filters
    const searchInput = document.getElementById('searchInput').value.trim();
    if (searchInput) {
        performSearch();
    }
}

function clearFilters() {
    currentFilters = {};
    
    // Clear checkboxes
    document.querySelectorAll('#typeFilters input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Clear select elements
    document.getElementById('productFilter').value = '';
    document.getElementById('priorityFilter').value = '';
    
    // Re-run search if there's a query
    const searchInput = document.getElementById('searchInput').value.trim();
    if (searchInput) {
        performSearch();
    }
}

async function showStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stats = await response.json();
        
        let statsHtml = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <h6><i class="fas fa-database me-2"></i>Total Documents</h6>
                    <h4 class="text-primary">${stats.total_documents || 0}</h4>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-hdd me-2"></i>Collection Size</h6>
                    <h4 class="text-info">${formatBytes(stats.collection_size || 0)}</h4>
                </div>
            </div>
            
            <div class="mb-3">
                <h6><i class="fas fa-chart-pie me-2"></i>Document Types</h6>
                <div class="row">
        `;
        
        if (stats.type_distribution) {
            Object.entries(stats.type_distribution).forEach(([type, count]) => {
                const percentage = ((count / stats.total_documents) * 100).toFixed(1);
                statsHtml += `
                    <div class="col-md-4 mb-2">
                        <div class="d-flex align-items-center">
                            <i class="${getTypeIcon(type)} me-2"></i>
                            <div>
                                <div>${type}: ${count}</div>
                                <div class="text-muted small">${percentage}%</div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        statsHtml += `
                </div>
            </div>
            
            <div class="mb-3">
                <h6><i class="fas fa-ruler me-2"></i>Average Document Size</h6>
                <p class="mb-0">${formatBytes(stats.average_document_size || 0)}</p>
            </div>
            
            <div class="mb-3">
                <h6><i class="fas fa-index me-2"></i>Indexes</h6>
                <p class="mb-0">${stats.indexes || 0} indexes created</p>
            </div>
        `;
        
        document.getElementById('statsModalBody').innerHTML = statsHtml;
        
        const modal = new bootstrap.Modal(document.getElementById('statsModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading stats:', error);
        alert('Failed to load statistics');
    }
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function showLoading(show) {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const searchResults = document.getElementById('searchResults');
    
    if (show) {
        loadingSpinner.style.display = 'block';
    } else {
        loadingSpinner.style.display = 'none';
    }
}

function showError(message) {
    document.getElementById('searchResults').innerHTML = `
        <div class="alert alert-danger" role="alert">
            <h5 class="alert-heading">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error
            </h5>
            <p>${message}</p>
        </div>
    `;
}
