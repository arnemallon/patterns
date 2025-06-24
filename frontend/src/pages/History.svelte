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
  <div class="page-header">
    <h1>Classification History</h1>
    <p>View and manage your Bitcoin address classification history.</p>
  </div>

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
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
  }

  .filter-group label {
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #2c3e50;
    font-size: 0.9rem;
  }

  .filter-group input,
  .filter-group select {
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-size: 0.9rem;
    font-family: inherit;
  }

  .filter-group input:focus,
  .filter-group select:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }

  /* History Container */
  .history-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .filters-grid {
      grid-template-columns: 1fr;
    }
  }
</style> 