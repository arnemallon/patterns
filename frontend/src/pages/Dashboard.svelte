<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { apiService } from '../services/api.js';
  import CategoryChart from '../components/CategoryChart.svelte';
  import LineChart from '../components/LineChart.svelte';

  let recentActivity = [];
  let activeAlerts = [];
  let categoryDistribution = {};
  let stats = {
    totalAddresses: 0,
    suspiciousAddresses: 0,
    activeCases: 0,
    pendingAlerts: 0
  };  
  let addressCountOverTime = {};
  let lastAddresses = [];
  let alerts = [];

  onMount(async () => {
    try {
      // Fetch actual statistics from the backend
      const statistics = await apiService.getStatistics();
      stats = {
        totalAddresses: statistics.total_addresses || 0,
        suspiciousAddresses: statistics.suspicious_addresses || 0,
        activeCases: 0, // This would need a separate endpoint for cases
        pendingAlerts: 0 // This would need a separate endpoint for alerts
      };

      // Fetch category distribution for the chart
      const distribution = await apiService.getCategoryDistribution();
      console.log('Fetched category distribution from API:', distribution);
      // Sort and keep top 5 categories
      const sorted = Object.entries(distribution)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      categoryDistribution = Object.fromEntries(sorted);
      console.log('categoryDistribution state (top 5):', categoryDistribution);

      // Fetch address count over time for the line chart
      addressCountOverTime = await apiService.getAddressCountOverTime();

      // Fetch last 6 analyzed addresses
      const history = await apiService.getHistory(6, 0, {});
      lastAddresses = history.classifications || [];

      // Fetch alerts (replace with real API call if available)
      // Example: alerts = await apiService.getAlerts();
      alerts = [
        {
          id: 1,
          type: 'High Risk Transaction',
          description: 'Large transaction detected from known mixer address'
        },
        {
          id: 2,
          type: 'New Transaction',
          description: 'New transaction detected on monitored address'
        }
      ];
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
      // Keep default values if API call fails
    }

    // Mock data - in real implementation, this would come from API
    recentActivity = [
      {
        id: 1,
        type: 'classification',
        address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
        result: 'suspicious',
        timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
        riskScore: 0.85
      },
      {
        id: 2,
        type: 'case_created',
        caseName: 'Exchange Investigation',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
      },
      {
        id: 3,
        type: 'alert_triggered',
        address: '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
        alertType: 'new_transaction',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
      }
    ];

    activeAlerts = [
      {
        id: 1,
        address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
        type: 'high_risk_transaction',
        severity: 'high',
        timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
        description: 'Large transaction detected from known mixer address'
      },
      {
        id: 2,
        address: '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
        type: 'new_transaction',
        severity: 'medium',
        timestamp: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
        description: 'New transaction detected on monitored address'
      }
    ];
  });

  function formatTimeAgo(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  }

  function getSeverityColor(severity) {
    switch (severity) {
      case 'high': return 'var(--error-color)';
      case 'medium': return 'var(--warning-color)';
      case 'low': return 'var(--success-color)';
      default: return 'var(--text-tertiary)';
    }
  }

  function getCategoryDescription(prediction) {
    const categories = [
      'Blackmail', 'Cyber-security Service', 'Darknet Market', 'Centralized Exchange',
      'P2P Financial Infrastructure Service', 'P2P Financial Service', 'Gambling',
      'Government Criminal Blacklist', 'Money Laundering', 'Ponzi Scheme',
      'Mining Pool', 'Tumbler', 'Individual Wallet'
    ];
    const index = Math.round(prediction);
    const clampedIndex = Math.max(0, Math.min(12, index));
    return categories[clampedIndex];
  }
</script>

<div class="dashboard" in:fly={{ y: 20, duration: 500 }}>
  <div class="dashboard-columns">
    <div class="left-col">
      <!-- Statistics Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-content">
            <span class="stat-number">{stats.totalAddresses.toLocaleString()}</span>
            <span class="stat-desc">Total Addresses<br/>Analyzed</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-content">
            <span class="stat-number">{stats.suspiciousAddresses}</span>
            <span class="stat-desc">Suspicious<br/>Addresses</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-content">
            <span class="stat-number">{stats.pendingAlerts}</span>
            <span class="stat-desc">Pending Alerts</span>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <!-- Category Distribution -->
      <div class="dashboard-card">
        <div class="card-header">
          <h2>Category Distribution</h2>
        </div>
        <div class="category-distribution">
          {#if Object.keys(categoryDistribution).length > 0}
            <CategoryChart data={categoryDistribution} />
          {:else}
            <p style="text-align:center; color: var(--text-secondary); margin-top: 2rem;">No data to display</p>
          {/if}
        </div>
      </div>

      <!-- Addresses Analyzed Over Time -->
      <div class="dashboard-card">
        <div class="card-header">
          <h2>Addresses Analyzed Over Time</h2>
        </div>
        <div class="line-distribution">
          {#if Object.keys(addressCountOverTime).length > 0}
            <LineChart data={addressCountOverTime} />
          {:else}
            <p style="text-align:center; color: var(--text-secondary); margin-top: 2rem;">No data to display</p>
          {/if}
        </div>
      </div>
    </div>
    <div class="right-col">
      <!-- Alerts Widget -->
      <div class="dashboard-card alerts-widget">
        <div class="card-header">
          <h2>Alerts Triggered ({alerts.length})</h2>
        </div>
        <div class="alerts-widget-content">
          {#if alerts.length > 0}
            <ul class="alerts-list-widget">
              {#each alerts as alert}
                <li><span class="alert-type">{alert.type}</span> <span class="alert-desc">- {alert.description}</span></li>
              {/each}
            </ul>
          {:else}
            <p class="no-alerts-text">No alerts have been triggered yet.</p>
          {/if}
        </div>
      </div>

      <!-- Recent Addresses -->
      <div class="dashboard-card recent-history-card">
        <div class="card-header">
          <h2>Recent Addresses</h2>
        </div>
        <table class="recent-addresses-table">
          <thead>
            <tr>
              <th>Address</th>
              <th>Category</th>
            </tr>
          </thead>
          <tbody>
            {#each lastAddresses as item, i}
              <tr class={i % 2 === 0 ? 'even-row' : 'odd-row'}>
                <td><code>{item.address.slice(0, 10)}...</code></td>
                <td class="category-col">{getCategoryDescription(item.classification)}</td>
              </tr>
            {/each}
            {#if lastAddresses.length === 0}
              <tr><td colspan="2" style="text-align:center; color: var(--text-secondary);">No data</td></tr>
            {/if}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<style>
  /* Make the dashboard fit the viewport and prevent scrolling */
  html, body {
    min-height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden;
  }
  .dashboard {
    max-width: 1200px;
    margin: 0 auto;
    min-height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .dashboard-columns {
    flex: 1 1 0;
    min-height: 0;
    overflow: hidden;
  }
  .left-col, .right-col {
    gap: 0.7rem;
    padding-bottom: 0;
  }
  /* Make category distribution more compact */
  .category-distribution {
    padding-bottom: 0.2rem;
  }
  .dashboard-card {
    padding: var(--spacing-xs) var(--spacing-md);
  }
  .card-header h2 {
    font-size: 1.1rem;
    margin-bottom: 0.2rem;
  }
  /* Reduce font size for y-axis labels in CategoryChart.svelte if needed */

  .dashboard-header {
    margin-bottom: var(--spacing-xl);
  }

  .dashboard-header h1 {
    margin-bottom: var(--spacing-sm);
    color: var(--text-primary);
  }

  .dashboard-header p {
    color: var(--text-secondary);
    font-size: var(--font-size-lg);
    margin: 0;
  }

  /* Statistics Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-md);
    margin-bottom: 0;
    margin-left: 0;
    margin-right: 0;
    justify-items: start;
    width: 100%;
  }

  .stat-card {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-sm) var(--spacing-xl);
    transition: border-color var(--transition-fast);
    min-width: 180px;
    max-width: none;
    width: 100%;
    min-height: 80px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
  }

  .stat-card:hover {
    border-color: var(--border-color-light);
  }

  .stat-content {
    display: flex;
    align-items: center;
    gap: 1rem;
    height: 100%;
  }
  .stat-number {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0;
    line-height: 1;
  }
  .stat-desc {
    color: var(--text-secondary);
    font-size: var(--font-size-xs);
    margin: 0;
    white-space: nowrap;
  }

  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
  }

  @media (max-width: 1200px) {
    .dashboard-grid {
      grid-template-columns: 1fr 1fr;
    }
  }

  @media (max-width: 768px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }
  }

  .dashboard-columns {
    display: flex;
    flex-direction: row;
    gap: var(--spacing-xl);
    align-items: flex-start;
  }
  .left-col {
    flex: 1 1 0;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
  .right-col {
    flex: 0 0 400px;
    max-width: 450px;
    min-width: 300px;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
  }
  .dashboard-card {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-md);
    transition: border-color var(--transition-fast);
    width: 100%;
    max-width: 100%;
    min-width: 0;
    box-sizing: border-box;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
  }

  .card-header h2 {
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
  }

  .view-all {
    font-size: var(--font-size-sm);
    color: var(--accent-color);
    font-weight: var(--font-weight-medium);
  }

  /* Addresses Analyzed Over Time */
  .line-distribution {
    padding-bottom: 0.5rem;
  }

  /* Recent Addresses Table */
  .recent-addresses-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
  }
  .recent-addresses-table th, .recent-addresses-table td {
    padding: 0.4rem 0.6rem;
    text-align: left;
  }
  .recent-addresses-table th {
    color: var(--text-secondary);
    font-weight: 500;
    border-bottom: 1px solid var(--border-color);
  }
  .recent-addresses-table td {
    color: var(--text-primary);
    border-bottom: 1px solid var(--border-color-light);
  }
  .recent-addresses-table tr:last-child td {
    border-bottom: none;
  }

  .recent-addresses-table .category-col {
    color: var(--accent-color);
    font-weight: var(--font-weight-medium);
  }
  .recent-addresses-table .even-row {
    background: var(--background-secondary);
  }
  .recent-addresses-table .odd-row {
    background: var(--background-primary);
  }

  .recent-history-card {
    padding-top: var(--spacing-xl);
    padding-right: 0;
    padding-bottom: 0;
    padding-left: 0;
    border-radius: var(--border-radius-lg);
    overflow: hidden;
    min-height: 140px;
  }
  .recent-history-card .card-header {
    padding-left: var(--spacing-xl);
    padding-right: var(--spacing-xl);
    justify-content: flex-start;
  }
  .recent-history-card .card-header h2 {
    text-align: left;
    margin-left: 0;
  }
  .recent-history-card .recent-addresses-table {
    margin: 0;
    padding: 0;
    border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
    overflow: hidden;
  }
  .recent-addresses-table tr:last-child td {
    border-bottom: none;
  }

  .alerts-widget-content {
    padding: 0.5rem 0 0.5rem 0;
  }
  .alerts-list-widget {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .alerts-list-widget li {
    padding: 0.3rem 0;
    color: var(--text-primary);
    font-size: 0.97rem;
  }
  .alert-type {
    color: var(--accent-color);
    font-weight: 500;
  }
  .alert-desc {
    color: var(--text-secondary);
  }
  .no-alerts-text {
    color: var(--text-secondary);
    text-align: center;
  }

  .alerts-widget {
    min-height: 240px;
  }
</style> 