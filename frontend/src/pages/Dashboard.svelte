<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { navigate } from 'svelte-routing';
  import { apiService, alertsApi } from '../services/api.js';
  import CategoryChart from '../components/CategoryChart.svelte';
  import LineChart from '../components/LineChart.svelte';

  let categoryDistribution = {};
  let stats = null;
  let addressCountOverTime = {};
  let lastAddresses = null;
  let alerts = null;

  // Individual loading flags so widgets can render independently
  let statsLoaded = false;
  let categoryLoaded = false;
  let timelineLoaded = false;
  let addressesLoaded = false;
  let alertsLoaded = false;

  onMount(async () => {
    try {
      const statistics = await apiService.getStatistics();
      stats = {
        totalAddresses: statistics.total_addresses || 0,
        suspiciousAddresses: statistics.suspicious_addresses || 0,
        activeCases: 0,
        pendingAlerts: 0
      };
      statsLoaded = true;

      const distribution = await apiService.getCategoryDistribution();
      const sorted = Object.entries(distribution)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      categoryDistribution = Object.fromEntries(sorted);
      categoryLoaded = true;

      addressCountOverTime = await apiService.getAddressCountOverTime();
      timelineLoaded = true;

      const history = await apiService.getHistory(6, 0, {});
      lastAddresses = history.classifications || [];
      addressesLoaded = true;

      try {
        const alertsResponse = await alertsApi.getTriggered();
        const triggeredAlerts = alertsResponse.alerts || [];
        alerts = triggeredAlerts.map(alert => ({
          id: alert.id,
          type: getAlertTypeLabel(alert.type),
          description: `${alert.type.replace('_', ' ')} alert triggered for ${alert.address.substring(0, 8)}...`,
          address: alert.address,
          lastTriggered: alert.last_triggered ? new Date(alert.last_triggered) : null,
          triggerCount: alert.trigger_count || 0
        }));
        if (stats) stats.pendingAlerts = triggeredAlerts.length;
      } catch (error) {
        console.error('Failed to fetch triggered alerts:', error);
        alerts = [];
      }
      alertsLoaded = true;
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
      statsLoaded = true;
      categoryLoaded = true;
      timelineLoaded = true;
      addressesLoaded = true;
      alertsLoaded = true;
    }
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

  function getAlertTypeLabel(type) {
    switch (type) {
      case 'new_transaction': return 'New Transaction';
      case 'high_risk_transaction': return 'High Risk';
      case 'large_transaction': return 'Large Transaction';
      case 'suspicious_pattern': return 'Suspicious Pattern';
      default: return type;
    }
  }

  function handleAddressClick(address) {
    // Client-side navigation to the analysis page (a full page load would
    // 404 on static hosts without SPA rewrites)
    navigate(`/analysis?address=${encodeURIComponent(address)}`);
  }

</script>

<div class="dashboard" in:fly={{ y: 20, duration: 500 }}>
  <div class="dashboard-columns">
    <div class="left-col">
      <!-- Statistics Cards -->
      <div class="stats-grid">
        {#if statsLoaded && stats}
          <div class="stat-card">
            <div class="stat-content">
              <span class="stat-number">{stats.totalAddresses.toLocaleString()}</span>
              <span class="stat-desc">Total Addresses <br/>Analyzed</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <span class="stat-number">{stats.suspiciousAddresses}</span>
              <span class="stat-desc">Suspicious <br/>Addresses</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <span class="stat-number">{stats.pendingAlerts}</span>
              <span class="stat-desc">Pending Alerts</span>
            </div>
          </div>
        {:else}
          {#each Array(3) as _}
            <div class="stat-card skeleton-pulse">
              <div class="stat-content">
                <span class="skel-block" style="width:2.5rem; height:1.8rem;"></span>
                <span class="skel-block" style="width:5rem; height:0.8rem;"></span>
              </div>
            </div>
          {/each}
        {/if}
      </div>

      <!-- Category Distribution -->
      <div class="dashboard-card">
        <div class="card-header">
          <h2>Category Distribution</h2>
        </div>
        <div class="category-distribution">
          {#if categoryLoaded}
            {#if Object.keys(categoryDistribution).length > 0}
              <CategoryChart data={categoryDistribution} />
            {:else}
              <p style="text-align:center; color: var(--text-secondary); margin-top: 2rem;">No data to display</p>
            {/if}
          {:else}
            <div class="chart-skeleton">
              {#each Array(5) as _, i}
                <div class="chart-skel-row">
                  <span class="skel-block" style="width:5rem; height:0.7rem;"></span>
                  <span class="skel-block" style="flex:1; max-width:{70 - i * 12}%; height:0.9rem;"></span>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>

      <!-- Addresses Analyzed Over Time -->
      <div class="dashboard-card">
        <div class="card-header">
          <h2>Addresses Analyzed Over Time</h2>
        </div>
        <div class="line-distribution">
          {#if timelineLoaded}
            {#if Object.keys(addressCountOverTime).length > 0}
              <LineChart data={addressCountOverTime} />
            {:else}
              <p style="text-align:center; color: var(--text-secondary); margin-top: 2rem;">No data to display</p>
            {/if}
          {:else}
            <div class="skel-block" style="width:100%; height:180px; border-radius:var(--border-radius-md);"></div>
          {/if}
        </div>
      </div>
    </div>
    <div class="right-col">
      <!-- Alerts Widget -->
      <div class="dashboard-card alerts-widget">
        <div class="card-header">
          <h2>Alerts Triggered ({(alerts || []).length})</h2>
          <a href="/alerts" class="view-all">View All</a>
        </div>
        <div class="alerts-widget-content">
          {#if alertsLoaded}
            {#if (alerts || []).length > 0}
              <ul class="alerts-list-widget">
                {#each alerts as alert}
                  <li class="alert-item" on:click={() => handleAddressClick(alert.address)}>
                    <div class="alert-header">
                      <span class="alert-type">{alert.type}</span>
                      <span class="alert-time">{formatTimeAgo(alert.lastTriggered || new Date())}</span>
                    </div>
                    <div class="alert-desc">{alert.description}</div>
                    <div class="alert-meta">Triggered {alert.triggerCount} time{alert.triggerCount !== 1 ? 's' : ''}</div>
                  </li>
                {/each}
              </ul>
            {:else}
              <p class="no-alerts-text">No alerts have been triggered yet.</p>
            {/if}
          {:else}
            <div class="skel-lines">
              {#each Array(3) as _}
                <div class="skel-block" style="width:100%; height:0.7rem; margin-bottom:0.6rem;"></div>
              {/each}
            </div>
          {/if}
        </div>
      </div>

      <!-- Recent Addresses -->
      <div class="dashboard-card recent-history-card">
        <div class="card-header">
          <h2>Recent Addresses</h2>
          <a href="/history" class="view-all">View All</a>
        </div>
        <table class="recent-addresses-table">
          <thead>
            <tr>
              <th>Address</th>
              <th>Category</th>
            </tr>
          </thead>
          <tbody>
            {#if addressesLoaded}
              {#each (lastAddresses || []) as item, i}
                <tr
                  class={i % 2 === 0 ? 'even-row' : 'odd-row'}
                  on:click={() => handleAddressClick(item.address)}
                  title="Click to re-classify this address"
                >
                  <td><code>{item.address.slice(0, 10)}...</code></td>
                  <td class="category-col">{getCategoryDescription(item.classification)}</td>
                </tr>
              {/each}
              {#if (lastAddresses || []).length === 0}
                <tr><td colspan="2" style="text-align:center; color: var(--text-secondary);">No data</td></tr>
              {/if}
            {:else}
              {#each Array(6) as _, i}
                <tr class={i % 2 === 0 ? 'even-row' : 'odd-row'}>
                  <td><span class="skel-block" style="width:5rem; height:0.7rem;"></span></td>
                  <td><span class="skel-block" style="width:6rem; height:0.7rem;"></span></td>
                </tr>
              {/each}
            {/if}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<style>
  .dashboard {
    margin: 0 auto;
    display: flex;
    flex-direction: column;
  }
  .dashboard-columns {
    min-height: 0;
  }
  .left-col, .right-col {
    gap: 0.7rem;
    padding-bottom: 0;
  }
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

  /* Statistics Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-md);
    margin-bottom: 0;
    width: 100%;
  }

  .stat-card {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-sm) var(--spacing-xl);
    transition: border-color var(--transition-fast);
    min-width: 0;
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
  }

  .dashboard-columns {
    display: flex;
    flex-direction: row;
    gap: var(--spacing-lg);
    align-items: stretch;
  }
  .left-col {
    flex: 3 1 0;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
  .right-col {
    flex: 2 1 0;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
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
    table-layout: fixed;
  }
  .recent-addresses-table th, .recent-addresses-table td {
    padding: 0.4rem 0.6rem;
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
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
    cursor: pointer;
    transition: background-color var(--transition-fast);
  }
  .recent-addresses-table .odd-row {
    background: var(--background-primary);
    cursor: pointer;
    transition: background-color var(--transition-fast);
  }
  .recent-addresses-table .even-row:hover,
  .recent-addresses-table .odd-row:hover {
    background: var(--accent-color-light);
  }

  .recent-history-card {
    padding-top: var(--spacing-md);
    padding-right: 0;
    padding-bottom: 0;
    padding-left: 0;
    border-radius: var(--border-radius-lg);
    overflow: hidden;
    min-height: 140px;
  }
  .recent-history-card .card-header {
    padding-left: var(--spacing-md);
    padding-right: var(--spacing-md);
    justify-content: space-between;
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


  .alerts-list-widget {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .alert-item {
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border-color-light);
    cursor: pointer;
    transition: background-color var(--transition-fast);
  }
  .alert-item:last-child {
    border-bottom: none;
  }
  .alert-item:hover {
    background-color: var(--background-secondary);
    border-radius: var(--border-radius-md);
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }
  .alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
  }
  .alert-type {
    color: var(--accent-color);
    font-weight: 600;
    font-size: 0.9rem;
  }
  .alert-time {
    color: var(--text-tertiary);
    font-size: 0.8rem;
  }
  .alert-desc {
    color: var(--text-primary);
    font-size: 0.85rem;
    margin-bottom: 0.25rem;
  }
  .alert-meta {
    color: var(--text-secondary);
    font-size: 0.8rem;
  }
  .no-alerts-text {
    color: var(--text-secondary);
    text-align: center;
    height: 100%;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .alerts-widget {
    flex: 1 1 0;
    min-height: 140px;
    display: flex;
    flex-direction: column;
  }

  .alerts-widget-content {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem 0 0.5rem 0;
  }

  /* Stack columns when the content area gets narrow.
     Above 900px the sidebar takes 280px, so viewport 1100px → ~780px content.
     Below 900px sidebar becomes top bar → full viewport available. */
  @media (max-width: 1100px) {
    .dashboard-columns {
      flex-direction: column;
    }

    .left-col,
    .right-col {
      flex: 1 1 auto;
      width: 100%;
      gap: var(--spacing-md);
    }
  }

  @media (max-width: 600px) {
    .stats-grid {
      grid-template-columns: 1fr;
    }

    .stat-desc br {
      display: none;
    }
  }

  /* Skeleton loading */
  .skel-block {
    display: inline-block;
    background: linear-gradient(
      90deg,
      var(--background-secondary) 25%,
      var(--background-tertiary) 50%,
      var(--background-secondary) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
  }

  .skeleton-pulse {
    pointer-events: none;
  }

  .chart-skeleton {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.5rem 0 1rem;
  }

  .chart-skel-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .skel-lines {
    padding: 1rem 0;
  }

  @keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }
</style> 