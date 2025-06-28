<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';

  let alerts = [];
  let triggeredAlerts = [];
  let activeAlerts = [];
  let showCreateAlertModal = false;
  let newAlertAddress = '';
  let newAlertType = 'new_transaction';
  let newAlertThreshold = 0.1;
  let newAlertEmail = '';

  onMount(() => {
    // Mock data
    alerts = [
      {
        id: 1,
        address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
        type: 'new_transaction',
        threshold: 0.1,
        email: 'investigator@example.com',
        status: 'active',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2),
        last_triggered: new Date(Date.now() - 1000 * 60 * 60 * 6),
        trigger_count: 3
      },
      {
        id: 2,
        address: '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
        type: 'high_risk_transaction',
        threshold: 0.7,
        email: 'investigator@example.com',
        status: 'active',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5),
        last_triggered: null,
        trigger_count: 0
      },
      {
        id: 3,
        address: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
        type: 'large_transaction',
        threshold: 0.5,
        email: 'analyst@example.com',
        status: 'active',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1),
        last_triggered: new Date(Date.now() - 1000 * 60 * 60 * 2),
        trigger_count: 1
      },
      {
        id: 4,
        address: '1FvzCLoTPGANNjWoUo6jUGuAG3wg1w4YjR',
        type: 'suspicious_pattern',
        threshold: 0.8,
        email: 'investigator@example.com',
        status: 'paused',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10),
        last_triggered: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3),
        trigger_count: 5
      }
    ];

    // Separate alerts into triggered and active
    triggeredAlerts = alerts.filter(alert => alert.trigger_count > 0);
    activeAlerts = alerts.filter(alert => alert.status === 'active');
  });

  function handleCreateAlert() {
    if (newAlertAddress.trim() && newAlertEmail.trim()) {
      const newAlert = {
        id: Date.now(),
        address: newAlertAddress,
        type: newAlertType,
        threshold: newAlertThreshold,
        email: newAlertEmail,
        status: 'active',
        created_at: new Date(),
        last_triggered: null,
        trigger_count: 0
      };
      
      alerts = [...alerts, newAlert];
      activeAlerts = alerts.filter(alert => alert.status === 'active');
      triggeredAlerts = alerts.filter(alert => alert.trigger_count > 0);
      
      showCreateAlertModal = false;
      newAlertAddress = '';
      newAlertType = 'new_transaction';
      newAlertThreshold = 0.1;
      newAlertEmail = '';
    }
  }

  function handleToggleAlert(alertId) {
    alerts = alerts.map(alert => 
      alert.id === alertId 
        ? { ...alert, status: alert.status === 'active' ? 'paused' : 'active' }
        : alert
    );
    
    // Update filtered arrays
    activeAlerts = alerts.filter(alert => alert.status === 'active');
    triggeredAlerts = alerts.filter(alert => alert.trigger_count > 0);
  }

  function handleDeleteAlert(alertId) {
    if (confirm('Are you sure you want to delete this alert?')) {
      alerts = alerts.filter(alert => alert.id !== alertId);
      activeAlerts = alerts.filter(alert => alert.status === 'active');
      triggeredAlerts = alerts.filter(alert => alert.trigger_count > 0);
    }
  }

  function getAlertTypeLabel(type) {
    switch (type) {
      case 'new_transaction': return 'New Transaction';
      case 'high_risk_transaction': return 'High Risk Transaction';
      case 'large_transaction': return 'Large Transaction';
      case 'suspicious_pattern': return 'Suspicious Pattern';
      default: return type;
    }
  }

  function getAlertTypeIcon(type) {
    switch (type) {
      case 'new_transaction': return '🔄';
      case 'high_risk_transaction': return '⚠️';
      case 'large_transaction': return '💰';
      case 'suspicious_pattern': return '🚨';
      default: return '🔔';
    }
  }

  function getStatusColor(status) {
    return status === 'active' ? '#28a745' : '#6c757d';
  }

  function formatDate(date) {
    if (!date) return 'Never';
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  }

  function formatAddress(address) {
    return `${address.substring(0, 12)}...${address.substring(address.length - 8)}`;
  }
</script>

<div class="alerts" in:fly={{ y: 20, duration: 500 }}>
  <!-- Alerts Overview -->
  <div class="alerts-overview">
    <div class="overview-card">
      <div class="overview-content">
        <h3>{alerts.length}</h3>
        <p>Total Alerts</p>
      </div>
    </div>
    <div class="overview-card">
      <div class="overview-content">
        <h3>{activeAlerts.length}</h3>
        <p>Active Alerts</p>
      </div>
    </div>
    <div class="overview-card">
      <div class="overview-content">
        <h3>{triggeredAlerts.length}</h3>
        <p>Triggered Alerts</p>
      </div>
    </div>
    <div class="overview-card">
      <div class="overview-content">
        <h3>{alerts.filter(a => a.status === 'paused').length}</h3>
        <p>Paused Alerts</p>
      </div>
    </div>
  </div>

  <!-- Triggered Alerts Table -->
  <div class="alerts-section">
    <div class="section-header">
      <h2>Triggered Alerts ({triggeredAlerts.length})</h2>
      <button class="btn btn-primary" on:click={() => showCreateAlertModal = true}>
        Create Alert
      </button>
    </div>

    {#if triggeredAlerts.length > 0}
      <div class="table-container">
        <table class="alerts-table">
          <thead>
            <tr>
              <th>Address</th>
              <th>Alert Type</th>
              <th>Threshold</th>
              <th>Last Triggered</th>
              <th>Trigger Count</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each triggeredAlerts as alert, i}
              <tr class={i % 2 === 0 ? 'even-row' : 'odd-row'}>
                <td><code title={alert.address}>{formatAddress(alert.address)}</code></td>
                <td>
                  <span class="alert-type-badge">
                    {getAlertTypeIcon(alert.type)} {getAlertTypeLabel(alert.type)}
                  </span>
                </td>
                <td>{(alert.threshold * 100).toFixed(0)}%</td>
                <td>{formatDate(alert.last_triggered)}</td>
                <td>
                  <span class="trigger-count">{alert.trigger_count}</span>
                </td>
                <td>
                  <span class="status-badge {alert.status}">
                    {alert.status.charAt(0).toUpperCase() + alert.status.slice(1)}
                  </span>
                </td>
                <td class="actions-cell">
                  <button 
                    class="action-btn"
                    on:click={() => handleToggleAlert(alert.id)}
                    title={alert.status === 'active' ? 'Pause Alert' : 'Resume Alert'}
                  >
                    {alert.status === 'active' ? '⏸️' : '▶️'}
                  </button>
                  <button 
                    class="action-btn delete-btn"
                    on:click={() => handleDeleteAlert(alert.id)}
                    title="Delete Alert"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <div class="empty-state">
        <div class="empty-icon">🔔</div>
        <h4>No triggered alerts</h4>
        <p>Alerts that have been triggered will appear here.</p>
      </div>
    {/if}
  </div>

  <!-- Active Alerts Table -->
  <div class="alerts-section">
    <div class="section-header">
      <h2>Active Alerts ({activeAlerts.length})</h2>
    </div>

    {#if activeAlerts.length > 0}
      <div class="table-container">
        <table class="alerts-table">
          <thead>
            <tr>
              <th>Address</th>
              <th>Alert Type</th>
              <th>Threshold</th>
              <th>Email</th>
              <th>Created</th>
              <th>Last Triggered</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each activeAlerts as alert, i}
              <tr class={i % 2 === 0 ? 'even-row' : 'odd-row'}>
                <td><code title={alert.address}>{formatAddress(alert.address)}</code></td>
                <td>
                  <span class="alert-type-badge">
                    {getAlertTypeIcon(alert.type)} {getAlertTypeLabel(alert.type)}
                  </span>
                </td>
                <td>{(alert.threshold * 100).toFixed(0)}%</td>
                <td>{alert.email}</td>
                <td>{formatDate(alert.created_at)}</td>
                <td>{formatDate(alert.last_triggered)}</td>
                <td class="actions-cell">
                  <button 
                    class="action-btn"
                    on:click={() => handleToggleAlert(alert.id)}
                    title="Pause Alert"
                  >
                    ⏸️
                  </button>
                  <button 
                    class="action-btn delete-btn"
                    on:click={() => handleDeleteAlert(alert.id)}
                    title="Delete Alert"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <div class="empty-state">
        <div class="empty-icon">🔔</div>
        <h4>No active alerts</h4>
        <p>Create your first alert to start monitoring Bitcoin addresses for suspicious activity.</p>
        <button class="btn btn-primary" on:click={() => showCreateAlertModal = true}>
          Create First Alert
        </button>
      </div>
    {/if}
  </div>

  <!-- Create Alert Modal -->
  {#if showCreateAlertModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Create New Alert</h3>
          <button class="modal-close" on:click={() => showCreateAlertModal = false}>×</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label for="alert-address">Bitcoin Address:</label>
            <input 
              id="alert-address" 
              type="text" 
              bind:value={newAlertAddress}
              placeholder="Enter Bitcoin address to monitor..."
            />
          </div>
          
          <div class="form-group">
            <label for="alert-type">Alert Type:</label>
            <select id="alert-type" bind:value={newAlertType}>
              <option value="new_transaction">New Transaction</option>
              <option value="high_risk_transaction">High Risk Transaction</option>
              <option value="large_transaction">Large Transaction</option>
              <option value="suspicious_pattern">Suspicious Pattern</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="alert-threshold">Risk Threshold (%):</label>
            <input 
              id="alert-threshold" 
              type="range" 
              min="0" 
              max="100" 
              bind:value={newAlertThreshold}
              on:input={(e) => newAlertThreshold = e.target.value / 100}
            />
            <span class="threshold-value">{(newAlertThreshold * 100).toFixed(0)}%</span>
          </div>
          
          <div class="form-group">
            <label for="alert-email">Notification Email:</label>
            <input 
              id="alert-email" 
              type="email" 
              bind:value={newAlertEmail}
              placeholder="Enter email for notifications..."
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showCreateAlertModal = false}>Cancel</button>
          <button class="btn btn-primary" on:click={handleCreateAlert}>Create Alert</button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .alerts {
    max-width: 1200px;
    margin: 0 auto;
  }

  .alerts-overview {
    display: flex;
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
  }

  .overview-card {
    flex: 1;
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 0;
    box-shadow: none;
  }

  .overview-content h3 {
    margin: 0;
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
  }

  .overview-content p {
    margin: 0;
    color: var(--text-secondary);
    font-size: var(--font-size-base);
  }

  .alerts-section {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
  }

  .section-header h2 {
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }

  .alerts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: var(--spacing-lg);
  }

  .alert-card {
    background: var(--background-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-lg);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    box-shadow: none;
  }

  .alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
  }

  .alert-type .type-label {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }

  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    background: var(--background-tertiary);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
  }

  .status-badge.active {
    background: var(--accent-color);
    color: white;
    border: 1px solid var(--accent-color);
  }

  .status-badge.paused {
    background: var(--background-tertiary);
    color: var(--text-tertiary);
    border: 1px solid var(--border-color);
  }

  .alert-content {
    margin-bottom: 1rem;
  }

  .address-info {
    display: flex;
    gap: var(--spacing-xs);
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  .address-label {
    font-weight: var(--font-weight-medium);
    color: var(--text-tertiary);
  }

  .address-value {
    font-family: monospace;
    color: var(--text-primary);
  }

  .alert-details {
    display: flex;
    gap: var(--spacing-lg);
    margin-top: var(--spacing-sm);
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .detail-label {
    color: var(--text-tertiary);
    font-size: var(--font-size-xs);
  }

  .detail-value {
    color: var(--text-primary);
    font-size: var(--font-size-sm);
  }

  .alert-actions {
    display: flex;
    gap: 0.5rem;
  }

  .empty-state {
    text-align: center;
    padding: 3rem;
    color: #6c757d;
  }

  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .empty-state h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .empty-state p {
    margin: 0 0 1.5rem 0;
    font-size: 1rem;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-primary {
    background-color: #007bff;
    color: white;
  }

  .btn-primary:hover {
    background-color: #0056b3;
  }

  .btn-secondary {
    background-color: #6c757d;
    color: white;
  }

  .btn-secondary:hover {
    background-color: #545b62;
  }

  .btn-danger {
    background-color: #dc3545;
    color: white;
  }

  .btn-danger:hover {
    background-color: #c82333;
  }

  .btn-icon {
    margin-right: 0.5rem;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal {
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #6c757d;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-close:hover {
    color: #2c3e50;
  }

  .modal-content {
    padding: 1.5rem;
  }

  .modal-footer {
    padding: 1.5rem;
    border-top: 1px solid #e9ecef;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #2c3e50;
  }

  .form-group input,
  .form-group select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-size: 0.9rem;
    font-family: inherit;
  }

  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }

  .threshold-value {
    margin-left: 1rem;
    font-weight: 500;
    color: #007bff;
  }

  @media (max-width: 768px) {
    .section-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .alerts-grid {
      grid-template-columns: 1fr;
    }

    .alert-actions {
      flex-direction: column;
    }
  }
</style> 