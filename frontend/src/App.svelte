<script>
  import { onMount } from 'svelte';
  import { Router, Link, Route } from 'svelte-routing';
  import { fly, fade } from 'svelte/transition';
  
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
              <button class="logout-btn" on:click={handleLogout}>
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
  :global(body) {
    margin: 0;
    background-color: #f8f9fa;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #212529;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* App Layout */
  .app-layout {
    display: flex;
    min-height: 100vh;
  }

  /* Sidebar */
  .sidebar {
    width: 280px;
    background: #f8f9fa;
    color: #495057;
    display: flex;
    flex-direction: column;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    border-right: 1px solid #e9ecef;
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 100;
  }

  .sidebar-header {
    padding: 2rem 1.5rem 1rem;
    border-bottom: 1px solid #e9ecef;
    background: #ffffff;
  }

  .sidebar-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .nav-links {
    flex: 1;
    padding: 1rem 0;
    display: flex;
    flex-direction: column;
  }

  .nav-links :global(a.nav-link) {
    display: flex;
    align-items: center;
    padding: 0.85rem 1.5rem;
    color: #495057; /* Default link color */
    text-decoration: none !important; /* Remove underline */
    transition: all 0.2s ease;
    border-left: 3px solid transparent;
    font-weight: 500;
    margin: 0.2rem 0;
  }

  .nav-links :global(a.nav-link:visited) {
    color: #495057; /* Visited link color */
  }

  .nav-links :global(a.nav-link:hover) {
    background-color: #e9ecef;
    color: #2c3e50;
  }

  .nav-links :global(a.nav-link.active) {
    background-color: #e9ecef;
    border-left-color: #007bff;
    color: #007bff;
    font-weight: 600;
  }

  .nav-icon {
    margin-right: 0.75rem;
    font-size: 0.9rem;
    width: 20px;
    text-align: center;
    font-weight: 600;
    color: #6c757d;
  }

  .sidebar-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid #e9ecef;
    background: #ffffff;
    margin-top: auto;
  }

  .user-info {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
  }

  .user-avatar {
    margin-right: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: #6c757d;
  }

  .user-name {
    font-weight: 500;
    color: #2c3e50;
  }

  .logout-btn {
    width: 100%;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    color: #495057;
    padding: 0.5rem;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    font-weight: 500;
  }

  .logout-btn:hover {
    background: #e9ecef;
    color: #2c3e50;
  }

  /* Main Content */
  .main-content {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
    margin-left: 280px; /* Same as sidebar width */
  }

  /* Auth Container */
  .auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  /* Loading Screen */
  .loading-screen {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .loading-content {
    text-align: center;
    color: white;
  }

  .loading-spinner {
    width: 60px;
    height: 60px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 2rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .loading-content h2 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    font-weight: 600;
  }

  .loading-content p {
    margin: 0;
    opacity: 0.8;
    font-size: 1rem;
  }

  /* Global smooth scrolling */
  :global(html) {
    scroll-behavior: smooth;
  }

  /* Global transition for all interactive elements */
  :global(button, input, select, textarea) {
    transition: all 0.2s ease-in-out;
  }

  /* Global focus styles */
  :global(*:focus) {
    outline: 2px solid #007bff;
    outline-offset: 2px;
  }

  /* Global selection styles */
  :global(::selection) {
    background-color: #007bff;
    color: white;
  }
</style> 