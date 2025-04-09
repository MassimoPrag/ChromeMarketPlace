// Constants
const API_URL = 'http://localhost:5000/api';
const ITEMS_ENDPOINT = `${API_URL}/items`;
const REFRESH_ENDPOINT = `${API_URL}/refresh`;

// DOM Elements
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const refreshButton = document.getElementById('refresh-button');
const loadingElement = document.getElementById('loading');
const errorElement = document.getElementById('error-message');
const itemsContainer = document.getElementById('items-container');

// Event Listeners
document.addEventListener('DOMContentLoaded', fetchItems);
searchButton.addEventListener('click', handleSearch);
searchInput.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') handleSearch();
});
refreshButton.addEventListener('click', refreshData);

// Functions
async function fetchItems(searchQuery = '') {
    showLoading(true);
    hideError();
    
    try {
        const url = searchQuery ? `${ITEMS_ENDPOINT}?q=${encodeURIComponent(searchQuery)}` : ITEMS_ENDPOINT;
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`Failed to fetch items: ${errorData.message || response.statusText}`);
        }
        
        const items = await response.json();
        
        if (items.error) {
            throw new Error(`API Error: ${items.error}`);
        }
        
        renderItems(items);
    } catch (error) {
        showError(`Error fetching items: ${error.message}. Please try refreshing the data or check the server.`);
        console.error('Error fetching items:', error);
    } finally {
        showLoading(false);
    }
}

async function refreshData() {
    showLoading(true);
    hideError();
    refreshButton.disabled = true;
    
    try {
        // First check if the server is reachable
        try {
            const pingResponse = await fetch(`${API_URL}/debug`, { 
                method: 'GET',
                // Add a timeout to avoid long waiting times
                signal: AbortSignal.timeout(5000)
            });
            if (!pingResponse.ok) {
                throw new Error('Server is not responding properly');
            }
        } catch (pingError) {
            throw new Error(`Cannot connect to server. Please ensure the Flask API is running at ${API_URL}`);
        }
        
        // Then try to refresh data
        const response = await fetch(REFRESH_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // Use a longer timeout for the scraping operation
            signal: AbortSignal.timeout(120000) // 2 minutes timeout
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`Server error: ${errorData.message || response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'error') {
            throw new Error(`Scraping error: ${result.message}`);
        }
        
        console.log('Data refresh result:', result);
        showMessage(`${result.message}`, 'success');
        
        // Fetch the updated items
        await fetchItems();
    } catch (error) {
        let errorMessage = error.message;
        
        // Provide more specific guidance based on error type
        if (error.name === 'AbortError') {
            errorMessage = 'The operation timed out. Scraping takes longer than expected.';
        } else if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            errorMessage = 'Failed to connect to the server. Please make sure the Flask API is running.';
        }
        
        showError(`Error refreshing data: ${errorMessage}`);
        
        // Show a helpful guide for common issues
        const troubleshootingGuide = document.createElement('div');
        troubleshootingGuide.className = 'troubleshooting-guide';
        troubleshootingGuide.innerHTML = `
            <h4>Troubleshooting Tips:</h4>
            <ul>
                <li>Make sure the Flask server is running at ${API_URL}</li>
                <li>Check that your internet connection is working</li>
                <li>The scraping process might take longer than expected</li>
                <li>Try adding sample data using the <a href="debug.html">Debug Page</a></li>
            </ul>
        `;
        errorElement.appendChild(troubleshootingGuide);
        
        console.error('Error refreshing data:', error);
    } finally {
        showLoading(false);
        refreshButton.disabled = false;
    }
}

function handleSearch() {
    const query = searchInput.value.trim();
    fetchItems(query);
}

function renderItems(items) {
    if (!items || items.length === 0) {
        itemsContainer.innerHTML = '<p class="no-items">No items found</p>';
        return;
    }
    
    itemsContainer.innerHTML = '';
    
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'item-card';
        
        // Format the price if it exists
        const formattedPrice = typeof item.price === 'number' 
            ? `$${item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` 
            : 'Price unavailable';
        
        // Determine if the item has a valid image URL
        const hasValidImage = item.image_url && item.image_url !== 'N/A';
        
        card.innerHTML = `
            <div class="item-image">
                ${hasValidImage 
                    ? `<img src="${item.image_url}" alt="${item.item_name}" onerror="this.onerror=null; this.parentNode.innerHTML='<div class=\\'item-image-placeholder\\'>Image not available</div>';">`
                    : `<div class="item-image-placeholder">Image not available</div>`
                }
            </div>
            <div class="item-details">
                <h3 class="item-name">${item.item_name || 'Unknown Item'}</h3>
                <p class="item-price">${formattedPrice}</p>
                <p class="item-size">Size: ${item.size || 'N/A'}</p>
                <p class="item-availability ${item.availability ? 'available' : 'unavailable'}">
                    ${item.availability ? 'In Stock' : 'Out of Stock'}
                </p>
                ${item.item_url && item.item_url !== 'N/A' 
                    ? `<a href="${item.item_url}" target="_blank" class="item-link">View Item</a>` 
                    : ''}
            </div>
        `;
        
        itemsContainer.appendChild(card);
    });
}

function showLoading(isLoading) {
    loadingElement.classList.toggle('hidden', !isLoading);
}

function showError(message) {
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
}

function hideError() {
    errorElement.classList.add('hidden');
}

// Add a success message function
function showMessage(message, type = 'info') {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.textContent = message;
    
    // Insert before items container
    itemsContainer.parentNode.insertBefore(messageElement, itemsContainer);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageElement.remove();
    }, 5000);
}
