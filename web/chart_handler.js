/* MoMo Analytics Dashboard JavaScript */

// Configuration
const API_ENDPOINT = 'http://localhost:8000';
const PAGE_SIZE = 20;

let currentPage = 0;
let allCharts = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeEventListeners();
    loadDashboardData();
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link and corresponding section
            this.classList.add('active');
            const sectionId = this.getAttribute('href').substring(1);
            document.getElementById(sectionId).classList.add('active');
        });
    });

    // Set Overview as default active
    document.querySelector('[href="#overview"]').classList.add('active');
    document.getElementById('overview').classList.add('active');
}

// Event Listeners
function initializeEventListeners() {
    // Pagination
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (currentPage > 0) {
            currentPage--;
            loadTransactions();
        }
    });

    document.getElementById('nextBtn').addEventListener('click', () => {
        currentPage++;
        loadTransactions();
    });

    // Filters
    document.getElementById('typeFilter').addEventListener('change', () => {
        currentPage = 0;
        loadTransactions();
    });

    document.getElementById('statusFilter').addEventListener('change', () => {
        currentPage = 0;
        loadTransactions();
    });

    document.getElementById('searchInput').addEventListener('input', debounce(() => {
        currentPage = 0;
        loadTransactions();
    }, 300));
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

async function fetchAPI(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_ENDPOINT}${endpoint}`, options);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'RWF',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);
}

function formatDate(dateString) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(new Date(dateString));
}

// Load Dashboard Data
async function loadDashboardData() {
    await Promise.all([
        loadAnalyticsSummary(),
        loadTransactionTypeChart(),
        loadDailyVolumeChart(),
        loadTopSenders(),
        loadTopRecipients(),
        checkAPIStatus(),
        loadTransactions(),
    ]);
}

// Analytics Summary
async function loadAnalyticsSummary() {
    const data = await fetchAPI('/api/v1/analytics/summary');
    
    if (data) {
        document.getElementById('total-transactions').textContent = 
            data.total_transactions.toLocaleString();
        document.getElementById('total-amount').textContent = 
            formatCurrency(data.total_amount);
        document.getElementById('average-amount').textContent = 
            formatCurrency(data.average_amount);
    }
}

// Transaction Type Chart
async function loadTransactionTypeChart() {
    const data = await fetchAPI('/api/v1/analytics/by-type');
    
    if (!data || !data.data) return;

    const ctx = document.getElementById('transactionTypeChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (allCharts.transactionType) {
        allCharts.transactionType.destroy();
    }

    allCharts.transactionType = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.data.map(d => d.type),
            datasets: [{
                data: data.data.map(d => d.count),
                backgroundColor: [
                    '#3498db',
                    '#2ecc71',
                    '#e74c3c',
                    '#f39c12',
                    '#9b59b6',
                    '#1abc9c',
                    '#34495e',
                ],
                borderColor: 'white',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
}

// Daily Volume Chart
async function loadDailyVolumeChart() {
    const data = await fetchAPI('/api/v1/analytics/by-date-range?days=30');
    
    if (!data || !data.data) return;

    const ctx = document.getElementById('dailyVolumeChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (allCharts.dailyVolume) {
        allCharts.dailyVolume.destroy();
    }

    allCharts.dailyVolume = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.data.map(d => d.date),
            datasets: [{
                label: 'Transaction Count',
                data: data.data.map(d => d.count),
                backgroundColor: '#3498db',
                borderColor: '#2980b9',
                borderWidth: 1,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                }
            }
        }
    });
}

// Top Senders Table
async function loadTopSenders() {
    const data = await fetchAPI('/api/v1/analytics/summary');
    
    if (!data || !data.top_senders) return;

    let html = '<table><thead><tr><th>Phone</th><th>Count</th><th>Total Amount</th></tr></thead><tbody>';
    
    data.top_senders.forEach(sender => {
        html += `<tr>
            <td>${sender.sender}</td>
            <td>${sender.count}</td>
            <td>${formatCurrency(sender.total_amount)}</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    document.getElementById('topSendersTable').innerHTML = html;
}

// Top Recipients Table
async function loadTopRecipients() {
    const data = await fetchAPI('/api/v1/analytics/summary');
    
    if (!data || !data.top_recipients) return;

    let html = '<table><thead><tr><th>Phone</th><th>Count</th><th>Total Amount</th></tr></thead><tbody>';
    
    data.top_recipients.forEach(recipient => {
        html += `<tr>
            <td>${recipient.recipient}</td>
            <td>${recipient.count}</td>
            <td>${formatCurrency(recipient.total_amount)}</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    document.getElementById('topRecipientsTable').innerHTML = html;
}

// Load Transactions
async function loadTransactions() {
    const skip = currentPage * PAGE_SIZE;
    const typeFilter = document.getElementById('typeFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const searchTerm = document.getElementById('searchInput').value;

    let url = `/api/v1/transactions/?skip=${skip}&limit=${PAGE_SIZE}`;
    
    if (typeFilter) url += `&transaction_type=${typeFilter}`;
    if (statusFilter) url += `&status=${statusFilter}`;

    const data = await fetchAPI(url);
    
    if (!data || !data.items) return;

    let html = '<table><thead><tr><th>ID</th><th>Date</th><th>Sender</th><th>Recipient</th><th>Amount</th><th>Type</th><th>Status</th></tr></thead><tbody>';
    
    data.items.forEach(transaction => {
        // Filter by search term if provided
        if (searchTerm && !JSON.stringify(transaction).toLowerCase().includes(searchTerm.toLowerCase())) {
            return;
        }

        html += `<tr>
            <td>${transaction.transaction_id.substring(0, 8)}...</td>
            <td>${formatDate(transaction.timestamp)}</td>
            <td>${transaction.sender || '-'}</td>
            <td>${transaction.recipient || '-'}</td>
            <td>${formatCurrency(transaction.amount)}</td>
            <td><span class="badge badge-${transaction.transaction_type}">${transaction.transaction_type}</span></td>
            <td><span class="status-badge ${transaction.status.toLowerCase()}">${transaction.status}</span></td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    document.getElementById('transactionsTable').innerHTML = html;

    // Update pagination
    document.getElementById('pageInfo').textContent = 
        `Page ${currentPage + 1} (${data.items.length}/${data.total} records)`;
    document.getElementById('prevBtn').disabled = currentPage === 0;
}

// Check API Status
async function checkAPIStatus() {
    const data = await fetchAPI('/health');
    
    const statusElement = document.getElementById('api-status');
    const statusDetailElement = document.getElementById('apiStatusDetail');
    
    if (data && data.status === 'healthy') {
        statusElement.textContent = '✓ Connected';
        statusElement.style.color = '#27ae60';
        statusDetailElement.textContent = 'Connected';
        statusDetailElement.className = 'status-badge connected';
    } else {
        statusElement.textContent = '✗ Disconnected';
        statusElement.style.color = '#e74c3c';
        statusDetailElement.textContent = 'Disconnected';
        statusDetailElement.className = 'status-badge disconnected';
    }
}

// Export Data
async function exportData() {
    const data = await fetchAPI('/api/v1/transactions/?skip=0&limit=999999');
    
    if (!data || !data.items) {
        alert('Failed to export data');
        return;
    }

    const jsonData = JSON.stringify(data.items, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transactions_export_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Refresh data every 5 minutes
setInterval(loadDashboardData, 5 * 60 * 1000);
