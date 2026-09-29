/* MoMo Analytics Dashboard JavaScript */

// The page is served by api/server.py, so it uses the same address.
// The browser asks for the Basic Auth login once and sends it with every request.
const API_ENDPOINT = window.location.origin;
const PAGE_SIZE = 20;
const COLORS = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22', '#95a5a6'];

let currentPage = 0;
let allCharts = {};
let transactions = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('apiEndpoint').textContent = API_ENDPOINT;
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
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            this.classList.add('active');
            const sectionId = this.getAttribute('href').substring(1);
            document.getElementById(sectionId).classList.add('active');
        });
    });

    document.querySelector('[href="#overview"]').classList.add('active');
    document.getElementById('overview').classList.add('active');
}

// Event Listeners
function initializeEventListeners() {
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (currentPage > 0) {
            currentPage--;
            renderTransactions();
        }
    });

    document.getElementById('nextBtn').addEventListener('click', () => {
        currentPage++;
        renderTransactions();
    });

    document.getElementById('typeFilter').addEventListener('change', () => {
        currentPage = 0;
        renderTransactions();
    });

    document.getElementById('searchInput').addEventListener('input', debounce(() => {
        currentPage = 0;
        renderTransactions();
    }, 300));
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_ENDPOINT}${endpoint}`);
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
    return Math.round(value).toLocaleString('en-US') + ' RWF';
}

function escapeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text == null ? '' : String(text);
    return div.innerHTML;
}

// count and sum amounts grouped by a key
function groupBy(list, keyFn) {
    const groups = {};
    list.forEach(t => {
        const key = keyFn(t);
        if (!groups[key]) groups[key] = { count: 0, total: 0 };
        groups[key].count++;
        groups[key].total += Number(t.amount) || 0;
    });
    return groups;
}

function drawChart(id, type, labels, datasets, options = {}) {
    if (allCharts[id]) allCharts[id].destroy();
    allCharts[id] = new Chart(document.getElementById(id).getContext('2d'), {
        type: type,
        data: { labels: labels, datasets: datasets },
        options: Object.assign({ responsive: true, maintainAspectRatio: true }, options),
    });
}

// Load Dashboard Data
async function loadDashboardData() {
    const data = await fetchAPI('/transactions');
    setStatus(data !== null);
    if (!data) return;

    transactions = data;
    loadAnalyticsSummary();
    loadTransactionTypeChart();
    loadDailyVolumeChart();
    loadTopTable('topSendersTable', 'sender', 'Sender');
    loadTopTable('topRecipientsTable', 'receiver', 'Recipient');
    loadTrendsChart();
    loadDistributionChart();
    renderTransactions();
    document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
}

// Analytics Summary
function loadAnalyticsSummary() {
    const total = transactions.reduce((sum, t) => sum + (Number(t.amount) || 0), 0);
    document.getElementById('total-transactions').textContent = transactions.length.toLocaleString();
    document.getElementById('total-amount').textContent = formatCurrency(total);
    document.getElementById('average-amount').textContent =
        formatCurrency(transactions.length ? total / transactions.length : 0);
}

// Transaction Type Chart
function loadTransactionTypeChart() {
    const groups = groupBy(transactions, t => t.type);
    const labels = Object.keys(groups);
    drawChart('transactionTypeChart', 'doughnut', labels, [{
        data: labels.map(k => groups[k].count),
        backgroundColor: COLORS,
        borderColor: 'white',
        borderWidth: 2,
    }], { plugins: { legend: { position: 'bottom' } } });
}

// Daily Volume Chart (last 30 days that have data)
function loadDailyVolumeChart() {
    const groups = groupBy(transactions, t => (t.timestamp || '').slice(0, 10));
    const days = Object.keys(groups).filter(d => d).sort().slice(-30);
    drawChart('dailyVolumeChart', 'bar', days, [{
        label: 'Transaction Count',
        data: days.map(d => groups[d].count),
        backgroundColor: '#3498db',
    }], { scales: { y: { beginAtZero: true } } });
}

// Top Senders / Recipients (excluding the account owner "me")
function loadTopTable(elementId, field, title) {
    const groups = groupBy(transactions.filter(t => t[field] && t[field] !== 'me'), t => t[field]);
    const top = Object.entries(groups).sort((a, b) => b[1].total - a[1].total).slice(0, 5);

    let html = `<table><thead><tr><th>${title}</th><th>Count</th><th>Total Amount</th></tr></thead><tbody>`;
    top.forEach(([name, g]) => {
        html += `<tr><td>${escapeHTML(name)}</td><td>${g.count}</td><td>${formatCurrency(g.total)}</td></tr>`;
    });
    document.getElementById(elementId).innerHTML = html + '</tbody></table>';
}

// Monthly totals (Analytics tab)
function loadTrendsChart() {
    const groups = groupBy(transactions, t => (t.timestamp || '').slice(0, 7));
    const months = Object.keys(groups).filter(m => m).sort();
    drawChart('trendsChart', 'line', months, [{
        label: 'Total Amount (RWF)',
        data: months.map(m => groups[m].total),
        borderColor: '#2ecc71',
        backgroundColor: 'rgba(46, 204, 113, 0.2)',
        fill: true,
    }]);
}

// Amount ranges (Analytics tab)
function loadDistributionChart() {
    const ranges = [[0, 1000], [1000, 5000], [5000, 20000], [20000, 100000], [100000, Infinity]];
    const labels = ['< 1k', '1k - 5k', '5k - 20k', '20k - 100k', '100k +'];
    const counts = ranges.map(([lo, hi]) =>
        transactions.filter(t => t.amount >= lo && t.amount < hi).length);
    drawChart('distributionChart', 'bar', labels, [{
        label: 'Number of Transactions',
        data: counts,
        backgroundColor: COLORS,
    }], { scales: { y: { beginAtZero: true } } });
}

// Transactions table with filter, search and paging
function renderTransactions() {
    const typeFilter = document.getElementById('typeFilter').value;
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();

    const filtered = transactions.filter(t =>
        (!typeFilter || t.type === typeFilter) &&
        (!searchTerm || JSON.stringify(t).toLowerCase().includes(searchTerm)));

    const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    if (currentPage >= pages) currentPage = pages - 1;
    const pageItems = filtered.slice(currentPage * PAGE_SIZE, (currentPage + 1) * PAGE_SIZE);

    let html = '<table><thead><tr><th>ID</th><th>Date</th><th>Sender</th><th>Recipient</th><th>Amount</th><th>Type</th></tr></thead><tbody>';
    pageItems.forEach(t => {
        html += `<tr>
            <td>${t.id}</td>
            <td>${escapeHTML(t.timestamp)}</td>
            <td>${escapeHTML(t.sender) || '-'}</td>
            <td>${escapeHTML(t.receiver) || '-'}</td>
            <td>${formatCurrency(Number(t.amount) || 0)}</td>
            <td><span class="badge badge-${escapeHTML(t.type)}">${escapeHTML(t.type)}</span></td>
        </tr>`;
    });
    document.getElementById('transactionsTable').innerHTML = html + '</tbody></table>';

    document.getElementById('pageInfo').textContent =
        `Page ${currentPage + 1} of ${pages} (${filtered.length} records)`;
    document.getElementById('prevBtn').disabled = currentPage === 0;
    document.getElementById('nextBtn').disabled = currentPage >= pages - 1;
}

// API Status
function setStatus(ok) {
    const statusElement = document.getElementById('api-status');
    const detail = document.getElementById('apiStatusDetail');
    statusElement.textContent = ok ? '✓ Connected' : '✗ Disconnected';
    statusElement.style.color = ok ? '#27ae60' : '#e74c3c';
    detail.textContent = ok ? 'Connected' : 'Disconnected';
    detail.className = 'status-badge ' + (ok ? 'connected' : 'disconnected');
}

async function checkAPIStatus() {
    await loadDashboardData();
}

// Export Data
function exportData() {
    if (!transactions.length) {
        alert('No data to export');
        return;
    }
    const blob = new Blob([JSON.stringify(transactions, null, 2)], { type: 'application/json' });
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
