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
      case 'high': return '#dc3545';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  }
</script>

<div class="dashboard" in:fly={{ y: 20, duration: 500 }}>
  <div class="dashboard-header">
    <h1>Dashboard</h1>
    <p>Welcome back! Here's what's happening with your Bitcoin analysis.</p>
  </div>

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
        <h3>Set Up Alerts</h3>
        <p>Monitor addresses for activity</p>
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
    margin-bottom: 2rem;
  }

  .dashboard-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2.5rem;
    font-weight: 700;
    color: #2c3e50;
  }

  .dashboard-header p {
    margin: 0;
    color: #6c757d;
    font-size: 1.1rem;
  }

  /* Statistics Grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .stat-card {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    transition: all 0.2s ease;
  }

  .stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  }

  .stat-icon {
    font-size: 2rem;
    margin-right: 1rem;
    color: #007bff;
  }

  .stat-content h3 {
    margin: 0 0 0.25rem 0;
    font-size: 1.8rem;
    font-weight: 700;
    color: #2c3e50;
  }

  .stat-content p {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
  }

  /* Dashboard Grid */
  .dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .dashboard-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .card-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .card-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .view-all {
    color: #007bff;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
  }

  .view-all:hover {
    text-decoration: underline;
  }

  /* Activity List */
  .activity-list {
    margin-top: 1rem;
  }

  .activity-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid #e9ecef;
  }

  .activity-item:last-child {
    border-bottom: none;
  }

  .activity-icon {
    font-size: 1.2rem;
    margin-right: 1rem;
  }

  .activity-content {
    flex: 1;
  }

  .activity-title {
    font-weight: 500;
    color: #2c3e50;
    margin-bottom: 0.25rem;
  }

  .activity-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.85rem;
    color: #6c757d;
  }

  .address {
    font-family: monospace;
    background-color: #f8f9fa;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
  }

  .risk-score {
    color: #dc3545;
    font-weight: 500;
  }

  /* Alerts List */
  .alerts-list {
    padding: 1rem;
  }

  .alert-item {
    display: flex;
    align-items: flex-start;
    padding: 1rem;
    border-radius: 8px;
    transition: background-color 0.2s ease;
  }

  .alert-item:hover {
    background-color: #f8f9fa;
  }

  .alert-severity {
    width: 4px;
    height: 100%;
    border-radius: 2px;
    margin-right: 1rem;
    margin-top: 0.25rem;
  }

  .alert-content {
    flex: 1;
  }

  .alert-title {
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 0.25rem;
    font-size: 0.9rem;
  }

  .alert-description {
    color: #6c757d;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
  }

  .alert-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.8rem;
    color: #6c757d;
  }

  /* Quick Actions */
  .quick-actions {
    margin-top: 2rem;
  }

  .quick-actions h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 1rem;
  }

  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
  }

  .action-card {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    text-decoration: none;
    color: inherit;
    transition: all 0.2s ease;
    text-align: center;
  }

  .action-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  }

  .action-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: #007bff;
  }

  .action-card h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #6c757d;
  }

  .action-card p {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }
    
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .actions-grid {
      grid-template-columns: 1fr;
    }
  }
</style> 