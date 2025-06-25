<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import ClassificationHistory from '../components/ClassificationHistory.svelte';

  let searchTerm = '';
  let selectedFilter = 'all';
  let dateRange = 'all';

  function handleReclassify(event) {
    // Navigate to analysis page with the address
    window.location.href = `/analysis?address=${event.detail}`;
  }
</script>

<div class="history" in:fly={{ y: 20, duration: 500 }}>
  <!-- Filters -->
  <div class="filters-section">
    <div class="filters-grid">
      <div class="filter-group">
        <label for="search">Search Addresses:</label>
        <input 
          id="search" 
          type="text" 
          bind:value={searchTerm}
          placeholder="Search by address..."
        />
      </div>
      
      <div class="filter-group">
        <label for="classification-filter">Classification:</label>
        <select id="classification-filter" bind:value={selectedFilter}>
          <option value="all">All Classifications</option>
          <option value="suspicious">Suspicious</option>
          <option value="normal">Normal</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="date-filter">Date Range:</label>
        <select id="date-filter" bind:value={dateRange}>
          <option value="all">All Time</option>
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="year">This Year</option>
        </select>
      </div>
    </div>
  </div>

  <!-- History Component -->
  <div class="history-container">
    <ClassificationHistory 
      on:classify={handleReclassify}
    />
  </div>
</div>

<style>
  .history {
    max-width: 1200px;
    margin: 0 auto;
    font-family: var(--font-family);
    color: var(--text-primary);
    font-weight: var(--font-weight-normal);
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

  /* Filters Section */
  .filters-section {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
  }

  .filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
  }

  .filter-group {
    display: flex;
    flex-direction: column;
  }

  .filter-group label {
    margin-bottom: var(--spacing-xs);
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
  }

  .filter-group input,
  .filter-group select {
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-sm);
    font-family: var(--font-family);
    background: var(--background-primary);
    color: var(--text-primary);
    transition: border-color 0.2s;
  }

  .filter-group input:focus,
  .filter-group select:focus {
    outline: none;
    border-color: var(--accent-color);
  }

  /* History Container */
  .history-container {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    overflow: hidden;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .filters-grid {
      grid-template-columns: 1fr;
    }
  }
</style> 