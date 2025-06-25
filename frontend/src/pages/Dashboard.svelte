<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';

  let recentActivity = [];
  let activeAlerts = [];
  let stats = {
    totalAddresses: 0,
    suspiciousAddresses: 0,
    activeCases: 0,
    pendingAlerts: 0
  };

  onMount(() => {
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

    stats = {
      totalAddresses: 1247,
      suspiciousAddresses: 89,
      activeCases: 12,
      pendingAlerts: 5
    };
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
</script>

<div class="dashboard" in:fly={{ y: 20, duration: 500 }}>
  <!-- Statistics Cards -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-content">
        <h3>{stats.totalAddresses.toLocaleString()}</h3>
        <p>Total Addresses Analyzed</p>
      </div>
    </div>
    
    <div class="stat-card">
      <div class="stat-content">
        <h3>{stats.suspiciousAddresses}</h3>
        <p>Suspicious Addresses</p>
      </div>
    </div>
    
    <div class="stat-card">
      <div class="stat-content">
        <h3>{stats.activeCases}</h3>
        <p>Active Cases</p>
      </div>
    </div>
    
    <div class="stat-card">
      <div class="stat-content">
        <h3>{stats.pendingAlerts}</h3>
        <p>Pending Alerts</p>
      </div>
    </div>
  </div>

  <!-- Main Content Grid -->
  <div class="dashboard-grid">
    <!-- Recent Activity -->
    <div class="dashboard-card">
      <div class="card-header">
        <h2>Recent Activity</h2>
        <a href="/history" class="view-all">View All</a>
      </div>
      
      <div class="activity-list">
        {#each recentActivity as activity}
          <div class="activity-item" in:fade={{ delay: activity.id * 100 }}>
            <div class="activity-content">
              <div class="activity-title">
                {#if activity.type === 'classification'}
                  Address classified as {activity.result}
                {:else if activity.type === 'case_created'}
                  Case "{activity.caseName}" created
                {:else if activity.type === 'alert_triggered'}
                  Alert triggered for {activity.address.substring(0, 12)}...
                {/if}
              </div>
              <div class="activity-meta">
                {#if activity.address}
                  <span class="address">{activity.address.substring(0, 12)}...</span>
                {/if}
                {#if activity.riskScore}
                  <span class="risk-score">Risk: {(activity.riskScore * 100).toFixed(0)}%</span>
                {/if}
                <span class="timestamp">{formatTimeAgo(activity.timestamp)}</span>
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Active Alerts -->
    <div class="dashboard-card">
      <div class="card-header">
        <h2>Active Alerts</h2>
        <a href="/alerts" class="view-all">View All</a>
      </div>
      
      <div class="alerts-list">
        {#each activeAlerts as alert}
          <div class="alert-item" in:fade={{ delay: alert.id * 100 }}>
            <div class="alert-severity" style="background-color: {getSeverityColor(alert.severity)}"></div>
            <div class="alert-content">
              <div class="alert-title">{alert.type.replace('_', ' ').toUpperCase()}</div>
              <div class="alert-description">{alert.description}</div>
              <div class="alert-meta">
                <span class="address">{alert.address.substring(0, 12)}...</span>
                <span class="timestamp">{formatTimeAgo(alert.timestamp)}</span>
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>

  <!-- Quick Actions -->
  <div class="quick-actions">
    <h2>Quick Actions</h2>
    <div class="actions-grid">
      <a href="/analysis" class="action-card">
        <h3>Analyze Address</h3>
        <p>Classify a single Bitcoin address</p>
      </a>
      
      <a href="/batch" class="action-card">
        <h3>Batch Analysis</h3>
        <p>Analyze multiple addresses at once</p>
      </a>
      
      <a href="/cases" class="action-card">
        <h3>Create Case</h3>
        <p>Start a new investigation case</p>
      </a>
      
      <a href="/alerts" class="action-card">
        <h3>View Alerts</h3>
        <p>Check all active alerts</p>
      </a>
    </div>
  </div>
</div>

<style>
  .dashboard {
    max-width: 1200px;
    margin: 0 auto;
  }

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
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
  }

  .stat-card {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    transition: border-color var(--transition-fast);
  }

  .stat-card:hover {
    border-color: var(--border-color-light);
  }

  .stat-content h3 {
    font-size: var(--font-size-3xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0 0 var(--spacing-sm) 0;
  }

  .stat-content p {
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
    margin: 0;
  }

  /* Dashboard Grid */
  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
  }

  @media (max-width: 768px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }
  }

  .dashboard-card {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
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

  /* Activity List */
  .activity-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .activity-item {
    padding: var(--spacing-md);
    border: 1px solid var(--border-color-light);
    border-radius: var(--border-radius-md);
    background: var(--background-secondary);
  }

  .activity-title {
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);
    font-size: var(--font-size-sm);
  }

  .activity-meta {
    display: flex;
    gap: var(--spacing-md);
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
  }

  .address {
    font-family: monospace;
  }

  .risk-score {
    color: var(--accent-color);
    font-weight: var(--font-weight-medium);
  }

  /* Alerts List */
  .alerts-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .alert-item {
    display: flex;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    border: 1px solid var(--border-color-light);
    border-radius: var(--border-radius-md);
    background: var(--background-secondary);
  }

  .alert-severity {
    width: 4px;
    border-radius: var(--border-radius-sm);
    flex-shrink: 0;
  }

  .alert-content {
    flex: 1;
  }

  .alert-title {
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);
    font-size: var(--font-size-sm);
  }

  .alert-description {
    color: var(--text-secondary);
    margin-bottom: var(--spacing-xs);
    font-size: var(--font-size-sm);
  }

  .alert-meta {
    display: flex;
    gap: var(--spacing-md);
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
  }

  /* Quick Actions */
  .quick-actions {
    margin-top: var(--spacing-xl);
  }

  .quick-actions h2 {
    margin-bottom: var(--spacing-lg);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
  }

  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
  }

  .action-card {
    display: block;
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    text-decoration: none;
    transition: all var(--transition-fast);
  }

  .action-card:hover {
    border-color: var(--accent-color);
    background: var(--background-secondary);
  }

  .action-card h3 {
    color: var(--text-primary);
    margin: 0 0 var(--spacing-sm) 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
  }

  .action-card p {
    color: var(--text-secondary);
    margin: 0;
    font-size: var(--font-size-sm);
  }
</style> 