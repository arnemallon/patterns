<script>
  import { onMount, createEventDispatcher, onDestroy } from 'svelte';
  import { apiService } from '../services/api.js';
  import { fly, fade, scale } from 'svelte/transition';
  
  let classifications = [];
  let loading = true;
  let error = null;
  let intervalId;
  
  // Pagination state
  let currentPage = 1;
  let limit = 10;
  let totalItems = 0;
  $: totalPages = Math.ceil(totalItems / limit);
  
  const dispatch = createEventDispatcher();
  
  onMount(async () => {
    await loadHistory();
    intervalId = setInterval(loadHistory, 10000); // Poll every 10 seconds
  });

  onDestroy(() => {
    if (intervalId) {
      clearInterval(intervalId);
    }
  });
  
  export async function loadHistory(resetPage = false) {
    if (resetPage) {
      currentPage = 1;
    }

    loading = true;
    error = null;
    try {
      const offset = (currentPage - 1) * limit;
      const response = await apiService.getHistory(limit, offset);
      classifications = response.classifications;
      totalItems = response.total;
    } catch (err) {
      error = err.message || 'Failed to load history';
    } finally {
      loading = false;
    }
  }

  function getCategoryDescription(prediction) {
    const categories = [
      'Blackmail', 'Cyber-security Service', 'Darknet Market', 'Centralized Exchange',
      'P2P Financial Infrastructure Service', 'P2P Financial Service', 'Gambling',
      'Government Criminal Blacklist', 'Money Laundering', 'Ponzi Scheme',
      'Mining Pool', 'Tumbler', 'Individual Wallet'
    ];
    const index = Math.round(prediction);
    const clampedIndex = Math.max(0, Math.min(12, index));
    return categories[clampedIndex];
  }
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleString('en-US', { 
        year: 'numeric', month: 'short', day: 'numeric', 
        hour: 'numeric', minute: '2-digit' 
    });
  }
  
  function formatAddress(address) {
    return `${address.substring(0, 12)}...${address.substring(address.length - 8)}`;
  }

  function handleAddressClick(address) {
    dispatch('classify', address);
  }

  function nextPage() {
    if (currentPage < totalPages) {
      currentPage++;
      loadHistory();
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
      loadHistory();
    }
  }
</script>

<div class="history-container" in:fly={{ y: 20, duration: 300 }}>
    <div class="header">
        <h2>Classification History</h2>
        {#if loading}
          <div class="loading-indicator">
            <div class="loading-spinner"></div>
            <span>Updating...</span>
          </div>
        {/if}
    </div>
  
  {#if error}
    <div class="error-display" in:fly={{ y: 20, duration: 300 }} out:fly={{ y: -20, duration: 200 }}>
      {error}
    </div>
  {/if}

  <div class="table-container">
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Address</th>
                <th>Category</th>
                <th>Confidence</th>
            </tr>
        </thead>
        <tbody>
            {#if loading && classifications.length === 0}
                {#each Array(5) as _, i}
                  <tr class="skeleton-row" in:fly={{ y: 20, duration: 300, delay: i * 100 }}>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                  </tr>
                {/each}
            {:else if classifications.length === 0}
                 <tr><td colspan="4" class="status-cell">No history found.</td></tr>
            {:else}
                {#each classifications as item, i}
                    <tr 
                      class="history-item" 
                      on:click={() => handleAddressClick(item.address)} 
                      title="Click to re-classify this address"
                      in:fly={{ y: 20, duration: 300, delay: i * 50 }}
                      out:fly={{ y: -20, duration: 200 }}
                    >
                        <td class="date-cell">{formatDate(item.created_at)}</td>
                        <td><code title={item.address}>{formatAddress(item.address)}</code></td>
                        <td class="category-col">{getCategoryDescription(item.classification)}</td>
                        <td>{(item.confidence * 100).toFixed(1)}%</td>
                    </tr>
                {/each}
            {/if}
        </tbody>
    </table>
  </div>

  {#if totalPages > 1}
    <div class="pagination-controls" in:fly={{ y: 20, duration: 300 }}>
        <button on:click={prevPage} disabled={currentPage === 1 || loading}>
            &larr; Previous
        </button>
        <span>Page {currentPage} of {totalPages}</span>
        <button on:click={nextPage} disabled={currentPage >= totalPages || loading}>
            Next &rarr;
        </button>
    </div>
  {/if}
</div>

<style>
  .history-container {
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    background: var(--background-primary);
    color: var(--text-primary);
    font-family: var(--font-family);
    font-weight: var(--font-weight-normal);
  }

  .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--spacing-lg);
      border-bottom: 1px solid var(--border-color);
      background: var(--background-primary);
  }

  h2 {
    font-size: var(--font-size-lg);
    margin: 0;
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }

  .loading-indicator {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
  }

  .loading-spinner {
    width: 12px;
    height: 12px;
    border: 2px solid transparent;
    border-top: 2px solid var(--accent-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .table-container {
      width: 100%;
      background: var(--background-primary);
  }

  table {
      width: 100%;
      border-collapse: collapse;
      font-size: var(--font-size-sm);
      background: var(--background-primary);
  }

  th, td {
      padding: var(--spacing-md);
      border-bottom: 1px solid var(--border-color);
      text-align: left;
  }
  
  th {
      color: var(--text-secondary);
      font-weight: var(--font-weight-medium);
      background: var(--background-secondary);
      text-transform: uppercase;
      letter-spacing: 0.03em;
  }
  
  tr:nth-child(even) td {
      background: var(--background-secondary);
  }
  
  tr:nth-child(odd) td {
      background: var(--background-primary);
  }
  
  .confidence-col {
      color: var(--accent-color);
      font-weight: var(--font-weight-medium);
  }
  
  .date-cell {
      white-space: nowrap;
      color: var(--text-secondary);
  }

  .status-cell {
      color: var(--text-tertiary);
      text-align: center;
      padding: var(--spacing-lg);
  }

  .error-display {
    padding: 1rem 1.5rem;
    background-color: #f8d7da;
    color: #721c24;
    animation: shake 0.5s ease-in-out;
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }

  /* Skeleton Loading Styles */
  .skeleton-row {
    animation: pulse 1.5s ease-in-out infinite;
  }

  .skeleton-cell {
    height: 1.2em;
    background: var(--background-tertiary);
    border-radius: var(--border-radius-sm);
    animation: shimmer 1.5s infinite;
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  .history-item {
    cursor: pointer;
    transition: all 0.2s;
  }

  .history-item:hover {
    background-color: #f8f9fa;
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
    background: var(--background-primary);
    border-top: 1px solid var(--border-color);
  }

  .pagination-controls button {
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

  .pagination-controls button:disabled {
    background: var(--border-color);
    color: var(--text-primary);
    font-weight: var(--font-weight-medium);
    opacity: 0.7;
    border-color: var(--border-color);
    cursor: not-allowed;
  }
  
  .pagination-controls span {
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
  }

  .category-col {
      color: var(--accent-color);
      font-weight: var(--font-weight-medium);
  }
</style> 