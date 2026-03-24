<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { apiService, alertsApi } from '../services/api.js';

  let alerts = [];
  let triggeredAlerts = [];
  let activeAlerts = [];
  let showCreateAlertModal = false;
  let newAlertAddress = '';
  let newAlertType = 'new_transaction';
  let newAlertThreshold = 10; // Store as percentage (0-100)
  let newAlertEmail = '';
  let loading = true;
  let creating = false;
  let error = null;

  onMount(async () => {
    await loadAlerts();
  });

  async function loadAlerts() {
    try {
      loading = true;
      const { alerts: serverAlerts } = await alertsApi.list();
      alerts = (serverAlerts || []).map(a => ({
        ...a,
        // normalize date strings to Date objects for formatting
        created_at: a.created_at ? new Date(a.created_at) : null,
        last_triggered: a.last_triggered ? new Date(a.last_triggered) : null
      }));
      triggeredAlerts = alerts.filter(alert => (alert.trigger_count || 0) > 0);
      activeAlerts = alerts.filter(alert => alert.status === 'active');
    } catch (err) {
      error = err.message || 'Failed to load alerts';
    } finally {
      loading = false;
    }
  }

  async function handleCreateAlert() {
    // Basic validation
    if (!newAlertAddress.trim()) {
      error = 'Bitcoin address is required';
      return;
    }
    
    if (!newAlertEmail.trim()) {
      error = 'Email address is required';
      return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newAlertEmail.trim())) {
      error = 'Please enter a valid email address';
      return;
    }
    
    // Basic Bitcoin address validation
    if (!(newAlertAddress.startsWith('1') || newAlertAddress.startsWith('3') || newAlertAddress.startsWith('bc1'))) {
      error = 'Please enter a valid Bitcoin address';
      return;
    }
    
    try {
      creating = true;
      const { alert: created } = await alertsApi.create({
        address: newAlertAddress,
        type: newAlertType,
        threshold: newAlertThreshold / 100, // Convert percentage to decimal
        email: newAlertEmail
      });
      const newAlert = {
        ...created,
        created_at: created.created_at ? new Date(created.created_at) : new Date(),
        last_triggered: created.last_triggered ? new Date(created.last_triggered) : null
      };
      alerts = [...alerts, newAlert];
      activeAlerts = alerts.filter(alert => alert.status === 'active');
      triggeredAlerts = alerts.filter(alert => (alert.trigger_count || 0) > 0);
      
      showCreateAlertModal = false;
      newAlertAddress = '';
      newAlertType = 'new_transaction';
      newAlertThreshold = 10; // Reset to 10%
      newAlertEmail = '';
      error = null; // Clear any previous errors
    } catch (err) {
      error = err.message || 'Failed to create alert';
    } finally {
      creating = false;
    }
  }

  async function handleToggleAlert(alertId) {
    try {
      const { alert: updated } = await alertsApi.toggle(alertId);
      alerts = alerts.map(alert => 
        alert.id === alertId 
          ? { ...alert, ...updated, created_at: updated.created_at ? new Date(updated.created_at) : alert.created_at, last_triggered: updated.last_triggered ? new Date(updated.last_triggered) : alert.last_triggered }
          : alert
      );
      activeAlerts = alerts.filter(alert => alert.status === 'active');
      triggeredAlerts = alerts.filter(alert => (alert.trigger_count || 0) > 0);
    } catch (err) {
      error = err.message || 'Failed to toggle alert';
    }
  }

  async function handleDeleteAlert(alertId) {
    if (confirm('Are you sure you want to delete this alert?')) {
      try {
        await alertsApi.remove(alertId);
        alerts = alerts.filter(alert => alert.id !== alertId);
        activeAlerts = alerts.filter(alert => alert.status === 'active');
        triggeredAlerts = alerts.filter(alert => (alert.trigger_count || 0) > 0);
      } catch (err) {
        error = err.message || 'Failed to delete alert';
      }
    }
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

  function getStatusColor(status) {
    return status === 'active' ? 'rgb(0, 136, 255)' : '#6c757d';
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

  function handleAddressClick(address) {
    window.location.href = `/analysis?address=${address}`;
  }

  // Reactive statement to update threshold slider background
  $: thresholdGradient = `linear-gradient(to right, #e9ecef 0%, #e9ecef ${newAlertThreshold}%, rgb(0, 136, 255) ${newAlertThreshold}%, rgb(0, 136, 255) 100%)`;
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

  {#if error}
    <div class="error-message" in:fade>
      {error}
    </div>
  {/if}

  <!-- Triggered Alerts Table -->
  <div class="alerts-section">
    <div class="section-header">
      <h2>Triggered Alerts ({triggeredAlerts.length})</h2>
    </div>

    {#if loading}
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading alerts...</p>
      </div>
    {:else if triggeredAlerts.length > 0}
      <div class="table-container">
        <table class="alerts-table">
          <thead>
            <tr>
              <th>Address</th>
              <th>Alert Type</th>
              <th>Threshold</th>
              <th>Last Triggered</th>
              <th>Trigger Count</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each triggeredAlerts as alert, i}
              <tr>
                <td>
                  <button 
                    class="clickable-address"
                    title={alert.address}
                    on:click={() => handleAddressClick(alert.address)}
                  >
                    {formatAddress(alert.address)}
                  </button>
                </td>
                <td>
                  <span class="alert-type-badge">
                    {getAlertTypeLabel(alert.type)}
                  </span>
                </td>
                <td>{(alert.threshold * 100).toFixed(0)}%</td>
                <td class="date-cell">{formatDate(alert.last_triggered)}</td>
                <td>
                  <span class="trigger-count">{alert.trigger_count}</span>
                </td>
                <td class="actions-cell">
                  <button 
                    class="action-btn"
                    on:click={() => handleToggleAlert(alert.id)}
                    title={alert.status === 'active' ? 'Pause Alert' : 'Resume Alert'}
                  >
                    {alert.status === 'active' ? 'Pause' : 'Resume'}
                  </button>
                  <button 
                    class="action-btn delete-btn"
                    on:click={() => handleDeleteAlert(alert.id)}
                    title="Delete Alert"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <div class="empty-state">
        <h4>No triggered alerts</h4>
        <p>Alerts that have been triggered will appear here.</p>
      </div>
    {/if}
  </div>

  <!-- Active Alerts Table -->
  <div class="alerts-section">
    <div class="section-header">
      <h2>Active Alerts ({activeAlerts.length})</h2>
      <button class="btn btn-primary" on:click={() => showCreateAlertModal = true}>
        Create Alert
      </button>
    </div>

    {#if loading}
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading alerts...</p>
      </div>
    {:else if activeAlerts.length > 0}
      <div class="table-container">
        <table class="alerts-table">
          <thead>
            <tr>
              <th>Address</th>
              <th>Alert Type</th>
              <th>Threshold</th>
              <th>Last Triggered</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each activeAlerts as alert, i}
              <tr>
                <td>
                  <button 
                    class="clickable-address"
                    title={alert.address}
                    on:click={() => handleAddressClick(alert.address)}
                  >
                    {formatAddress(alert.address)}
                  </button>
                </td>
                <td>
                  <span class="alert-type-badge">
                    {getAlertTypeLabel(alert.type)}
                  </span>
                </td>
                <td>{(alert.threshold * 100).toFixed(0)}%</td>
                <td class="date-cell">{formatDate(alert.last_triggered)}</td>
                <td class="actions-cell">
                  <button 
                    class="action-btn"
                    on:click={() => handleToggleAlert(alert.id)}
                    title="Pause Alert"
                  >
                    Pause
                  </button>
                  <button 
                    class="action-btn delete-btn"
                    on:click={() => handleDeleteAlert(alert.id)}
                    title="Delete Alert"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <div class="empty-state">
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
            <label for="alert-address">Bitcoin Address</label>
            <input 
              id="alert-address" 
              type="text" 
              bind:value={newAlertAddress}
              placeholder="Enter Bitcoin address to monitor"
            />
          </div>
          
          <div class="form-group">
            <label for="alert-type">Alert Type</label>
            <select id="alert-type" bind:value={newAlertType}>
              <option value="new_transaction">New Transaction</option>
              <option value="high_risk_transaction">High Risk Transaction</option>
              <option value="large_transaction">Large Transaction</option>
              <option value="suspicious_pattern">Suspicious Pattern</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="alert-threshold">Risk Threshold</label>
            <div class="threshold-container">
              <input 
                id="alert-threshold" 
                type="range" 
                min="0" 
                max="100" 
                bind:value={newAlertThreshold}
                style="background: {thresholdGradient}"
              />
              <span class="threshold-value">{newAlertThreshold}%</span>
            </div>
          </div>
          
          <div class="form-group">
            <label for="alert-email">Notification Email</label>
            <input 
              id="alert-email" 
              type="email" 
              bind:value={newAlertEmail}
              placeholder="Enter email for notifications"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showCreateAlertModal = false} disabled={creating}>Cancel</button>
          <button class="btn btn-primary" on:click={handleCreateAlert} disabled={creating}>
            {creating ? 'Creating...' : 'Create Alert'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .alerts {
    max-width: 1200px;
    margin: 0 auto;
    font-family: 'Mulish', sans-serif;
    color: var(--text-primary);
  }

  .alerts-overview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
  }

  .overview-card {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100px;
  }

  .overview-content h3 {
    margin: 0;
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.2;
  }

  .overview-content p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.5;
  }

  .alerts-section {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    margin-bottom: var(--spacing-xl);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 0;
  }

  .section-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.2;
  }

  .table-container {
    width: 100%;
    background: var(--background-primary);
  }

  .alerts-table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--font-size-sm);
    background: var(--background-primary);
  }

  .alerts-table th,
  .alerts-table td {
    padding: var(--spacing-md);
    border-bottom: 1px solid var(--border-color);
    text-align: left;
  }

  .alerts-table th {
    color: var(--text-secondary);
    font-weight: var(--font-weight-medium);
    background: var(--background-secondary);
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .alerts-table tr:nth-child(even) td {
    background: var(--background-secondary);
  }

  .alerts-table tr:nth-child(odd) td {
    background: var(--background-primary);
  }

  .alerts-table tr {
    cursor: pointer;
    transition: all 0.2s;
  }

  .alerts-table tr:hover {
    background-color: #f8f9fa;
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .clickable-address {
    cursor: pointer;
    color: rgb(0, 136, 255);
    transition: color var(--transition-fast);
    font-family: monospace;
    background: var(--background-tertiary);
    padding: 0.2rem 0.4rem;
    border-radius: var(--border-radius-sm);
    font-size: 0.85rem;
    border: none;
    text-align: left;
    width: 100%;
  }

  .clickable-address:hover {
    color: rgb(0, 102, 204);
  }

  .alert-type-badge {
    color: rgb(0, 136, 255);
    font-weight: var(--font-weight-medium);
  }



  .trigger-count {
    color: rgb(0, 136, 255);
    font-weight: var(--font-weight-medium);
  }

  .date-cell {
    white-space: nowrap;
    color: var(--text-secondary);
  }

  .actions-cell {
    display: flex;
    gap: var(--spacing-xs);
  }

  .action-btn {
    padding: 0.25rem 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    background: var(--background-primary);
    color: var(--text-primary);
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .action-btn:hover {
    background: var(--background-secondary);
    border-color: var(--border-color-light);
  }

  .action-btn.delete-btn {
    color: #dc3545;
    border-color: #dc3545;
  }

  .action-btn.delete-btn:hover {
    background: #dc3545;
    color: white;
  }

  .empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--text-secondary);
  }

  .empty-state h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.2;
  }

  .empty-state p {
    margin: 0 0 1.5rem 0;
    font-size: 0.9rem;
    line-height: 1.5;
  }

  .loading-state {
    text-align: center;
    padding: 3rem;
    color: var(--text-secondary);
  }

  .loading-spinner {
    width: 24px;
    height: 24px;
    border: 2px solid var(--border-color);
    border-top: 2px solid rgb(0, 136, 255);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .error-message {
    background: #f8d7da;
    color: #721c24;
    padding: var(--spacing-md);
    border: 1px solid #f5c6cb;
    border-radius: var(--border-radius-md);
    margin-bottom: var(--spacing-lg);
  }

  .btn {
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 1rem;
    border: 1px solid transparent;
    border-radius: var(--border-radius-md);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
    font-family: 'Mulish', sans-serif;
  }

  .btn-primary {
    background: rgb(0, 136, 255);
    color: white;
    border-color: rgb(0, 136, 255);
  }

  .btn-primary:hover {
    background: rgb(0, 102, 204);
    border-color: rgb(0, 102, 204);
  }

  .btn-primary:disabled {
    background: #6c757d;
    border-color: #6c757d;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: var(--background-secondary);
    color: var(--text-primary);
    border-color: var(--border-color);
  }

  .btn-secondary:hover {
    background: var(--background-tertiary);
    border-color: var(--border-color-light);
  }

  .btn-secondary:disabled {
    background: var(--background-tertiary);
    color: var(--text-tertiary);
    cursor: not-allowed;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.2;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--text-secondary);
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-close:hover {
    color: var(--text-primary);
  }

  .modal-content {
    padding: var(--spacing-lg);
  }

  .modal-footer {
    padding: var(--spacing-lg);
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-md);
  }

  .form-group {
    margin-bottom: var(--spacing-lg);
  }

  .form-group label {
    display: block;
    margin-bottom: var(--spacing-xs);
    font-weight: 500;
    color: var(--text-primary);
    font-size: 0.9rem;
  }

  .form-group input,
  .form-group select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    font-size: 0.9rem;
    font-family: 'Mulish', sans-serif;
    background: var(--background-primary);
    color: var(--text-primary);
  }

  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: rgb(0, 136, 255);
  }

  .threshold-container {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
  }

  .threshold-container input[type="range"] {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: var(--background-secondary);
    outline: none;
    -webkit-appearance: none;
    appearance: none;
  }

  .threshold-container input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: rgb(0, 136, 255);
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .threshold-container input[type="range"]::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: rgb(0, 136, 255);
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .threshold-value {
    font-weight: 600;
    color: rgb(0, 136, 255);
    min-width: 3rem;
    text-align: right;
    font-size: 0.9rem;
  }

  @media (max-width: 768px) {
    .alerts-overview {
      grid-template-columns: repeat(2, 1fr);
    }

    .section-header {
      flex-direction: column;
      gap: var(--spacing-md);
      align-items: stretch;
    }

    .actions-cell {
      flex-direction: column;
    }

    .modal {
      margin: 1rem;
    }
  }
</style> 