<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';

  let alerts = [];
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
      }
    ];
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
  }

  function handleDeleteAlert(alertId) {
    if (confirm('Are you sure you want to delete this alert?')) {
      alerts = alerts.filter(alert => alert.id !== alertId);
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
</script>

<div class="alerts" in:fly={{ y: 20, duration: 500 }}>
  <div class="page-header">
    <h1>Alerts</h1>
    <p>Monitor Bitcoin addresses for specific activities and receive notifications.</p>
  </div>

  <!-- Alerts Overview -->
  <div class="alerts-overview">
    <div class="overview-card">
      <div class="overview-icon">🔔</div>
      <div class="overview-content">
        <h3>{alerts.length}</h3>
        <p>Total Alerts</p>
      </div>
    </div>
    
    <div class="overview-card">
      <div class="overview-icon">✅</div>
      <div class="overview-content">
        <h3>{alerts.filter(a => a.status === 'active').length}</h3>
        <p>Active Alerts</p>
      </div>
    </div>
    
    <div class="overview-card">
      <div class="overview-icon">📊</div>
      <div class="overview-content">
        <h3>{alerts.reduce((sum, a) => sum + a.trigger_count, 0)}</h3>
        <p>Total Triggers</p>
      </div>
    </div>
    
    <div class="overview-card">
      <div class="overview-icon">⏸️</div>
      <div class="overview-content">
        <h3>{alerts.filter(a => a.status === 'paused').length}</h3>
        <p>Paused Alerts</p>
      </div>
    </div>
  </div>

  <!-- Alerts Management -->
  <div class="alerts-section">
    <div class="section-header">
      <h2>Alert Management</h2>
      <button class="btn btn-primary" on:click={() => showCreateAlertModal = true}>
        <span class="btn-icon">➕</span>
        Create Alert
      </button>
    </div>

    {#if alerts.length > 0}
      <div class="alerts-grid">
        {#each alerts as alert}
          <div class="alert-card" in:fade={{ delay: alert.id * 50 }}>
            <div class="alert-header">
              <div class="alert-type">
                <span class="type-icon">{getAlertTypeIcon(alert.type)}</span>
                <span class="type-label">{getAlertTypeLabel(alert.type)}</span>
              </div>
              <div class="alert-status">
                <span 
                  class="status-badge"
                  style="background-color: {getStatusColor(alert.status)}"
                >
                  {alert.status}
                </span>
              </div>
            </div>
            
            <div class="alert-content">
              <div class="address-info">
                <span class="address-label">Address:</span>
                <span class="address-value">{alert.address.substring(0, 12)}...</span>
              </div>
              
              <div class="alert-details">
                <div class="detail-item">
                  <span class="detail-label">Threshold:</span>
                  <span class="detail-value">{(alert.threshold * 100).toFixed(0)}%</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">Email:</span>
                  <span class="detail-value">{alert.email}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">Created:</span>
                  <span class="detail-value">{formatDate(alert.created_at)}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">Last Triggered:</span>
                  <span class="detail-value">{formatDate(alert.last_triggered)}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">Trigger Count:</span>
                  <span class="detail-value">{alert.trigger_count}</span>
                </div>
              </div>
            </div>
            
            <div class="alert-actions">
              <button 
                class="btn btn-secondary"
                on:click={() => handleToggleAlert(alert.id)}
              >
                {alert.status === 'active' ? '⏸️ Pause' : '▶️ Resume'}
              </button>
              <button 
                class="btn btn-danger"
                on:click={() => handleDeleteAlert(alert.id)}
              >
                🗑️ Delete
              </button>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="empty-state">
        <div class="empty-icon">🔔</div>
        <h4>No alerts configured</h4>
        <p>Create your first alert to start monitoring Bitcoin addresses for suspicious activity.</p>
        <button class="btn btn-primary" on:click={() => showCreateAlertModal = true}>
          Create First Alert
        </button>
      </div>
    {/if}
  </div>

  <!-- Alert Types Info -->
  <div class="alert-types-info">
    <h3>Alert Types</h3>
    <div class="types-grid">
      <div class="type-info">
        <div class="type-icon">🔄</div>
        <h4>New Transaction</h4>
        <p>Triggered when a new transaction is detected on the monitored address.</p>
      </div>
      
      <div class="type-info">
        <div class="type-icon">⚠️</div>
        <h4>High Risk Transaction</h4>
        <p>Triggered when a transaction with high risk score is detected.</p>
      </div>
      
      <div class="type-info">
        <div class="type-icon">💰</div>
        <h4>Large Transaction</h4>
        <p>Triggered when a transaction exceeds a specified amount threshold.</p>
      </div>
      
      <div class="type-info">
        <div class="type-icon">🚨</div>
        <h4>Suspicious Pattern</h4>
        <p>Triggered when suspicious transaction patterns are detected.</p>
      </div>
    </div>
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

  .page-header {
    margin-bottom: 2rem;
  }

  .page-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2.5rem;
    font-weight: 700;
    color: #2c3e50;
  }

  .page-header p {
    margin: 0;
    color: #6c757d;
    font-size: 1.1rem;
  }

  /* Alerts Overview */
  .alerts-overview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .overview-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .overview-icon {
    font-size: 2rem;
  }

  .overview-content h3 {
    margin: 0 0 0.25rem 0;
    font-size: 1.8rem;
    font-weight: 700;
    color: #2c3e50;
  }

  .overview-content p {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
  }

  /* Alerts Section */
  .alerts-section {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 2rem;
    margin-bottom: 2rem;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .section-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .alerts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
  }

  .alert-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid #e9ecef;
  }

  .alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .alert-type {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .type-icon {
    font-size: 1.2rem;
  }

  .type-label {
    font-weight: 600;
    color: #2c3e50;
  }

  .status-badge {
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
  }

  .alert-content {
    margin-bottom: 1rem;
  }

  .address-info {
    margin-bottom: 1rem;
  }

  .address-label {
    font-weight: 500;
    color: #2c3e50;
    margin-right: 0.5rem;
  }

  .address-value {
    font-family: monospace;
    background-color: #e9ecef;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-size: 0.85rem;
  }

  .alert-details {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .detail-label {
    font-weight: 500;
    color: #2c3e50;
    font-size: 0.85rem;
  }

  .detail-value {
    color: #6c757d;
    font-size: 0.85rem;
  }

  .alert-actions {
    display: flex;
    gap: 0.5rem;
  }

  /* Empty State */
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

  /* Alert Types Info */
  .alert-types-info {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }

  .alert-types-info h3 {
    margin: 0 0 1.5rem 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .types-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .type-info {
    text-align: center;
    padding: 1.5rem;
    border-radius: 8px;
    background-color: #f8f9fa;
  }

  .type-info .type-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
  }

  .type-info h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .type-info p {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
    line-height: 1.5;
  }

  /* Buttons */
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

  /* Modal Styles */
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

  /* Form Styles */
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

  /* Responsive Design */
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

    .types-grid {
      grid-template-columns: 1fr;
    }
  }
</style> 