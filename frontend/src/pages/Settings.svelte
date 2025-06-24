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
  <div class="page-header">
    <h1>Settings</h1>
    <p>Manage your account settings and preferences.</p>
  </div>

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
          <span class="btn-icon">📥</span>
          Export My Data
        </button>
        
        <button class="btn btn-danger" on:click={handleDeleteAccount}>
          <span class="btn-icon">🗑️</span>
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

  /* Settings Grid */
  .settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
  }

  /* Settings Section */
  .settings-section {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }

  .settings-section h2 {
    margin: 0 0 1.5rem 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
  }

  /* Form Groups */
  .form-group {
    margin-bottom: 1.5rem;
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

  /* Setting Items */
  .setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid #e9ecef;
  }

  .setting-item:last-child {
    border-bottom: none;
  }

  .setting-info h3 {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .setting-info p {
    margin: 0;
    color: #6c757d;
    font-size: 0.85rem;
  }

  /* Toggle Switch */
  .toggle {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 24px;
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
    background-color: #ccc;
    transition: 0.4s;
    border-radius: 24px;
  }

  .slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: 0.4s;
    border-radius: 50%;
  }

  input:checked + .slider {
    background-color: #007bff;
  }

  input:checked + .slider:before {
    transform: translateX(26px);
  }

  /* Data Management */
  .data-actions {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .data-info h3 {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .data-stats {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
  }

  .stat-label {
    color: #6c757d;
    font-size: 0.9rem;
  }

  .stat-value {
    font-weight: 600;
    color: #2c3e50;
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
    margin-right: 1rem;
    margin-bottom: 1rem;
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

  /* Responsive Design */
  @media (max-width: 768px) {
    .settings-grid {
      grid-template-columns: 1fr;
    }

    .data-actions {
      flex-direction: column;
    }

    .setting-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }
  }
</style> 