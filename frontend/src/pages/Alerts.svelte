<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { navigate } from 'svelte-routing';
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
  let modalError = null;
  let deleteTarget = null;
  let deleting = false;

  onMount(async () => {
    await loadAlerts();
  });

  function openCreateAlertModal() {
    modalError = null;
    showCreateAlertModal = true;
  }

  function closeCreateAlertModal() {
    if (creating) return;
    showCreateAlertModal = false;
    modalError = null;
  }

  function handleKeydown(event) {
    if (event.key === 'Escape') {
      if (showCreateAlertModal) closeCreateAlertModal();
      if (deleteTarget) deleteTarget = null;
    }
  }

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
    // Basic validation (errors are shown inside the modal)
    if (!newAlertAddress.trim()) {
      modalError = 'Bitcoin address is required';
      return;
    }
    
    // Basic Bitcoin address validation
    if (!(newAlertAddress.startsWith('1') || newAlertAddress.startsWith('3') || newAlertAddress.startsWith('bc1'))) {
      modalError = 'Please enter a valid Bitcoin address';
      return;
    }
    
    if (!newAlertEmail.trim()) {
      modalError = 'Email address is required';
      return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newAlertEmail.trim())) {
      modalError = 'Please enter a valid email address';
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
      modalError = null;
      error = null; // Clear any previous errors
    } catch (err) {
      modalError = err.details || err.message || 'Failed to create alert';
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

  function handleDeleteAlert(alertId) {
    deleteTarget = alerts.find(alert => alert.id === alertId) || null;
  }

  async function confirmDeleteAlert() {
    if (!deleteTarget) return;
    try {
      deleting = true;
      await alertsApi.remove(deleteTarget.id);
      alerts = alerts.filter(alert => alert.id !== deleteTarget.id);
      activeAlerts = alerts.filter(alert => alert.status === 'active');
      triggeredAlerts = alerts.filter(alert => (alert.trigger_count || 0) > 0);
      deleteTarget = null;
    } catch (err) {
      error = err.message || 'Failed to delete alert';
      deleteTarget = null;
    } finally {
      deleting = false;
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
    navigate(`/analysis?address=${encodeURIComponent(address)}`);
  }

  // Threshold slider: accent-colored fill up to the thumb, theme-aware track after it
  $: thresholdGradient = `linear-gradient(to right, var(--accent-color) 0%, var(--accent-color) ${newAlertThreshold}%, var(--background-tertiary) ${newAlertThreshold}%, var(--background-tertiary) 100%)`;
</script>

<svelte:window on:keydown={handleKeydown} />

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
      <button class="btn btn-primary" on:click={openCreateAlertModal}>
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
        <button class="btn btn-primary" on:click={openCreateAlertModal}>
          Create First Alert
        </button>
      </div>
    {/if}
  </div>

  <!-- Create Alert Modal -->
  {#if showCreateAlertModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }} on:click|self={closeCreateAlertModal}>
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="create-alert-title" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3 id="create-alert-title">Create New Alert</h3>
          <button class="modal-close" on:click={closeCreateAlertModal} aria-label="Close">×</button>
        </div>
        <form on:submit|preventDefault={handleCreateAlert}>
          <div class="modal-content">
            {#if modalError}
              <div class="modal-error" in:fade={{ duration: 150 }}>
                {modalError}
              </div>
            {/if}

            <div class="form-group">
              <label for="alert-address">Bitcoin Address</label>
              <input 
                id="alert-address" 
                type="text" 
                bind:value={newAlertAddress}
                placeholder="Enter Bitcoin address to monitor"
                spellcheck="false"
                autocomplete="off"
                disabled={creating}
              />
            </div>
            
            <div class="form-group">
              <label for="alert-type">Alert Type</label>
              <select id="alert-type" bind:value={newAlertType} disabled={creating}>
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
                  disabled={creating}
                />
                <span class="threshold-value">{newAlertThreshold}%</span>
              </div>
              <p class="form-hint">You will be notified when the classification confidence for suspicious activity exceeds this threshold.</p>
            </div>
            
            <div class="form-group">
              <label for="alert-email">Notification Email</label>
              <input 
                id="alert-email" 
                type="email" 
                bind:value={newAlertEmail}
                placeholder="Enter email for notifications"
                disabled={creating}
              />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" on:click={closeCreateAlertModal} disabled={creating}>Cancel</button>
            <button type="submit" class="btn btn-primary" disabled={creating}>
              {#if creating}<span class="btn-spinner"></span>{/if}
              {creating ? 'Creating...' : 'Create Alert'}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  <!-- Delete Confirmation Modal -->
  {#if deleteTarget}
    <div class="modal-overlay" in:fade={{ duration: 200 }} on:click|self={() => !deleting && (deleteTarget = null)}>
      <div class="modal modal-small" role="dialog" aria-modal="true" aria-labelledby="delete-alert-title" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3 id="delete-alert-title">Delete Alert</h3>
          <button class="modal-close" on:click={() => deleteTarget = null} aria-label="Close" disabled={deleting}>×</button>
        </div>
        <div class="modal-content">
          <p class="delete-question">Are you sure you want to delete this alert?</p>
          <div class="delete-summary">
            <code class="delete-address">{deleteTarget.address}</code>
            <span class="delete-meta">{getAlertTypeLabel(deleteTarget.type)} · {(deleteTarget.threshold * 100).toFixed(0)}% threshold</span>
          </div>
          <p class="delete-note">This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => deleteTarget = null} disabled={deleting}>Cancel</button>
          <button class="btn btn-danger" on:click={confirmDeleteAlert} disabled={deleting}>
            {#if deleting}<span class="btn-spinner"></span>{/if}
            {deleting ? 'Deleting...' : 'Delete Alert'}
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
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .alerts-table {
    width: 100%;
    min-width: 640px;
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

  .alerts-table tr:hover td {
    background-color: var(--background-tertiary);
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
    background: color-mix(in srgb, var(--error-color) 12%, var(--background-primary));
    color: var(--error-color);
    padding: var(--spacing-md);
    border: 1px solid color-mix(in srgb, var(--error-color) 40%, transparent);
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
    color: var(--accent-color);
    min-width: 3rem;
    text-align: right;
    font-size: 0.9rem;
  }

  .form-hint {
    margin: var(--spacing-xs) 0 0 0;
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .modal-error {
    background: color-mix(in srgb, var(--error-color) 12%, var(--background-primary));
    color: var(--error-color);
    border: 1px solid color-mix(in srgb, var(--error-color) 40%, transparent);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-sm) var(--spacing-md);
    margin-bottom: var(--spacing-lg);
    font-size: 0.9rem;
  }

  .modal-small {
    max-width: 420px;
  }

  .btn-danger {
    background: var(--error-color);
    color: white;
    border-color: var(--error-color);
  }

  .btn-danger:hover:not(:disabled) {
    filter: brightness(0.9);
  }

  .btn-danger:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .btn-spinner {
    width: 12px;
    height: 12px;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-right: 0.4rem;
  }

  .delete-question {
    margin: 0 0 var(--spacing-md) 0;
    color: var(--text-primary);
  }

  .delete-summary {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    background: var(--background-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
  }

  .delete-address {
    font-family: monospace;
    font-size: 0.85rem;
    color: var(--text-primary);
    word-break: break-all;
  }

  .delete-meta {
    font-size: 0.8rem;
    color: var(--text-secondary);
  }

  .delete-note {
    margin: 0;
    font-size: 0.85rem;
    color: var(--text-secondary);
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