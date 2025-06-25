<script>
  import { onMount } from 'svelte';
  import { Router, Link, Route } from 'svelte-routing';
  import { fly, fade } from 'svelte/transition';
  import './app.css';
  
  // Import all the page components
  import Dashboard from './pages/Dashboard.svelte';
  import AddressAnalysis from './pages/AddressAnalysis.svelte';
  import BatchAnalysis from './pages/BatchAnalysis.svelte';
  import CaseManagement from './pages/CaseManagement.svelte';
  import Alerts from './pages/Alerts.svelte';
  import History from './pages/History.svelte';
  import Settings from './pages/Settings.svelte';
  import Login from './pages/Login.svelte';
  import Register from './pages/Register.svelte';

  export let url = '';

  let pageLoaded = false;
  let currentUser = null; // This would be managed by a store in a real implementation

  // Check for existing user session on load
  onMount(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      currentUser = JSON.parse(savedUser);
    }
  });

  // Add a small delay to show loading animation
  setTimeout(() => {
    pageLoaded = true;
  }, 100);

  function handleLogin(userData) {
    currentUser = userData;
    localStorage.setItem('currentUser', JSON.stringify(userData));
  }

  function handleLogout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    // Redirect to login page
    window.location.href = '/login';
  }
</script>

{#if pageLoaded}
  <Router {url}>
    <main in:fly={{ y: 20, duration: 500, delay: 200 }}>
      {#if currentUser}
        <!-- Main Application Layout with Sidebar -->
        <div class="app-layout">
          <!-- Sidebar Navigation -->
          <nav class="sidebar">
            <div class="sidebar-header">
              <h2>Bitcoin Classifier</h2>
            </div>
            
            <div class="nav-links">
              <Link to="/" class="nav-link">
                Dashboard
              </Link>
              <Link to="/analysis" class="nav-link">
                Address Analysis
              </Link>
              <Link to="/batch" class="nav-link">
                Batch Analysis
              </Link>
              <Link to="/cases" class="nav-link">
                Cases
              </Link>
              <Link to="/alerts" class="nav-link">
                Alerts
              </Link>
              <Link to="/history" class="nav-link">
                History
              </Link>
              <Link to="/settings" class="nav-link">
                Settings
              </Link>
            </div>
            
            <div class="sidebar-footer">
              <div class="user-info">
                <span class="user-name">{currentUser.username}</span>
              </div>
              <button class="btn btn-secondary logout-btn" on:click={handleLogout}>
                Logout
              </button>
            </div>
          </nav>

          <!-- Main Content Area -->
          <div class="main-content">
            <Route path="/" component={Dashboard} />
            <Route path="/analysis" component={AddressAnalysis} />
            <Route path="/batch" component={BatchAnalysis} />
            <Route path="/cases" component={CaseManagement} />
            <Route path="/alerts" component={Alerts} />
            <Route path="/history" component={History} />
            <Route path="/settings" component={Settings} />
          </div>
        </div>
      {:else}
        <!-- Authentication Pages -->
        <div class="auth-container">
          <Route path="/login" component={Login} {handleLogin} />
          <Route path="/register" component={Register} />
          <Route path="/" component={Login} {handleLogin} />
        </div>
      {/if}
    </main>
  </Router>
{:else}
  <div class="loading-screen">
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <h2>Loading Bitcoin Classifier</h2>
      <p>Initializing application...</p>
    </div>
  </div>
{/if}

<style>
  /* App Layout */
  .app-layout {
    display: flex;
    min-height: 100vh;
  }

  /* Sidebar */
  .sidebar {
    width: 280px;
    background: var(--background-primary);
    color: var(--text-primary);
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--border-color);
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 100;
  }

  .sidebar-header {
    padding: var(--spacing-xl) var(--spacing-lg) var(--spacing-md);
    border-bottom: 1px solid var(--border-color);
    background: var(--background-primary);
  }

  .sidebar-header h2 {
    margin: 0;
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
  }

  .nav-links {
    flex: 1;
    padding: var(--spacing-md) 0;
    display: flex;
    flex-direction: column;
  }

  .nav-links :global(a.nav-link) {
    display: flex;
    align-items: center;
    padding: var(--spacing-md) var(--spacing-lg);
    color: var(--text-secondary);
    text-decoration: none !important;
    transition: all var(--transition-fast);
    border-left: 3px solid transparent;
    font-weight: var(--font-weight-medium);
    margin: var(--spacing-xs) 0;
    font-size: var(--font-size-sm);
  }

  .nav-links :global(a.nav-link:visited) {
    color: var(--text-secondary);
  }

  .nav-links :global(a.nav-link:hover) {
    background-color: var(--background-secondary);
    color: var(--text-primary);
  }

  .nav-links :global(a.nav-link.active) {
    background-color: var(--background-secondary);
    border-left-color: var(--accent-color);
    color: var(--accent-color);
    font-weight: var(--font-weight-semibold);
  }

  .sidebar-footer {
    padding: var(--spacing-lg);
    border-top: 1px solid var(--border-color);
    background: var(--background-primary);
    margin-top: auto;
  }

  .user-info {
    display: flex;
    align-items: center;
    margin-bottom: var(--spacing-md);
  }

  .user-name {
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    font-size: var(--font-size-sm);
  }

  .logout-btn {
    width: 100%;
    font-size: var(--font-size-sm);
  }

  /* Main Content */
  .main-content {
    flex: 1;
    padding: var(--spacing-xl);
    overflow-y: auto;
    margin-left: 280px;
    background-color: var(--background-secondary);
  }

  /* Auth Container */
  .auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: var(--background-secondary);
  }

  /* Loading Screen */
  .loading-screen {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: var(--background-secondary);
  }

  .loading-content {
    text-align: center;
    color: var(--text-primary);
  }

  .loading-spinner {
    width: 60px;
    height: 60px;
    border: 4px solid var(--border-color);
    border-top: 4px solid var(--accent-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto var(--spacing-xl);
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .loading-content h2 {
    margin: 0 0 var(--spacing-sm) 0;
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-semibold);
  }

  .loading-content p {
    margin: 0;
    opacity: 0.8;
    font-size: var(--font-size-base);
    color: var(--text-secondary);
  }
</style> 