<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import ClassificationHistory from '../components/ClassificationHistory.svelte';

  let searchTerm = '';
  let selectedFilter = 'all';
  let dateRange = 'all';
  let searchTimeout;

  function handleReclassify(event) {
    // Navigate to analysis page with the address
    window.location.href = `/analysis?address=${event.detail}`;
  }

  function handleSearchInput(event) {
    const value = event.target.value;
    searchTerm = value;
    
    // Clear existing timeout
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    // Debounce search - wait 500ms after user stops typing
    searchTimeout = setTimeout(() => {
      // The ClassificationHistory component will automatically reload due to reactive statement
    }, 500);
  }

  function handleFilterChange() {
    // Reset to first page when filters change
    // The ClassificationHistory component will automatically reload due to reactive statement
  }

  function clearAllFilters() {
    searchTerm = '';
    selectedFilter = 'all';
    dateRange = 'all';
  }

  function getCategoryLabel(filterValue) {
    const categories = [
      'Blackmail', 'Cyber-security Service', 'Darknet Market', 'Centralized Exchange',
      'P2P Financial Infrastructure Service', 'P2P Financial Service', 'Gambling',
      'Government Criminal Blacklist', 'Money Laundering', 'Ponzi Scheme',
      'Mining Pool', 'Tumbler', 'Individual Wallet'
    ];
    const index = parseInt(filterValue);
    return categories[index] || filterValue;
  }

  function getDateRangeLabel(dateRange) {
    const labels = {
      'today': 'Today',
      'week': 'This Week',
      'month': 'This Month',
      'year': 'This Year'
    };
    return labels[dateRange] || dateRange;
  }
</script>

<div class="history" in:fly={{ y: 20, duration: 500 }}>
  <!-- Filters -->
  <div class="filters-section">
    <div class="filters-header">
      <h3>Filters</h3>
      <button 
        class="clear-filters-btn" 
        class:disabled={!searchTerm && selectedFilter === 'all' && dateRange === 'all'}
        on:click={clearAllFilters}
        disabled={!searchTerm && selectedFilter === 'all' && dateRange === 'all'}
      >
        Clear Filters
      </button>
    </div>
    <div class="filters-grid">
      <div class="filter-group">
        <label for="search">Search Addresses:</label>
        <input 
          id="search" 
          type="text" 
          value={searchTerm}
          on:input={handleSearchInput}
          placeholder="Search by address..."
        />
      </div>
      
      <div class="filter-group">
        <label for="classification-filter">Classification:</label>
        <select 
          id="classification-filter" 
          bind:value={selectedFilter}
          on:change={handleFilterChange}
        >
          <option value="all">All Classifications</option>
          <option value="0">Blackmail</option>
          <option value="1">Cyber-security Service</option>
          <option value="2">Darknet Market</option>
          <option value="3">Centralized Exchange</option>
          <option value="4">P2P Financial Infrastructure Service</option>
          <option value="5">P2P Financial Service</option>
          <option value="6">Gambling</option>
          <option value="7">Government Criminal Blacklist</option>
          <option value="8">Money Laundering</option>
          <option value="9">Ponzi Scheme</option>
          <option value="10">Mining Pool</option>
          <option value="11">Tumbler</option>
          <option value="12">Individual Wallet</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="date-filter">Date Range:</label>
        <select 
          id="date-filter" 
          bind:value={dateRange}
          on:change={handleFilterChange}
        >
          <option value="all">All Time</option>
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="year">This Year</option>
        </select>
      </div>
    </div>
  </div>

  <!-- Active Filters Summary -->
  {#if searchTerm || selectedFilter !== 'all' || dateRange !== 'all'}
    <div class="active-filters" in:fade>
      <div class="filters-summary">
        <span class="filters-label">Active Filters:</span>
        {#if searchTerm}
          <span class="filter-tag">Search: "{searchTerm}"</span>
        {/if}
        {#if selectedFilter !== 'all'}
          <span class="filter-tag">Category: {getCategoryLabel(selectedFilter)}</span>
        {/if}
        {#if dateRange !== 'all'}
          <span class="filter-tag">Date: {getDateRangeLabel(dateRange)}</span>
        {/if}
      </div>
    </div>
  {/if}

  <!-- History Component -->
  <div class="history-container">
    <ClassificationHistory 
      {searchTerm}
      {selectedFilter}
      {dateRange}
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

  .filters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
  }

  .filters-header h3 {
    margin: 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }

  .clear-filters-btn {
    background: var(--background-secondary);
    color: var(--accent-color);
    border: 1px solid var(--accent-color);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-xs) var(--spacing-md);
    font-size: var(--font-size-sm);
    font-family: var(--font-family);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
  }

  .clear-filters-btn:hover {
    background: var(--accent-color);
    color: white;
  }

  .clear-filters-btn:disabled,
  .clear-filters-btn.disabled {
    background: var(--border-color);
    color: var(--text-secondary);
    border-color: var(--border-color);
    cursor: not-allowed;
    opacity: 0.8;
  }

  .clear-filters-btn:disabled:hover,
  .clear-filters-btn.disabled:hover {
    background: var(--border-color);
    color: var(--text-secondary);
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

  /* Active Filters */
  .active-filters {
    background: var(--background-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
  }

  .filters-summary {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    flex-wrap: wrap;
  }

  .filters-label {
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
  }

  .filter-tag {
    background: var(--accent-color);
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
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