<script>
  import { Router, Link, Route } from 'svelte-routing';
  import { fly, fade } from 'svelte/transition';
  import './app.css';
  import { useLocation } from 'svelte-routing';

  import Dashboard from './pages/Dashboard.svelte';
  import AddressAnalysis from './pages/AddressAnalysis.svelte';
  import BatchAnalysis from './pages/BatchAnalysis.svelte';
  import CaseManagement from './pages/CaseManagement.svelte';
  import Alerts from './pages/Alerts.svelte';
  import History from './pages/History.svelte';
  import Settings from './pages/Settings.svelte';

  export let url = '';

  let pageLoaded = false;

  const location = useLocation();

  let indicatorY = 0;
  let indicatorScale = 1;

  let navLink0, navLink1, navLink2, navLink3, navLink4;
  $: navLinks = [navLink0, navLink1, navLink2, navLink3, navLink4];

  $: activeIndex = navLinks.findIndex(link => link && typeof link.getAttribute === 'function' && link.getAttribute('aria-current') === 'page');

  $: {
    if (navLinks[activeIndex]) {
      const el = navLinks[activeIndex];
      indicatorY = el.offsetTop;
      indicatorScale = el.offsetHeight / 48;
    }
  }

  setTimeout(() => {
    pageLoaded = true;
  }, 100);
</script>

{#if pageLoaded}
  <Router {url}>
    <main in:fly={{ y: 20, duration: 500, delay: 200 }}>
      <div class="app-layout">
          <nav class="sidebar">
            <div class="sidebar-header">
              <img src="/patterns_logo.svg" alt="Patterns Logo" class="sidebar-logo" />
            </div>
            <div class="nav-links" style="position: relative;">
              {#if activeIndex >= 0}
                <div class="nav-indicator" style="transform: translateY({indicatorY}px) scaleY({indicatorScale});"></div>
              {/if}
              <Link to="/" class="nav-link" bind:this={navLink0}>Dashboard</Link>
              <Link to="/analysis" class="nav-link" bind:this={navLink1}>Address Analysis</Link>
              <Link to="/batch" class="nav-link" bind:this={navLink2}>Batch Analysis</Link>
              <Link to="/alerts" class="nav-link" bind:this={navLink3}>Alerts</Link>
              <Link to="/history" class="nav-link" bind:this={navLink4}>History</Link>
            </div>
            
            <div class="sidebar-footer">
            </div>
          </nav>

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

  .sidebar-header img {
    height: 2.5rem;
    width: auto;
    display: block;
    margin-bottom: var(--spacing-lg);
  }

  .nav-links {
    flex: 1;
    padding: var(--spacing-md) 0;
    display: flex;
    flex-direction: column;
    position: relative;
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
    position: relative;
    z-index: 2;
  }

  .nav-links :global(a.nav-link:visited) {
    color: var(--text-secondary);
  }

  .nav-links :global(a.nav-link:hover) {
    background-color: var(--background-secondary);
    color: var(--text-primary);
  }

  .nav-links :global(a.nav-link[aria-current='page']) {
    color: var(--accent-color);
    border-left: 3px solid var(--accent-color);
    background: none;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    letter-spacing: 0.01em;
    box-shadow: none;
    transition: color 0.2s, border-color 0.2s;
  }

  .sidebar-footer {
    padding: var(--spacing-lg);
    /* border-top: 1px solid var(--border-color); */
    background: var(--background-primary);
    margin-top: auto;
  }

  /* Main Content */
  .main-content {
    flex: 1;
    padding: var(--spacing-xl);
    overflow-y: auto;
    margin-left: 280px;
    background-color: var(--background-secondary);
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

  .sidebar-logo {
    height: 2.5rem;
    width: auto;
    display: block;
    margin-bottom: var(--spacing-lg);
  }

  .nav-indicator {
    position: absolute;
    left: 0;
    width: 3px;
    height: 48px;
    background: var(--accent-color);
    border-radius: 2px;
    transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
    z-index: 1;
  }
</style> 