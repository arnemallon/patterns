<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';

  let userProfile = {
    username: 'investigator',
    email: 'investigator@example.com',
    notifications: {
      email: true,
      browser: true,
      highRiskOnly: false
    },
    preferences: {
      defaultRiskThreshold: 0.5,
      autoSaveCases: true,
      theme: 'light'
    }
  };

  let showChangePasswordModal = false;
  let currentPassword = '';
  let newPassword = '';
  let confirmPassword = '';

  function handleSaveProfile() {
    // In real implementation, this would call an API
    console.log('Saving profile:', userProfile);
  }

  function handleChangePassword() {
    if (newPassword === confirmPassword && newPassword.length >= 8) {
      // In real implementation, this would call an API
      console.log('Changing password');
      showChangePasswordModal = false;
      currentPassword = '';
      newPassword = '';
      confirmPassword = '';
    } else {
      alert('Passwords do not match or are too short');
    }
  }

  function handleExportData() {
    // In real implementation, this would export user data
    console.log('Exporting user data');
  }

  function handleDeleteAccount() {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      // In real implementation, this would call an API
      console.log('Deleting account');
    }
  }
</script>

<div class="settings" in:fly={{ y: 20, duration: 500 }}>
  <div class="settings-grid">
    <!-- Profile Settings -->
    <div class="settings-section">
      <h2>Profile Settings</h2>
      <div class="form-group">
        <label for="username">Username:</label>
        <input 
          id="username" 
          type="text" 
          bind:value={userProfile.username}
        />
      </div>
      
      <div class="form-group">
        <label for="email">Email:</label>
        <input 
          id="email" 
          type="email" 
          bind:value={userProfile.email}
        />
      </div>
      
      <button class="btn btn-primary" on:click={handleSaveProfile}>
        Save Profile
      </button>
      
      <button class="btn btn-secondary" on:click={() => showChangePasswordModal = true}>
        Change Password
      </button>
    </div>

    <!-- Notification Settings -->
    <div class="settings-section">
      <h2>Notification Settings</h2>
      
      <div class="setting-item">
        <div class="setting-info">
          <h3>Email Notifications</h3>
          <p>Receive alerts and updates via email</p>
        </div>
        <label class="toggle">
          <input 
            type="checkbox" 
            bind:checked={userProfile.notifications.email}
          />
          <span class="slider"></span>
        </label>
      </div>
      
      <div class="setting-item">
        <div class="setting-info">
          <h3>Browser Notifications</h3>
          <p>Receive real-time notifications in your browser</p>
        </div>
        <label class="toggle">
          <input 
            type="checkbox" 
            bind:checked={userProfile.notifications.browser}
          />
          <span class="slider"></span>
        </label>
      </div>
      
      <div class="setting-item">
        <div class="setting-info">
          <h3>High Risk Only</h3>
          <p>Only notify for high-risk transactions</p>
        </div>
        <label class="toggle">
          <input 
            type="checkbox" 
            bind:checked={userProfile.notifications.highRiskOnly}
          />
          <span class="slider"></span>
        </label>
      </div>
    </div>

    <!-- Preferences -->
    <div class="settings-section">
      <h2>Preferences</h2>
      
      <div class="form-group">
        <label for="risk-threshold">Default Risk Threshold: {(userProfile.preferences.defaultRiskThreshold * 100).toFixed(0)}%</label>
        <input 
          id="risk-threshold" 
          type="range" 
          min="0" 
          max="100" 
          bind:value={userProfile.preferences.defaultRiskThreshold}
          on:input={(e) => userProfile.preferences.defaultRiskThreshold = e.target.value / 100}
        />
      </div>
      
      <div class="setting-item">
        <div class="setting-info">
          <h3>Auto-save Cases</h3>
          <p>Automatically save addresses to cases</p>
        </div>
        <label class="toggle">
          <input 
            type="checkbox" 
            bind:checked={userProfile.preferences.autoSaveCases}
          />
          <span class="slider"></span>
        </label>
      </div>
      
      <div class="form-group">
        <label for="theme">Theme:</label>
        <select id="theme" bind:value={userProfile.preferences.theme}>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="auto">Auto</option>
        </select>
      </div>
    </div>

    <!-- Data Management -->
    <div class="settings-section">
      <h2>Data Management</h2>
      
      <div class="data-actions">
        <button class="btn btn-secondary" on:click={handleExportData}>
          Export My Data
        </button>
        
        <button class="btn btn-danger" on:click={handleDeleteAccount}>
          Delete Account
        </button>
      </div>
      
      <div class="data-info">
        <h3>Data Usage</h3>
        <div class="data-stats">
          <div class="stat-item">
            <span class="stat-label">Addresses Analyzed:</span>
            <span class="stat-value">1,247</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Cases Created:</span>
            <span class="stat-value">12</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Alerts Configured:</span>
            <span class="stat-value">5</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Change Password Modal -->
  {#if showChangePasswordModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Change Password</h3>
          <button class="modal-close" on:click={() => showChangePasswordModal = false}>×</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label for="current-password">Current Password:</label>
            <input 
              id="current-password" 
              type="password" 
              bind:value={currentPassword}
            />
          </div>
          
          <div class="form-group">
            <label for="new-password">New Password:</label>
            <input 
              id="new-password" 
              type="password" 
              bind:value={newPassword}
            />
          </div>
          
          <div class="form-group">
            <label for="confirm-password">Confirm New Password:</label>
            <input 
              id="confirm-password" 
              type="password" 
              bind:value={confirmPassword}
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showChangePasswordModal = false}>Cancel</button>
          <button class="btn btn-primary" on:click={handleChangePassword}>Change Password</button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .settings {
    max-width: 1200px;
    margin: 0 auto;
    font-family: var(--font-family);
    color: var(--text-primary);
    font-weight: var(--font-weight-normal);
  }

  .settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: var(--spacing-xl);
  }

  .settings-section {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .settings-section h2 {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0 0 var(--spacing-md) 0;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-md);
  }

  .form-group label {
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
  }

  .form-group input,
  .form-group select {
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-sm);
    font-family: var(--font-family);
    background: var(--background-primary);
    color: var(--text-primary);
    transition: border-color 0.2s;
  }

  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: var(--accent-color);
  }

  .setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-md);
    padding: var(--spacing-sm) 0;
  }

  .setting-info h3 {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    margin: 0 0 var(--spacing-xs) 0;
  }

  .setting-info p {
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
    margin: 0;
  }

  .toggle {
    position: relative;
    display: inline-block;
    width: 40px;
    height: 22px;
  }

  .toggle input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--background-secondary);
    border: 1px solid var(--border-color);
    border-radius: 22px;
    transition: background 0.2s, border-color 0.2s;
  }

  .toggle input:checked + .slider {
    background: var(--accent-color);
    border-color: var(--accent-color);
  }

  .slider:before {
    position: absolute;
    content: '';
    height: 18px;
    width: 18px;
    left: 2px;
    bottom: 2px;
    background: var(--background-primary);
    border-radius: 50%;
    transition: transform 0.2s;
  }

  .toggle input:checked + .slider:before {
    transform: translateX(18px);
  }

  input[type='range'] {
    width: 100%;
    margin-top: var(--spacing-xs);
    accent-color: var(--accent-color);
    background: transparent;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-sm) var(--spacing-lg);
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--border-color);
    background: var(--background-primary);
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    letter-spacing: 0.01em;
  }

  .btn-primary {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
  }

  .btn-primary:disabled {
    background: var(--border-color);
    color: var(--text-tertiary);
    border-color: var(--border-color);
    cursor: not-allowed;
  }

  .btn-secondary {
    background: var(--background-secondary);
    color: var(--accent-color);
    border-color: var(--accent-color);
  }

  .btn-secondary:hover {
    background: var(--accent-color);
    color: white;
  }

  .btn-danger {
    background: var(--error-color);
    color: white;
    border-color: var(--error-color);
  }

  .btn-danger:hover {
    background: var(--background-primary);
    color: var(--error-color);
    border-color: var(--error-color);
  }

  .data-actions {
    display: flex;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
  }

  .data-info h3 {
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    margin: 0 0 var(--spacing-xs) 0;
  }

  .data-stats {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .stat-item {
    display: flex;
    justify-content: space-between;
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  .stat-label {
    font-weight: var(--font-weight-medium);
  }

  .stat-value {
    color: var(--accent-color);
    font-weight: var(--font-weight-semibold);
  }

  @media (max-width: 768px) {
    .settings-grid {
      grid-template-columns: 1fr;
    }
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
</style> 