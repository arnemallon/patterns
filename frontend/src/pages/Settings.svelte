<script>
  import { onMount } from 'svelte';
  import { fly, fade, scale } from 'svelte/transition';
  import { usersApi } from '../services/api.js';

  // User data state
  let userProfile = null;
  let userPreferences = null;
  let userNotifications = null;
  let userStats = null;
  let userActivity = [];
  
  // Loading states
  let loading = {
    profile: true,
    preferences: true,
    notifications: true,
    stats: true,
    activity: true
  };
  
  let showExportModal = false;
  
  // Form validation
  let errors = {};
  let successMessage = '';
  
  // Activity filter
  let activityFilter = 'all'; // all, today, week, month
  
  onMount(async () => {
    await loadAllUserData();
  });
  
  async function loadAllUserData() {
    try {
      await Promise.all([
        loadProfile(),
        loadPreferences(),
        loadNotifications(),
        loadStats(),
        loadActivity()
      ]);
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  }
  
  async function loadProfile() {
    try {
      loading.profile = true;
      userProfile = await usersApi.getProfile();
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      loading.profile = false;
    }
  }
  
  async function loadPreferences() {
    try {
      loading.preferences = true;
      userPreferences = await usersApi.getPreferences();
    } catch (error) {
      console.error('Error loading preferences:', error);
    } finally {
      loading.preferences = false;
    }
  }
  
  async function loadNotifications() {
    try {
      loading.notifications = true;
      userNotifications = await usersApi.getNotifications();
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      loading.notifications = false;
    }
  }
  
  async function loadStats() {
    try {
      loading.stats = true;
      userStats = await usersApi.getStats();
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      loading.stats = false;
    }
  }
  
  async function loadActivity() {
    try {
      loading.activity = true;
      const response = await usersApi.getActivity();
      userActivity = response.activities || [];
    } catch (error) {
      console.error('Error loading activity:', error);
    } finally {
      loading.activity = false;
    }
  }
  
  async function handleSaveProfile() {
    try {
      errors = {};
      successMessage = '';
      
      const profileData = {
        first_name: userProfile.first_name,
        email: userProfile.email
      };
      
      await usersApi.updateProfile(profileData);
      successMessage = 'Profile updated successfully!';
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        successMessage = '';
      }, 3000);
      
    } catch (error) {
      errors.profile = error.response?.data?.error || 'Failed to update profile';
    }
  }
  
  async function handleSavePreferences() {
    try {
      errors = {};
      successMessage = '';
      
      await usersApi.updatePreferences(userPreferences);
      successMessage = 'Preferences updated successfully!';
      
      setTimeout(() => {
        successMessage = '';
      }, 3000);
      
    } catch (error) {
      errors.preferences = error.response?.data?.error || 'Failed to update preferences';
    }
  }
  
  async function handleSaveNotifications() {
    try {
      errors = {};
      successMessage = '';
      
      await usersApi.updateNotifications(userNotifications);
      successMessage = 'Notification settings updated successfully!';
      
      setTimeout(() => {
        successMessage = '';
      }, 3000);
      
    } catch (error) {
      errors.notifications = error.response?.data?.error || 'Failed to update notifications';
    }
  }
  
  async function handleExportData() {
    try {
      const response = await usersApi.exportData();
      showExportModal = true;
      successMessage = 'Data export requested successfully!';
      
      setTimeout(() => {
        successMessage = '';
      }, 3000);
      
    } catch (error) {
      errors.export = error.response?.data?.error || 'Failed to request data export';
    }
  }
  
  function getFilteredActivity() {
    if (activityFilter === 'all') return userActivity;
    
    const now = new Date();
    const filterDate = new Date();
    
    switch (activityFilter) {
      case 'today':
        filterDate.setHours(0, 0, 0, 0);
        break;
      case 'week':
        filterDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        filterDate.setMonth(now.getMonth() - 1);
        break;
    }
    
    return userActivity.filter(activity => 
      new Date(activity.created_at) >= filterDate
    );
  }
  
  function formatActivityTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  }
  

</script>

<div class="settings" in:fly={{ y: 20, duration: 500 }}>
  <!-- Success Message -->
  {#if successMessage}
    <div class="success-message" in:scale={{ duration: 300 }}>
      {successMessage}
    </div>
  {/if}
  
  <!-- Error Messages -->
  {#if Object.keys(errors).length > 0}
    <div class="error-messages" in:scale={{ duration: 300 }}>
      {#each Object.entries(errors) as [field, message]}
        <div class="error-message">{message}</div>
      {/each}
    </div>
  {/if }
  
  <div class="settings-grid">
    <!-- Profile Settings -->
    <div class="settings-section" in:fly={{ y: 20, duration: 300, delay: 100 }}>
      <div class="section-header">
        <h2>Profile Settings</h2>
        <div class="section-actions">
          <button class="btn btn-primary" on:click={handleSaveProfile} disabled={loading.profile}>
            {loading.profile ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </div>
      
      {#if loading.profile}
        <div class="loading-skeleton">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
        </div>
      {:else if userProfile}
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            id="username" 
            type="text" 
            value={userProfile.username}
            disabled
            class="disabled-input"
          />
          <small>Username cannot be changed</small>
        </div>
        
        <div class="form-group">
          <label for="first-name">First Name</label>
          <input 
            id="first-name" 
            type="text" 
            bind:value={userProfile.first_name}
            placeholder="Enter your first name"
          />
        </div>
        
        <div class="form-group">
          <label for="email">Email Address</label>
          <input 
            id="email" 
            type="email" 
            bind:value={userProfile.email}
            placeholder="Enter your email"
          />
        </div>
        
        <div class="form-group">
          <label for="role">Role</label>
          <input 
            id="role" 
            type="text" 
            value={userProfile.role}
            disabled
            class="disabled-input"
          />
        </div>
      {/if}
    </div>

    <!-- Notification Settings -->
    <div class="settings-section" in:fly={{ y: 20, duration: 300, delay: 200 }}>
      <div class="section-header">
        <h2>Notification Settings</h2>
        <div class="section-actions">
          <button class="btn btn-primary" on:click={handleSaveNotifications} disabled={loading.notifications}>
            {loading.notifications ? 'Saving...' : 'Save Notifications'}
          </button>
        </div>
      </div>
      
      {#if loading.notifications}
        <div class="loading-skeleton">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
        </div>
      {:else if userNotifications}
        <div class="setting-item">
          <div class="setting-info">
            <h3>Email Notifications</h3>
            <p>Receive alerts and updates via email</p>
          </div>
          <label class="toggle">
            <input 
              type="checkbox" 
              bind:checked={userNotifications.email_notifications}
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
              bind:checked={userNotifications.browser_notifications}
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
              bind:checked={userNotifications.high_risk_only}
            />
            <span class="slider"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Daily Summary</h3>
            <p>Receive daily activity summaries</p>
          </div>
          <label class="toggle">
            <input 
              type="checkbox" 
              bind:checked={userNotifications.daily_summary}
            />
            <span class="slider"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Weekly Report</h3>
            <p>Receive weekly analysis reports</p>
          </div>
          <label class="toggle">
            <input 
              type="checkbox" 
              bind:checked={userNotifications.weekly_report}
            />
            <span class="slider"></span>
          </label>
        </div>
      {/if}
    </div>

    <!-- Preferences -->
    <div class="settings-section" in:fly={{ y: 20, duration: 300, delay: 300 }}>
      <div class="section-header">
        <h2>Preferences</h2>
        <div class="section-actions">
          <button class="btn btn-primary" on:click={handleSavePreferences} disabled={loading.preferences}>
            {loading.preferences ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </div>
      
      {#if loading.preferences}
        <div class="loading-skeleton">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
        </div>
      {:else if userPreferences}
        <div class="form-group">
          <label for="risk-threshold">
            Default Risk Threshold: {(userPreferences.default_risk_threshold * 100).toFixed(0)}%
          </label>
          <div class="range-container">
            <input 
              id="risk-threshold" 
              type="range" 
              min="0" 
              max="100" 
              bind:value={userPreferences.default_risk_threshold}
              on:input={(e) => userPreferences.default_risk_threshold = e.target.value / 100}
              class="range-slider"
            />
            <div class="range-labels">
              <span>Low</span>
              <span>High</span>
            </div>
          </div>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <h3>Auto-save Cases</h3>
            <p>Automatically save addresses to cases</p>
          </div>
          <label class="toggle">
            <input 
              type="checkbox" 
              bind:checked={userPreferences.auto_save_cases}
            />
            <span class="slider"></span>
          </label>
        </div>
        
        <div class="form-group">
          <label for="theme">Theme</label>
          <select id="theme" bind:value={userPreferences.theme}>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="language">Language</label>
          <select id="language" bind:value={userPreferences.language}>
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="timezone">Timezone</label>
          <select id="timezone" bind:value={userPreferences.timezone}>
            <option value="UTC">UTC</option>
            <option value="America/New_York">Eastern Time</option>
            <option value="America/Chicago">Central Time</option>
            <option value="America/Denver">Mountain Time</option>
            <option value="America/Los_Angeles">Pacific Time</option>
            <option value="Europe/London">London</option>
            <option value="Europe/Paris">Paris</option>
            <option value="Asia/Tokyo">Tokyo</option>
          </select>
        </div>
      {/if}
    </div>

    <!-- Data Management -->
    <div class="settings-section" in:fly={{ y: 20, duration: 300, delay: 400 }}>
      <div class="section-header">
        <h2>Data Management</h2>
      </div>
      
      {#if loading.stats}
        <div class="loading-skeleton">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
        </div>
      {:else if userStats}
        <div class="data-stats">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{userStats.classifications_count}</div>
              <div class="stat-label">Addresses Analyzed</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{userStats.alerts_count}</div>
              <div class="stat-label">Alerts Configured</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{userStats.recent_activity_count}</div>
              <div class="stat-label">Recent Activities</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{userStats.account_age_days}</div>
              <div class="stat-label">Account Age (Days)</div>
            </div>
          </div>
        </div>
        
        <div class="data-actions">
          <button class="btn btn-secondary" on:click={handleExportData}>
            Export My Data
          </button>
        </div>
      {/if}
    </div>

    <!-- Activity Log -->
    <div class="settings-section full-width" in:fly={{ y: 20, duration: 300, delay: 500 }}>
      <div class="section-header">
        <h2>Activity Log</h2>
        <div class="activity-filter">
          <select bind:value={activityFilter}>
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
        </div>
      </div>
      
      {#if loading.activity}
        <div class="loading-skeleton">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
        </div>
      {:else if userActivity.length === 0}
        <div class="empty-state">
          <p>No activity to display</p>
        </div>
      {:else}
        <div class="activity-list">
          {#each getFilteredActivity() as activity}
                    <div class="activity-item" in:fly={{ y: 20, duration: 300 }}>
          <div class="activity-content">
            <div class="activity-action">{activity.action.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
            <div class="activity-time">{formatActivityTime(activity.created_at)}</div>
            {#if activity.details}
              <div class="activity-details">
                {Object.entries(activity.details).map(([key, value]) => `${key}: ${value}`).join(', ')}
              </div>
            {/if}
          </div>
        </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Export Modal -->
  {#if showExportModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Data Export</h3>
          <button class="modal-close" on:click={() => showExportModal = false}>×</button>
        </div>
        <div class="modal-content">
          <div class="export-info">
            <h4>Your data export has been requested</h4>
            <p>We're preparing your data export. This may take a few minutes depending on the amount of data.</p>
            <p>You'll receive an email notification when your export is ready for download.</p>
            <div class="export-progress">
              <div class="progress-bar">
                <div class="progress-fill"></div>
              </div>
              <span>Processing...</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" on:click={() => showExportModal = false}>Close</button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .settings {
    max-width: 1400px;
    margin: 0 auto;
    font-family: var(--font-family);
    color: var(--text-primary);
    font-weight: var(--font-weight-normal);
    padding: var(--spacing-lg);
  }

  .success-message {
    background: var(--success-color, #10b981);
    color: white;
    padding: var(--spacing-md);
    border-radius: var(--border-radius-md);
    margin-bottom: var(--spacing-lg);
    text-align: center;
    font-weight: var(--font-weight-medium);
  }

  .error-messages {
    background: var(--error-color, #ef4444);
    color: white;
    padding: var(--spacing-md);
    border-radius: var(--border-radius-md);
    margin-bottom: var(--spacing-lg);
  }

  .error-message {
    margin-bottom: var(--spacing-xs);
  }

  .error-message:last-child {
    margin-bottom: 0;
  }

  .settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
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

  .settings-section.full-width {
    grid-column: 1 / -1;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
    padding-bottom: var(--spacing-md);
    border-bottom: 2px solid var(--border-color);
  }

  .section-header h2 {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    margin: 0;
  }

  .section-actions {
    display: flex;
    gap: var(--spacing-sm);
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
    transition: all 0.2s;
  }

  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .disabled-input {
    background: var(--background-secondary);
    color: var(--text-tertiary);
    cursor: not-allowed;
  }

  .form-group small {
    color: var(--text-tertiary);
    font-size: var(--font-size-xs);
  }

  .range-container {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .range-slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: var(--background-secondary);
    outline: none;
    -webkit-appearance: none;
  }

  .range-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgb(0, 136, 255);
    cursor: pointer;
  }

  .range-slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgb(0, 136, 255);
    cursor: pointer;
    border: none;
  }

  .range-labels {
    display: flex;
    justify-content: space-between;
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
  }

  .setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: var(--background-secondary);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--border-color);
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
    width: 50px;
    height: 26px;
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
    border-radius: 26px;
    transition: all 0.3s ease;
  }

  .toggle input:checked + .slider {
    background: rgb(0, 136, 255);
    border-color: rgb(0, 136, 255);
  }

  .slider:before {
    position: absolute;
    content: '';
    height: 20px;
    width: 20px;
    left: 3px;
    bottom: 3px;
    background: var(--background-primary);
    border-radius: 50%;
    transition: transform 0.3s ease;
  }

  .toggle input:checked + .slider:before {
    transform: translateX(24px);
  }

  .data-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
  }

  .stat-card {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg);
    background: var(--background-secondary);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--border-color);
  }



  .stat-content {
    flex: 1;
  }

  .stat-value {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: rgb(0, 136, 255);
    line-height: 1;
  }

  .stat-label {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    margin-top: var(--spacing-xs);
  }

  .data-actions {
    display: flex;
    gap: var(--spacing-md);
    flex-wrap: wrap;
  }

  .activity-filter {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
  }

  .activity-filter select {
    padding: var(--spacing-xs) var(--spacing-sm);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    background: var(--background-primary);
    color: var(--text-primary);
    font-size: var(--font-size-sm);
  }

  .activity-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    max-height: 400px;
    overflow-y: auto;
  }

  .activity-item {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: var(--background-secondary);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--border-color);
    transition: all 0.2s ease;
  }

  .activity-item:hover {
    background: var(--background-primary);
    border-color: rgb(0, 136, 255);
  }



  .activity-content {
    flex: 1;
  }

  .activity-action {
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);
  }

  .activity-time {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  .activity-details {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    margin-top: var(--spacing-xs);
    font-family: monospace;
  }

  .empty-state {
    text-align: center;
    padding: var(--spacing-xl);
    color: var(--text-secondary);
  }



  .loading-skeleton {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .skeleton-line {
    height: 20px;
    background: var(--background-secondary);
    border-radius: var(--border-radius-sm);
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
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
    transition: all 0.2s ease;
    text-decoration: none;
    letter-spacing: 0.01em;
    gap: var(--spacing-xs);
  }

  .btn:hover {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
  }

  .btn-primary {
    background: rgb(0, 136, 255);
    color: white;
    border-color: rgb(0, 136, 255);
  }

  .btn-primary:hover {
    background: rgb(0, 145, 255);
    border-color: rgb(0, 145, 255);
  }

  .btn-primary:disabled {
    background: var(--border-color);
    color: var(--text-tertiary);
    border-color: var(--border-color);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  .btn-secondary {
    background: var(--background-secondary);
    color: rgb(0, 136, 255);
    border-color: rgb(0, 136, 255);
  }

  .btn-secondary:hover {
    background: rgb(0, 136, 255);
    color: white;
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
    background: var(--background-primary);
    border-radius: var(--border-radius-lg);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
    border: 1px solid var(--border-color);
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
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
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
    border-radius: var(--border-radius-sm);
    transition: all 0.2s ease;
  }

  .modal-close:hover {
    color: var(--text-primary);
    background: var(--background-secondary);
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

  .export-info {
    text-align: center;
    padding: var(--spacing-lg);
  }



  .export-info h4 {
    color: rgb(0, 136, 255);
    margin-bottom: var(--spacing-md);
  }

  .export-progress {
    margin-top: var(--spacing-lg);
  }

  .progress-bar {
    width: 100%;
    height: 8px;
    background: var(--background-secondary);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: var(--spacing-sm);
  }

  .progress-fill {
    height: 100%;
    background: rgb(0, 136, 255);
    border-radius: 4px;
    animation: progress 2s ease-in-out infinite;
  }

  @keyframes progress {
    0% { width: 0%; }
    50% { width: 70%; }
    100% { width: 100%; }
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .settings {
      padding: var(--spacing-md);
    }
    
    .settings-grid {
      grid-template-columns: 1fr;
      gap: var(--spacing-lg);
    }
    
    .section-header {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-sm);
    }
    
    .data-stats {
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
    
    .data-actions {
      flex-direction: column;
    }
    
    .modal {
      margin: var(--spacing-md);
    }
  }
</style> 